# app/components/graph_setup.py

from langgraph.graph import StateGraph, END

from .state import GraphState
from .orchestrator import orchestrator_node
from .agents import agent_a_node, agent_b_node, finalizer_node


builder = StateGraph(GraphState)

# Nodes
builder.add_node("orchestrator", orchestrator_node)
builder.add_node("agent_a", agent_a_node)
builder.add_node("agent_b", agent_b_node)
builder.add_node("finalizer", finalizer_node)

# Entry point
builder.set_entry_point("orchestrator")


def route_from_orchestrator(state: GraphState) -> str:
    """
    Decide which node to go to after orchestrator.
    """
    route = state.get("task_route") or "agent_a"
    if route == "agent_a":
        return "agent_a"
    elif route == "agent_b":
        return "agent_b"
    else:
        # Safety fallback
        return "agent_a"


# Conditional edges from orchestrator
builder.add_conditional_edges(
    "orchestrator",
    route_from_orchestrator,
    {
        "agent_a": "agent_a",
        "agent_b": "agent_b",
    },
)

# After any agent, go to finalizer
builder.add_edge("agent_a", "finalizer")
builder.add_edge("agent_b", "finalizer")

# Finalizer ends the graph
builder.add_edge("finalizer", END)

graph = builder.compile()
