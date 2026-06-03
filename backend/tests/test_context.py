"""recent_context: the router's short conversation window for follow-ups."""
from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from app._util import recent_context


def test_excludes_the_latest_human_turn():
    msgs = [
        HumanMessage(content="build me a leg day"),
        AIMessage(content="Here's a workout built from your library."),
        HumanMessage(content="make it harder"),  # the turn being routed
    ]
    ctx = recent_context(msgs)
    assert "make it harder" not in ctx
    assert "User: build me a leg day" in ctx
    assert "Coach: Here's a workout built from your library." in ctx


def test_empty_for_first_turn():
    assert recent_context([HumanMessage(content="hi")]) == ""


def test_truncates_long_lines():
    long = "x" * 500
    msgs = [HumanMessage(content=long), AIMessage(content="ok"), HumanMessage(content="next")]
    ctx = recent_context(msgs, max_chars=240)
    assert "…" in ctx
    assert len(ctx.splitlines()[0]) <= len("User: ") + 240
