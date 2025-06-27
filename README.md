[![CI](https://github.com/haroon0x/TheAgent/actions/workflows/ci.yml/badge.svg)](https://github.com/haroon0x/TheAgent/actions/workflows/ci.yml)

# TheAgent

> TheAgent: Your all-in-one Python CLI code agent for docstrings, summaries, migration, tests, bug detection, and more—powered by PocketFlow and Alchemist AI.

**TheAgent** is a powerful, extensible command-line tool that automates Python code understanding and transformation tasks. With a single CLI, you can:
- Generate Google-style docstrings, summaries, and type annotations
- Migrate code to new versions or libraries
- Detect bugs, refactor code, and generate tests
- Orchestrate multi-step code workflows using natural language instructions

Built on a modular, agentic architecture, TheAgent leverages PocketFlow for flexible node orchestration and Alchemist AI for LLM-powered code analysis. Its design makes it easy to add new agent types and integrate with any LLM backend.

## Architecture Overview

```mermaid
flowchart TD
    U["User"]
    CLI["CLI"]
    Config["Config"]
    ModeSwitch{{"Mode"}}
    Orchestrator["Orchestrator"]
    AgentSelector["Agent Selector"]
    AgentNodes["Agents"]
    DocNode["Doc"]
    SummaryNode["Summary"]
    TypeNode["Type"]
    MigrationNode["Migrate"]
    TestNode["Test"]
    BugNode["Bug"]
    RefactorNode["Refactor"]
    Parser["Parser"]
    AgentLogic["Logic"]
    LLMProxy["LLM Proxy"]
    LLM["LLM"]
    OutputHandler["Output"]
    FileWriter["File"]
    Console["Console"]
    Backup["Backup"]

    %% User interaction
    U -->|"Command/Instruction"| CLI
    CLI -->|"Args/Config"| Config
    CLI -->|"Mode"| ModeSwitch
    CLI -->|"Progress/Errors"| U
    Config -->|"Env"| CLI

    %% Mode selection
    ModeSwitch -- "Orchestrator" --> Orchestrator
    ModeSwitch -- "Direct" --> AgentSelector
    Orchestrator -->|"Instruction"| AgentSelector
    AgentSelector -->|"Dispatch"| AgentNodes

    %% Agent nodes
    AgentNodes --> DocNode
    AgentNodes --> SummaryNode
    AgentNodes --> TypeNode
    AgentNodes --> MigrationNode
    AgentNodes --> TestNode
    AgentNodes --> BugNode
    AgentNodes --> RefactorNode

    %% Agent workflow
    DocNode -->|"Parse"| Parser
    SummaryNode -->|"Parse"| Parser
    TypeNode -->|"Parse"| Parser
    MigrationNode -->|"Parse"| Parser
    TestNode -->|"Parse"| Parser
    BugNode -->|"Parse"| Parser
    RefactorNode -->|"Parse"| Parser

    Parser -->|"Info"| AgentLogic
    AgentLogic -->|"LLM Req"| LLMProxy
    LLMProxy -->|"API"| LLM
    LLM -->|"Resp"| LLMProxy
    LLMProxy -->|"Output"| AgentLogic
    AgentLogic -->|"Result"| OutputHandler

    %% Output
    OutputHandler -->|"File"| FileWriter
    OutputHandler -->|"Console"| Console
    OutputHandler -->|"Backup"| Backup
    FileWriter -->|"Modified"| U
    Console -->|"Printed"| U
    Backup -->|"Backup"| U

    %% Styling for visibility
    classDef user fill:#222,color:#fff,stroke:#000,stroke-width:3,font-size:18px;
    classDef cli fill:#0057b7,color:#fff,stroke:#000,stroke-width:3,font-size:18px;
    classDef config fill:#ffb300,color:#000,stroke:#000,stroke-width:3,font-size:16px;
    classDef mode fill:#6a1b9a,color:#fff,stroke:#000,stroke-width:3,font-size:16px;
    classDef orchestrator fill:#388e3c,color:#fff,stroke:#000,stroke-width:3,font-size:16px;
    classDef selector fill:#0288d1,color:#fff,stroke:#000,stroke-width:3,font-size:16px;
    classDef agents fill:#ffd600,color:#000,stroke:#000,stroke-width:3,font-size:16px;
    classDef agent fill:#fff176,color:#000,stroke:#000,stroke-width:2,font-size:15px;
    classDef parser fill:#ff7043,color:#fff,stroke:#000,stroke-width:3,font-size:16px;
    classDef logic fill:#8d6e63,color:#fff,stroke:#000,stroke-width:3,font-size:16px;
    classDef llmproxy fill:#1976d2,color:#fff,stroke:#000,stroke-width:3,font-size:16px;
    classDef llm fill:#c51162,color:#fff,stroke:#000,stroke-width:3,font-size:16px;
    classDef output fill:#43a047,color:#fff,stroke:#000,stroke-width:3,font-size:16px;
    classDef file fill:#fff,color:#000,stroke:#000,stroke-width:2,font-size:15px;
    classDef console fill:#fff,color:#000,stroke:#000,stroke-width:2,font-size:15px;
    classDef backup fill:#fff,color:#000,stroke:#000,stroke-width:2,font-size:15px;

    class U user;
    class CLI cli;
    class Config config;
    class ModeSwitch mode;
    class Orchestrator orchestrator;
    class AgentSelector selector;
    class AgentNodes agents;
    class DocNode,SummaryNode,TypeNode,MigrationNode,TestNode,BugNode,RefactorNode agent;
    class Parser parser;
    class AgentLogic logic;
    class LLMProxy llmproxy;
    class LLM llm;
    class OutputHandler output;
    class FileWriter file;
    class Console console;
    class Backup backup;
```

## Overview
This project provides an intelligent agent called **TheAgent** that automates the creation of high-quality, Google-style docstrings for Python functions and much more. It uses PocketFlow for agent orchestration and Alchemist AI (via a proxy) for LLM-powered code analysis and generation.

**Why TheAgent?**
- Flexible: Supports docstring, summary, type annotation, migration, test generation, bug detection, refactor, and orchestrator agents.
- Brandable: TheAgent is designed to be extended for any code automation or analysis task.
- User-centric: CLI and chat modes for both power users and beginners.

*TheAgent is a strong, brandable name chosen for its flexibility and future-proofing. You can extend it to any code automation or agentic workflow you need.*

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
| `--agent <type>`                | Agent type: `