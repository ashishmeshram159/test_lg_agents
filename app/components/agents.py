# # app/components/agents.py

# from typing import List, cast, Optional

# from langchain_openai import ChatOpenAI
# from langchain_core.messages import (
#     HumanMessage,
#     BaseMessage,
#     SystemMessage,
#     AIMessage,
#     ToolMessage,
# )
# from langchain_core.tools import Tool

# from components.state import GraphState
# from components.tools import tavily_custom_search, math_tool, sqlite_select_tool


# # Shared LLM for all agents
# agent_llm = ChatOpenAI(
#     model="gpt-4o",
#     temperature=0.2,
# )

# # Tools per agent
# general_tools: List[Tool] = [tavily_custom_search]
# math_tools: List[Tool] = [math_tool]
# db_tools: List[Tool] = [sqlite_select_tool]


# # ---------- Helper: get last human & last tool message ---------- #

# def _get_last_human(messages: List[BaseMessage]) -> Optional[HumanMessage]:
#     for m in reversed(messages):
#         if isinstance(m, HumanMessage):
#             return m
#     return None


# def _get_last_tool(messages: List[BaseMessage]) -> Optional[ToolMessage]:
#     for m in reversed(messages):
#         if isinstance(m, ToolMessage):
#             return m
#     return None


# # ============================================================
# # GENERAL AGENT
# # ============================================================

# def agent_general_node(state: GraphState) -> GraphState:
#     """
#     GENERAL agent:
#     - First pass: can request Tavily via tool_calls.
#     - Second pass (after tools): uses tool results as plain text, no tools.
#     """
#     messages = cast(List[BaseMessage], state["messages"])
#     payload = state.get("task_payload") or {}
#     task_desc = payload.get("description", "")

#     system_msg = SystemMessage(
#         content=(
#             "You are the GENERAL agent.\n"
#             "You handle general questions and web-based information.\n"
#             "You have access to a web search tool to retrieve factual or current info.\n"
#             "When tool results are provided to you as text, use them to answer clearly.\n"
#         )
#     )

#     last_msg = messages[-1]

#     # SECOND PASS: last message is a ToolMessage -> use plain LLM, no tools
#     if isinstance(last_msg, ToolMessage):
#         tool_output = last_msg.content
#         user_msg = _get_last_human(messages)
#         user_text = user_msg.content if user_msg else ""

#         final_response = agent_llm.invoke(
#             [
#                 system_msg,
#                 HumanMessage(
#                     content=(
#                         f"User question:\n{user_text}\n\n"
#                         f"Tool result:\n{tool_output}\n\n"
#                         f"Task from orchestrator: {task_desc}\n\n"
#                         "Using the tool result, give a clear, concise answer to the user."
#                     )
#                 ),
#             ]
#         )

#         new_state = state.copy()
#         new_state["messages"] = messages + [final_response]
#         return new_state

#     # FIRST PASS: no tool output yet -> allow tool calls
#     model_with_tools = agent_llm.bind_tools(general_tools)

#     first_response = model_with_tools.invoke(
#         [system_msg] + messages + [HumanMessage(content=f"Task: {task_desc}")]
#     )

#     new_state = state.copy()
#     new_state["messages"] = messages + [first_response]
#     return new_state


# # ============================================================
# # MATH AGENT
# # ============================================================

# def agent_math_node(state: GraphState) -> GraphState:
#     """
#     MATH agent:
#     - First pass: can request math_tool via tool_calls.
#     - Second pass: uses tool results as plain text, no tools.
#     """
#     messages = cast(List[BaseMessage], state["messages"])
#     payload = state.get("task_payload") or {}
#     task_desc = payload.get("description", "")

#     system_msg = SystemMessage(
#         content=(
#             "You are the MATH agent.\n"
#             "You handle calculations and numeric reasoning.\n"
#             "When tool results are provided as text, use them to explain the answer simply.\n"
#         )
#     )

#     last_msg = messages[-1]

#     # SECOND PASS: after math_tool has been called
#     if isinstance(last_msg, ToolMessage):
#         tool_output = last_msg.content
#         user_msg = _get_last_human(messages)
#         user_text = user_msg.content if user_msg else ""

#         final_response = agent_llm.invoke(
#             [
#                 system_msg,
#                 HumanMessage(
#                     content=(
#                         f"User question:\n{user_text}\n\n"
#                         f"Tool result:\n{tool_output}\n\n"
#                         f"Task from orchestrator: {task_desc}\n\n"
#                         "Using the tool result, clearly explain the calculation and final answer."
#                     )
#                 ),
#             ]
#         )

#         new_state = state.copy()
#         new_state["messages"] = messages + [final_response]
#         return new_state

#     # FIRST PASS: let LLM decide math_tool call
#     model_with_tools = agent_llm.bind_tools(math_tools)

#     first_response = model_with_tools.invoke(
#         [system_msg] + messages + [HumanMessage(content=f"Task: {task_desc}")]
#     )

#     new_state = state.copy()
#     new_state["messages"] = messages + [first_response]
#     return new_state


# # ============================================================
# # DB AGENT
# # ============================================================

# def agent_db_node(state: GraphState) -> GraphState:
#     """
#     DB agent:
#     - First pass: must call sqlite_select_tool via tool_calls.
#     - Second pass: uses tool results as plain text, no tools.
#     """
#     messages = cast(List[BaseMessage], state["messages"])
#     payload = state.get("task_payload") or {}
#     task_desc = payload.get("description", "")

#     system_msg = SystemMessage(
#         content=(
#             "You are the DB agent.\n"
#             "You answer questions by querying a SQLite database.\n"
#             "You have a tool called 'sqlite_select_tool' which executes SELECT queries.\n"
#             "First, you use the tool (via the system) to retrieve rows.\n"
#             "Then, when tool results are provided to you as text, you summarize them clearly.\n"
#         )
#     )

#     last_msg = messages[-1]

#     # SECOND PASS: last message is a ToolMessage (DB result)
#     if isinstance(last_msg, ToolMessage):
#         tool_output = last_msg.content
#         user_msg = _get_last_human(messages)
#         user_text = user_msg.content if user_msg else ""

#         final_response = agent_llm.invoke(
#             [
#                 system_msg,
#                 HumanMessage(
#                     content=(
#                         f"User question:\n{user_text}\n\n"
#                         f"Tool (database) result:\n{tool_output}\n\n"
#                         f"Task from orchestrator: {task_desc}\n\n"
#                         "Using the database result, explain clearly to the user what the last 5 orders are."
#                     )
#                 ),
#             ]
#         )

#         new_state = state.copy()
#         new_state["messages"] = messages + [final_response]
#         return new_state

#     # FIRST PASS: no tool result yet -> call sqlite_select_tool via tool_calls
#     model_with_tools = agent_llm.bind_tools(db_tools)

#     first_response = model_with_tools.invoke(
#         [system_msg] + messages + [HumanMessage(content=f"Task: {task_desc}")]
#     )

#     new_state = state.copy()
#     new_state["messages"] = messages + [first_response]
#     return new_state


# # ============================================================
# # FINALIZER
# # ============================================================

# def finalizer_node(state: GraphState) -> GraphState:
#     """
#     Finalizer: mark answer as ready.
#     """
#     new_state = state.copy()
#     new_state["final_answer_ready"] = True
#     return new_state


# app/components/agents.py

from typing import List, Optional, cast

from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    BaseMessage,
    SystemMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.tools import Tool

from components.state import GraphState
from components.tools import tavily_custom_search, math_tool, sqlite_select_tool


# ============================================================
# SHARED LLM + TOOLS
# ============================================================

agent_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
)

general_tools: List[Tool] = [tavily_custom_search]
math_tools: List[Tool] = [math_tool]
db_tools: List[Tool] = [sqlite_select_tool]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _get_last_human(messages: List[BaseMessage]) -> Optional[HumanMessage]:
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            return m
    return None


# ============================================================
# GENERAL AGENT
# ============================================================

def agent_general_node(state: GraphState) -> GraphState:
    """
    GENERAL agent:
    - First pass: uses Tavily via tool_calls.
    - Second pass: consumes tool result as plain text and explains with LLM.
    """
    messages = cast(List[BaseMessage], state["messages"])
    payload = state.get("task_payload") or {}
    task_desc = payload.get("description", "")

    system_msg = SystemMessage(
        content=(
            "You are the GENERAL agent.\n"
            "You handle general questions and web-based information.\n"
            "You have access to a web search tool to retrieve factual or current info.\n"
            "When tool results are provided to you as text, use them to answer clearly.\n"
        )
    )

    last_msg = messages[-1]

    # SECOND PASS: last message is a ToolMessage -> use plain LLM (no tools)
    if isinstance(last_msg, ToolMessage):
        tool_output = last_msg.content
        user_msg = _get_last_human(messages)
        user_text = user_msg.content if user_msg else ""

        final_response = agent_llm.invoke(
            [
                system_msg,
                HumanMessage(
                    content=(
                        f"User question:\n{user_text}\n\n"
                        f"Tool result:\n{tool_output}\n\n"
                        f"Task from orchestrator: {task_desc}\n\n"
                        "Using the tool result, give a clear, concise answer to the user."
                    )
                ),
            ]
        )

        new_state = state.copy()
        new_state["messages"] = messages + [final_response]
        return new_state

    # FIRST PASS: no tool output yet -> allow Tavily tool_calls
    model_with_tools = agent_llm.bind_tools(general_tools)

    first_response = model_with_tools.invoke(
        [system_msg] + messages + [HumanMessage(content=f"Task: {task_desc}")]
    )

    new_state = state.copy()
    new_state["messages"] = messages + [first_response]
    return new_state


# ============================================================
# MATH AGENT (TOOL RESULT IS GROUND TRUTH)
# ============================================================

def agent_math_node(state: GraphState) -> GraphState:
    """
    MATH agent:
    - First pass: uses math_tool via tool_calls.
    - Second pass: returns the tool's numeric result directly
      (no extra LLM math to avoid hallucinations).
    """
    messages = cast(List[BaseMessage], state["messages"])
    payload = state.get("task_payload") or {}
    task_desc = payload.get("description", "")

    system_msg = SystemMessage(
        content=(
            "You are the MATH agent.\n"
            "You handle calculations and numeric reasoning.\n"
            "You MUST trust the external calculator tool's numeric result for the final answer.\n"
            "Do NOT recompute or change the numeric result on your own.\n"
        )
    )

    last_msg = messages[-1]

    # SECOND PASS: we already have a ToolMessage from math_tool
    if isinstance(last_msg, ToolMessage):
        tool_output = last_msg.content  # e.g. "Result: 8048.0"

        # Try to extract the number from "Result: 8048.0"
        value_str = tool_output
        if isinstance(tool_output, str) and "Result" in tool_output:
            try:
                value_str = tool_output.split(":", 1)[1].strip()
            except Exception:
                value_str = tool_output

        # Build final AIMessage WITHOUT calling LLM again
        final_text = f"The result of the calculation is {value_str}."
        final_response = AIMessage(content=final_text)

        new_state = state.copy()
        new_state["messages"] = messages + [final_response]
        return new_state

    # FIRST PASS: no tool result yet -> allow math_tool calls
    model_with_tools = agent_llm.bind_tools(math_tools)

    first_response = model_with_tools.invoke(
        [system_msg] + messages + [HumanMessage(content=f"Task: {task_desc}")]
    )

    new_state = state.copy()
    new_state["messages"] = messages + [first_response]
    return new_state


# ============================================================
# DB AGENT
# ============================================================

def agent_db_node(state: GraphState) -> GraphState:
    """
    DB agent:
    - First pass: uses sqlite_select_tool via tool_calls.
    - Second pass: consumes tool result as text and summarizes with LLM.
    """
    messages = cast(List[BaseMessage], state["messages"])
    payload = state.get("task_payload") or {}
    task_desc = payload.get("description", "")

    system_msg = SystemMessage(
        content=(
            "You are the DB agent.\n"
            "You answer questions by querying a SQLite database.\n"
            "You use the 'sqlite_select_tool' tool to fetch data (SELECT queries only).\n"
            "After the tool result is provided as text, you summarize it clearly for the user.\n"
        )
    )

    last_msg = messages[-1]

    # SECOND PASS: last message is a ToolMessage (DB query result)
    if isinstance(last_msg, ToolMessage):
        tool_output = last_msg.content
        user_msg = _get_last_human(messages)
        user_text = user_msg.content if user_msg else ""

        final_response = agent_llm.invoke(
            [
                system_msg,
                HumanMessage(
                    content=(
                        f"User question:\n{user_text}\n\n"
                        f"Database (tool) result:\n{tool_output}\n\n"
                        f"Task from orchestrator: {task_desc}\n\n"
                        "Using the database result, summarize the answer clearly for the user."
                    )
                ),
            ]
        )

        new_state = state.copy()
        new_state["messages"] = messages + [final_response]
        return new_state

    # FIRST PASS: no tool result yet -> allow sqlite_select_tool calls
    model_with_tools = agent_llm.bind_tools(db_tools)

    first_response = model_with_tools.invoke(
        [system_msg] + messages + [HumanMessage(content=f"Task: {task_desc}")]
    )

    new_state = state.copy()
    new_state["messages"] = messages + [first_response]
    return new_state


# ============================================================
# FINALIZER
# ============================================================

def finalizer_node(state: GraphState) -> GraphState:
    """
    Finalizer: mark answer as ready.
    """
    new_state = state.copy()
    new_state["final_answer_ready"] = True
    return new_state
