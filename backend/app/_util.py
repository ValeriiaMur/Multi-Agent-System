"""Small shared helpers for graph nodes."""
from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage


def last_human_text(messages: list[Any]) -> str:
    """Return the text of the most recent human turn (supports message objects
    and ("human", text) tuples)."""
    for m in reversed(messages or []):
        if isinstance(m, HumanMessage):
            return str(m.content)
        if isinstance(m, tuple) and len(m) == 2 and m[0] == "human":
            return str(m[1])
    if messages:
        last = messages[-1]
        return str(getattr(last, "content", last))
    return ""
