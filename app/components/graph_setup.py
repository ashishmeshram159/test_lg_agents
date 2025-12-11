# app/components/graph_setup.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage

from components.state import GraphState
from components.orchestrator import orchestrator_node
from components.agents import (
    agent_general_node,
    agent_math_node,
    agent_db_node,
    finalizer_node,
)
from .tools import tavily_custom_search, math_tool, sqlite_select_tool


builder = StateGraph(GraphState)

# ---- Nodes ---- #
builder.add_node("orchestrator", orchestrator_node)

builder.add_node("agent_general", agent_general_node)
builder.add_node("agent_math", agent_math_node)
builder.add_node("agent_db", agent_db_node)

builder.add_node("finalizer", finalizer_node)

# Tool nodes (execute actual tools)
tools_general_node = ToolNode([tavily_custom_search])
tools_math_node = ToolNode([math_tool])
tools_db_node = ToolNode([sqlite_select_tool])

builder.add_node("tools_general", tools_general_node)
builder.add_node("tools_math", tools_math_node)
builder.add_node("tools_db", tools_db_node)

# Entry point
builder.set_entry_point("orchestrator")


# ---- Orchestrator routing -> agents ---- #

def route_from_orchestrator(state: GraphState) -> str:
    route = (state.get("task_route") or "general").lower()

    if route == "general":
        return "agent_general"
    elif route == "math":
        return "agent_math"
    elif route == "db":
        return "agent_db"
    else:
        return "agent_general"


builder.add_conditional_edges(
    "orchestrator",
    route_from_orchestrator,
    {
        "agent_general": "agent_general",
        "agent_math": "agent_math",
        "agent_db": "agent_db",
    },
)


# ---- After each agent, decide: go to tools or finalize ---- #

def _last_ai_has_tool_calls(state: GraphState) -> bool:
    messages = state["messages"]
    if not messages:
        return False
    last = messages[-1]
    return isinstance(last, AIMessage) and bool(getattr(last, "tool_calls", None))


def route_after_general(state: GraphState) -> str:
    if _last_ai_has_tool_calls(state):
        return "tools_general"
    return "finalizer"


builder.add_conditional_edges(
    "agent_general",
    route_after_general,
    {
        "tools_general": "tools_general",
        "finalizer": "finalizer",
    },
)


def route_after_math(state: GraphState) -> str:
    if _last_ai_has_tool_calls(state):
        return "tools_math"
    return "finalizer"


builder.add_conditional_edges(
    "agent_math",
    route_after_math,
    {
        "tools_math": "tools_math",
        "finalizer": "finalizer",
    },
)


def route_after_db(state: GraphState) -> str:
    if _last_ai_has_tool_calls(state):
        return "tools_db"
    return "finalizer"


builder.add_conditional_edges(
    "agent_db",
    route_after_db,
    {
        "tools_db": "tools_db",
        "finalizer": "finalizer",
    },
)

# After tools, go back to same agent to interpret results
builder.add_edge("tools_general", "agent_general")
builder.add_edge("tools_math", "agent_math")
builder.add_edge("tools_db", "agent_db")

# Final node
builder.add_edge("finalizer", END)

graph = builder.compile()
