"""Coach sub-agent: a compiled StateGraph."""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .._util import last_human_text
from ..observability import log_event
from ..state import HubState

COACH_PROMPT = (
    "You are an expert strength & conditioning coach. Answer the user's training, "
    "technique, anatomy, or programming question clearly and accurately. Ground "
    "claims about muscles and joints in established exercise science. Be concise."
)


def build_coach_graph(llm, exercises=None):
    """Return a compiled StateGraph answering coaching questions."""

    def coach(state: HubState) -> dict:
        text = last_human_text(state["messages"])
        log_event("llm", "coach", {"chars": len(text)})
        reply = llm.invoke([("system", COACH_PROMPT), ("human", text)])
        return {"messages": [reply]}

    g = StateGraph(HubState)
    g.add_node("coach", coach)
    g.add_edge(START, "coach")
    g.add_edge("coach", END)
    return g.compile()
