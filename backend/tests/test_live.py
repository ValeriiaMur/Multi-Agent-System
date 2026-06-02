"""Golden live tests — hit the real Anthropic model. Excluded by default.

Run with:  pytest -m live      (requires ANTHROPIC_API_KEY)

These guard against behavioral regressions that the offline FakeLLM cannot catch:
that the real model routes clear inputs correctly, falls back to CLARIFY on
ambiguous ones, and that the generator returns only real exercise IDs.
"""
from __future__ import annotations

import os

import pytest
from langchain_core.messages import HumanMessage

pytestmark = pytest.mark.live

_NEEDS_KEY = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set"
)


@_NEEDS_KEY
def test_live_routes_clear_inputs():
    from app.hub.router import route_message
    from app.llm import get_llm

    llm = get_llm()
    assert route_message("What muscles does a deadlift work?", llm).route == "COACH"
    assert route_message("Build me a 30 min dumbbell upper body session", llm).route == "WORKOUT_GENERATE"
    assert route_message("I just did 3x10 bench press at 185 lbs", llm).route == "WORKOUT_LOG"


@_NEEDS_KEY
def test_live_ambiguous_input_clarifies():
    from app.hub.router import route_message
    from app.llm import get_llm

    decision = route_message("Bench press", get_llm())
    assert decision.route == "CLARIFY"


@_NEEDS_KEY
def test_live_generator_uses_only_real_ids(exercises):
    from app.hub.graph import build_hub_graph
    from app.llm import get_llm

    graph = build_hub_graph(get_llm(), exercises)
    state = graph.invoke(
        {"messages": [HumanMessage(content="Build me a 20 min dumbbell chest workout")]}
    )
    valid = {e.id for e in exercises}
    if state.get("workout"):
        for item in state["workout"]["main"]:
            assert item["exercise_id"] in valid  # never a hallucinated ID
