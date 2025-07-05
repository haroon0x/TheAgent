from typing import Any

class LLMProviderBase:
    """
    Base interface for all LLM provider adapters.
    """
    def __init__(self, api_key: str = None, host: str = None):
        self.api_key = api_key
        self.host = host

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the LLM given a prompt.
        """
        raise NotImplementedError

    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        (Optional) Chat-style interface for providers that support it.
        """
        raise NotImplementedError 