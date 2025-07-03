import argparse
import os
import sys
import json
from theagent.flow import (
    create_doc_agent_flow, create_enhanced_agent_flow, create_simple_enhanced_flow,
    create_chat_flow
)
from theagent.utils.call_llm import AlchemistAIProxy

class Args:
    pass

SESSION_FILE_DEFAULT = "theagent_session.json"

def setup_shared_context(args_obj):
    """Setup shared context with current directory and file information."""
    shared = {
        'chat_history': [],
        'current_directory': os.getcwd(),
        'verbose': getattr(args_obj, 'verbose', False),
        'no_confirm': getattr(args_obj, 'no_confirm', False),
        'provider': getattr(args_obj, 'provider', 'openai'),
        'model': getattr(args_obj, 'model', None),
    }

    if hasattr(args_obj, 'file') and args_obj.file:
        shared['file'] = args_obj.file
        if os.path.exists(args_obj.file):
            shared['file_exists'] = True
            shared['file_size'] = os.path.getsize(args_obj.file)
        else:
            shared['file_exists'] = False
            shared['last_error'] = f"File not found: {args_obj.file}"
    
    return shared

def handle_error(error, shared, args_obj):
    """Handle errors gracefully with user-friendly messages."""
    print(f"[ERROR] An unexpected error occurred: {error}")
    if shared.get('verbose', False):
        import traceback
        traceback.print_exc()
    sys.exit(1)

def setup_llm_proxy(args):
    """Always use AlchemistAIProxy for all LLM calls."""
    return AlchemistAIProxy()

def run_sync_flow(flow, shared):
    """Run a synchronous flow."""
    return flow.run(shared)

def save_session(shared, filename=SESSION_FILE_DEFAULT):
    data = {
        'chat_history': shared.get('chat_history', []),
        'project_context': shared.get('project_context', {})
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"[INFO] Session saved to {filename}")

def load_session(shared, filename=SESSION_FILE_DEFAULT):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        shared['chat_history'] = data.get('chat_history', [])
        shared['project_context'] = data.get('project_context', {})
        print(f"[INFO] Session loaded from {filename}")
    except Exception as e:
        print(f"[WARN] Could not load session: {e}")

def load_project_context(shared, files=None):
    """Load project context (README, main files, config) into shared['project_context']."""
    context = {}
    if files is None:
        files = []
        # Default: README.md, pyproject.toml, requirements.txt, main.py
        for fname in ["README.md", "pyproject.toml", "requirements.txt", "main.py"]:
            if os.path.exists(fname):
                files.append(fname)
    for fname in files:
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                context[fname] = f.read()
        except Exception as e:
            context[fname] = f"[ERROR] Could not load: {e}"
    shared['project_context'] = context

def chat_with_theagent(args_obj, llm_proxy):
    """Enhanced chat function with better context awareness and error handling."""
    print("\n[TheAgent Chat] Type your instructions or questions. Type 'exit' to quit.")
    print("[TIP] Try: 'list files', 'read main.py', 'generate docstrings for main.py', or ask general questions.\n")
    
    shared = setup_shared_context(args_obj)
    if getattr(args_obj, 'load_session', None):
        load_session(shared, args_obj.load_session)
    # Load project context
    context_files = getattr(args_obj, 'context_files', None)
    if context_files:
        files = [f.strip() for f in context_files.split(',') if f.strip()]
        load_project_context(shared, files)
    else:
        load_project_context(shared)
    
    # Pass provider/model to flow if needed
    flow = create_chat_flow(args_obj, llm_proxy, provider=shared['provider'], model=shared['model'])
    
    while True:
        try:
            user_input = input('You: ')
            if user_input.strip().lower() in {'exit', 'quit', 'bye'}:
                print('[GOODBYE] Thanks for using TheAgent!')
                if getattr(args_obj, 'save_session', None):
                    save_session(shared, args_obj.save_session)
                break
            
            shared['chat_history'].append({'role': 'user', 'content': user_input})
            args_obj.instruction = user_input
            try:
                result = flow.run(shared)
                if result:
                    print(f"TheAgent: {result}")
                    shared['chat_history'].append({'role': 'agent', 'content': result})
            except Exception as e:
                handle_error(e, shared, args_obj)
                print("[RECOVER] Attempting to recover...")
                shared['last_error'] = e
                
        except KeyboardInterrupt:
            print("\n\n[GOODBYE] Chat interrupted. Goodbye!")
            if getattr(args_obj, 'save_session', None):
                save_session(shared, args_obj.save_session)
            break
        except EOFError:
            print("\n\n[GOODBYE] End of input. Goodbye!")
            if getattr(args_obj, 'save_session', None):
                save_session(shared, args_obj.save_session)
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            print("[RESTART] Restarting chat...")
            shared = setup_shared_context(args_obj)
            if getattr(args_obj, 'load_session', None):
                load_session(shared, args_obj.load_session)

def main():
    """Main entry point for TheAgent."""
    parser = argparse.ArgumentParser(description="TheAgent - AI-powered code assistant")
    
    parser.add_argument("--file", "-f", help="Python file to process")
    parser.add_argument("--agent", "-a", choices=["doc", "summary", "test", "bug", "refactor", "type", "migration"], 
                       help="Type of agent to use")
    
    parser.add_argument("--output", "-o", choices=["console", "in-place", "new-file"], 
                       default="console", help="Output mode")
    
    parser.add_argument("--llm", choices=["alchemyst", "openai", "anthropic", "ollama"], 
                       default="alchemyst", help="LLM provider to use")
    
    parser.add_argument("--enhanced", action="store_true", 
                       help="Use enhanced flow with safety checks and user approval")
    parser.add_argument("--chat", action="store_true", 
                       help="Start interactive chat mode")
    
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    parser.add_argument("--no-confirm", action="store_true", 
                       help="Skip user confirmation prompts")
    parser.add_argument("--migration-target", default="Python 3", 
                       help="Target for code migration")
    
    parser.add_argument("--save-session", help="Save chat session to file on exit")
    parser.add_argument("--load-session", help="Load chat session from file at start")
    parser.add_argument("--context-files", help="Comma-separated list of files to load as project context")
    parser.add_argument("--provider", choices=["openai", "anthropic", "google", "ollama"], default="openai", help="LLM provider to use")
    parser.add_argument("--model", help="LLM model to use (e.g., gpt-4o, claude-3-haiku-20240307, gemini-2.5-flash)")
    
    args_obj = parser.parse_args()
    
    shared = {
        "verbose": args_obj.verbose,
        "no_confirm": args_obj.no_confirm
    }
    
    try:
        llm_proxy = setup_llm_proxy(args_obj)
        
        if args_obj.chat:
            print("[INFO] Starting chat mode...")
            chat_with_theagent(args_obj, llm_proxy)
        elif args_obj.file and args_obj.agent:
            print("[INFO] Starting processing...")
            flow_args = dict(provider=getattr(args_obj, 'provider', 'openai'), model=getattr(args_obj, 'model', None))
            if args_obj.enhanced:
                flow = create_enhanced_agent_flow(args_obj, llm_proxy, **flow_args)
            else:
                if args_obj.agent == "doc":
                    flow = create_doc_agent_flow(args_obj, llm_proxy, **flow_args)
                elif args_obj.agent == "summary":
                    flow = create_simple_enhanced_flow(args_obj, llm_proxy, **flow_args)
                else:
                    flow = create_simple_enhanced_flow(args_obj, llm_proxy, **flow_args)
            run_sync_flow(flow, shared)
        else:
            parser.print_help()
            return
        
        print("[SUCCESS] Processing complete!")
        
    except Exception as e:
        handle_error(e, shared, args_obj)

if __name__ == "__main__":
    main()
