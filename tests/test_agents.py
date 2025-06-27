import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import tempfile
import os
from theagent.nodes import DocAgentNode, SummaryAgentNode, TypeAnnotationAgentNode, MigrationAgentNode, TestGenerationAgentNode, BugDetectionAgentNode, RefactorCodeAgentNode

class DummyArgs:
    def __init__(self, file, output='console', llm='dummy', no_confirm=True, verbose=False, migration_target='Python 3'):
        self.file = file
        self.output = output
        self.llm = llm
        self.no_confirm = no_confirm
        self.verbose = verbose
        self.migration_target = migration_target

class DummyLLMProxy:
    def generate_docstring(self, function_code, model_name):
        return 'Dummy docstring.'
    def summarize_code(self, code, model_name):
        return 'Dummy summary.'
    def suggest_type_annotations(self, function_code, model_name):
        return 'def foo(x: int) -> int:'
    def migration_code(self, code, migration_target, model_name):
        return code.replace('print', 'print') + ' # migrated'
    def test_generation(self, function_code, model_name):
        return 'def test_foo(): assert foo(1) == 2'
    def bug_detection(self, code, model_name):
        return 'No bugs found.'
    def refactor_code(self, code, model_name):
        return code + ' # refactored'

def make_temp_pyfile(code):
    tf = tempfile.NamedTemporaryFile('w+', suffix='.py', delete=False)
    tf.write(code)
    tf.close()  # Ensure file is closed so it can be deleted on Windows
    return tf.name

def test_doc_agent_node_parses_and_inserts_docstring():
    code = 'def foo(x):\n    return x + 1\n'
    tf_name = make_temp_pyfile(code)
    args = DummyArgs(tf_name, output='new-file', no_confirm=True)
    node = DocAgentNode(args, DummyLLMProxy())
    shared = {}
    functions = node.prep(shared)
    docstrings = node.exec(functions)
    node.post(shared, functions, docstrings)
    new_file = tf_name.replace('.py', '_documented.py')
    assert os.path.exists(new_file)
    with open(new_file) as f:
        content = f.read()
        assert 'Dummy docstring.' in content
    os.remove(tf_name)
    os.remove(new_file)

def test_summary_agent_node():
    code = 'def foo(x):\n    return x + 1\n'
    tf_name = make_temp_pyfile(code)
    args = DummyArgs(tf_name)
    node = SummaryAgentNode(args, DummyLLMProxy())
    shared = {}
    source = node.prep(shared)
    summary = node.exec(source)
    assert summary == 'Dummy summary.'
    os.remove(tf_name)

def test_type_annotation_agent_node():
    code = 'def foo(x):\n    return x + 1\n'
    tf_name = make_temp_pyfile(code)
    args = DummyArgs(tf_name)
    node = TypeAnnotationAgentNode(args, DummyLLMProxy())
    shared = {}
    functions = node.prep(shared)
    suggestions = node.exec(functions)
    assert suggestions[0]['suggestion'] == 'def foo(x: int) -> int:'
    os.remove(tf_name)

def test_migration_agent_node():
    code = 'print("hello")\n'
    tf_name = make_temp_pyfile(code)
    args = DummyArgs(tf_name, output='new-file', migration_target='Python 3')
    node = MigrationAgentNode(args, DummyLLMProxy())
    with open(tf_name) as f:
        migrated = node.exec(f.read())
    node.write_output(migrated, 'migrated', 'Migrated Code')
    new_file = tf_name.replace('.py', '_migrated.py')
    assert os.path.exists(new_file)
    with open(new_file) as f:
        content = f.read()
        assert '# migrated' in content
    os.remove(tf_name)
    os.remove(new_file)

def test_test_generation_agent_node():
    code = 'def foo(x):\n    return x + 1\n'
    tf_name = make_temp_pyfile(code)
    args = DummyArgs(tf_name, output='new-file')
    node = TestGenerationAgentNode(args, DummyLLMProxy())
    shared = {}
    functions = node.prep(shared)
    tests = node.exec(functions)
    node.post(shared, functions, tests)
    test_file = tf_name.replace('.py', '_testgen.py')
    assert os.path.exists(test_file)
    with open(test_file) as f:
        content = f.read()
        assert 'def test_foo()' in content
    os.remove(tf_name)
    os.remove(test_file)

def test_bug_detection_agent_node():
    code = 'def foo(x):\n    return x + 1\n'
    tf_name = make_temp_pyfile(code)
    args = DummyArgs(tf_name)
    node = BugDetectionAgentNode(args, DummyLLMProxy())
    with open(tf_name) as f:
        bug_report = node.exec(f.read())
    assert bug_report == 'No bugs found.'
    os.remove(tf_name)

def test_refactor_code_agent_node():
    code = 'def foo(x):\n    return x + 1\n'
    tf_name = make_temp_pyfile(code)
    args = DummyArgs(tf_name, output='new-file')
    node = RefactorCodeAgentNode(args, DummyLLMProxy())
    with open(tf_name) as f:
        refactored = node.exec(f.read())
    node.write_output(refactored, 'refactored', 'Refactored Code')
    new_file = tf_name.replace('.py', '_refactored.py')
    assert os.path.exists(new_file)
    with open(new_file) as f:
        content = f.read()
        assert '# refactored' in content
    os.remove(tf_name)
    os.remove(new_file) 