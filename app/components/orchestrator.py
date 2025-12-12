# app/components/orchestrator.py

import json
from typing import List, cast, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from components.state import GraphState


orchestrator_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.0,
    # JSON mode: safer parsing
    model_kwargs={"response_format": {"type": "json_object"}},
)


def orchestrator_node(state: GraphState) -> GraphState:
    """
    Look at the latest user message and decide:
    - which agent to route to: 'general', 'math', 'db', or 'medical'
    - what task description to give that agent
    Also:
    - normalize and persist customer + customer_id in the state so all
      agents/tools can use them consistently.
    """
    messages = cast(List[BaseMessage], state["messages"])
    last_msg_content = messages[-1].content if messages else ""

    # ---- Normalize customer context into state (persistent per run) ----
    # Start from any existing payload
    existing_payload: Dict[str, Any] = dict(state.get("task_payload") or {})

    customer = (
        existing_payload.get("customer")
        or state.get("customer")
        or {}
    )

    customer_id = (
        existing_payload.get("customer_id")
        or customer.get("id")
        or customer.get("customer_id")
        or customer.get("customerId")
        or state.get("customer_id")
    )

    # ---- Build routing prompt ----
    system_prompt = (
        "You are the ORCHESTRATOR for a multi-agent system.\n"
        "You must choose EXACTLY ONE route for each user message:\n\n"
        "  - 'general' : For general conversation, explanations, or information "
        "that may use web search.\n"
        "  - 'math'    : For questions involving calculations, percentages, "
        "numeric reasoning, etc.\n"
        "  - 'db'      : For questions that explicitly mention a database, "
        "tables, rows, records, or reading from stored data (non-medical).\n"
        "  - 'medical' : For questions about health, symptoms, diagnoses, "
        "medications, clinical history, lab results, or doctor's advice "
        "for the customer.\n\n"
        "You NEVER answer the user directly. You only decide:\n"
        "  - which agent (route) should handle this turn\n"
        "  - a short task description for that agent\n\n"
        "Return ONLY JSON like:\n"
        "{\n"
        '  \"route\": \"general\" | \"math\" | \"db\" | \"medical\",\n'
        '  \"task\": \"<short description of what the agent should do>\"\n'
        "}\n\n"
        "Routing rules:\n"
        "- If the user explicitly talks about a DATABASE, TABLES, ROWS, or generic\n"
        "  stored data (not health-specific), choose 'db'.\n"
        "- If the user clearly asks for calculations or numeric processing, choose 'math'.\n"
        "- If the user asks about health, symptoms, conditions, diagnoses, medications,\n"
        "  clinical history, doctor's advice, or \"my health\" for the customer, choose 'medical'.\n"
        "- Otherwise, choose 'general'.\n"
    )

    user_prompt = (
        "User message:\n"
        f"{last_msg_content}\n\n"
        "Decide the route and a short task description. Return ONLY the JSON."
    )

    resp = orchestrator_llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    try:
        parsed = json.loads(resp.content)
    except json.JSONDecodeError:
        # Fallback
        parsed = {
            "route": "general",
            "task": "Provide a helpful general answer to the user's question.",
        }

    route = parsed.get("route", "general")
    task = parsed.get("task", "")

    # ---- Build new state ----
    new_state = state.copy()

    # Persist normalized customer context for the whole run
    new_state["customer"] = customer
    if customer_id:
        new_state["customer_id"] = customer_id

    new_state["task_route"] = route

    # Merge description into existing payload instead of overwriting everything
    existing_payload["description"] = task
    new_state["task_payload"] = existing_payload

    return new_state
