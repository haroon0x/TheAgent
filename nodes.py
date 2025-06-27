from pocketflow import Node
from utils.call_llm import AlchemistAIProxy
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

    def post(self, shared, prep_res, exec_res):
        output_mode = getattr(self.args, 'output', 'console')
        file_path = self.args.file
        verbose = getattr(self.args, 'verbose', False)
        if output_mode == 'console':
            print("\n=== Generated Unit Tests ===\n")
            for item in exec_res:
                print(f"Function: {item['name']}")
                print(item['test_code'])
                print("-"*40)
        else:
            test_file = file_path.replace('.py', '_testgen.py')
            with open(test_file, 'w', encoding='utf-8') as f:
                for item in exec_res:
                    f.write(f"# Tests for {item['name']}\n{item['test_code']}\n\n")
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
        if not instruction:
            raise ValueError("No instruction provided for orchestrator agent.")
        shared['instruction'] = instruction
        return instruction

    def exec(self, instruction):
        # Use the LLM to map the instruction to a list of agent types
        # For simplicity, we use a strong prompt and expect a YAML or JSON list of agent types
        from langchain_openai import ChatOpenAI
        system_prompt = (
            "You are an expert agent orchestrator for a code analysis system. "
            "Given a user instruction, output a Python list of agent types (from: 'doc', 'summary', 'type', 'migration', 'test', 'bug', 'refactor') "
            "that should be run, in order, to fulfill the instruction. "
            "Only output the list, nothing else."
        )
        prompt = f"User instruction: {instruction}\nOutput the list of agent types to run."
        llm = ChatOpenAI(
            api_key=self.llm_proxy.api_key,
            model=getattr(self.args, 'llm', 'alchemyst-ai/alchemyst-c1'),
            base_url=self.llm_proxy.base_url,
            temperature=0.1,
            top_p=0.9,
            max_tokens=128,
        )
        result = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        # Try to parse the output as a Python list
        import ast as _ast
        try:
            agent_list = _ast.literal_eval(result.content.strip())
            if not isinstance(agent_list, list):
                raise ValueError
        except Exception:
            raise ValueError(f"Could not parse agent list from LLM output: {result.content}")
        return agent_list

    def post(self, shared, prep_res, exec_res):
        # exec_res is the list of agent types to run
        agent_types = exec_res
        file_path = self.args.file
        results = {}
        for agent_type in agent_types:
            # Create a new args object for each agent
            import copy
            agent_args = copy.deepcopy(self.args)
            agent_args.agent = agent_type
            # For migration, pass migration_target
            node = create_doc_agent_nodes(agent_args, self.llm_proxy)
            shared_local = {}
            # For doc, type, test, run the full flow; for summary, bug, refactor, just print/return
            try:
                if hasattr(node, 'prep') and hasattr(node, 'exec') and hasattr(node, 'post'):
                    prep_res = node.prep(shared_local)
                    exec_res = node.exec(prep_res)
                    post_res = node.post(shared_local, prep_res, exec_res)
                    results[agent_type] = post_res
                else:
                    results[agent_type] = node.run(shared_local)
            except Exception as e:
                results[agent_type] = f"Error: {e}"
        print("\n=== Orchestrator Summary ===\n")
        for agent_type in agent_types:
            print(f"Agent '{agent_type}' completed. Result: {results[agent_type]}")
        return 'done'

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