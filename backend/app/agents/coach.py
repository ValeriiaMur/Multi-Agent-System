"""Coach sub-agent: a compiled StateGraph."""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .._util import history_messages, last_human_text
from ..data import Exercise, load_exercises
from ..observability import log_event
from ..state import HubState

COACH_PROMPT = (
    "You are an expert strength & conditioning coach. Answer the user's training, "
    "technique, anatomy, or programming question clearly and accurately. Ground "
    "claims about muscles and joints in established exercise science. Be concise."
)
_CONTEXT_PROMPT = (
    "Relevant exercises from the user's library (cite these where helpful; do not "
    "invent others):\n{items}"
)


def relevant_exercises(question: str, exercises: list[Exercise], k: int = 5) -> list[Exercise]:
    """Return up to k catalog exercises whose muscle group or name appears in the
    question — used to ground the coach's answer in real data."""
    q = question.lower()
    hits = [
        e
        for e in exercises
        if any(m in q for m in e.muscle_groups) or e.name.lower() in q
    ]
    return hits[:k]


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
        return {"messages": [reply]}

    g = StateGraph(HubState)
    g.add_node("coach", coach)
    g.add_edge(START, "coach")
    g.add_edge("coach", END)
    return g.compile()
