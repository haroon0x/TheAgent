# TheAgent

[![Build Status](https://img.shields.io/github/actions/workflow/status/haroon0x/theagent/ci.yml?branch=main)](https://github.com/haroon0x/theagent/actions)
[![PyPI version](https://img.shields.io/pypi/v/theagent.svg)](https://pypi.org/project/theagent/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A powerful AI-powered code assistant that helps you generate documentation, refactor code, detect bugs, and more using Large Language Models (LLMs).

## ⚡ Quick Install

```bash
pip install theagent
```

> **Note:** Only Google Gemini (google-genai) is required by default. If you use OpenAI, Anthropic, or Ollama, TheAgent will prompt you to install the required package the first time you use that provider.

## 🚀 Features

- **Documentation Generation**: Generate comprehensive docstrings for Python functions
- **Code Summarization**: Get clear summaries of your code's functionality
- **Test Generation**: Automatically generate unit tests for your code
- **Bug Detection**: Identify potential bugs and issues in your code
- **Code Refactoring**: Improve code quality and readability
- **Type Annotation**: Add type hints to your Python code
- **Code Migration**: Migrate code to newer Python versions
- **Interactive Chat**: Chat with the agent for code-related questions
- **Enhanced Safety**: Built-in safety checks and user approval workflows
- **File Management**: List, read, and manage files in your project
- **Context Awareness**: Understand your project structure and file relationships

## 🔌 Supported Providers & Environment Variables

| Provider   | Models (examples)         | Env Variable(s)         | PyPI Package         |
|------------|--------------------------|------------------------|----------------------|
| openai     | gpt-4o, gpt-3.5-turbo    | `OPENAI_API_KEY`       | `openai` (optional)  |
| anthropic  | claude-3-haiku-20240307  | `ANTHROPIC_API_KEY`    | `anthropic` (optional) |
| google     | gemini-2.5-flash         | `GOOGLE_GENAI_API_KEY` | `google-genai` (default) |
| ollama     | llama2, phi3, etc.       | `OLLAMA_HOST` (opt.)   | `ollama` (optional)  |

> **Provider packages are installed on demand.** If you select a provider and the required package is missing, TheAgent will prompt you to install it automatically.

## 📦 Installation

```bash
# Clone the repository
# (for development or latest version)
git clone https://github.com/haroon0x/theagent.git
cd theagent
pip install -e .
```

## 🔧 Setup

1. **Get API Keys**: Sign up for your preferred LLM provider:
   - **OpenAI**: Get your API key at [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Anthropic**: Get your API key at [Anthropic Console](https://console.anthropic.com/)
   - **Google**: Get your API key at [Google AI Studio](https://aistudio.google.com/app/apikey)
   - **Ollama**: Install locally at [Ollama.ai](https://ollama.ai/) (no API key needed)

2. **Environment Setup**: Create a `.env` file with your API keys:
   ```bash
   # Choose one or more providers
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_GENAI_API_KEY=your_google_key_here
   OLLAMA_HOST=http://localhost:11434  # Optional, defaults to localhost
   ```

## 🎯 Quick Start

### Basic Usage

```bash
# Generate docstrings for a Python file using OpenAI GPT-4o
theagent --file main.py --agent doc --provider openai --model gpt-4o

# Use Anthropic Claude 3
theagent --file main.py --agent doc --provider anthropic --model claude-3-haiku-20240307

# Use Google Gemini
theagent --file main.py --agent doc --provider google --model gemini-2.5-flash

# Use Ollama (local)
theagent --file main.py --agent doc --provider ollama --model llama2
```

### Interactive Chat Mode

```bash
# Start interactive chat with Gemini
theagent --chat --provider google --model gemini-2.5-flash
```

### Enhanced Mode with Safety Checks

```bash
# Use enhanced mode with Anthropic Claude 3
theagent --file main.py --agent doc --enhanced --provider anthropic --model claude-3-haiku-20240307
```

## 📋 Command Line Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--file, -f` | Python file to process | None | For file processing |
| `--agent, -a` | Type of agent (doc, summary, test, bug, refactor, type, migration) | None | For file processing |
| `--output, -o` | Output mode (console, in-place, new-file) | console | No |
| `--provider` | LLM provider (openai, anthropic, google, ollama) | openai | No |
| `--model` | LLM model to use (e.g., gpt-4o, claude-3-haiku-20240307, gemini-2.5-flash) | None | No |
| `--enhanced` | Use enhanced flow with safety checks | False | No |
| `--chat` | Start interactive chat mode | False | No |
| `--verbose, -v` | Enable verbose output | False | No |
| `--no-confirm` | Skip user confirmation prompts | False | No |
| `--migration-target` | Target for code migration | Python 3 | No |
| `--save-session` | Save chat session to file on exit | None | No |
| `--load-session` | Load chat session from file at start | None | No |
| `--context-files` | Comma-separated list of files to load as project context | None | No |
| `--openai-api-key` | OpenAI API key (overrides env/config) | None | No |
| `--anthropic-api-key` | Anthropic API key (overrides env/config) | None | No |
| `--google-api-key` | Google Gemini API key (overrides env/config) | None | No |
| `--ollama-host` | Ollama host URL (overrides env/config) | None | No |

- Use `theagent --help` for full CLI help.
- Use `theagent --version` to print the current version.

## ⚙️ Configuration File (.theagent.toml)

You can also store your API keys and Ollama host in a `.theagent.toml` file in your project root:

```toml
openai_api_key = "sk-..."
anthropic_api_key = "..."
google_api_key = "..."
ollama_host = "http://localhost:11434"
```

**Precedence order:**
1. CLI argument (e.g. `--openai-api-key`)
2. `.theagent.toml` config file
3. Environment variable (e.g. `OPENAI_API_KEY`)
4. `.env` file (auto-loaded)
5. Provider default (for Ollama host)

This makes it easy to manage credentials for different projects or environments.

## 🔍 Examples

### Generate Documentation

```bash
# Generate docstrings for all functions in main.py
theagent --file main.py --agent doc --output in-place
```

### Code Analysis

```bash
# Get a summary of your code
theagent --file main.py --agent summary

# Detect potential bugs
theagent --file main.py --agent bug --verbose
```

### Interactive Development

```bash
# Start chat mode for interactive help
theagent --chat

# In chat mode, try these commands:
# - "list files in current directory"
# - "read main.py"
# - "generate docstrings for main.py"
# - "what does this code do?"
```

### Enhanced Safety Mode

```bash
# Use enhanced mode with safety checks and user approval
theagent --file main.py --agent doc --enhanced

# This will:
# 1. Check file safety before modification
# 2. Generate the requested changes
# 3. Ask for user approval
# 4. Allow refinement if needed
```

## 🏗️ Architecture

TheAgent uses a modular architecture with:

- **Flow-based Processing**: Uses PocketFlow for orchestration
- **Node-based Agents**: Specialized nodes for different tasks, each aware of provider/model
- **LLM Integration**: Supports OpenAI, Anthropic, Google Gemini, and Ollama (local)
- **Safety Features**: Built-in checks and user approval workflows
- **Error Handling**: Robust error handling with fallback responses

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agent_nodes_comprehensive.py

# Run with verbose output
pytest -v
```

## 📁 Project Structure

```
theagent/
├── src/theagent/
│   ├── __init__.py
│   ├── main.py              # Main CLI entry point
│   ├── flow.py              # Flow definitions
│   ├── nodes.py             # Agent node implementations
│   └── utils/
│       ├── __init__.py
│       ├── call_llm.py      # LLM integration
│       └── visualize_flow.py # Flow visualization
├── docs/                    # Documentation
├── tests/                   # Test files
├── requirements.txt         # Dependencies
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

## 🔧 Development

### Adding New Agents

1. Create a new node in `src/theagent/nodes.py`
2. Add the node to the flow in `src/theagent/flow.py`
3. Update the CLI options in `src/theagent/main.py`
4. Add tests and documentation

### Flow Visualization

```bash
# Visualize a specific flow
python -m src.theagent.utils.visualize_flow src.theagent.flow:create_chat_flow

# This generates a Mermaid diagram showing the flow structure
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Join discussions about features and improvements
- **Documentation**: Check the `docs/` folder for detailed documentation

## 🚀 Roadmap

- [ ] Web interface
- [ ] More LLM providers (OpenAI, Anthropic, Ollama)
- [ ] Advanced code analysis
- [ ] Integration with IDEs
- [ ] Batch processing
- [ ] Custom agent training

---

**TheAgent** - Making code development easier with AI! 🤖✨