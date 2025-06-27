[![CI](https://github.com/haroon0x/TheAgent/actions/workflows/ci.yml/badge.svg)](https://github.com/haroon0x/TheAgent/actions/workflows/ci.yml)

# The Code Documentation Agent

## Overview
This project provides an intelligent agent that automates the creation of high-quality, Google-style docstrings for Python functions. It uses PocketFlow for agent orchestration and Alchemist AI (via a proxy) for LLM-powered docstring generation.

## Extensibilty - To add a new agent:
- Add a method to AlchemistAIProxy.
- Add a Node class in nodes.py.
- Add a case in create_doc_agent_nodes and the CLI.

## Features

- Reads Python source files and extracts all function definitions
- Calls an LLM to generate Google-style docstrings for each function
- Supports output to console, in-place file modification (with backup), or writing to a new file
- CLI interface with options for LLM model, confirmation prompts, and verbosity
- **Multiple agent types:** docstring, summary, type annotation, migration, test generation, bug detection, refactor
- **Automated tests and CI integration**

## Installation

1. Install [uv](https://github.com/astral-sh/uv):
   ```sh
   pip install uv
   ```
2. Install dependencies:
   ```sh
   uv pip install -r requirements.txt
   ```
   Or, using pyproject.toml:
   ```sh
   uv pip install -r requirements.txt
   uv pip install -e .
   ```

3. Set your Alchemist AI API key in your environment:
   ```sh
   export ALCHEMYST_API_KEY=your_key_here
   ```
   Or create a `.env` file with:
   ```
   ALCHEMYST_API_KEY=your_key_here
   ```

## Usage

```sh
python main.py --file my_module.py --output in-place --llm alchemyst-ai/alchemyst-c1 --verbose
```

- `--file <filepath>`: Path to the Python file to process (required)
  - Example: `--file my_module.py`
- `--output <mode>`: Output mode: `console` (default), `in-place`, or `new-file`
  - Example: `--output in-place`
- `--llm <model_name>`: LLM model to use (default: `alchemyst-ai/alchemyst-c1`)
  - Example: `--llm alchemyst-ai/alchemyst-c1`
- `--no-confirm`: Skip confirmation prompts for destructive actions
  - Example: `--no-confirm`
- `--verbose`: Print detailed progress
  - Example: `--verbose`
- `--agent <type>`: Agent type: `doc`, `summary`, `type`, `migration`, `test`, `bug`, `refactor`
  - Example: `--agent doc`
- `--migration-target <target>`: Migration target for migration agent (e.g., "Python 3")
  - Example: `--migration-target "Python 3"`

## CLI Arguments

| Argument                        | Description                                                                 | Example Usage                                      |
|---------------------------------|-----------------------------------------------------------------------------|----------------------------------------------------|
| `--file <filepath>`             | Path to the Python file to process (**required**)                            | `--file my_module.py`                              |
| `--output <mode>`               | Output mode: `console` (default), `in-place`, or `new-file`                 | `--output in-place`                                |
| `--llm <model_name>`            | LLM model to use (default: `alchemyst-ai/alchemyst-c1`)                     | `--llm alchemyst-ai/alchemyst-c1`                  |
| `--no-confirm`                  | Skip confirmation prompts for destructive actions (e.g., in-place changes)   | `--no-confirm`                                     |
| `--verbose`                     | Print detailed progress                                                     | `--verbose`                                        |
| `--agent <type>`                | Agent type: `doc`, `summary`, `type`, `migration`, `test`, `bug`, `refactor`| `--agent doc`                                      |
| `--migration-target <target>`   | Migration target for migration agent (e.g., `"Python 3"`)                  | `--migration-target "Python 3"`                  |

**Note:**
- You can combine any arguments in any order.
- Flags like `--no-confirm` and `--verbose` do not require a value—just include them to activate.

### Example Commands for Each Agent

**Docstring Agent (in-place, skip confirmation):**
```sh
python main.py --file my_module.py --agent doc --output in-place --no-confirm
```

**Summary Agent (console, verbose):**
```sh
python main.py --file my_module.py --agent summary --verbose
```

**Type Annotation Agent:**
```sh
python main.py --file my_module.py --agent type
```

**Migration Agent (to Python 3, new file):**
```sh
python main.py --file my_module.py --agent migration --migration-target "Python 3" --output new-file
```

**Test Generation Agent:**
```sh
python main.py --file my_module.py --agent test --output new-file
```

**Bug Detection Agent:**
```sh
python main.py --file my_module.py --agent bug
```

**Refactor Code Agent (in-place, verbose):**
```sh
python main.py --file my_module.py --agent refactor --output in-place --verbose
```

## Orchestrator Agent

The Orchestrator Agent lets you use natural language to control the system. Just tell it what you want (e.g., "Add docstrings and generate tests"), and it will decide which agents to run and in what order.

**Usage:**
```sh
python main.py --file my_module.py --agent orchestrator --instruction "Add docstrings and generate tests"
```

If you omit `--instruction`, you will be prompted to enter your instruction interactively:
```sh
python main.py --file my_module.py --agent orchestrator
# Enter your instruction for the orchestrator agent: Add docstrings and generate tests
```

The orchestrator will:
- Parse your instruction
- Decide which agent(s) to run (e.g., doc, test, etc.)
- Run them in order and print a summary

---

## Future: Interactive Chat with the Orchestrator

A future version could allow you to chat interactively with the orchestrator agent, enabling multi-turn workflows and more dynamic control. If you want this feature, let us know or contribute!

---

## Project Structure
- `main.py`: Main entrypoint and CLI
- `nodes.py`: All agent node classes
- `flow.py`: Flow creation logic
- `utils/call_llm.py`: AlchemistAIProxy for LLM calls
- `requirements.txt`, `pyproject.toml`: Dependency management
- `tests/`: Unit and integration tests

## Testing & Continuous Integration

This project uses **pytest** for testing and **GitHub Actions** for CI.

### Run tests locally
```sh
pytest tests/test_agents.py
```
Or run all tests:
```sh
pytest tests/
```

### CI
A GitHub Actions workflow runs all tests on every push and pull request. See `.github/workflows/ci.yml`.

## License
MIT
