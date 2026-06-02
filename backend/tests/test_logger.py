"""Workout logger: fuzzy matching + structured extraction. RED until Phase 3."""
from __future__ import annotations

from app.agents.workout_logger import fuzzy_match_exercise


def test_fuzzy_match_colloquial_name(exercises):
    match = fuzzy_match_exercise("bench press", exercises)
    assert match is not None
    assert "bench" in match.name.lower()


def test_fuzzy_match_unknown_returns_none(exercises):
    assert fuzzy_match_exercise("zzz not an exercise", exercises) is None
