from .llm_base import LLMProviderBase
import sys
import subprocess
from typing import Any

def ensure_anthropic():
    try:
        import anthropic
        return anthropic
    except ImportError:
        print("[ERROR] The required package 'anthropic' is not installed.")
        resp = input("Would you like to install it now with 'pip install anthropic'? [Y/n]: ").strip().lower()
        if resp in {"", "y", "yes"}:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
                print("[INFO] Successfully installed anthropic. Please rerun your command.")
                sys.exit(0)
            except Exception as e:
                print(f"[ERROR] Failed to install anthropic: {e}")
                sys.exit(1)
        else:
            print("Please install it manually: pip install anthropic")
            sys.exit(1)

class AnthropicProvider(LLMProviderBase):
    """
    Anthropic LLM provider adapter.
    """
    def generate(self, prompt: str, model: str = 'claude-3-haiku-20240307', max_tokens: int = 1024, **kwargs) -> str:
        anthropic = ensure_anthropic()
        client = anthropic.Anthropic(api_key=self.api_key)
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip() if response.content else "Error: No response from LLM"
        except Exception as e:
            print(f"[AnthropicProvider] API error: {e}")
            return f"Error: Failed to call Anthropic LLM - {e}"

    def chat(self, messages: list[dict], model: str = 'claude-3-haiku-20240307', max_tokens: int = 1024, **kwargs) -> str:
        anthropic = ensure_anthropic()
        client = anthropic.Anthropic(api_key=self.api_key)
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages
            )
            return response.content[0].text.strip() if response.content else "Error: No response from LLM"
        except Exception as e:
            print(f"[AnthropicProvider] API error: {e}")
            return f"Error: Failed to call Anthropic LLM - {e}" 