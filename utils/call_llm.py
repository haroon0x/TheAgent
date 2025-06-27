# utils/call_llm.py
import os
from dotenv import load_dotenv

class AlchemistAIProxy:
    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("ALCHEMYST_API_KEY")
        self.base_url = "https://platform-backend.getalchemystai.com/api/v1/proxy/default"

    def generate_docstring(self, function_code: str, model_name: str = "alchemyst-ai/alchemyst-c1") -> str:
        """
        Generate a Google-style docstring for the given function code using the specified LLM model.
        """
        from langchain_openai import ChatOpenAI
        # System prompt is now much more detailed
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
        )
        prompt = f"Document this Python function:\n{function_code}"
        try:
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=model_name,
                base_url=self.base_url,
                temperature=0.2,
                top_p=0.9,
                max_tokens=1024,
            )
            result = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            return result.content.strip()
        except Exception as e:
            print(f"[AlchemistAIProxy] LLM API error: {e}")
            return ""  # Or raise, depending on desired behavior

    def summarize_code(self, code: str, model_name: str = "alchemyst-ai/alchemyst-c1") -> str:
        from langchain_openai import ChatOpenAI
        system_prompt = (
            "You are an expert Python code summarization agent. "
            "Your job is to read Python code and generate a concise, high-level summary of what the code does. "
            "- Only output the summary, do NOT include any code, markdown, or extra text. "
            "- The summary should mention the main purpose, key functions/classes, and any important algorithms or patterns. "
            "- If the code is a script, mention its entry point and main workflow. "
            "- If the code is a module, mention its API and usage. "
            "- Be clear, accurate, and concise. "
        )
        prompt = "Summarize this Python code:\n" + code
        try:
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=model_name,
                base_url=self.base_url,
                temperature=0.2,
                top_p=0.9,
                max_tokens=512,
            )
            result = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            return result.content.strip()
        except Exception as e:
            print(f"[AlchemistAIProxy] LLM API error: {e}")
            return ""

    def suggest_type_annotations(self, function_code: str, model_name: str = "alchemyst-ai/alchemyst-c1") -> str:
        from langchain_openai import ChatOpenAI
        system_prompt = (
            "You are an expert Python type annotation agent. "
            "Your job is to suggest precise and idiomatic type annotations for Python functions. "
            "- Only output the function signature with type hints, do NOT include any code, markdown, or extra text. "
            "- If the function already has type hints, suggest improvements if possible. "
            "- Use standard Python typing (PEP 484/PEP 604). "
            "- For arguments with unclear types, use Any. "
            "- If the function is a generator, use Iterator or Generator as appropriate. "
            "- If the function is async, use Awaitable or Coroutine as appropriate. "
            "- Do not include the function body or docstring. "
        )
        prompt = "Suggest type annotations for this Python function:\n" + function_code
        try:
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=model_name,
                base_url=self.base_url,
                temperature=0.2,
                top_p=0.9,
                max_tokens=256,
            )
            result = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            return result.content.strip()
        except Exception as e:
            print(f"[AlchemistAIProxy] LLM API error: {e}")
            return ""

    def test_generation(self, function_code: str, model_name: str = "alchemyst-ai/alchemyst-c1") -> str:
        from langchain_openai import ChatOpenAI
        system_prompt = (
            "You are an expert Python unit test generation agent. "
            "Your job is to generate high-quality pytest-style unit tests for the given function. "
            "- Only output the test code, do NOT include any explanations, markdown, or extra text. "
            "- Use pytest conventions. "
            "- Cover edge cases and typical usage. "
            "- If the function has side effects, test them. "
            "- If the function raises exceptions, test those cases. "
        )
        prompt = "Write pytest unit tests for this Python function:\n" + function_code
        try:
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=model_name,
                base_url=self.base_url,
                temperature=0.2,
                top_p=0.9,
                max_tokens=1024,
            )
            result = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            return result.content.strip()
        except Exception as e:
            print(f"[AlchemistAIProxy] LLM API error: {e}")
            return ""

    def bug_detection(self, code: str, model_name: str = "alchemyst-ai/alchemyst-c1") -> str:
        from langchain_openai import ChatOpenAI
        system_prompt = (
            "You are an expert Python bug detection agent. "
            "Your job is to analyze the given code and identify any bugs, logical errors, or bad practices. "
            "- Only output the bug report, do NOT include any code, markdown, or extra text. "
            "- For each bug, explain what is wrong and how to fix it. "
            "- If the code is correct, say so. "
        )
        prompt = "Find bugs in this Python code:\n" + code
        try:
    llm = ChatOpenAI(
                api_key=self.api_key,
                model=model_name,
                base_url=self.base_url,
                temperature=0.2,
                top_p=0.9,
                max_tokens=1024,
    )
    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])
            return result.content.strip()
        except Exception as e:
            print(f"[AlchemistAIProxy] LLM API error: {e}")
            return ""

    def refactor_code(self, code: str, model_name: str = "alchemyst-ai/alchemyst-c1") -> str:
        from langchain_openai import ChatOpenAI
        system_prompt = (
            "You are an expert Python code refactoring agent. "
            "Your job is to suggest improvements to the given code for readability, performance, and maintainability. "
            "- Only output the improved code, do NOT include any explanations, markdown, or extra text. "
            "- Use idiomatic Python and best practices. "
            "- If the code is already optimal, say so. "
        )
        prompt = "Refactor this Python code:\n" + code
        try:
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=model_name,
                base_url=self.base_url,
                temperature=0.2,
                top_p=0.9,
                max_tokens=1024,
            )
            result = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            return result.content.strip()
        except Exception as e:
            print(f"[AlchemistAIProxy] LLM API error: {e}")
            return ""

    def migration_code(self, code: str, migration_target: str = "Python 3", model_name: str = "alchemyst-ai/alchemyst-c1") -> str:
        """
        Rewrite the provided code so it is fully compatible with the specified migration target (e.g., Python 3, TensorFlow 2).
        Args:
            code: The Python code to migrate.
            migration_target: The migration target (e.g., 'Python 3', 'TensorFlow 2', etc.)
            model_name: The LLM model to use.
        Returns:
            str: The migrated code.
        """
        from langchain_openai import ChatOpenAI
        system_prompt = (
            "You are a Python code migration agent. "
            "Your job is to rewrite the provided code so it is fully compatible with the specified migration target (e.g., Python 3, TensorFlow 2). "
            "- Only output the migrated code, do NOT include any explanations, markdown, or extra text. "
            "- Update all syntax, APIs, and idioms as needed for the migration target. "
            "- If the code is already compatible, output it unchanged. "
        )
        prompt = f"Migration target: {migration_target}\nRewrite this Python code for migration:\n" + code
        try:
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=model_name,
                base_url=self.base_url,
                temperature=0.2,
                top_p=0.9,
                max_tokens=4096,
            )
            result = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            return result.content.strip()
        except Exception as e:
            print(f"[AlchemistAIProxy] LLM API error: {e}")
            return ""