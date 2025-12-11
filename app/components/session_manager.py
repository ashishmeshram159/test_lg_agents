# app/components/session_manager.py

from typing import Dict, List
from threading import Lock
from langchain_core.messages import BaseMessage


class SessionManager:
    """
    Simple in-memory session manager (singleton).

    Maps:
        session_id -> List[BaseMessage]
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SessionManager, cls).__new__(cls)
                    cls._instance._sessions = {}
        return cls._instance

    def get_history(self, session_id: str) -> List[BaseMessage]:
        """Return a copy of the stored history for this session."""
        return list(self._sessions.get(session_id, []))

    def set_history(self, session_id: str, history: List[BaseMessage]) -> None:
        """Overwrite the session history completely."""
        self._sessions[session_id] = list(history)

    def append_message(self, session_id: str, message: BaseMessage) -> None:
        """Append a single message to the session history."""
        history = self._sessions.get(session_id, [])
        history = history + [message]
        self._sessions[session_id] = history

    def clear_session(self, session_id: str) -> None:
        """Clear history for a specific session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def clear_all(self) -> None:
        """Wipe all sessions (useful in tests)."""
        self._sessions.clear()
