from .llm_base import LLMProviderBase
import sys
import subprocess
from typing import Any

def ensure_ollama():
    try:
        import ollama
        return ollama
    except ImportError:
        print("[ERROR] The required package 'ollama' is not installed.")
        resp = input("Would you like to install it now with 'pip install ollama'? [Y/n]: ").strip().lower()
        if resp in {"", "y", "yes"}:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
                print("[INFO] Successfully installed ollama. Please rerun your command.")
                sys.exit(0)
            except Exception as e:
                print(f"[ERROR] Failed to install ollama: {e}")
                sys.exit(1)
        else:
            print("Please install it manually: pip install ollama")
            sys.exit(1)

class OllamaProvider(LLMProviderBase):
    """
    Ollama LLM provider adapter.
    """
    def generate(self, prompt: str, model: str = 'llama2', **kwargs) -> str:
        ollama = ensure_ollama()
        host = self.host or "http://localhost:11434"
        try:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                base_url=host
            )
            return response.message.content.strip() if response.message else "Error: No response from LLM"
        except Exception as e:
            print(f"[OllamaProvider] API error: {e}")
            return f"Error: Failed to call Ollama LLM - {e}"

    def chat(self, messages: list[dict], model: str = 'llama2', **kwargs) -> str:
        ollama = ensure_ollama()
        host = self.host or "http://localhost:11434"
        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                base_url=host
            )
            return response.message.content.strip() if response.message else "Error: No response from LLM"
        except Exception as e:
            print(f"[OllamaProvider] API error: {e}")
            return f"Error: Failed to call Ollama LLM - {e}" 