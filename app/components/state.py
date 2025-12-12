# # app/components/state.py

# from typing import TypedDict, Optional, List
# from langchain_core.messages import BaseMessage


# class GraphState(TypedDict):
#     """
#     Shared state flowing through the LangGraph.

#     - messages: full conversation history (user + AI messages)
#     - task_route: which agent should handle the current turn
#     - task_payload: structured instructions from orchestrator to agent
#     - final_answer_ready: marker that we're done for this turn
#     """
#     messages: List[BaseMessage]
#     task_route: Optional[dict]
#     task_payload: Optional[dict]
#     final_answer_ready: bool



# app/components/state.py

from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage

class GraphState(TypedDict, total=False):
    """
    Global state that flows through the whole LangGraph.

    This acts as per-run "memory":
    anything you put here is visible to orchestrator, agents, tools, and finalizer.
    """

    # Conversation history (user + AI + tool messages)
    messages: List[BaseMessage]

    # ---- Orchestrator-related ----
    # Chosen route from orchestrator: "general", "math", "db", "medical", etc.
    task_route: Optional[str]

    # Free-form payload (from caller / session manager / orchestrator)
    # Example:
    # {
    #   "description": "Answer health questions for this customer",
    #   "customer": { "id": "CUST_001", "name": "Rahul" },
    #   "customer_id": "CUST_001",
    #   ...
    # }
    task_payload: Dict[str, Any]

    # ---- Persistent customer context for this run ----
    # Full customer JSON
    customer: Dict[str, Any]

    # Canonical ID used in DB/tools queries
    customer_id: str

    # ---- Control ----
    # Mark that final answer is ready
    final_answer_ready: bool
