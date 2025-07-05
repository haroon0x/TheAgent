from .llm_base import LLMProviderBase
from typing import Any
import sys
import subprocess

def ensure_openai():
    try:
        import openai
        return openai
    except ImportError:
        print("[ERROR] The required package 'openai' is not installed.")
        resp = input("Would you like to install it now with 'pip install openai'? [Y/n]: ").strip().lower()
        if resp in {"", "y", "yes"}:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
                print("[INFO] Successfully installed openai. Please rerun your command.")
                sys.exit(0)
            except Exception as e:
                print(f"[ERROR] Failed to install openai: {e}")
                sys.exit(1)
        else:
            print("Please install it manually: pip install openai")
            sys.exit(1)

class OpenAIProvider(LLMProviderBase):
    """
    OpenAI LLM provider adapter.
    """
    def generate(self, prompt: str, model: str = 'gpt-4o', temperature: float = 0.2, top_p: float = 0.9, max_tokens: int = 1024, **kwargs) -> str:
        openai = ensure_openai()
        openai.api_key = self.api_key
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[OpenAIProvider] API error: {e}")
            return f"Error: Failed to call OpenAI LLM - {e}"

    def chat(self, messages: list[dict], model: str = 'gpt-4o', temperature: float = 0.2, top_p: float = 0.9, max_tokens: int = 1024, **kwargs) -> str:
        openai = ensure_openai()
        openai.api_key = self.api_key
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[OpenAIProvider] API error: {e}")
            return f"Error: Failed to call OpenAI LLM - {e}" 