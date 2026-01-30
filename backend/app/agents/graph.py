from langgraph.graph import StateGraph, END
from .state import EireGateState
from .nodes import extract_node, tailor_node, visa_gap_node
from .checkpointers import checkpointer

workflow = StateGraph(EireGateState)

workflow.add_node("extract", extract_node)
workflow.add_node("tailor", tailor_node)
# workflow.add_node("visa_gap", visa_gap_node)

workflow.set_entry_point("extract")
workflow.add_edge("extract", "tailor")
workflow.add_edge("tailor", END)
# workflow.add_edge("tailor", "visa_gap")
# workflow.add_edge("visa_gap", END)

graph = workflow.compile(checkpointer=checkpointer)
