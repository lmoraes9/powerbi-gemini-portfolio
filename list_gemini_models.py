import os
from dotenv import load_dotenv
import google.generativeai as genai

def list_available_gemini_models():
    """
    Connects to the Gemini API and lists models that support 'generateContent'.
    """
    # Load environment variables from .env file to get the API key
    load_dotenv()
    google_api_key = os.getenv('GOOGLE_API_KEY')

    if not google_api_key:
        print("Error: GOOGLE_API_KEY not found in .env file or environment variables.")
        print("Please ensure your API key is correctly set up.")
        return

    try:
        # Configure the Gemini API client
        genai.configure(api_key=google_api_key)

        print("Fetching available Gemini models...\n")
        print("Models supporting 'generateContent' method:")
        print("-" * 40)

        models_found = 0
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"- Name: {model.name}")
                # You can print other model attributes if needed:
                # print(f"  Display Name: {model.display_name}")
                # print(f"  Description: {model.description}")
                # print(f"  Supported Methods: {model.supported_generation_methods}")
                # print("-" * 20)
                models_found += 1
        
        if models_found == 0:
            print("No models found that support 'generateContent'.")
            print("This could be due to API key issues, network problems, or no available models for your account.")
        
        print("-" * 40)

    except Exception as e:
        print(f"An error occurred while trying to list Gemini models: {e}")
        print("Please check your API key, internet connection, and ensure the 'google-generativeai' library is installed correctly.")

if __name__ == "__main__":
    list_available_gemini_models()