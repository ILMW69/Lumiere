
from typing import Dict, List, TypedDict
import threading


class MemoryItem(TypedDict):
    type: str        # e.g. "fact", "preference", "goal"
    content: str     # the remembered information
    turn: int        # conversation turn index


# In-memory store: session_id -> list of MemoryItem
_SESSION_MEMORY: Dict[str, List[MemoryItem]] = {}

# Simple lock to make writes thread-safe
_LOCK = threading.Lock()


def get_session_memory(session_id: str) -> List[MemoryItem]:
    """
    Retrieve all memory items for a given session.

    Returns an empty list if the session has no memory.
    """
    return _SESSION_MEMORY.get(session_id, []).copy()


def append_session_memory(session_id: str, item: MemoryItem) -> None:
    """
    Append a new memory item to a session.

    This function is intentionally explicit:
    - No automatic summarization
    - No deduplication
    - No embedding
    """
    with _LOCK:
        if session_id not in _SESSION_MEMORY:
            _SESSION_MEMORY[session_id] = []

        _SESSION_MEMORY[session_id].append(item)


def clear_session_memory(session_id: str) -> None:
    """
    Clear all memory for a session.
    Useful when a session ends or is reset.
    """
    with _LOCK:
        _SESSION_MEMORY.pop(session_id, None)