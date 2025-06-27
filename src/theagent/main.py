import argparse
from theagent.flow import create_doc_agent_flow
from theagent.utils.call_llm import AlchemistAIProxy

class Args:
    pass

def main():
    parser = argparse.ArgumentParser(description="Code Documentation Agent: Generate Google-style docstrings, summaries, type annotations, migrations, tests, bug reports, or refactored code for Python files.")
    parser.add_argument('--file', required=True, help='Path to the Python file to process')
    parser.add_argument('--output', default='console', choices=['console', 'in-place', 'new-file'], help='Output mode (for doc, migration, refactor, test agents)')
    parser.add_argument('--llm', default='alchemyst-ai/alchemyst-c1', help='LLM model to use')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompts for destructive actions')
    parser.add_argument('--verbose', action='store_true', help='Print detailed progress')
    parser.add_argument('--agent', default='doc', choices=['doc', 'summary', 'type', 'migration', 'test', 'bug', 'refactor', 'orchestrator'], help='Agent type: doc (default), summary, type, migration, test, bug, refactor, or orchestrator')
    parser.add_argument('--migration-target', default='Python 3', help='Migration target for migration agent (e.g., "Python 3", "TensorFlow 2")')
    parser.add_argument('--instruction', default=None, help='Instruction for the orchestrator agent (natural language)')
    parser.add_argument('--chat', action='store_true', help='Enable chat mode with the orchestrator agent')
    args = parser.parse_args()
    # Convert argparse Namespace to object with attribute access for PocketFlow
    args_obj = Args()
    for k, v in vars(args).items():
        setattr(args_obj, k.replace('-', '_'), v)
    llm_proxy = AlchemistAIProxy()
    if getattr(args_obj, 'chat', False):
        print("\n[Chat Mode] Type your instructions for the orchestrator agent. Type 'exit' or 'quit' to stop.\n")
        while True:
            user_input = input('>>> ')
            if user_input.strip().lower() in {'exit', 'quit'}:
                print('Exiting chat mode.')
                break
            args_obj.agent = 'orchestrator'
            args_obj.instruction = user_input
            try:
                flow = create_doc_agent_flow(args_obj, llm_proxy)
                shared = {}
                flow.run(shared)
            except Exception as e:
                print(f"[Error] {e}")
    else:
        if getattr(args_obj, 'agent', 'doc') == 'orchestrator' and not getattr(args_obj, 'instruction', None):
            args_obj.instruction = input('Enter your instruction for the orchestrator agent: ')
        try:
            flow = create_doc_agent_flow(args_obj, llm_proxy)
            shared = {}
            flow.run(shared)
        except Exception as e:
            print(f"[Error] {e}")

if __name__ == "__main__":
    main()
