"""Small shared helpers for graph nodes."""
from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage


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


def _role_and_text(m: Any) -> tuple[str, str] | None:
    """Normalize a message (object or ("human"/"ai", text) tuple) to (role, text)."""
    if isinstance(m, HumanMessage):
        return "User", str(m.content)
    if isinstance(m, AIMessage):
        return "Coach", str(m.content)
    if isinstance(m, tuple) and len(m) == 2 and m[0] in ("human", "ai", "assistant"):
        return ("User" if m[0] == "human" else "Coach"), str(m[1])
    return None


def recent_context(messages: list[Any], turns: int = 4, max_chars: int = 240) -> str:
    """Format the conversation *before* the latest human turn as a short labeled
    transcript, so the router can resolve follow-ups ("make it harder", "next
    one"). Excludes the latest human message (that's classified separately) and
    truncates each line to keep the prompt small."""
    msgs = list(messages or [])
    # drop the trailing human turn (the message currently being routed)
    for i in range(len(msgs) - 1, -1, -1):
        rt = _role_and_text(msgs[i])
        if rt and rt[0] == "User":
            msgs = msgs[:i]
            break
    lines: list[str] = []
    for m in msgs[-turns:]:
        rt = _role_and_text(m)
        if not rt or not rt[1].strip():
            continue
        text = " ".join(rt[1].split())
        if len(text) > max_chars:
            text = text[: max_chars - 1] + "…"
        lines.append(f"{rt[0]}: {text}")
    return "\n".join(lines)
