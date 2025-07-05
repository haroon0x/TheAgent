# utils/call_llm.py
import os
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from .utils import ProgressTracker, create_progress_tracker
import sys
import subprocess
from theagent.providers.openai_provider import OpenAIProvider
from theagent.providers.anthropic_provider import AnthropicProvider
from theagent.providers.google_provider import GoogleProvider
from theagent.providers.ollama_provider import OllamaProvider

# Load .env only once at module level
load_dotenv()

def ensure_package(pkg_name, import_name=None):
    import_name = import_name or pkg_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        print(f"[ERROR] The required package '{pkg_name}' is not installed.")
        resp = input(f"Would you like to install it now with 'pip install {pkg_name}'? [Y/n]: ").strip().lower()
        if resp in {"", "y", "yes"}:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
                print(f"[INFO] Successfully installed {pkg_name}. Please rerun your command.")
                sys.exit(0)
            except Exception as e:
                print(f"[ERROR] Failed to install {pkg_name}: {e}")
                sys.exit(1)
        else:
            print(f"Please install it manually: pip install {pkg_name}")
            sys.exit(1)
        return False

class GeneralLLMProxy:
    """
    Modular LLM proxy supporting OpenAI, Anthropic, Google Gemini, and Ollama.
    """
    def __init__(self, openai_api_key=None, anthropic_api_key=None, google_api_key=None, ollama_host=None):
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.google_api_key = google_api_key or os.environ.get("GOOGLE_GENAI_API_KEY")
        self.ollama_host = ollama_host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.providers = {
            'openai': OpenAIProvider(api_key=self.openai_api_key),
            'anthropic': AnthropicProvider(api_key=self.anthropic_api_key),
            'google': GoogleProvider(api_key=self.google_api_key),
            'ollama': OllamaProvider(host=self.ollama_host),
        }

    def call_llm(self, prompt, provider='openai', **kwargs):
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        return self.providers[provider].generate(prompt, **kwargs)

    # Agent methods
    def generate_docstring(self, function_code: str, provider='openai', model='gpt-4o', **kwargs) -> str:
        system_prompt = (
            "You are an expert Python documentation agent. "
            "Your job is to generate professional, comprehensive, and accurate Google-style docstrings for Python functions. "
            "You must strictly follow these rules: "
            "- Only output the docstring content, do NOT include triple quotes or markdown code fences. "
            "- Do NOT include any explanations, code, or extra text. "
            "- The docstring must adhere to the Google Python style guide and include, where applicable: "
            "  1. A concise one-line summary of the function's purpose. "
            "  2. A detailed multi-line description of what the function does, including important context or algorithm details. "
            "  3. Args: List each argument with its type hint and a clear description. "
            "  4. Returns: Describe the return value, its type hint, and what it represents. "
            "  5. Raises: (If applicable) Describe any exceptions that the function might raise. "
            "  6. Yields: (If applicable) Describe any values yielded by a generator function. "
            "  7. Note: (Optional) Any important notes or caveats. "
            "  8. Examples: (Highly Recommended) One or more clear code examples using >>>. "
            "- For boolean arguments, explain what True and False signify. "
            "- For arguments with default values, mention them in the description. "
            "- Ensure correct indentation and formatting. "
            "- If the function is a generator, document Yields instead of Returns. "
            "- If the function is a method, document 'self' only if it is relevant. "
            "- If the function has *args or **kwargs, document them. "
            "- If the function has type hints, use them in the docstring. "
            "- If the function has an existing docstring, replace it. "
            "- Do not repeat the function signature. "
            "- Do not include any markdown or code fences. "
            "\n\nOutput Format:\nOnly output the docstring content, no triple quotes, no markdown, no extra text.\n\nSample Output (for a function that adds two numbers):\nAdds two numbers together.\n\nArgs:\n    a (int): The first number.\n    b (int): The second number.\n\nReturns:\n    int: The sum of a and b.\n"
        )
        prompt = f"Document this Python function:\n{function_code}"
        return self.call_llm(f"{system_prompt}\n\n{prompt}", provider=provider, model=model, **kwargs)

    def summarize_code(self, code: str, provider='openai', model='gpt-4o', **kwargs) -> str:
        system_prompt = (
            "You are an expert Python code summarization agent. "
            "Your job is to read Python code and generate a concise, high-level summary of what the code does. "
            "- Only output the summary, do NOT include any code, markdown, or extra text. "
            "- The summary should mention the main purpose, key functions/classes, and any important algorithms or patterns. "
            "- If the code is a script, mention its entry point and main workflow. "
            "- If the code is a module, mention its API and usage. "
            "- Be clear, accurate, and concise. "
            "\n\nOutput Format:\nA single concise paragraph. No code, no markdown, no extra text.\n\nSample Output:\nThis script processes CSV files and generates summary statistics for each column, including mean, median, and standard deviation. The main function orchestrates file loading, data cleaning, and result output."
        )
        prompt = f"Summarize this Python code:\n{code}"
        return self.call_llm(f"{system_prompt}\n\n{prompt}", provider=provider, model=model, **kwargs)

    def generate_tests(self, function_code: str, provider='openai', model='gpt-4o', **kwargs) -> str:
        system_prompt = (
            "You are an expert Python testing agent. "
            "Your job is to generate comprehensive unit tests for Python functions. "
            "- Only output the test code, do NOT include any explanations, markdown, or extra text. "
            "- Use pytest style tests with clear test names. "
            "- Include tests for normal cases, edge cases, and error cases. "
            "- Import necessary modules and use appropriate assertions. "
            "- If the function has multiple parameters, test different combinations. "
            "- If the function can raise exceptions, test those cases. "
            "\n\nOutput Format:\nOnly output the test code. No explanations, no markdown, no extra text.\n\nSample Output:\nimport pytest\nfrom mymodule import my_function\n\ndef test_my_function_normal_case():\n    assert my_function(2, 3) == 5\n\ndef test_my_function_edge_case():\n    assert my_function(0, 0) == 0\n"
        )
        prompt = f"Generate unit tests for this Python function:\n{function_code}"
        return self.call_llm(f"{system_prompt}\n\n{prompt}", provider=provider, model=model, **kwargs)

    def detect_bugs(self, code: str, provider='openai', model='gpt-4o', **kwargs) -> str:
        system_prompt = (
            "You are an expert Python code review agent specializing in bug detection. "
            "Your job is to analyze Python code and identify potential bugs, issues, or improvements. "
            "- Only output the analysis, do NOT include any code, markdown, or extra text. "
            "- Focus on logical errors, potential runtime issues, and best practice violations. "
            "- Be specific about what could go wrong and why. "
            "- Suggest improvements where applicable. "
            "- If no significant issues are found, mention that the code appears to be well-written. "
            "\n\nOutput Format:\nA clear analysis of potential issues. No code, no markdown, no extra text.\n\nSample Output:\nThe code looks generally well-structured, but there are a few potential issues: 1) The function doesn't handle the case where the input list is empty, which could cause an IndexError. 2) There's no validation of input parameters, which could lead to unexpected behavior with invalid inputs. 3) The variable naming could be more descriptive to improve readability."
        )
        prompt = f"Analyze this Python code for potential bugs and issues:\n{code}"
        return self.call_llm(f"{system_prompt}\n\n{prompt}", provider=provider, model=model, **kwargs)

    def refactor_code(self, code: str, provider='openai', model='gpt-4o', **kwargs) -> str:
        system_prompt = (
            "You are an expert Python refactoring agent. "
            "Your job is to refactor Python code to improve readability, performance, and maintainability. "
            "- Only output the refactored code, do NOT include any explanations, markdown, or extra text. "
            "- Maintain the same functionality while improving code quality. "
            "- Use modern Python features and best practices. "
            "- Improve variable names, function structure, and code organization. "
            "- Add appropriate comments where needed. "
            "- Ensure the code is PEP 8 compliant. "
            "\n\nOutput Format:\nOnly output the refactored code. No explanations, no markdown, no extra text.\n\nSample Output:\ndef calculate_average(numbers: list[float]) -> float:\n    \"\"\"Calculate the average of a list of numbers.\"\"\"\n    if not numbers:\n        raise ValueError(\"Cannot calculate average of empty list\")\n    return sum(numbers) / len(numbers)\n"
        )
        prompt = f"Refactor this Python code to improve quality:\n{code}"
        return self.call_llm(f"{system_prompt}\n\n{prompt}", provider=provider, model=model, **kwargs)

    def migrate_code(self, code: str, migration_target: str = "Python 3", provider='openai', model='gpt-4o', **kwargs) -> str:
        system_prompt = (
            "You are an expert Python code migration agent. "
            "Your job is to migrate Python code to the specified target version. "
            "- Only output the migrated code, do NOT include any explanations, markdown, or extra text. "
            "- Ensure the code is compatible with the target Python version. "
            "- Update deprecated functions and syntax. "
            "- Use modern Python features where appropriate. "
            "- Maintain the original functionality. "
            "\n\nOutput Format:\nOnly output the migrated code. No explanations, no markdown, no extra text.\n\nSample Output:\nfrom typing import List\n\ndef process_items(items: List[str]) -> List[str]:\n    return [item.upper() for item in items]\n"
        )
        prompt = f"Migrate this Python code to {migration_target}:\n{code}"
        return self.call_llm(f"{system_prompt}\n\n{prompt}", provider=provider, model=model, **kwargs)

    def add_type_annotations(self, code: str, provider='openai', model='gpt-4o', **kwargs) -> str:
        system_prompt = (
            "You are an expert Python type annotation agent. "
            "Your job is to add proper type hints to Python functions. "
            "- Only output the function with type annotations, do NOT include any explanations, markdown, or extra text. "
            "- Use modern Python type hints (Python 3.7+). "
            "- Import necessary types from typing module if needed. "
            "- If the function is already properly typed, return it unchanged. "
            "\n\nOutput Format:\nOnly output the function with type annotations. No explanations, no markdown, no extra text.\n\nSample Output:\nfrom typing import List, Optional\n\ndef process_data(items: List[str], count: Optional[int] = None) -> List[str]:\n    return items[:count] if count else items\n"
        )
        prompt = f"Add type annotations to this Python function:\n{code}"
        return self.call_llm(f"{system_prompt}\n\n{prompt}", provider=provider, model=model, **kwargs)

    def chat(self, prompt: str, provider='openai', model='gpt-4o', **kwargs) -> str:
        """General chat method for intent recognition and other conversational tasks."""
        return self.call_llm(prompt, provider=provider, model=model, **kwargs)