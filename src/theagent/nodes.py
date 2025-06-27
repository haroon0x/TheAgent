from pocketflow import Node
from theagent.utils.call_llm import AlchemistAIProxy
import ast
import os
import shutil
import re

class BaseAgentNode(Node):
    def __init__(self, args, llm_proxy):
        super().__init__()
        self.args = args
        self.llm_proxy = llm_proxy

    def read_source(self):
        file_path = self.args.file
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_output(self, content, suffix, console_title=None):
        output_mode = getattr(self.args, 'output', 'console')
        file_path = self.args.file
        verbose = getattr(self.args, 'verbose', False)
        if output_mode == 'console':
            if console_title:
                print(f"\n=== {console_title} ===\n")
            print(content)
        elif output_mode == 'in-place':
            backup_path = file_path + '.bak'
            shutil.copyfile(file_path, backup_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.rstrip() + '\n')
            if verbose:
                print(f"Wrote {console_title or 'output'} to {file_path} (backup at {backup_path})")
        elif output_mode == 'new-file':
            new_file = file_path.replace('.py', f'_{suffix}.py')
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write(content.rstrip() + '\n')
            if verbose:
                print(f"Wrote {console_title or 'output'} to {new_file}")

    def _find_end_line(self, node):
        max_line = getattr(node, 'lineno', 0)
        for child in ast.iter_child_nodes(node):
            child_line = self._find_end_line(child)
            if child_line > max_line:
                max_line = child_line
        return max_line

    def _manual_source_segment(self, source_code, start, end):
        lines = source_code.splitlines()
        return '\n'.join(lines[start-1:end])

class DocAgentNode(BaseAgentNode):
    def prep(self, shared):
        # Read and parse the Python file
        source_code = self.read_source()
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {self.args.file}: {e}")
        # Extract all function definitions
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get start and end line numbers
                start_line = node.lineno
                # Try to get end line (Python 3.8+)
                end_line = getattr(node, 'end_lineno', None)
                if end_line is None:
                    # Fallback: estimate end line
                    end_line = self._find_end_line(node)
                # Get source segment
                try:
                    func_source = ast.get_source_segment(source_code, node)
                except Exception:
                    func_source = self._manual_source_segment(source_code, start_line, end_line)
                # Get indentation
                def_line = source_code.splitlines()[start_line-1]
                indentation = def_line[:len(def_line)-len(def_line.lstrip())]
                functions.append({
                    'name': node.name,
                    'source_code': func_source,
                    'start_line': start_line,
                    'end_line': end_line,
                    'indentation': indentation,
                })
        if not functions:
            raise ValueError("No functions found in the file.")
        shared['functions'] = functions
        shared['source_code'] = source_code
        return functions

    def _clean_docstring(self, doc):
        doc = doc.strip()
        # Remove code fences
        doc = re.sub(r'^```(?:python)?', '', doc, flags=re.IGNORECASE).strip()
        doc = re.sub(r'```$', '', doc, flags=re.IGNORECASE).strip()
        # Remove leading/trailing triple quotes
        doc = re.sub(r'^(["\"])\1\1', '', doc).strip()
        doc = re.sub(r'(["\"])\1\1$', '', doc).strip()
        return doc

    def exec(self, functions):
        # For each function, generate a docstring
        docstrings = []
        for func in functions:
            docstring = self.llm_proxy.generate_docstring(func['source_code'], self.args.llm)
            docstrings.append(docstring)
        return docstrings
    
    def post(self, shared, prep_res, exec_res):
        output_mode = self.args.output
        file_path = self.args.file
        docstrings = exec_res
        functions = shared['functions']
        source_lines = shared['source_code'].splitlines()
        verbose = getattr(self.args, 'verbose', False)
        no_confirm = getattr(self.args, 'no_confirm', False)
        if output_mode == 'console':
            for func, doc in zip(functions, docstrings):
                print(f"\nFunction: {func['name']}\n{'-'*40}")
                print(func['source_code'])
                print(f"\nGenerated docstring:\n{self._clean_docstring(doc)}\n")
            return 'done'
        # Prepare new file content
        new_lines = source_lines[:]
        offset = 0
        for idx, (func, doc) in enumerate(zip(functions, docstrings)):
            clean_doc = self._clean_docstring(doc)
            start = func['start_line'] - 1 + offset
            end = func['end_line'] - 1 + offset
            func_lines = new_lines[start:end+1]
            # Remove old docstring if present
            func_body_idx = 1
            if (len(func_lines) > 1 and func_lines[1].lstrip().startswith(('"""', "'''"))):
                doc_end = self._find_docstring_end(func_lines, func_lines[1].lstrip()[:3])
                func_body_idx = doc_end + 1
            # Insert new docstring after def line
            docstring_lines = [func['indentation'] + '    ' + l for l in clean_doc.splitlines()]
            docstring_block = [func['indentation'] + '    """'] + docstring_lines + [func['indentation'] + '    """']
            new_func_lines = [func_lines[0]] + docstring_block + func_lines[func_body_idx:]
            new_lines[start:end+1] = new_func_lines
            offset += len(new_func_lines) - len(func_lines)
            if output_mode in ('in-place', 'new-file') and not no_confirm:
                confirm = input(f"Replace docstring for function '{func['name']}'? [y/N]: ")
                if confirm.strip().lower() != 'y':
                    continue
            if verbose:
                print(f"Processed function: {func['name']}")
        # Write output
        if output_mode == 'in-place':
            backup_path = file_path + '.bak'
            shutil.copyfile(file_path, backup_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines) + '\n')
            if verbose:
                print(f"Wrote updated file to {file_path} (backup at {backup_path})")
        elif output_mode == 'new-file':
            new_file = file_path.replace('.py', '_documented.py')
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines) + '\n')
            if verbose:
                print(f"Wrote documented file to {new_file}")
        return 'done'

    def _find_docstring_end(self, func_lines, quote):
        # Find the end of the docstring block
        for i, line in enumerate(func_lines[1:], 1):
            if line.lstrip().startswith(quote) and i != 1:
                return i
        return 1

class SummaryAgentNode(BaseAgentNode):
    def prep(self, shared):
        source_code = self.read_source()
        shared['source_code'] = source_code
        return source_code

    def exec(self, source_code):
        # Summarize the file
        summary = self.llm_proxy.summarize_code(source_code, self.args.llm)
        return summary

    def post(self, shared, prep_res, exec_res):
        print("\n=== File Summary ===\n")
        print(exec_res)
        return 'done'

class TypeAnnotationAgentNode(BaseAgentNode):
    def prep(self, shared):
        source_code = self.read_source()
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {self.args.file}: {e}")
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = getattr(node, 'end_lineno', None)
                if end_line is None:
                    end_line = self._find_end_line(node)
                try:
                    func_source = ast.get_source_segment(source_code, node)
                except Exception:
                    func_source = self._manual_source_segment(source_code, start_line, end_line)
                functions.append({'name': node.name, 'source_code': func_source})
        shared['functions'] = functions
        return functions

    def exec(self, functions):
        suggestions = []
        for func in functions:
            suggestion = self.llm_proxy.suggest_type_annotations(func['source_code'], self.args.llm)
            suggestions.append({'name': func['name'], 'suggestion': suggestion})
        return suggestions
    
    def post(self, shared, prep_res, exec_res):
        print("\n=== Type Annotation Suggestions ===\n")
        for item in exec_res:
            print(f"Function: {item['name']}")
            print(item['suggestion'])
            print("-"*40)
        return 'done'

class MigrationAgentNode(BaseAgentNode):
    def exec(self, source_code):
        migration_target = getattr(self.args, 'migration_target', 'Python 3')
        migrated_code = self.llm_proxy.migration_code(source_code, migration_target, self.args.llm)
        return migrated_code

    def post(self, shared, prep_res, exec_res):
        output_mode = getattr(self.args, 'output', 'console')
        file_path = self.args.file
        migrated_code = exec_res
        verbose = getattr(self.args, 'verbose', False)
        if output_mode == 'console':
            print("\n=== Migrated Code ===\n")
            print(migrated_code)
        elif output_mode == 'in-place':
            backup_path = file_path + '.bak'
            shutil.copyfile(file_path, backup_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(migrated_code.rstrip() + '\n')
            if verbose:
                print(f"Wrote migrated file to {file_path} (backup at {backup_path})")
        elif output_mode == 'new-file':
            new_file = file_path.replace('.py', '_migrated.py')
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write(migrated_code.rstrip() + '\n')
            if verbose:
                print(f"Wrote migrated file to {new_file}")
        return 'done'

class TestGenerationAgentNode(BaseAgentNode):
    def prep(self, shared):
        source_code = self.read_source()
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {self.args.file}: {e}")
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = getattr(node, 'end_lineno', None)
                if end_line is None:
                    end_line = self._find_end_line(node)
                try:
                    func_source = ast.get_source_segment(source_code, node)
                except Exception:
                    func_source = self._manual_source_segment(source_code, start_line, end_line)
                functions.append({'name': node.name, 'source_code': func_source})
        shared['functions'] = functions
        return functions

    def exec(self, functions):
        tests = []
        for func in functions:
            test_code = self.llm_proxy.test_generation(func['source_code'], self.args.llm)
            tests.append({'name': func['name'], 'test_code': test_code})
        return tests

    def _clean_test_code(self, code):
        import re
        code = re.sub(r'^```(?:python)?', '', code, flags=re.MULTILINE).strip()
        code = re.sub(r'```$', '', code, flags=re.MULTILINE).strip()
        return code

    def post(self, shared, prep_res, exec_res):
        output_mode = getattr(self.args, 'output', 'console')
        file_path = self.args.file
        verbose = getattr(self.args, 'verbose', False)
        import os
        if output_mode == 'console':
            print("\n=== Generated Unit Tests ===\n")
            for item in exec_res:
                print(f"Function: {item['name']}")
                print(self._clean_test_code(item['test_code']))
                print("-"*40)
        else:
            # Write to test_<filename>.py
            base = os.path.basename(file_path)
            if base.endswith('.py'):
                base = base[:-3]
            test_file = os.path.join(os.path.dirname(file_path), f"test_{base}.py")
            with open(test_file, 'w', encoding='utf-8') as f:
                for item in exec_res:
                    clean_code = self._clean_test_code(item['test_code'])
                    f.write(f"# Tests for {item['name']}\n{clean_code}\n\n")
            if verbose:
                print(f"Wrote generated tests to {test_file}")
        return 'done'

class BugDetectionAgentNode(BaseAgentNode):
    def exec(self, source_code):
        bug_report = self.llm_proxy.bug_detection(source_code, self.args.llm)
        return bug_report

    def post(self, shared, prep_res, exec_res):
        print("\n=== Bug Report ===\n")
        print(exec_res)
        return 'done'

class RefactorCodeAgentNode(BaseAgentNode):
    def exec(self, source_code):
        refactored_code = self.llm_proxy.refactor_code(source_code, self.args.llm)
        return refactored_code
    
    def post(self, shared, prep_res, exec_res):
        output_mode = getattr(self.args, 'output', 'console')
        file_path = self.args.file
        verbose = getattr(self.args, 'verbose', False)
        if output_mode == 'console':
            print("\n=== Refactored Code ===\n")
            print(exec_res)
        elif output_mode == 'in-place':
            backup_path = file_path + '.bak'
            shutil.copyfile(file_path, backup_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(exec_res.rstrip() + '\n')
            if verbose:
                print(f"Wrote refactored file to {file_path} (backup at {backup_path})")
        elif output_mode == 'new-file':
            new_file = file_path.replace('.py', '_refactored.py')
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write(exec_res.rstrip() + '\n')
            if verbose:
                print(f"Wrote refactored file to {new_file}")
        return 'done'

class OrchestratorAgentNode(BaseAgentNode):
    def prep(self, shared):
        # Get the user's instruction
        instruction = getattr(self.args, 'instruction', None)
        shared['instruction'] = instruction
        return instruction

    def exec(self, instruction):
        # Use the LLM to map the instruction to a list of agent types or answer
        from langchain_openai import ChatOpenAI
        system_prompt = (
            "You are TheAgent, an expert developer assistant and orchestrator for code analysis and automation.\n"
            "You can run the following specialized agents:\n"
            "- 'doc': Generate Google-style docstrings for all functions in a Python file.\n"
            "- 'summary': Summarize the main purpose and structure of a Python file.\n"
            "- 'type': Suggest type annotations for all functions.\n"
            "- 'migration': Migrate code to a new version or framework (e.g., Python 3, TensorFlow 2).\n"
            "- 'test': Generate pytest-style unit tests for the code.\n"
            "- 'bug': Find bugs and suggest fixes.\n"
            "- 'refactor': Refactor code for readability and maintainability.\n"
            "\n"
            "Given a user instruction, output a Python list of agent types (from the above) that should be run, in order, to fulfill the instruction.\n"
            "If the instruction is a general question or not related to code, respond with a string answer instead of a list.\n"
            "If the instruction is ambiguous, ask the user for clarification.\n"
            "\n"
            "Examples:\n"
            "Instruction: 'Summarize and generate docstrings.'\n"
            "Output: ['summary', 'doc']\n"
            "Instruction: 'Find bugs and refactor.'\n"
            "Output: ['bug', 'refactor']\n"
            "Instruction: 'What is the meaning of life?'\n"
            "Output: 'The meaning of life is subjective, but many say it is to find happiness and purpose.'\n"
            "Instruction: 'Can you help me?'\n"
            "Output: 'Of course! Please tell me what you need help with.'\n"
            "\n"
            "Output Format:\n"
            "- If the instruction is about code, output a valid Python list, e.g. ['doc', 'test', 'bug']. No explanations, markdown, or extra text.\n"
            "- If the instruction is a general question, output a string answer.\n"
            "- If you need clarification, output a string question for the user.\n"
        )
        prompt = f"User instruction: {instruction}\nOutput the list of agent types to run or answer the question."
        llm = ChatOpenAI(
            api_key=self.llm_proxy.api_key,
            model=getattr(self.args, 'llm', 'alchemyst-ai/alchemyst-c1'),
            base_url=self.llm_proxy.base_url,
            temperature=0.1,
            top_p=0.9,
            max_tokens=256,
        )
        result = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        import ast as _ast
        # Try to parse as a Python list, otherwise treat as a string answer
        content = result.content.strip()
        try:
            agent_list = _ast.literal_eval(content)
            if isinstance(agent_list, list):
                return agent_list
        except Exception:
            pass
        # If not a list, return the string answer
        return content

    def post(self, shared, prep_res, exec_res):
        # If exec_res is a string, treat it as a direct answer (general chat)
        if isinstance(exec_res, str):
            if not exec_res.strip():
                return "I'm sorry, I didn't understand that. Please rephrase your question or instruction."
            return exec_res

        # If exec_res is a list, validate agent types
        if isinstance(exec_res, list):
            valid_agents = {'doc', 'summary', 'type', 'migration', 'test', 'bug', 'refactor'}
            filtered = [a for a in exec_res if a in valid_agents]
            invalid = [a for a in exec_res if a not in valid_agents]
            response_lines = []

            if not filtered and invalid:
                # If all are invalid, treat as a chat response
                return " ".join(str(x) for x in exec_res)

            if invalid:
                response_lines.append(f"Warning: The following actions are not supported and will be ignored: {', '.join(invalid)}")

            file_path = getattr(self.args, 'file', None)
            if not file_path and any(a in valid_agents for a in filtered):
                response_lines.append("This action requires a file. Please provide one with --file or upload it.")
                return "\n".join(response_lines)

            # Run valid agent nodes
            results = {}
            for agent_type in filtered:
                import copy
                agent_args = copy.deepcopy(self.args)
                agent_args.agent = agent_type
                node = create_doc_agent_nodes(agent_args, self.llm_proxy)
                shared_local = {}
                try:
                    if hasattr(node, 'prep') and hasattr(node, 'exec') and hasattr(node, 'post'):
                        prep_res = node.prep(shared_local)
                        exec_res = node.exec(prep_res)
                        post_res = node.post(shared_local, prep_res, exec_res)
                        results[agent_type] = post_res
                        response_lines.append(f"Agent '{agent_type}' completed.")
                    else:
                        results[agent_type] = node.run(shared_local)
                        response_lines.append(f"Agent '{agent_type}' completed.")
                except Exception as e:
                    results[agent_type] = f"Error: {e}"
                    response_lines.append(f"Agent '{agent_type}' failed: {e}")

            if response_lines:
                return "\n".join(response_lines)
            else:
                return "All requested agent actions completed."

        # Fallback: unknown output
        return "I'm sorry, I didn't understand that. Please rephrase your question or instruction."

class UserApprovalNode(Node):
    def __init__(self, key_to_review, message="Please review the result below:", title="User Approval"):
        super().__init__()
        self.key_to_review = key_to_review
        self.message = message
        self.title = title

    def prep(self, shared):
        return shared.get(self.key_to_review, "")

    def exec(self, value):
        print(f"\n=== {self.title} ===\n")
        print(self.message)
        print(value)
        resp = input("Is this result good? (y/n): ").strip().lower()
        return resp

    def post(self, shared, prep_res, exec_res):
        if exec_res == "y":
            return "approved"
        else:
            return "refine"

def create_doc_agent_nodes(args, llm_proxy):
    agent_type = getattr(args, 'agent', 'doc')
    if agent_type == 'doc':
        return DocAgentNode(args, llm_proxy)
    elif agent_type == 'summary':
        return SummaryAgentNode(args, llm_proxy)
    elif agent_type == 'type':
        return TypeAnnotationAgentNode(args, llm_proxy)
    elif agent_type == 'migration':
        return MigrationAgentNode(args, llm_proxy)
    elif agent_type == 'test':
        return TestGenerationAgentNode(args, llm_proxy)
    elif agent_type == 'bug':
        return BugDetectionAgentNode(args, llm_proxy)
    elif agent_type == 'refactor':
        return RefactorCodeAgentNode(args, llm_proxy)
    elif agent_type == 'orchestrator':
        return OrchestratorAgentNode(args, llm_proxy)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")