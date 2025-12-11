# app/components/orchestrator.py

import json
from typing import List, cast

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
    - which agent to route to: 'general', 'math', or 'db'
    - what task description to give that agent
    """
    messages = cast(List[BaseMessage], state["messages"])
    last_msg_content = messages[-1].content if messages else ""
    
    system_prompt = (
        "You are the ORCHESTRATOR for a multi-agent system.\n"
        "You must choose EXACTLY ONE route for each user message:\n\n"
        "  - 'general' : For general conversation, explanations, or information "
        "that may use web search.\n"
        "  - 'math'    : For questions involving calculations, percentages, "
        "numeric reasoning, etc.\n"
        "  - 'db'      : For questions that explicitly mention a database, "
        "tables, rows, records, or reading from stored data.\n\n"
        "You NEVER answer the user directly. You only decide:\n"
        "  - which agent (route) should handle this turn\n"
        "  - a short task description for that agent\n\n"
        "Return ONLY JSON like:\n"
        "{\n"
        '  \"route\": \"general\" | \"math\" | \"db\",\n'
        '  \"task\": \"<short description of what the agent should do>\"\n'
        "}\n\n"
        "Rules:\n"
        "- If the user mentions 'database', 'table', 'orders', 'rows', etc. "
        "you MUST choose 'db'.\n"
        "- If the user clearly asks for calculations or numeric processing, "
        "you MUST choose 'math'.\n"
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

    new_state = state.copy()
    new_state["task_route"] = route
    new_state["task_payload"] = {"description": task}
    return new_state
