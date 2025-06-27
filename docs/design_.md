# Project Specification: The Code Documentation Agent

---

## 1. Project Overview

**Project Name:** The Code Documentation Agent

**Objective:** To automate the generation of high-quality, Google-style docstrings for Python functions. This agent will read source code, understand function logic, interact with an LLM via the `alchemist_ai_proxy`, and then either display the generated docstrings or insert them into the source file. This addresses the common problem of undocumented code, improving maintainability and team onboarding.

**Target User:** Python developers.

**Expected Outcome:** A robust, command-line tool for automated code documentation.

---

## 2. Agentic Design Principles

This project embodies core agentic principles:

* **Perception:** Reads and parses Python source code using `ast` to identify functions.
* **Thinking:** Leverages an LLM (via `alchemist_ai_proxy`) to analyze function code and generate structured docstrings.
* **Action:** Presents or inserts generated docstrings into the source file.
* **Environment Interaction:** Interacts with the file system and an external LLM service.

---

## 3. Technical Requirements & Architecture

### 3.1 Core Components

1.  **Command-Line Interface (CLI):** `argparse` for user input.
2.  **Code Parser:** `ast` for robust source code parsing and function extraction.
3.  **LLM Interaction Module:** Custom `alchemist_ai_proxy` (in `call_llm.py`) for all LLM calls.
4.  **Agent Framework:** PocketFlow for orchestrating the agent's workflow.

### 3.2 Detailed Component Specifications

#### 3.2.1 Command-Line Interface (CLI)

* **Library:** `argparse`.
* **Arguments:**
    * `--file <filepath>` (Required): Path to the Python source file.
    * `--output <mode>` (Optional, Default: `console`):
        * `console`: Prints to standard output.
        * `in-place`: Modifies the original file (creates `.bak` backup).
        * `new-file`: Writes to `filename_documented.py`.
    * `--llm <model_name>` (Optional, Default: `gpt-4o`): Specifies the LLM model for `alchemist_ai_proxy`.
    * `--no-confirm` (Optional, Default: `False`): Skip user confirmation for `in-place`/`new-file` modes.
    * `--verbose` (Optional, Default: `False`): Prints detailed progress messages.
* **Error Handling:** File not found, invalid file extension, parsing errors, LLM API errors.

#### 3.2.2 Code Parser (Perception)

* **Library:** `ast`.
* **Functionality:**
    1.  Reads file content.
    2.  Uses `ast.parse()` to build AST.
    3.  Traverses AST with `ast.walk()` to find `ast.FunctionDef` nodes.
    4.  For each function: Extracts name, full source code (with `ast.get_source_segment` if Python 3.9+), start/end lines, and indentation.
* **Output:** List of dictionaries: `{'name': str, 'source_code': str, 'start_line': int, 'end_line': int, 'indentation': str}`.

#### 3.2.3 LLM Interaction Module (`alchemist_ai_proxy` in `call_llm.py`)

* **Purpose:** Unified interface for LLM calls using `alchemist_ai`.
* **File:** `call_llm.py`.
* **Class/Function:** `AlchemistAIProxy` class with `generate_docstring(function_code: str, model_name: str) -> str`.
* **Dependencies:** Placeholder for `alchemist_ai` library.
* **Configuration:** API keys loaded from environment variables (e.g., `ALCHEMIST_AI_API_KEY`).
* **Error Handling:** Robust `try-except` for API calls.
* **Prompt Engineering:**
    ```python
    prompt = f"""You are an expert Python programmer specialized in documentation. Your task is to analyze the following Python function and generate a professional, comprehensive, and accurate Google-style docstring for it.

    Your response MUST ONLY contain the docstring text. Do NOT include any other text, code, or explanations. The docstring should immediately follow the triple quotes.

    The docstring must adhere strictly to the Google style guide and include the following sections where applicable:

    1.  A concise one-line summary of the function's purpose.
    2.  A more detailed, multi-line description of what the function does.
    3.  `Args:`: Details each argument (name, type, description).
    4.  `Returns:`: Details the return value (type, description).
    5.  `Raises:`: (If applicable) Describes exceptions.
    6.  `Yields:`: (If applicable) Describes yielded values for generators.
    7.  `Note:`: (Optional) Important notes or caveats.
    8.  `Examples:`: (Highly Recommended) Code examples using `>>>`.

    Ensure correct indentation and formatting.

    Here is the Python function to document:

    ```python
    {function_code}
    ```
    """
    ```
* **LLM Parameters:** `temperature: 0.2`, `top_p: 0.9`, `max_tokens: 512-1024`.

#### 3.2.4 Agent Framework (PocketFlow)

* **Integration:** `doc_agent.py` will use PocketFlow for orchestration.
* **Agent Definition:** `DocAgent` class inheriting from a PocketFlow Agent.
* **Workflow:**
    1.  Initializes `DocAgent` with `AlchemistAIProxy` and CLI args.
    2.  Calls Code Parser to get function data.
    3.  Iterates functions, calls `AlchemistAIProxy.generate_docstring()`.
    4.  Based on `--output` mode: prints or inserts docstring (with correct indentation, replacing old if present).
    5.  Manages backup for `in-place` mode and user confirmation.

### 3.4 Dependencies

* `argparse` (built-in)
* `ast` (built-in)
* `os` (built-in)
* `shutil` (built-in)
* `pocketflow`
* `alchemist_ai` (placeholder for actual library name)
* `python-dotenv` (recommended for env vars)

---

## 4. Workflow (Sequence of Operations)

1.  **User Execution:** `python doc_agent.py --file my_module.py --output in-place`.
2.  **CLI Parsing:** `argparse` processes arguments.
3.  **Agent Initialization:** `DocAgent` initializes with `AlchemistAIProxy` and args.
4.  **File Reading & AST Parsing:** Agent reads file and builds AST.
5.  **Function Identification:** Agent extracts function details from AST.
6.  **Iterative Docstring Generation (Thinking):** For each function, calls `alchemist_ai_proxy.generate_docstring()`.
7.  **Docstring Integration (Action):** Based on `--output` mode:
    * `console`: Prints function and docstring.
    * `in-place`: Creates backup, inserts docstring into original file.
    * `new-file`: Inserts docstring, writes to new file.
    * Handles user confirmation if `--no-confirm` is not set.

---

## 5. Error Handling and Edge Cases

* **Empty File/No Functions:** Inform user.
* **Syntax Errors:** Catch `SyntaxError` from `ast.parse`.
* **LLM API Failures:** Implement retries and error logging for `alchemist_ai_proxy`.
* **Existing Docstrings:** New docstring correctly replaces old one.
* **Indentation:** Crucial for correct Python code, ensure docstring matches function's indentation.

---

## 6. Testing Strategy

* **Unit Tests:** For `call_llm.py` (mocking LLM), Code Parser, Docstring Insertion Logic.
* **Integration Tests:** Run CLI against sample files, verify docstring quality and file modification.
* **Regression Tests:** Ensure new changes don't break existing functionality.

---
