# app/components/agents.py

from typing import List, cast

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage

from .state import GraphState


# One shared LLM for both agents (you can split later if needed)
agent_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
)


def agent_a_node(state: GraphState) -> GraphState:
    """
    Agent A:
    - Handles general chat / web info style tasks.
    - For now: plain LLM, no tools.
    """
    messages = cast(List[BaseMessage], state["messages"])
    payload = state.get("task_payload") or {}
    task_desc = payload.get("description", "")

    system_msg = (
        "You are Agent A.\n"
        "You handle general knowledge, explanations, and helpful responses.\n"
        "Follow the orchestrator's task description exactly.\n"
        "Give a clear, concise answer to the user."
    )

    result = agent_llm.invoke(
        [
            SystemMessage(content=system_msg),
            HumanMessage(content=f"Task from orchestrator: {task_desc}"),
        ]
    )

    new_state = state.copy()
    new_state["messages"] = messages + [result]
    return new_state


def agent_b_node(state: GraphState) -> GraphState:
    """
    Agent B:
    - Handles math / numeric / structured analytical tasks.
    - For now: plain LLM, no tools.
    """
    messages = cast(List[BaseMessage], state["messages"])
    payload = state.get("task_payload") or {}
    task_desc = payload.get("description", "")

    system_msg = (
        "You are Agent B.\n"
        "You handle math, numeric reasoning, and analytical answers.\n"
        "Follow the orchestrator's task description strictly.\n"
        "Explain your reasoning simply when useful, but keep the answer focused."
    )

    result = agent_llm.invoke(
        [
            SystemMessage(content=system_msg),
            HumanMessage(content=f"Task from orchestrator: {task_desc}"),
        ]
    )

    new_state = state.copy()
    new_state["messages"] = messages + [result]
    return new_state


def finalizer_node(state: GraphState) -> GraphState:
    """
    Finalizer: mark the answer as ready.
    """
    new_state = state.copy()
    new_state["final_answer_ready"] = True
    return new_state
