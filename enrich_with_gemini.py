import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import os
from dotenv import load_dotenv
import time
import json
import re

# --- NLTK Resource Download ---
# Tenta baixar os recursos necessários. Se já existirem, não fará nada.
# É mais robusto do que tentar find() e depois capturar um DownloadError específico
# que pode ter mudado de nome entre versões do NLTK.
try:
    print("Checking/downloading NLTK resources (vader_lexicon, punkt)...")
    nltk.download('vader_lexicon', quiet=True) # quiet=True suprime a saída se já estiver baixado
    nltk.download('punkt', quiet=True)
    print("NLTK resources checked/downloaded.")
except Exception as e:
    print(f"An error occurred during NLTK resource download: {e}")
    print("Please ensure you can connect to the internet to download NLTK resources,")
    print("or download them manually using: import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')")
    # Você pode decidir sair aqui se os recursos forem críticos e não puderem ser baixados
    # exit()

# --- Load environment variables (still useful if you keep Gemini for other tasks) ---
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# --- VADER Sentiment Analyzer ---
vader_analyzer = SentimentIntensityAnalyzer()

# --- Gemini Model Configuration (if still used for other tasks) ---
USE_GEMINI_FOR_RFQ_AND_CAPABILITIES = True # Set to False to disable Gemini calls

if USE_GEMINI_FOR_RFQ_AND_CAPABILITIES:
    if not GOOGLE_API_KEY:
        print("Warning: Google API Key not found, but USE_GEMINI_FOR_RFQ_AND_CAPABILITIES is True.")
        print("Gemini calls for RFQ and Capabilities will fail. Set USE_GEMINI_FOR_RFQ_AND_CAPABILITIES to False or provide API Key.")
        # We can let it proceed and Gemini calls will fail gracefully, or exit:
        # exit()
    else:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        generation_config_gemini = {
            "temperature": 0.5,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 1024,
        }
        safety_settings_gemini = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        MODEL_NAME_GEMINI = "models/gemini-2.0-flash-lite"
        try:
            gemini_model = genai.GenerativeModel(
                model_name=MODEL_NAME_GEMINI,
                generation_config=generation_config_gemini,
                safety_settings=safety_settings_gemini
            )
            print(f"Successfully initialized Gemini model: {MODEL_NAME_GEMINI}")
        except Exception as e:
            print(f"Error initializing Gemini model {MODEL_NAME_GEMINI}: {e}")
            print("Gemini calls for RFQ and Capabilities will likely fail.")
            USE_GEMINI_FOR_RFQ_AND_CAPABILITIES = False # Disable if model init fails


def clean_gemini_json_response(text_response): # Still needed if Gemini is used
    if not text_response: return "{}"
    match_markdown = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text_response, re.DOTALL)
    if match_markdown: json_str = match_markdown.group(1)
    else:
        match_direct = re.search(r'(\{.*?\})', text_response, re.DOTALL)
        if match_direct: json_str = match_direct.group(1)
        else: return "{}"
    try:
        json.loads(json_str); return json_str
    except json.JSONDecodeError: return "{}"

def get_gemini_response_with_delay(prompt_text): # Still needed if Gemini is used
    if not USE_GEMINI_FOR_RFQ_AND_CAPABILITIES or not GOOGLE_API_KEY or 'gemini_model' not in globals():
        print("DEBUG: Gemini call skipped (not configured or disabled).")
        return "{}"

    max_retries = 3
    initial_retry_delay_seconds = 5
    DELAY_BETWEEN_CALLS_SECONDS = 2.1 # For 30 RPM
    current_retry_delay = initial_retry_delay_seconds

    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(prompt_text)
            time.sleep(DELAY_BETWEEN_CALLS_SECONDS)
            if response.candidates and response.candidates[0].content.parts:
                return clean_gemini_json_response(response.text)
            return "{}"
        except Exception as e:
            print(f"Error calling Gemini API (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(DELAY_BETWEEN_CALLS_SECONDS)
            if "429" in str(e) or "rate limit" in str(e).lower():
                current_retry_delay += (attempt + 1) * 2
            if attempt < max_retries - 1:
                print(f"Waiting {current_retry_delay:.2f} seconds before retrying...")
                time.sleep(current_retry_delay)
            else:
                return "{}"

def get_vader_sentiment_analysis(text):
    if not text or pd.isna(text):
        # Return a structure consistent with what Gemini was producing for sentiment
        return {"sentiment": "Not specified", "keywords": [], "vader_compound": 0.0}

    vs = vader_analyzer.polarity_scores(text)
    compound_score = vs['compound']

    if compound_score >= 0.05:
        sentiment_label = "Positive"
    elif compound_score <= -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    # VADER doesn't do keyword extraction. We'll return an empty list.
    # For keywords, you might consider TextBlob noun_phrases or a dedicated keyword extractor.
    return {
        "sentiment": sentiment_label,
        "keywords": [], # VADER doesn't provide keywords directly
        "vader_compound": round(compound_score, 4),
        "vader_positive": round(vs['pos'], 4),
        "vader_negative": round(vs['neg'], 4),
        "vader_neutral": round(vs['neu'], 4)
    }

# --- Load DataFrames ---
try:
    df_users = pd.read_csv('user_details.csv')
    df_interactions = pd.read_csv('marketing_interactions.csv')
except FileNotFoundError as e:
    print(f"Error: CSV file not found. {e}. Please run thomas_data.py first.")
    exit()

# Initialize new columns
df_users['vader_sentiment_analysis_json'] = "{}" # For VADER results
if USE_GEMINI_FOR_RFQ_AND_CAPABILITIES:
    df_users['gemini_supplier_capability_summary_json'] = "{}"
    df_interactions['gemini_rfq_analysis_json'] = "{}"
else: # Create empty columns if Gemini is disabled, to prevent errors if Power BI expects them
    df_users['gemini_supplier_capability_summary_json'] = "{}"
    df_interactions['gemini_rfq_analysis_json'] = "{}"


# --- Define Slices/Batches for Processing ---
BATCH_SIZE = 50 # Process N eligible items from each category per round. Increased because VADER is fast.

user_feedback_indices = df_users[df_users['user_feedback_text'].notna()].index.tolist()
supplier_capability_indices = df_users[
    df_users['supplier_capabilities_text'].notna() & (df_users['user_type'] == 'Supplier')
].index.tolist()
rfq_interaction_indices = df_interactions[
    (df_interactions['event_name'] == 'RFQ Submitted') & (df_interactions['interaction_details_text'].notna())
].index.tolist()

ptr_feedback, ptr_capability, ptr_rfq = 0, 0, 0
processed_total_api_calls = 0 # For Gemini calls if any
processed_total_vader_analyses = 0

print(f"Starting round-robin processing with BATCH_SIZE = {BATCH_SIZE}")
print(f"Eligible for User Feedback (VADER): {len(user_feedback_indices)}")
if USE_GEMINI_FOR_RFQ_AND_CAPABILITIES:
    print(f"Eligible for Supplier Capability (Gemini): {len(supplier_capability_indices)}")
    print(f"Eligible for RFQ Interaction (Gemini): {len(rfq_interaction_indices)}")

# --- Round-Robin Processing Loop ---
while True:
    items_processed_this_round = 0

    # 1. Process User Feedback with VADER
    batch_end_feedback = min(ptr_feedback + BATCH_SIZE, len(user_feedback_indices))
    for i in range(ptr_feedback, batch_end_feedback):
        idx = user_feedback_indices[i]
        row = df_users.loc[idx]
        # print(f"Analyzing User Feedback (VADER): user_id {row['user_id']} (Item {ptr_feedback + 1}/{len(user_feedback_indices)})")
        vader_result = get_vader_sentiment_analysis(row['user_feedback_text'])
        df_users.at[idx, 'vader_sentiment_analysis_json'] = json.dumps(vader_result)
        items_processed_this_round += 1
        processed_total_vader_analyses +=1
    ptr_feedback = batch_end_feedback
    if ptr_feedback % (BATCH_SIZE * 5) == 0 and ptr_feedback > 0 : # Print progress every N batches
        print(f"VADER: Processed {ptr_feedback}/{len(user_feedback_indices)} user feedbacks.")


    if USE_GEMINI_FOR_RFQ_AND_CAPABILITIES:
        # 2. Process Supplier Capabilities with Gemini
        batch_end_capability = min(ptr_capability + BATCH_SIZE, len(supplier_capability_indices))
        for i in range(ptr_capability, batch_end_capability):
            idx = supplier_capability_indices[i]
            row = df_users.loc[idx]
            print(f"\nAnalyzing Supplier Capabilities (Gemini): user_id {row['user_id']} (Item {ptr_capability + 1}/{len(supplier_capability_indices)})")
            prompt_capabilities = f"""
            Based on the following list of supplier capabilities, generate a concise summary (1-2 sentences)
            and identify up to 3 main service categories offered.
            Provide the response ONLY as a valid JSON object.
            The JSON object must have: "capability_summary" (string) and "main_categories" (list of strings).
            Supplier capabilities: "{row['supplier_capabilities_text']}"
            Respond strictly in English.
            """
            response_text = get_gemini_response_with_delay(prompt_capabilities)
            df_users.at[idx, 'gemini_supplier_capability_summary_json'] = response_text
            items_processed_this_round += 1
            processed_total_api_calls +=1
        ptr_capability = batch_end_capability

        # 3. Process RFQ Interactions with Gemini
        batch_end_rfq = min(ptr_rfq + BATCH_SIZE, len(rfq_interaction_indices))
        for i in range(ptr_rfq, batch_end_rfq):
            idx = rfq_interaction_indices[i]
            row = df_interactions.loc[idx]
            print(f"\nAnalyzing RFQ Interaction (Gemini): interaction_id {row['interaction_id']} (Item {ptr_rfq + 1}/{len(rfq_interaction_indices)})")
            prompt_rfq = f"""
            Analyze the RFQ text.
            1. Identify main service/product.
            2. Assess implied urgency: 'High', 'Medium', 'Low', or 'Not specified'.
               - 'High' examples: "ASAP", "urgent", "tight deadline".
               - 'Medium' examples: "soon", "standard lead time".
               - 'Low' examples: "budgetary", "exploring options".
            3. Extract up to 5 key specifications.
            Provide response ONLY as a valid JSON object with keys: "service_product_type", "implied_urgency", "key_specifications" (list of strings).
            RFQ text: "{row['interaction_details_text']}"
            Respond strictly in English.
            """
            response_text = get_gemini_response_with_delay(prompt_rfq)
            df_interactions.at[idx, 'gemini_rfq_analysis_json'] = response_text
            items_processed_this_round += 1
            processed_total_api_calls +=1
        ptr_rfq = batch_end_rfq

    # Check if all processing is done
    all_feedback_done = ptr_feedback >= len(user_feedback_indices)
    all_capabilities_done = not USE_GEMINI_FOR_RFQ_AND_CAPABILITIES or ptr_capability >= len(supplier_capability_indices)
    all_rfqs_done = not USE_GEMINI_FOR_RFQ_AND_CAPABILITIES or ptr_rfq >= len(rfq_interaction_indices)

    if all_feedback_done and all_capabilities_done and all_rfqs_done:
        print("\nAll eligible items processed.")
        break
    elif items_processed_this_round == 0 and (not all_feedback_done or not all_capabilities_done or not all_rfqs_done):
        # This case handles if one list finishes much earlier than others in a round
        # and no items were processed from the remaining lists in that specific partial batch.
        # We continue to ensure other lists get a chance.
        # A items_processed_this_round == 0 check AFTER all processing attempts in a full cycle
        # (like the one originally there) is a more robust stop for "nothing left at all".
        # For now, the combined condition above should be sufficient.
        print(f"\n--- End of Round --- Processed {processed_total_vader_analyses} VADER analyses. Processed {processed_total_api_calls} Gemini API calls. ---")


# --- Save Final DataFrames ---
df_users.to_csv('user_details_enriched.csv', index=False, encoding='utf-8-sig')
print(f"\nuser_details_enriched.csv saved successfully. VADER analyses: {processed_total_vader_analyses}.")
if USE_GEMINI_FOR_RFQ_AND_CAPABILITIES:
    print(f"Gemini supplier capability analyses: {ptr_capability}.")


df_interactions.to_csv('marketing_interactions_enriched.csv', index=False, encoding='utf-8-sig')
if USE_GEMINI_FOR_RFQ_AND_CAPABILITIES:
    print(f"marketing_interactions_enriched.csv saved successfully. Gemini RFQ analyses: {ptr_rfq}.")
else:
    print(f"marketing_interactions_enriched.csv saved (no Gemini RFQ analysis performed).")


print(f"\nTotal VADER analyses performed: {processed_total_vader_analyses}")
if USE_GEMINI_FOR_RFQ_AND_CAPABILITIES:
    print(f"Total Gemini API calls made (approx): {processed_total_api_calls}")
print("Enrichment process completed!")