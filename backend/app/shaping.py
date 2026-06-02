"""Map raw hub-graph state to the API contract the UI consumes."""
from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage


def shape_response(state: dict[str, Any]) -> dict[str, Any]:
    reply = ""
    for m in reversed(state.get("messages", [])):
        if isinstance(m, AIMessage):
            reply = str(m.content)
            break
    return {
        "route": state.get("route"),
        "confidence": state.get("confidence"),
        "reason": state.get("reason"),
        "reply": reply,
        "workout": state.get("workout"),
        "log_entries": state.get("log_entries"),
    }
