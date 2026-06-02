"""Tool unit tests (no LLM). RED until Phase 2."""
from __future__ import annotations

import pytest

from app.tools.build_workout import build_workout
from app.tools.schemas import BuildWorkoutInput, SearchExercisesInput, WorkoutItem
from app.tools.search_exercises import search_exercises


def test_search_by_muscle_group_returns_matches(exercises):
    out = search_exercises(SearchExercisesInput(muscle_groups=["chest"]), exercises)
    assert out and all("chest" in e.muscle_groups for e in out)


def test_search_unavailable_equipment_returns_empty(exercises):
    out = search_exercises(
        SearchExercisesInput(muscle_groups=["chest"], equipment=["nonexistent-machine"]),
        exercises,
    )
    assert out == []


def test_avoid_joints_excludes_loaded_exercises(exercises):
    out = search_exercises(SearchExercisesInput(avoid_joints=["shoulder"]), exercises)
    assert all("shoulder" not in e.joints_loaded for e in out)


def test_build_workout_with_valid_id(exercises):
    ex = exercises[0]
    spec = BuildWorkoutInput(
        duration_minutes=30,
        main=[WorkoutItem(exercise_id=ex.id, sets=3, reps=10, rest_seconds=90)],
    )
    workout = build_workout(spec, exercises)
    assert set(workout) >= {"warmup", "main", "cooldown"}


def test_build_workout_rejects_unknown_id(exercises):
    spec = BuildWorkoutInput(
        duration_minutes=30,
        main=[WorkoutItem(exercise_id="not-a-real-id", sets=3, reps=10, rest_seconds=90)],
    )
    with pytest.raises(Exception):
        build_workout(spec, exercises)
