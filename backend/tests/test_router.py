"""Critical path #1: routing + low-confidence fallback. RED until Phase 1."""
from __future__ import annotations

import pytest

from app.hub.router import RouterDecision, route_message


def test_clear_coach_question_routes_to_coach(fake_llm):
    llm = fake_llm(RouterDecision(route="COACH", confidence=0.95, reason="info question"))
    decision = route_message("What muscles does a deadlift work?", llm)
    assert decision.route == "COACH"


def test_clear_generate_request_routes_to_generate(fake_llm):
    llm = fake_llm(RouterDecision(route="WORKOUT_GENERATE", confidence=0.9, reason="build"))
    decision = route_message("Build me a 30 min upper body session with dumbbells", llm)
    assert decision.route == "WORKOUT_GENERATE"


def test_clear_log_routes_to_log(fake_llm):
    llm = fake_llm(RouterDecision(route="WORKOUT_LOG", confidence=0.92, reason="log"))
    decision = route_message("I just did 3x10 bench press at 185 lbs", llm)
    assert decision.route == "WORKOUT_LOG"


@pytest.mark.parametrize("text", [
    "I did a workout yesterday, can you adjust it?",
    "Bench press",
])
def test_low_confidence_falls_back_to_clarify(fake_llm, text):
    # Model is unsure -> below threshold -> CLARIFY, never a silent misroute.
    llm = fake_llm(RouterDecision(route="WORKOUT_LOG", confidence=0.3, reason="ambiguous"))
    decision = route_message(text, llm)
    assert decision.route == "CLARIFY"
