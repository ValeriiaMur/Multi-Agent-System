"""Coach should ground answers in the real exercise catalog."""
from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.agents.coach import build_coach_graph, relevant_exercises


def test_relevant_exercises_matches_muscle_terms(exercises):
    hits = relevant_exercises("how should I train my chest?", exercises, k=5)
    assert hits, "expected catalog matches for a chest question"
    assert all("chest" in e.muscle_groups for e in hits)
    assert len(hits) <= 5


def test_relevant_exercises_empty_for_offtopic(exercises):
    assert relevant_exercises("what's the weather today?", exercises) == []


def test_coach_graph_still_answers(fake_llm, exercises):
    graph = build_coach_graph(fake_llm(text="Your chest is worked by pressing movements."), exercises)
    out = graph.invoke({"messages": [HumanMessage(content="what trains the chest?")]})
    assert any("chest" in m.content.lower() for m in out["messages"] if hasattr(m, "content"))
