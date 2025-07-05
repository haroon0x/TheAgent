from .llm_base import LLMProviderBase
import sys
import subprocess
from typing import Any

def ensure_google_genai():
    try:
        from google import genai
        return genai
    except ImportError:
        print("[ERROR] The required package 'google-generativeai' is not installed.")
        resp = input("Would you like to install it now with 'pip install google-generativeai'? [Y/n]: ").strip().lower()
        if resp in {"", "y", "yes"}:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
                print("[INFO] Successfully installed google-generativeai. Please rerun your command.")
                sys.exit(0)
            except Exception as e:
                print(f"[ERROR] Failed to install google-generativeai: {e}")
                sys.exit(1)
        else:
            print("Please install it manually: pip install google-generativeai")
            sys.exit(1)

class GoogleProvider(LLMProviderBase):
    """
    Google Gemini LLM provider adapter.
    """
    def generate(self, prompt: str, model: str = 'gemini-2.5-flash', **kwargs) -> str:
        genai = ensure_google_genai()
        client = genai.Client(api_key=self.api_key)
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                **kwargs
            )
            return response.text.strip()
        except Exception as e:
            print(f"[GoogleProvider] API error: {e}")
            return f"Error: Failed to call Google Gemini - {e}"

    def chat(self, messages: list[dict], model: str = 'gemini-2.5-flash', **kwargs) -> str:
        genai = ensure_google_genai()
        client = genai.Client(api_key=self.api_key)
        try:
            # Convert messages to a single prompt for Gemini
            prompt = '\n'.join([m['content'] for m in messages if m['role'] == 'user'])
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                **kwargs
            )
            return response.text.strip()
        except Exception as e:
            print(f"[GoogleProvider] API error: {e}")
            return f"Error: Failed to call Google Gemini - {e}" 