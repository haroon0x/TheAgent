# Design Doc: TheAgent

## Requirements

TheAgent is an AI-powered code assistant that helps users generate documentation, summarize code, generate tests, detect bugs, refactor, add type annotations, migrate code, and interactively chat about code.

- **User Stories:**
  - As a developer, I want to generate docstrings for my Python functions automatically.
  - As a developer, I want to summarize what a Python file does.
  - As a developer, I want to generate unit tests for my code.
  - As a developer, I want to detect bugs and refactor code with AI assistance.
  - As a developer, I want to interactively chat with an agent to manage files and ask code-related questions.

## Flow Design

TheAgent uses a flow-based architecture with specialized nodes for each task. The main flows are:
- **Doc Agent Flow**: Generates docstrings for all functions in a file.
- **Enhanced Agent Flow**: Adds context awareness, safety checks, user approval, and error handling around the main agent node.
- **Simple Enhanced Flow**: Adds context awareness and error handling.
- **Chat Flow**: Interactive chat with intent recognition, clarification, file management, code generation, and analysis.

### Applicable Design Patterns
- **Agent**: The agent decides actions based on user input and context.
- **Workflow**: Tasks are decomposed into nodes and chained in flows.
- **Safety/Approval**: Enhanced flows add user approval and safety checks.

### High-Level Flow Example (Enhanced Agent Flow)

```mermaid
flowchart TD
    context[Context Awareness] --> safety[Safety Check]
    safety -- approved --> agent[Agent Node (Doc/Summary/Test/etc.)]
    safety -- denied --> error[Error Handling]
    agent --> approval[User Approval]
    approval -- approved --> error
    approval -- refine --> agent
```

## Utility Functions

1. **LLM Proxy** (`utils/call_llm.py`)
   - *Input*: prompt (str), function code (str), etc.
   - *Output*: response (str)
   - Used for all LLM tasks: docstring generation, summarization, test generation, bug detection, refactoring, type annotation, migration, and chat.
2. **Progress Tracker** (`utils/utils.py`)
   - *Input*: total (int), description (str)
   - *Output*: CLI progress updates
   - Used for tracking progress in CLI operations.
3. **Flow Visualization** (`utils/visualize_flow.py`)
   - *Input*: Flow object
   - *Output*: Mermaid diagram (str)
   - Used to visualize the flow structure.

*Note: No embedding or vector database utility is currently implemented, despite the template reference.*

## LLM Provider Abstraction and Modularity

TheAgent is designed to be provider-agnostic and modular. All LLM calls are routed through a single proxy (`GeneralLLMProxy`) that supports multiple providers (OpenAI, Anthropic, Google Gemini, Ollama, etc.).

- **Provider/model selection**: The CLI accepts `--provider` and `--model` arguments, which are passed through the shared context and all flows/nodes.
- **Node design**: Each agent node receives and stores the provider/model, and uses them for all LLM calls.
- **Extensibility**: New providers can be added by implementing a new method in the proxy and updating the CLI/flows.

### Rationale
- **Flexibility**: Users can select the best LLM for their needs, cost, or privacy.
- **Future-proofing**: Easy to add new providers or switch as the LLM landscape evolves.
- **Consistency**: All agent logic is provider-agnostic, reducing code duplication.

### Alternatives Considered
- **Hardcoding a single provider**: Not flexible, would require major refactoring to add new providers.
- **Provider-specific nodes**: Would lead to code duplication and maintenance burden.

### Trade-offs
- **Slightly more complex flow/node signatures** (must pass provider/model).
- **Some provider-specific features may require additional abstraction or conditional logic.**

Overall, this approach provides the best balance of flexibility, maintainability, and user empowerment for a modern, multi-provider LLM agent system.

## Node Design

### Shared Store

The shared store is a dictionary that holds context, results, and intermediate data for the flow.

```python
shared = {
    "history": [],
    "current_directory": "...",
    "file": "...",
    "summary": "...",
    "docstring_results": [...],
    "bug_analysis": "...",
    "typed_code": "...",
    "migrated_code": "...",
    "error_info": {...},
    ...
}
```

### Node Types and Steps

1. **ContextAwarenessNode**: Gathers environment info (directory, Python version, files).
   - *Type*: Regular
   - *prep*: Read args from shared
   - *exec*: Gather context
   - *post*: Write context info to shared
2. **SafetyCheckNode**: Confirms safety before in-place modifications.
   - *Type*: Regular
   - *prep*: Read context
   - *exec*: Ask user for approval
   - *post*: Return action ("approved"/"denied")
3. **Agent Nodes** (DocAgentNode, SummaryAgentNode, etc.): Perform the main LLM task.
   - *Type*: Regular
   - *prep*: Read file or code from shared
   - *exec*: Call LLM proxy for the specific task
   - *post*: Write result to shared, output to file/console
4. **UserApprovalNode**: Asks user to approve or refine the result.
   - *Type*: Regular
   - *prep*: Read result from shared
   - *exec*: Ask user for approval/refinement
   - *post*: Return action ("approved"/"refine"/"denied")
5. **ErrorHandlingNode**: Handles errors and provides suggestions.
   - *Type*: Regular
   - *prep*: Read error context
   - *exec*: Suggest fixes
   - *post*: Write error info to shared

*Other nodes include IntentRecognitionNode, ClarificationNode, FileManagementNode, etc., for chat and file operations.*

---

**Summary**  
TheAgent is a modular, flow-based AI code assistant. It uses LLMs for code understanding and generation, with safety and user approval features. The design is extensible, allowing new agent nodes and flows to be added easily.

---

# Project Roadmap

A living roadmap for TheAgent: a CLI-first, agentic Python code automation tool. This roadmap is designed for open source contributors and users to track progress and suggest new features.

## 🚀 Short-Term (v1.x)
- [ ] **Robust CLI/UX**
  - [ ] Improved help, error messages, and argument validation
  - [ ] Interactive prompts for all destructive actions
  - [ ] Chat mode polish (multi-turn, context retention)
- [ ] **Agent/Plugin System**
  - [ ] Clean agent interface for easy extension
  - [ ] Example: custom agent plugin template
- [ ] **LLM Backend Flexibility**
  - [ ] Support for OpenAI, Anthropic, local models (Ollama, etc.)
  - [ ] Configurable API keys and endpoints
- [ ] **Test & CI**
  - [ ] 100% test coverage for all agents and flows
  - [ ] Cross-platform CI (Windows, Linux, Mac)
- [ ] **PyPI Packaging**
  - [ ] Proper package structure, entry points, and metadata
  - [ ] Publish to PyPI for `pip install theagent`
- [ ] **Documentation**
  - [ ] Usage examples for every agent and mode
  - [ ] Architecture and contribution guide

## 🛠️ Mid-Term (v2.x)
- [ ] **Advanced Orchestration**
  - [ ] Conditional/branching flows (if/else, loops)
  - [ ] Multi-file and project-wide analysis
  - [ ] Agent memory and context passing
- [ ] **Plugin Ecosystem**
  - [ ] Third-party agent/plugin discovery and loading
  - [ ] Plugin registry or gallery
- [ ] **LLM Optimization**
  - [ ] Prompt caching and batching
  - [ ] Streaming and async LLM calls
- [ ] **Better Output Modes**
  - [ ] HTML/Markdown report generation
  - [ ] GitHub PR/commit integration
- [ ] **User Feedback Loop**
  - [ ] Built-in feedback and telemetry (opt-in)

## 🌟 Long-Term (v3.x+)
- [ ] **Web UI**
  - [ ] Visual flow builder and result explorer
- [ ] **IDE Integration**
  - [ ] VSCode and PyCharm plugins
- [ ] **Multi-language Support**
  - [ ] Extend agent framework to JavaScript, Java, etc.
- [ ] **Enterprise Features**
  - [ ] Team collaboration, RBAC, and audit logging
- [ ] **AI-Driven Agent Creation**
  - [ ] Let LLMs design and compose new agents/flows

## 📢 Community & Contribution
- [ ] Clear contribution guide and code of conduct
- [ ] Issue templates and feature request workflow
- [ ] Example gallery and user stories
- [ ] Regular roadmap updates and community calls

*Have ideas or want to contribute? Open an issue or PR, or join the discussion on GitHub!*
