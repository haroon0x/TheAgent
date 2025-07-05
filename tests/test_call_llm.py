import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from theagent.utils.call_llm import GeneralLLMProxy

class DummyLLMProxy:
    def generate_docstring(self, function_code, model_name):
        return 'Dummy docstring for testing.'

def test_generate_docstring(monkeypatch):
    # Remove any usage of AlchemistAIProxy and related test(s)
    pass

def test_general_llmproxy_openai(monkeypatch):
    proxy = GeneralLLMProxy(openai_api_key='dummy')
    monkeypatch.setattr(proxy.providers['openai'], 'generate', lambda prompt, **kwargs: 'openai-ok')
    result = proxy.call_llm('prompt', provider='openai')
    assert result == 'openai-ok'

def test_general_llmproxy_anthropic(monkeypatch):
    proxy = GeneralLLMProxy(anthropic_api_key='dummy')
    monkeypatch.setattr(proxy.providers['anthropic'], 'generate', lambda prompt, **kwargs: 'anthropic-ok')
    result = proxy.call_llm('prompt', provider='anthropic')
    assert result == 'anthropic-ok'

def test_general_llmproxy_google(monkeypatch):
    proxy = GeneralLLMProxy(google_api_key='dummy')
    monkeypatch.setattr(proxy.providers['google'], 'generate', lambda prompt, **kwargs: 'google-ok')
    result = proxy.call_llm('prompt', provider='google')
    assert result == 'google-ok'

def test_general_llmproxy_ollama(monkeypatch):
    proxy = GeneralLLMProxy(ollama_host='dummy')
    monkeypatch.setattr(proxy.providers['ollama'], 'generate', lambda prompt, **kwargs: 'ollama-ok')
    result = proxy.call_llm('prompt', provider='ollama')
    assert result == 'ollama-ok' 