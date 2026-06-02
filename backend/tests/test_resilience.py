"""Critical path #2: graceful failure. RED until Phase 5.

The generator must (a) recover when search returns no results without inventing
exercises, and (b) catch invalid tool calls (unknown exercise IDs).
"""
from __future__ import annotations

import pytest

from app.tools.build_workout import build_workout
from app.tools.schemas import BuildWorkoutInput, SearchExercisesInput, WorkoutItem
from app.tools.search_exercises import search_exercises


def test_empty_search_does_not_crash(exercises):
    out = search_exercises(SearchExercisesInput(equipment=["kettlebell-X9000"]), exercises)
    assert out == []  # caller handles empty; must not raise or hallucinate


def test_invalid_tool_call_is_caught(exercises):
    bad = BuildWorkoutInput(
        duration_minutes=20,
        main=[WorkoutItem(exercise_id="hallucinated-id", sets=3, reps=8, rest_seconds=60)],
    )
    with pytest.raises(Exception):
        build_workout(bad, exercises)
