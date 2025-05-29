import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time # Para adicionar delays e respeitar rate limits
import json # Para parsear o JSON da resposta, se necessário no Python
import re # Para limpeza de JSON

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a API Key do Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("API Key do Google não encontrada. Verifique seu arquivo .env")
genai.configure(api_key=GOOGLE_API_KEY)

# Configurações do modelo Gemini
generation_config = {
    "temperature": 0.6, # Um pouco menos criativo para respostas mais consistentes
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Certifique-se de usar um modelo que tenha um nível gratuito ou que você tenha configurado faturamento
# "models/gemini-1.5-flash-latest" é uma boa opção.
MODEL_NAME = "models/gemini-2.0-flash-lite"
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=generation_config,
    safety_settings=safety_settings
)
print(f"Usando o modelo Gemini: {MODEL_NAME}")

def clean_gemini_json_response(text_response):
    if not text_response:
        return "{}"

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text_response, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        match_simple = re.search(r'(\{.*?\})', text_response, re.DOTALL)
        if match_simple:
            json_str = match_simple.group(1)
        else:
            print(f"DEBUG: Resposta do Gemini não parece conter JSON: {text_response[:200]}...")
            return "{}"
    try:
        json.loads(json_str) # Valida se é JSON
        return json_str
    except json.JSONDecodeError:
        print(f"DEBUG: Conteúdo extraído não é JSON válido após limpeza: {json_str[:200]}...")
        return "{}"

def get_gemini_response(prompt_text):
    max_retries = 3
    # Este será o delay em caso de retry por erro
    initial_retry_delay_seconds = 5 # Pode manter ou ajustar

    # Este será o delay APÓS cada chamada bem-sucedida para controlar o RPM
    # Para 30 RPM, precisamos de pelo menos 2 segundos entre as chamadas.
    # Usar 2.1 ou 2.2 para uma pequena margem.
    DELAY_BETWEEN_CALLS_SECONDS = 2.1 # Ajuste este valor!

    current_retry_delay = initial_retry_delay_seconds

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt_text)

            # Adiciona o delay APÓS a chamada, antes de retornar
            # Isso garante que a próxima chamada não aconteça muito rapidamente.
            time.sleep(DELAY_BETWEEN_CALLS_SECONDS) # <<<< ADICIONADO AQUI

            if response.candidates and response.candidates[0].content.parts:
                cleaned_response = clean_gemini_json_response(response.text)
                return cleaned_response
            else:
                print(f"DEBUG: Resposta do Gemini vazia ou malformada: {response}")
                # Mesmo com resposta malformada, o delay já ocorreu
                return "{}"
        except Exception as e:
            print(f"Erro ao chamar a API do Gemini (tentativa {attempt + 1}/{max_retries}): {e}")
            if "429" in str(e):
                print("Erro de Rate Limit (429). Aumentando o delay de retry...")
                current_retry_delay *= (attempt + 2) # Aumenta o delay de retry
            if attempt < max_retries - 1:
                print(f"Aguardando {current_retry_delay:.2f} segundos antes de tentar novamente...")
                time.sleep(current_retry_delay)
            else:
                print("Máximo de tentativas atingido. Falha ao obter resposta do Gemini.")
                return "{}"

# --- Processar user_details.csv ---
print("Processando user_details.csv...")
try:
    df_users = pd.read_csv('user_details.csv')
except FileNotFoundError:
    print("Erro: user_details.csv não encontrado. Execute thomas_data.py primeiro.")
    exit()

df_users['gemini_sentiment_analysis'] = "{}" # Inicializa com JSON vazio
df_users['gemini_supplier_capability_summary'] = "{}" # Inicializa com JSON vazio

# Ajuste SAMPLE_SIZE_USERS:
# 0 ou um número grande para processar todos.
# Um número pequeno para testes rápidos.
SAMPLE_SIZE_USERS = 0 # Define como 0 para processar todas as linhas elegíveis
processed_count_users = 0
total_user_rows_to_process = len(df_users[(df_users['user_feedback_text'].notna()) |
                                          (df_users['supplier_capabilities_text'].notna() & (df_users['user_type'] == 'Supplier'))])
print(f"Total de linhas de usuários elegíveis para processamento com Gemini: {total_user_rows_to_process}")


for index, row in df_users.iterrows():
    made_api_call = False
    if SAMPLE_SIZE_USERS > 0 and processed_count_users >= SAMPLE_SIZE_USERS:
        print(f"Atingido o limite de amostra de {SAMPLE_SIZE_USERS} para usuários. Interrompendo processamento de usuários.")
        break

    # 1. Análise de Sentimento do Feedback do Usuário
    if pd.notna(row['user_feedback_text']):
        prompt_sentiment = f"""
        Analyze the following user feedback and classify the predominant sentiment as 'Positive', 'Negative', or 'Neutral'.
        Also, extract up to 3 keywords or short phrases that summarize the feedback.
        Provide the response ONLY as a valid JSON object, with no additional text or Markdown formatting before or after.
        The JSON object must have the following structure:
        {{
          "sentiment": "YourSentimentHere (Positive/Negative/Neutral)",
          "keywords": ["keyword1", "keyword2", "keyword3"]
        }}

        User feedback: "{row['user_feedback_text']}"

        Respond in English.
        """
        print(f"\nAnalyzing feedback for user_id: {row['user_id']} (User {processed_count_users + 1}/{total_user_rows_to_process if SAMPLE_SIZE_USERS == 0 else SAMPLE_SIZE_USERS})...")
        response_text = get_gemini_response(prompt_sentiment)
        df_users.at[index, 'gemini_sentiment_analysis'] = response_text
        made_api_call = True

    # 2. Resumo das Capacidades do Fornecedor
    if pd.notna(row['supplier_capabilities_text']) and row['user_type'] == 'Supplier':
        prompt_capabilities = f"""
        Based on the following list of supplier capabilities, generate a concise summary (1-2 sentences)
        and identify up to 3 main service categories offered.
        Provide the response ONLY as a valid JSON object, with no additional text or Markdown formatting before or after.
        The JSON object must have the following structure:
        {{
          "capability_summary": "YourSummaryHere",
          "main_categories": ["category1", "category2", "category3"]
        }}

        Supplier capabilities: "{row['supplier_capabilities_text']}"

        Respond in English.
        """
        print(f"\nAnalyzing capabilities for supplier_id: {row['user_id']} (User {processed_count_users + 1}/{total_user_rows_to_process if SAMPLE_SIZE_USERS == 0 else SAMPLE_SIZE_USERS})...")
        response_text = get_gemini_response(prompt_capabilities)
        df_users.at[index, 'gemini_supplier_capability_summary'] = response_text
        made_api_call = True

    if made_api_call:
        processed_count_users += 1
        # O delay já está dentro de get_gemini_response

df_users.to_csv('user_details_enriched.csv', index=False, encoding='utf-8-sig')
print(f"\nuser_details_enriched.csv saved successfully! Processed {processed_count_users} user rows with Gemini.")


# --- Processar marketing_interactions.csv (Exemplo: Análise de RFQs) ---
print("\nProcessando marketing_interactions.csv...")
try:
    df_interactions = pd.read_csv('marketing_interactions.csv')
except FileNotFoundError:
    print("Erro: marketing_interactions.csv não encontrado. Execute thomas_data.py primeiro.")
    exit()

df_interactions['gemini_rfq_analysis'] = "{}" # Inicializa com JSON vazio

SAMPLE_SIZE_INTERACTIONS = 0 # Define como 0 para processar todas as linhas elegíveis
processed_count_interactions = 0
total_interaction_rows_to_process = len(df_interactions[(df_interactions['event_name'] == 'RFQ Submitted') &
                                                        (df_interactions['interaction_details_text'].notna())])
print(f"Total de interações RFQ elegíveis para processamento com Gemini: {total_interaction_rows_to_process}")


for index, row in df_interactions.iterrows():
    if SAMPLE_SIZE_INTERACTIONS > 0 and processed_count_interactions >= SAMPLE_SIZE_INTERACTIONS:
        print(f"Atingido o limite de amostra de {SAMPLE_SIZE_INTERACTIONS} para interações RFQ. Interrompendo processamento de interações.")
        break

    if row['event_name'] == 'RFQ Submitted' and pd.notna(row['interaction_details_text']):
        prompt_rfq = f"""
        Analyze the following Request for Quotation (RFQ) text.
        Identify the main type of service or product requested.
        Assess the implied urgency (if any) as 'Low', 'Medium', or 'High', or 'Not specified'.
        Extract any key specifications mentioned (e.g., material, quantity, dimensions).
        Provide the response ONLY as a valid JSON object, with no additional text or Markdown formatting before or after.
        The JSON object must have the following structure:
        {{
          "service_product_type": "YourAnalysisHere",
          "implied_urgency": "Low/Medium/High/Not specified",
          "key_specifications": ["spec1", "spec2"]
        }}

        RFQ text: "{row['interaction_details_text']}"

        Respond in English.
        """
        print(f"\nAnalyzing RFQ interaction_id: {row['interaction_id']} (Interaction {processed_count_interactions + 1}/{total_interaction_rows_to_process if SAMPLE_SIZE_INTERACTIONS == 0 else SAMPLE_SIZE_INTERACTIONS})...")
        response_text = get_gemini_response(prompt_rfq)
        df_interactions.at[index, 'gemini_rfq_analysis'] = response_text
        processed_count_interactions += 1
        # O delay já está dentro de get_gemini_response


df_interactions.to_csv('marketing_interactions_enriched.csv', index=False, encoding='utf-8-sig')
print(f"\nmarketing_interactions_enriched.csv saved successfully! Processed {processed_count_interactions} RFQ interactions with Gemini.")

print("\nProcessing with Gemini completed!")