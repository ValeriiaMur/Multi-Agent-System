"""Coach remembers earlier turns: prior conversation is fed into its prompt."""
from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from app._util import history_messages
from app.agents.coach import build_coach_graph


class CapturingLLM:
    """Records the message list passed to invoke() so we can assert on it."""

    def __init__(self) -> None:
        self.seen: list = []

    def invoke(self, messages):
        self.seen = list(messages)
        return AIMessage(content="Because the hip thrust loads the glutes in hip extension.")


def test_history_messages_excludes_trailing_human_turn():
    msgs = [
        HumanMessage(content="what does a hip thrust train?"),
        AIMessage(content="It primarily targets the glutes."),
        HumanMessage(content="why does that work the glutes?"),  # current turn
    ]
    hist = history_messages(msgs)
    assert ("human", "what does a hip thrust train?") in hist
    assert ("ai", "It primarily targets the glutes.") in hist
    # the turn being answered is NOT duplicated into history
    assert all("why does that work" not in t for _, t in hist)


def test_coach_prompt_includes_prior_turns(exercises):
    llm = CapturingLLM()
    graph = build_coach_graph(llm, exercises)
    graph.invoke(
        {
            "messages": [
                HumanMessage(content="what does a hip thrust train?"),
                AIMessage(content="It primarily targets the glutes."),
                HumanMessage(content="why does that work the glutes?"),
            ]
        }
    )
    blob = " ".join(
        (m[1] if isinstance(m, tuple) else getattr(m, "content", "")) for m in llm.seen
    )
    # the coach saw the earlier exchange, not just the latest message
    assert "what does a hip thrust train?" in blob
    assert "It primarily targets the glutes." in blob
    assert "why does that work the glutes?" in blob
