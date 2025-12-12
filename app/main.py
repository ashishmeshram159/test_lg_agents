# # app/main.py

# from typing import List, cast, Optional
# import os
# from fastapi import FastAPI
# from pydantic import BaseModel
# from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
# import uvicorn

# # Loading env vars:
# from dotenv import load_dotenv
# load_dotenv()

# # env_keys = [ "OPENAI_API_KEY", "TAVILY_API_KEY", "SQLITE_DB_PATH" ]
# # for key_val in env_keys:    
# #     print(f"\n\nThe env_val for {key_val} is:\n{os.getenv(key_val)}\n\n") 

# from components.graph_setup import graph
# from components.state import GraphState
# from components.session_manager import SessionManager



# class CustomerInfo(BaseModel):
#     id: str
#     name: Optional[str] = None
#     dob: Optional[str] = None
#     email: Optional[str] = None


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str
#     customer: Optional[CustomerInfo] = None
#     customer_id: Optional[str] = None


# class ChatResponse(BaseModel):
#     reply: str


# app = FastAPI(
#     title="Multi-Agent Chatbot (LangGraph + FastAPI)",
#     version="1.0.0",
# )

# session_manager = SessionManager()




# def run_graph_for_chat(session_id: str, user_message: str) -> str:
#     """
#     Pipeline:
#     1. Load history for this session_id
#     2. Append new user message
#     3. Build GraphState
#     4. Run LangGraph
#     5. Save updated history
#     6. Return last AI message
#     """
#     # 1. Load existing history
#     history: List[BaseMessage] = session_manager.get_history(session_id)

#     # 2. Add new user message
#     history = history + [HumanMessage(content=user_message)]

#     # 3. Prepare state
#     initial_state: GraphState = {
#         "messages": history,
#         "task_route": None,
#         "task_payload": None,
#         "final_answer_ready": False,
#     }

#     print(f"\n\ninitial_state:\n{initial_state}\n\n")
    
#     # 4. Run graph
#     result_state = graph.invoke(initial_state)

#     # 5. Save updated history
#     messages = cast(List[BaseMessage], result_state["messages"])
    

#     print("=== DEBUG MESSAGES AFTER GRAPH ===")
#     for m in messages:
#         print(type(m), "=>", getattr(m, "content", None))
#     print("==================================")

#     session_manager.set_history(session_id, messages)

#     # 6. Return last AI message
#     ai_messages = [m for m in messages if isinstance(m, AIMessage)]
#     if not ai_messages:
#         return "Sorry, I couldn't generate a response."

#     return ai_messages[-1].content


# @app.post("/chat", response_model=ChatResponse)
# async def chat_endpoint(body: ChatRequest) -> ChatResponse:
#     """
#     POST /chat
#     {
#       "session_id": "uuid-or-any-id",
#       "message": "Hello"
#     }
#     """
#     reply = run_graph_for_chat(body.session_id, body.message)
#     return ChatResponse(reply=reply)


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True
#     )

# app/main.py

from typing import List, cast, Optional, Dict, Any  # 👈 added Dict, Any
import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import uvicorn

# Loading env vars:
from dotenv import load_dotenv
load_dotenv()

from components.graph_setup import graph
from components.state import GraphState
from components.session_manager import SessionManager


class CustomerInfo(BaseModel):
    id: str
    name: Optional[str] = None
    dob: Optional[str] = None
    email: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    # 👇 NEW: optional payload pieces
    customer: Optional[CustomerInfo] = None
    customer_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


app = FastAPI(
    title="Multi-Agent Chatbot (LangGraph + FastAPI)",
    version="1.0.0",
)

session_manager = SessionManager()


def run_graph_for_chat(
    session_id: str,
    user_message: str,
    extra_payload: Optional[Dict[str, Any]] = None,  # 👈 NEW
) -> str:
    """
    Pipeline:
    1. Load history for this session_id
    2. Append new user message
    3. Build GraphState (including task_payload)
    4. Run LangGraph
    5. Save updated history
    6. Return last AI message
    """
    # 1. Load existing history
    history: List[BaseMessage] = session_manager.get_history(session_id)

    # 2. Add new user message
    history = history + [HumanMessage(content=user_message)]

    # 3. Prepare state
    task_payload: Dict[str, Any] = {}
    if extra_payload:
        task_payload.update(extra_payload)

    initial_state: GraphState = {
        "messages": history,
        "task_route": None,
        "task_payload": task_payload,      # 👈 pass payload into orchestrator
        "final_answer_ready": False,
    }

    print(f"\n\ninitial_state:\n{initial_state}\n\n")

    # 4. Run graph
    result_state = graph.invoke(initial_state)

    # 5. Save updated history
    messages = cast(List[BaseMessage], result_state["messages"])

    print("=== DEBUG MESSAGES AFTER GRAPH ===")
    for m in messages:
        print(type(m), "=>", getattr(m, "content", None))
    print("==================================")

    session_manager.set_history(session_id, messages)

    # 6. Return last AI message
    ai_messages = [m for m in messages if isinstance(m, AIMessage)]
    if not ai_messages:
        return "Sorry, I couldn't generate a response."

    return ai_messages[-1].content


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest) -> ChatResponse:
    """
    POST /chat
    {
      "session_id": "uuid-or-any-id",
      "message": "Hello",
      "customer": { ... },      # optional
      "customer_id": "CUST_001" # optional
    }
    """
    # 👇 Build extra payload for orchestrator/agents
    extra_payload: Dict[str, Any] = {}

    if body.customer is not None:
        extra_payload["customer"] = body.customer.model_dump()

    if body.customer_id is not None:
        extra_payload["customer_id"] = body.customer_id

    reply = run_graph_for_chat(body.session_id, body.message, extra_payload)
    return ChatResponse(reply=reply)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
