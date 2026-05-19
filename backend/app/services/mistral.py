import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class MistralService:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY", "your_mistral_api_key")
        self.api_url = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")
        
        # Log warnings if configured with placeholder key
        if self.api_key == "your_mistral_api_key" or not self.api_key:
            logger.warning("MISTRAL_API_KEY is not configured or is a placeholder. API calls will fail.")

    def generate_response(self, prompt: str) -> str:
        """
        Sends the final prompt to the Mistral AI Chat Completions API.
        """
        if self.api_key == "your_mistral_api_key" or not self.api_key:
            return (
                "⚠️ Mistral API Key is missing or not configured. "
                "Please configure a valid MISTRAL_API_KEY in the backend/.env file to get responses."
            )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "mistral-small",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2, # Lower temperature for strictly structured RAG answers
            "max_tokens": 500
        }

        try:
            logger.info("Sending request to Mistral AI API...")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 401:
                return "⚠️ Unauthorized: The provided Mistral API Key is invalid or expired. Please check your .env configuration."
            
            response.raise_for_status()
            
            data = response.json()
            # Extract the content from the response JSON structure
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            
            return "⚠️ Received empty or invalid response structure from Mistral API."
            
        except requests.exceptions.Timeout:
            logger.error("Mistral API call timed out.")
            return "⏳ The connection to Mistral AI API timed out. Please try again later."
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Mistral API: {e}")
            return f"❌ Failed to connect to Mistral AI API: {str(e)}"

mistral_service = MistralService()
