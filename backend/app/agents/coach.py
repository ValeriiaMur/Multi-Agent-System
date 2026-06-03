"""Coach sub-agent: a compiled StateGraph."""
from __future__ import annotations

import re

from langgraph.graph import END, START, StateGraph

from .._util import history_messages, last_human_text
from ..data import Exercise, load_exercises
from ..observability import log_event
from ..state import HubState

MAX_REFERENCES = 3

COACH_PROMPT = (
    "You are an expert strength & conditioning coach. Answer the user's training, "
    "technique, anatomy, or programming question clearly and accurately. Ground "
    "claims about muscles and joints in established exercise science. Be concise."
)
_CONTEXT_PROMPT = (
    "Relevant exercises from the user's library (cite these where helpful; do not "
    "invent others):\n{items}"
)


def _tokens(text: str) -> list[str]:
    # drop 1–2 char tokens ("s" from possessives, "a", "to", "my") to avoid
    # spurious overlaps; all dataset muscle terms are 3+ chars.
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) >= 3]


def relevant_exercises(question: str, exercises: list[Exercise], k: int = 5) -> list[Exercise]:
    """Rank catalog exercises by token overlap with the question across name,
    muscle groups, movement patterns, and joints — so "what muscles does a
    deadlift work" surfaces deadlift variants even when no muscle is named."""
    query = set(_tokens(question))
    if not query:
        return []
    scored: list[tuple[int, Exercise]] = []
    for e in exercises:
        hay = _tokens(" ".join([e.name, *e.muscle_groups, *e.movement_patterns, *e.joints_loaded]))
        overlap = sum(1 for t in hay if t in query)
        if overlap:
            scored.append((overlap, e))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [e for _, e in scored[:k]]


def build_coach_graph(llm, exercises=None):
    """Return a compiled StateGraph answering coaching questions."""
    catalog = exercises if exercises is not None else load_exercises()

    def coach(state: HubState) -> dict:
        text = last_human_text(state["messages"])
        grounded = relevant_exercises(text, catalog)
        history = history_messages(state["messages"])
        log_event(
            "llm",
            "coach",
            {"chars": len(text), "grounded": len(grounded), "history": len(history)},
        )
        messages = [("system", COACH_PROMPT)]
        if grounded:
            items = "\n".join(f"- {e.name} ({', '.join(e.muscle_groups)})" for e in grounded)
            messages.append(("system", _CONTEXT_PROMPT.format(items=items)))
        messages.extend(history)  # prior turns -> the coach remembers the conversation
        messages.append(("human", text))
        reply = llm.invoke(messages)
        references = [
            {"id": e.id, "name": e.name, "muscle_groups": e.muscle_groups}
            for e in grounded[:MAX_REFERENCES]
        ]
        return {"messages": [reply], "references": references}

    g = StateGraph(HubState)
    g.add_node("coach", coach)
    g.add_edge(START, "coach")
    g.add_edge("coach", END)
    return g.compile()
