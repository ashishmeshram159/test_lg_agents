# app/components/state.py

from typing import TypedDict, Optional, Literal, List
from langchain_core.messages import BaseMessage


class GraphState(TypedDict):
    """
    Shared state flowing through the LangGraph.

    - messages: full conversation history (user + AI messages)
    - task_route: which agent should handle the current turn
    - task_payload: structured instructions from orchestrator to agent
    - final_answer_ready: marker that we're done for this turn
    """
    messages: List[BaseMessage]
    task_route: Optional[dict]
    task_payload: Optional[dict]
    final_answer_ready: bool
