# app/components/orchestrator.py

import json
from typing import cast

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from components.state import GraphState


# Orchestrator model (routing only)
orchestrator_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    model_kwargs={
        "response_format": {"type": "json_object"}
    }
)


def orchestrator_node(state: GraphState) -> GraphState:
    """
    Orchestrator:
    - Looks at the last user message (with context available in state["messages"]).
    - Decides route: 'agent_a', 'agent_b', or 'none'.
    - Builds a task description for the chosen agent.
    - DOES NOT answer the user or call tools.
    """
    messages = cast(list[BaseMessage], state["messages"])
    last_msg = messages[-1].content if messages else ""

    system_prompt = (
        "You are the orchestrator for a multi-agent chatbot.\n"
        "Your ONLY job is to:\n"
        "1. Understand the user's latest request, using the message content.\n"
        "2. Decide which agent should handle it:\n"
        "   - 'agent_a' for general chat / web info / search tasks.\n"
        "   - 'agent_b' for math, numeric reasoning, or database-related tasks.\n"
        "   - 'none' if no agent needs to be called (very rare).\n"
        "3. Create a short task description that the chosen agent must follow.\n\n"
        "STRICT RULES:\n"
        "- Do NOT solve the task yourself.\n"
        "- Do NOT call tools.\n"
        "- Do NOT provide a final user answer.\n"
        "- Respond ONLY in valid JSON with keys: 'route' and 'task'.\n"
        "Example:\n"
        "{\n"
        '  \"route\": \"agent_a\",\n'
        '  \"task\": \"Use web search to explain what Kyoto is famous for in autumn.\"\n'
        "}\n"
    )

    user_prompt = (
        "Here is the latest user message:\n"
        f"{last_msg}\n\n"
        "Decide routing and construct the task JSON now."
    )

    resp = orchestrator_llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    print(f"\n\nresp:\n{resp}\n\n")

    try:
        parsed = json.loads(resp.content)
    except json.JSONDecodeError:
        parsed = {"route": "none", "task": "Could not parse task."}

    route = parsed.get("route", "none")
    task = parsed.get("task", "")

    new_state = state.copy()
    new_state["task_route"] = route
    new_state["task_payload"] = {"description": task}
    # Orchestrator does NOT add messages to history
    print(f"\n\nnew_state:\n{new_state}\n\n")
    return new_state
