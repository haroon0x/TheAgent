from pocketflow import Flow
from nodes import create_doc_agent_nodes

def create_doc_agent_flow(args, llm_proxy):
    """Create and return the documentation agent flow."""
    start_node = create_doc_agent_nodes(args, llm_proxy)
    return Flow(start=start_node)