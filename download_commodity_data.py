import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

# --- Configuration ---
COMMODITIES_TO_TRACK = {
    "Steel_Futures_HRC": "HRC=F",
    "Aluminum_Futures_LME": "ALI=F",
    "Copper_Futures_HG": "HG=F",
    "Crude_Oil_Futures_WTI": "CL=F",
    "Steel_ETF_SLX": "SLX",
    "Industrial_Sector_ETF_XLI": "XLI"
}
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=5*365) # Ajuste para o período desejado, ex: 1 ano para testes mais rápidos
OUTPUT_FILENAME = "commodity_prices_en.csv"

def download_commodity_data(tickers_dict, start_date, end_date):
    all_commodity_data_list = [] # Renomeado para evitar confusão com o DataFrame final
    print(f"Downloading data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n")

    for friendly_name, ticker_symbol in tickers_dict.items():
        print(f"Fetching data for: {friendly_name} ({ticker_symbol})...")
        try:
            ticker_obj = yf.Ticker(ticker_symbol)
            # Usar 'history' pode dar mais controle e às vezes dados mais limpos para futuros
            ticker_data_hist = ticker_obj.history(start=start_date, end=end_date, auto_adjust=False) # auto_adjust=False mantém Open, High, Low, Close, Adj Close, Volume

            if ticker_data_hist.empty:
                print(f"  No data found for {ticker_symbol} for the given period.")
                continue
            
            # Selecionamos 'Close' e garantimos que o índice seja DatetimeIndex (geralmente já é)
            # O índice do yf.history() é nomeado 'Date'
            ticker_data_processed = ticker_data_hist[['Close']].copy()
            ticker_data_processed.rename(columns={'Close': friendly_name}, inplace=True)
            
            all_commodity_data_list.append(ticker_data_processed)
            print(f"  Successfully fetched {len(ticker_data_processed)} data points for {friendly_name}.")

        except Exception as e:
            print(f"  Could not download data for {ticker_symbol}. Error: {e}")
    
    if not all_commodity_data_list:
        print("\nNo commodity data was downloaded.")
        return pd.DataFrame()

    # Merge all DataFrames on their Date index
    if len(all_commodity_data_list) > 0:
        df_merged = all_commodity_data_list[0]
        for i in range(1, len(all_commodity_data_list)):
            df_merged = df_merged.join(all_commodity_data_list[i], how='outer')
        
        # O índice de df_merged agora é o 'Date' (DatetimeIndex)
        # Vamos transformá-lo em uma coluna chamada 'Date'
        df_merged.reset_index(inplace=True) # A coluna de data agora se chama 'Date'

        # Certificar que 'Date' é o nome e converter para formato de data (sem hora)
        if 'Date' in df_merged.columns:
            df_merged['Date'] = pd.to_datetime(df_merged['Date']).dt.date
        else:
            # Se o reset_index nomeou a coluna de data como 'index' por algum motivo
            if 'index' in df_merged.columns:
                 df_merged.rename(columns={'index': 'Date'}, inplace=True)
                 df_merged['Date'] = pd.to_datetime(df_merged['Date']).dt.date
            else:
                print("CRITICAL ERROR: 'Date' column not found after reset_index!")
                return pd.DataFrame()

        # Forward fill e backward fill para tratar NaNs de dias não negociados
        df_merged = df_merged.ffill().bfill()
        
        print(f"\nSuccessfully merged data for {len(df_merged.columns)-1} commodities.")
        return df_merged
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    print("--- Commodity Data Downloader ---")
    output_file_path = OUTPUT_FILENAME
    df_commodities = download_commodity_data(COMMODITIES_TO_TRACK, START_DATE, END_DATE)

    if not df_commodities.empty:
        print("\n--- Columns in df_commodities before melt ---")
        print(list(df_commodities.columns))
        print("--- Sample of df_commodities before melt (first 2 rows) ---")
        print(df_commodities.head(2))
        print("----------------------------------------------")

        # Agora o melt deve funcionar pois 'Date' é uma coluna regular
        try:
            df_melted = df_commodities.melt(id_vars=['Date'], var_name='Commodity', value_name='Price')
            df_melted.dropna(subset=['Price'], inplace=True) # Remove any rows that might still be all NaN for Price
            df_melted.to_csv(output_file_path, index=False, encoding='utf-8-sig')
            print(f"\nCommodity data saved to '{output_file_path}' in long format.")
            print(f"Total rows in melted data: {len(df_melted)}")
        except KeyError as e_melt:
            print(f"KeyError during melt operation: {e_melt}")
            print("This usually means the 'Date' column was not found or named correctly in df_commodities.")
            print("Please check the 'Columns in df_commodities before melt' output above.")
        except Exception as e_general:
            print(f"An unexpected error occurred during melt or save: {e_general}")

    else:
        print("No commodity data to save.")
        
    print("\n--- Download Process Finished ---")
