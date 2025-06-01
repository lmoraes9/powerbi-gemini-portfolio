import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import os
from dotenv import load_dotenv
import time
import json
import re

# --- NLTK Resource Download ---
try:
    print("Checking/downloading NLTK resources (vader_lexicon, punkt)...")
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    print("NLTK resources checked/downloaded.")
except Exception as e:
    print(f"An error occurred during NLTK resource download: {e}. Please ensure NLTK resources are available.")

# --- Configuration ---
USE_GEMINI_FOR_ADVANCED_ANALYSIS = True # <<< SET TO TRUE AS REQUESTED
DELAY_BETWEEN_GEMINI_CALLS_SECONDS = 2.1
BATCH_SIZE_PER_CATEGORY = 5 # <<< REDUCED BATCH SIZE FOR FOCUSED TESTING of insights part

# --- Load environment variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# --- VADER Sentiment Analyzer ---
vader_analyzer = SentimentIntensityAnalyzer()

# --- Gemini Model Configuration (conditionally initialized) ---
gemini_model = None
if USE_GEMINI_FOR_ADVANCED_ANALYSIS:
    if not GOOGLE_API_KEY:
        print("CRITICAL WARNING: Google API Key not found, but USE_GEMINI_FOR_ADVANCED_ANALYSIS is True.")
        print("Gemini calls WILL FAIL. Set USE_GEMINI_FOR_ADVANCED_ANALYSIS to False or provide a valid API Key.")
        USE_GEMINI_FOR_ADVANCED_ANALYSIS = False # Force disable if no key
    else:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            generation_config_gemini = {"temperature": 0.4, "top_p": 1, "top_k": 1, "max_output_tokens": 2048} # Increased tokens for insights
            safety_settings_gemini = [
                {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"} for c in
                ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]
            ]
            # Try Gemma first as per previous discussion, if it fails due to quota, you might need to switch
            MODEL_NAME_GEMINI = "models/gemma-3-4b-it" # Or "models/gemini-1.5-flash-latest" if Gemma is problematic
            # MODEL_NAME_GEMINI = "models/gemini-1.5-flash-latest" # Fallback if Gemma is too restrictive

            gemini_model = genai.GenerativeModel(
                model_name=MODEL_NAME_GEMINI,
                generation_config=generation_config_gemini,
                safety_settings=safety_settings_gemini
            )
            print(f"Successfully initialized Gemini model: {MODEL_NAME_GEMINI}")
        except Exception as e:
            print(f"Error initializing Gemini model {MODEL_NAME_GEMINI}: {e}")
            print("Disabling Gemini for advanced analysis for this run.")
            USE_GEMINI_FOR_ADVANCED_ANALYSIS = False

def clean_gemini_json_response(text_response):
    if not text_response: return "{}"
    match_markdown = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text_response, re.DOTALL) # Regex to match object or array
    json_str = match_markdown.group(1) if match_markdown else \
               (re.search(r'(\{.*?\})|(\[.*?\])', text_response, re.DOTALL).group(0) if re.search(r'(\{.*?\})|(\[.*?\])', text_response, re.DOTALL) else None) # Try to find object or array
    if not json_str:
        # print(f"DEBUG (clean_fn): No JSON structure found in response: {text_response[:100]}")
        return "{}"
    try:
        json.loads(json_str) # Validate
        return json_str
    except json.JSONDecodeError:
        # print(f"DEBUG (clean_fn): Extracted content is not valid JSON after cleaning: {json_str[:100]}")
        return "{}"

def call_gemini_api(prompt_text, task_name="API Call"):
    if not USE_GEMINI_FOR_ADVANCED_ANALYSIS or not gemini_model:
        print(f"DEBUG ({task_name}): Gemini call skipped (not configured or disabled).")
        return "{}"
    max_retries = 2; initial_retry_delay = 3; current_retry_delay = initial_retry_delay
    print(f"\nAttempting Gemini {task_name}...")
    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(prompt_text)
            time.sleep(DELAY_BETWEEN_GEMINI_CALLS_SECONDS)
            if response.candidates and response.candidates[0].content.parts:
                # print(f"DEBUG ({task_name}): Raw Gemini Response part: {response.text[:300]}") # Print start of raw response
                cleaned = clean_gemini_json_response(response.text)
                # print(f"DEBUG ({task_name}): Cleaned Gemini Response: {cleaned[:300]}")
                return cleaned
            # print(f"DEBUG ({task_name}): Gemini response was empty or malformed (no parts).")
            return "{}"
        except Exception as e:
            print(f"Error calling Gemini API for {task_name} (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(DELAY_BETWEEN_GEMINI_CALLS_SECONDS)
            if "429" in str(e) or "rate limit" in str(e).lower(): current_retry_delay += (attempt + 1) * 2
            if attempt < max_retries - 1: time.sleep(current_retry_delay)
            else:
                print(f"Max retries reached for {task_name}.")
                return "{}"

def get_vader_sentiment_analysis_results(text):
    if not text or pd.isna(text):
        return {"sentiment_label": "Not specified", "keywords": [], "compound_score": 0.0, "positive_score":0.0, "negative_score":0.0, "neutral_score":0.0}
    vs = vader_analyzer.polarity_scores(text)
    label = "Neutral"
    if vs['compound'] >= 0.05: label = "Positive"
    elif vs['compound'] <= -0.05: label = "Negative"
    return {"sentiment_label": label, "keywords": [], "compound_score": round(vs['compound'], 4),
            "positive_score":round(vs['pos'],4), "negative_score":round(vs['neg'],4), "neutral_score":round(vs['neu'],4)}

# --- Load DataFrames ---
try:
    df_users = pd.read_csv('user_details_en.csv')
    df_interactions = pd.read_csv('marketing_interactions_en.csv')
    df_campaigns = pd.read_csv('campaign_details_en.csv')
except FileNotFoundError as e:
    print(f"Error: CSV file not found: {e}. Please run generate_mock_data_en.py first.")
    exit()

df_users['vader_sentiment_analysis_json'] = "{}"
df_users['gemini_supplier_capability_json'] = "{}"
df_interactions['gemini_rfq_analysis_json'] = "{}"

# --- Prepare for Round-Robin Processing ---
user_feedback_indices = df_users[df_users['user_feedback_text'].notna()].index.tolist()
supplier_capability_indices = df_users[df_users['supplier_capabilities_text'].notna() & (df_users['user_type'] == 'Supplier')].index.tolist() if USE_GEMINI_FOR_ADVANCED_ANALYSIS else []
rfq_interaction_indices = df_interactions[(df_interactions['event_name'] == 'RFQ Submitted') & (df_interactions['interaction_details_text'].notna())].index.tolist() if USE_GEMINI_FOR_ADVANCED_ANALYSIS else []

ptr_feedback, ptr_capability, ptr_rfq = 0, 0, 0
total_vader_processed, total_gemini_calls = 0, 0

print(f"Starting NLP enrichment. VADER for sentiment. Gemini for advanced analysis (if enabled: {USE_GEMINI_FOR_ADVANCED_ANALYSIS}).")
print(f"Batch size for Gemini tasks: {BATCH_SIZE_PER_CATEGORY}")

# --- Round-Robin Processing Loop for User Feedback (VADER) and optional Gemini tasks ---
# For focused testing of insights, we can temporarily skip these loops or run very small batches
run_initial_enrichment_loops = True # Set to False to quickly get to insights generation

if run_initial_enrichment_loops:
    while True:
        processed_in_current_round = 0
        vader_batch_size = BATCH_SIZE_PER_CATEGORY * 2
        batch_end_feedback = min(ptr_feedback + vader_batch_size, len(user_feedback_indices))
        for i in range(ptr_feedback, batch_end_feedback):
            idx = user_feedback_indices[i]; vader_result = get_vader_sentiment_analysis_results(df_users.loc[idx, 'user_feedback_text'])
            df_users.at[idx, 'vader_sentiment_analysis_json'] = json.dumps(vader_result)
            processed_in_current_round += 1; total_vader_processed += 1
        ptr_feedback = batch_end_feedback
        if ptr_feedback > 0 and (ptr_feedback % (vader_batch_size * 2) == 0 or ptr_feedback == len(user_feedback_indices)):
            print(f"... VADER sentiment processed for {ptr_feedback} users.")

        if USE_GEMINI_FOR_ADVANCED_ANALYSIS:
            batch_end_capability = min(ptr_capability + BATCH_SIZE_PER_CATEGORY, len(supplier_capability_indices))
            for i in range(ptr_capability, batch_end_capability):
                idx = supplier_capability_indices[i]; row = df_users.loc[idx]
                print(f"GEMINI (Caps): User {row['user_id']} ({ptr_capability+1}/{len(supplier_capability_indices)})")
                prompt_capabilities = f"""Analyze supplier capabilities: "{row['supplier_capabilities_text']}".
                Return JSON ONLY: {{"capability_summary": "concise summary (1-2 sentences)", "main_categories": ["cat1", "cat2", "cat3"]}}. Respond in English."""
                df_users.at[idx, 'gemini_supplier_capability_json'] = call_gemini_api(prompt_capabilities, "Supplier Capabilities")
                processed_in_current_round += 1; total_gemini_calls += 1
            ptr_capability = batch_end_capability

            batch_end_rfq = min(ptr_rfq + BATCH_SIZE_PER_CATEGORY, len(rfq_interaction_indices))
            for i in range(ptr_rfq, batch_end_rfq):
                idx = rfq_interaction_indices[i]; row = df_interactions.loc[idx]
                print(f"GEMINI (RFQ): Interaction {row['interaction_id']} ({ptr_rfq+1}/{len(rfq_interaction_indices)})")
                prompt_rfq = f"""Analyze RFQ: "{row['interaction_details_text']}".
                Return JSON ONLY: {{"service_product_type": "type", "implied_urgency": "High/Medium/Low/Not specified", "key_specifications": ["spec1", "spec2"]}}.
                Urgency hints: High (ASAP, urgent), Medium (soon), Low (budgetary). Respond in English."""
                df_interactions.at[idx, 'gemini_rfq_analysis_json'] = call_gemini_api(prompt_rfq, "RFQ Analysis")
                processed_in_current_round += 1; total_gemini_calls += 1
            ptr_rfq = batch_end_rfq

        all_feedback_done = ptr_feedback >= len(user_feedback_indices)
        all_capabilities_done = not USE_GEMINI_FOR_ADVANCED_ANALYSIS or ptr_capability >= len(supplier_capability_indices)
        all_rfqs_done = not USE_GEMINI_FOR_ADVANCED_ANALYSIS or ptr_rfq >= len(rfq_interaction_indices)

        if all_feedback_done and all_capabilities_done and all_rfqs_done:
            print("Initial enrichment loops completed.")
            break
        if processed_in_current_round == 0 and not (all_feedback_done and all_capabilities_done and all_rfqs_done):
            # This condition means one or more lists still have items, but the current batch size didn't pick any up.
            # This can happen if one list is much shorter. The main 'break' above will handle full completion.
            # print(f"--- End of Round (partial completion) ---")
            pass # Continue to next round
else:
    print("Skipping initial enrichment loops to focus on insights/tasks generation.")


# --- Generate Strategic Insights & Actionable Tasks (using Gemini if enabled) ---
df_strategic_insights = pd.DataFrame(columns=['insight_id', 'insight_title', 'insight_explanation'])
df_actionable_tasks = pd.DataFrame(columns=['task_id', 'task_description', 'task_importance'])

if USE_GEMINI_FOR_ADVANCED_ANALYSIS:
    print("\nGenerating Strategic Insights (Gemini)...")
    # 1. Aggregate data for insights
    num_total_rfqs = len(df_interactions[df_interactions['event_name'] == 'RFQ Submitted'])
    rfq_types_list = []
    for json_str in df_interactions['gemini_rfq_analysis_json'].dropna(): # Ensure we only process valid strings
        try: data = json.loads(json_str); rfq_types_list.append(data.get('service_product_type'))
        except: pass
    top_rfq_types = pd.Series([t for t in rfq_types_list if t]).value_counts().nlargest(3).to_dict() if rfq_types_list else {}

    supplier_cats_list = []
    for json_str in df_users['gemini_supplier_capability_json'].dropna():
        try: data = json.loads(json_str); supplier_cats_list.extend(data.get('main_categories', []))
        except: pass
    top_supplier_cats = pd.Series([c for c in supplier_cats_list if c]).value_counts().nlargest(3).to_dict() if supplier_cats_list else {}

    sentiments_list = []
    for json_str in df_users['vader_sentiment_analysis_json'].dropna():
        try: data = json.loads(json_str); sentiments_list.append(data.get('sentiment_label'))
        except: pass
    sentiment_distribution = pd.Series([s for s in sentiments_list if s]).value_counts(normalize=True).multiply(100).round(1).to_dict() if sentiments_list else {}

    summary_for_insights = f"""
    Business Data Summary:
    - Total RFQs Processed for Type: {len(rfq_types_list)} (out of {num_total_rfqs} total RFQs submitted)
    - Top 3 RFQ Service/Product Types: {top_rfq_types if top_rfq_types else 'N/A or No RFQs Analyzed'}
    - Top 3 Supplier Main Categories from Processed Suppliers: {top_supplier_cats if top_supplier_cats else 'N/A or No Suppliers Analyzed'}
    - User Feedback Sentiment Distribution (% of analyzed feedback): {sentiment_distribution if sentiment_distribution else 'N/A or No Feedback Analyzed'}
    - Total Campaigns: {len(df_campaigns)}
    - Average Campaign Budget: ${df_campaigns['campaign_budget'].mean():.0f}
    - Average Campaign Spend: ${df_campaigns['campaign_spend'].mean():.0f}
    """
    print("\n--- SUMMARY FOR GEMINI STRATEGIC INSIGHTS (max 500 chars) ---")
    print(summary_for_insights[:500] + ("..." if len(summary_for_insights) > 500 else "")) # Print a truncated summary
    print("--------------------------------------------------------------")

    prompt_strategic_insights = f"""
    Based on the following data summary, identify 2-3 key strategic insights.
    For each insight, provide a short title and a brief explanation (1-2 sentences).
    Focus on potential opportunities, risks, supply/demand imbalances, or performance highlights/lowlights.
    Return ONLY a valid JSON list of objects. Each object must have "insight_id" (e.g., "INS001"), "insight_title", and "insight_explanation".
    Ensure the entire response is valid JSON.
    Respond strictly in English.

    Data Summary:
    {summary_for_insights}
    """
    print("\n--- PROMPT FOR STRATEGIC INSIGHTS (first 300 chars) ---") # Print part of the prompt
    print(prompt_strategic_insights[:300] + "...")
    print("--------------------------------------------------------")

    insights_response_json_str = call_gemini_api(prompt_strategic_insights, "Strategic Insights")
    total_gemini_calls +=1
    print(f"\n--- RAW/CLEANED RESPONSE FOR STRATEGIC INSIGHTS (first 300 chars) ---")
    print(insights_response_json_str[:300] + ("..." if len(insights_response_json_str) > 300 else ""))
    print("--------------------------------------------------------------------")

    try:
        insights_data_parsed = json.loads(insights_response_json_str)
        if isinstance(insights_data_parsed, list) and insights_data_parsed:
            df_strategic_insights = pd.DataFrame(insights_data_parsed)
            print(f"Successfully parsed and generated {len(df_strategic_insights)} strategic insights (list received).")
        elif isinstance(insights_data_parsed, dict) and insights_data_parsed: # Handle if Gemini returns a single object
            df_strategic_insights = pd.DataFrame([insights_data_parsed])
            print(f"Successfully parsed and generated {len(df_strategic_insights)} strategic insights (single object received and wrapped in list).")
        else:
            print("Strategic insights response was not a valid list or non-empty object as expected after parsing.")
            print(f"Parsed data type: {type(insights_data_parsed)}")
    except json.JSONDecodeError:
        print(f"CRITICAL: Failed to parse strategic insights JSON. Response was: {insights_response_json_str}")

    if not df_strategic_insights.empty:
        print("\nGenerating Actionable Tasks (Gemini)...")
        insights_for_tasks_prompt = "\n".join([f"- {row.get('insight_title', 'N/A')}: {row.get('insight_explanation', 'N/A')}" for _, row in df_strategic_insights.iterrows()])

        prompt_actionable_tasks = f"""
        Based on the following strategic insights, suggest 2-3 actionable tasks.
        For each task, provide a brief description and assign an importance level from 1 (Low) to 5 (Very High).
        Return ONLY a valid JSON list of objects. Each object must have "task_id" (e.g., "TASK001"), "task_description", and "task_importance" (integer 1-5).
        Ensure the entire response is valid JSON.
        Respond strictly in English.

        Strategic Insights:
        {insights_for_tasks_prompt}
        """
        print("\n--- PROMPT FOR ACTIONABLE TASKS (first 300 chars) ---")
        print(prompt_actionable_tasks[:300] + "...")
        print("------------------------------------------------------")

        tasks_response_json_str = call_gemini_api(prompt_actionable_tasks, "Actionable Tasks")
        total_gemini_calls +=1
        print(f"\n--- RAW/CLEANED RESPONSE FOR ACTIONABLE TASKS (first 300 chars) ---")
        print(tasks_response_json_str[:300] + ("..." if len(tasks_response_json_str) > 300 else ""))
        print("------------------------------------------------------------------")

        try:
            tasks_data_parsed = json.loads(tasks_response_json_str)
            if isinstance(tasks_data_parsed, list) and tasks_data_parsed:
                df_actionable_tasks = pd.DataFrame(tasks_data_parsed)
                print(f"Successfully parsed and generated {len(df_actionable_tasks)} actionable tasks (list received).")
            elif isinstance(tasks_data_parsed, dict) and tasks_data_parsed: # Handle single object
                df_actionable_tasks = pd.DataFrame([tasks_data_parsed])
                print(f"Successfully parsed and generated {len(df_actionable_tasks)} actionable tasks (single object received and wrapped in list).")
            else:
                print("Actionable tasks response was not a valid list or non-empty object as expected after parsing.")
                print(f"Parsed data type: {type(tasks_data_parsed)}")
        except json.JSONDecodeError:
            print(f"CRITICAL: Failed to parse actionable tasks JSON. Response was: {tasks_response_json_str}")

# --- Save Final DataFrames ---
# ... (resto do código de salvamento como antes) ...
output_path_users = 'user_details_enriched_en.csv'
output_path_interactions = 'marketing_interactions_enriched_en.csv'
output_path_insights = 'strategic_insights_en.csv'
output_path_tasks = 'actionable_tasks_en.csv'

df_users.to_csv(output_path_users, index=False, encoding='utf-8-sig')
print(f"\nSaved: {output_path_users} (VADER analyses: {total_vader_processed})")
df_interactions.to_csv(output_path_interactions, index=False, encoding='utf-8-sig')
print(f"Saved: {output_path_interactions}")

if not df_strategic_insights.empty:
    df_strategic_insights.to_csv(output_path_insights, index=False, encoding='utf-8-sig')
    print(f"Saved: {output_path_insights}")
else:
    print(f"{output_path_insights} is empty (no strategic insights generated).")

if not df_actionable_tasks.empty:
    df_actionable_tasks.to_csv(output_path_tasks, index=False, encoding='utf-8-sig')
    print(f"Saved: {output_path_tasks}")
else:
    print(f"{output_path_tasks} is empty (no actionable tasks generated).")


print(f"\nTotal VADER sentiment analyses performed: {total_vader_processed}")
if USE_GEMINI_FOR_ADVANCED_ANALYSIS:
    print(f"Total Gemini API calls made (approx): {total_gemini_calls}")
print("NLP enrichment process completed!")