"""Workout logger sub-agent: extraction StateGraph.

Extracts {exercise, sets, reps, weight} from natural language and fuzzy-matches
the exercise name against the dataset (e.g. "bench press" -> canonical name).
"""
from __future__ import annotations

import difflib

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from .._util import last_human_text
from ..data import Exercise, load_exercises
from ..observability import log_event, traced
from ..state import HubState

_MATCH_THRESHOLD = 0.6

LOG_PROMPT = (
    "Extract each exercise the user reports performing, with sets, reps, and weight "
    "(if mentioned). Use the user's own exercise wording; matching to the catalog "
    "happens downstream."
)


class RawEntry(BaseModel):
    exercise: str = Field(description="Exercise name exactly as the user said it.")
    sets: int = Field(description="Number of sets performed.")
    reps: int = Field(description="Reps per set.")
    weight: float | None = Field(default=None, description="Weight used, if stated.")


class RawLog(BaseModel):
    entries: list[RawEntry] = Field(description="One item per exercise reported.")


@traced(run_type="tool", name="fuzzy_match_exercise")
def fuzzy_match_exercise(name: str, exercises: list[Exercise]) -> Exercise | None:
    """Return the best dataset match for a colloquial exercise name, or None.

    Combines token containment (e.g. "bench press" ⊆ "Barbell Decline Bench
    Press") with a character-level similarity ratio so short colloquial names
    still match longer canonical names.
    """
    query = name.lower().strip()
    if not query:
        return None
    q_tokens = set(query.split())

    best: Exercise | None = None
    best_score = 0.0
    for e in exercises:
        canonical = e.name.lower()
        score = difflib.SequenceMatcher(None, query, canonical).ratio()
        if q_tokens and q_tokens <= set(canonical.split()):
            score += 0.5  # all query words present -> strong signal
        if score > best_score:
            best_score = score
            best = e
    return best if best_score >= _MATCH_THRESHOLD else None


def build_logger_graph(llm, exercises: list[Exercise] | None = None):
    """Return a compiled StateGraph that returns structured JSON log entries."""
    catalog = exercises if exercises is not None else load_exercises()

    def node(state: HubState) -> dict:
        text = last_human_text(state["messages"])
        raw = llm.with_structured_output(RawLog).invoke(
            [("system", LOG_PROMPT), ("human", text)]
        )
        entries = []
        for r in raw.entries:
            match = fuzzy_match_exercise(r.exercise, catalog)
            entries.append(
                {
                    "exercise": match.name if match else r.exercise,
                    "exercise_id": match.id if match else None,
                    "matched": match is not None,
                    "sets": r.sets,
                    "reps": r.reps,
                    "weight": r.weight,
                }
            )
        log_event("logger", "extract", {"entries": len(entries)})
        return {"messages": [AIMessage(content="Logged your session.")], "log_entries": entries}

    g = StateGraph(HubState)
    g.add_node("log", node)
    g.add_edge(START, "log")
    g.add_edge("log", END)
    return g.compile()
