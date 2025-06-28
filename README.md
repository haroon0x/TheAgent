# TheAgent

A powerful AI-powered code assistant that helps you generate documentation, refactor code, detect bugs, and more using Large Language Models (LLMs).

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

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/theagent.git
cd theagent

# Install dependencies
pip install -r requirements.txt

# Set up your API key
echo "ALCHEMYST_API_KEY=your_api_key_here" > .env
```

## 🔧 Setup

1. **Get an API Key**: Sign up at [AlchemistAI](https://alchemistai.com) to get your API key
2. **Environment Setup**: Create a `.env` file with your API key:
   ```bash
   ALCHEMYST_API_KEY=your_api_key_here
   ```

## 🎯 Quick Start

### Basic Usage

```bash
# Generate docstrings for a Python file
python -m theagent --file main.py --agent doc

# Summarize code
python -m theagent --file main.py --agent summary

# Generate tests
python -m theagent --file main.py --agent test

# Detect bugs
python -m theagent --file main.py --agent bug

# Refactor code
python -m theagent --file main.py --agent refactor

# Add type annotations
python -m theagent --file main.py --agent type

# Migrate code
python -m theagent --file main.py --agent migration
```

### Interactive Chat Mode

```bash
# Start interactive chat
python -m theagent --chat
```

### Enhanced Mode with Safety Checks

```bash
# Use enhanced mode with safety checks and user approval
python -m theagent --file main.py --agent doc --enhanced
```

## 📋 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file, -f` | Python file to process | None |
| `--agent, -a` | Type of agent (doc, summary, test, bug, refactor, type, migration) | None |
| `--output, -o` | Output mode (console, in-place, new-file) | console |
| `--llm` | LLM provider (alchemyst, openai, anthropic, ollama) | alchemyst |
| `--enhanced` | Use enhanced flow with safety checks | False |
| `--chat` | Start interactive chat mode | False |
| `--verbose, -v` | Enable verbose output | False |
| `--no-confirm` | Skip user confirmation prompts | False |
| `--migration-target` | Target for code migration | Python 3 |

## 🔍 Examples

### Generate Documentation

```bash
# Generate docstrings for all functions in main.py
python -m theagent --file main.py --agent doc --output in-place
```

### Code Analysis

```bash
# Get a summary of your code
python -m theagent --file main.py --agent summary

# Detect potential bugs
python -m theagent --file main.py --agent bug --verbose
```

### Interactive Development

```bash
# Start chat mode for interactive help
python -m theagent --chat

# In chat mode, try these commands:
# - "list files in current directory"
# - "read main.py"
# - "generate docstrings for main.py"
# - "what does this code do?"
```

## 🏗️ Architecture

TheAgent uses a modular architecture with:

- **Flow-based Processing**: Uses PocketFlow for orchestration
- **Node-based Agents**: Specialized nodes for different tasks
- **LLM Integration**: Multiple LLM provider support
- **Safety Features**: Built-in checks and user approval workflows
- **Error Handling**: Robust error handling with fallback responses

## 🧪 Testing

```bash
# Run the stability test
python test_stable_version.py
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
│       └── call_llm.py      # LLM integration
├── docs/                    # Documentation
├── tests/                   # Test files
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
└── README.md               # This file
```

## 🔧 Development

### Adding New Agents

1. Create a new node in `src/theagent/nodes.py`
2. Add the node to the flow in `src/theagent/flow.py`
3. Update the CLI options in `src/theagent/main.py`
4. Add tests and documentation

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
- [ ] More LLM providers
- [ ] Advanced code analysis
- [ ] Integration with IDEs
- [ ] Batch processing
- [ ] Custom agent training

---

**TheAgent** - Making code development easier with AI! 🤖✨