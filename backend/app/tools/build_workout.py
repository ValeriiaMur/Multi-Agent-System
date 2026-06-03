"""build_workout tool: assemble a {warmup, main, cooldown} workout from selected
exercises, validating every exercise_id against the dataset."""
from __future__ import annotations

from typing import Any

from ..data import Exercise
from ..observability import traced
from .schemas import BuildWorkoutInput


class UnknownExerciseError(ValueError):
    """Raised when a tool call references an exercise ID not in the dataset."""


@traced(run_type="tool", name="build_workout")
def build_workout(args: BuildWorkoutInput, exercises: list[Exercise]) -> dict[str, Any]:
    """Assemble a structured workout {warmup, main, cooldown}.

    Validates that every exercise_id exists in the dataset; unknown IDs are an
    invalid tool call and raise UnknownExerciseError so the agent can recover.
    """
    name_by_id = {e.id: e.name for e in exercises}

    def render(items):
        rendered = []
        for it in items:
            if it.exercise_id not in name_by_id:
                raise UnknownExerciseError(f"Unknown exercise_id: {it.exercise_id}")
            rendered.append(
                {
                    "exercise_id": it.exercise_id,
                    "name": name_by_id[it.exercise_id],
                    "sets": it.sets,
                    "reps": it.reps,
                    "rest_seconds": it.rest_seconds,
                }
            )
        return rendered

    return {
        "duration_minutes": args.duration_minutes,
        "warmup": render(args.warmup),
        "main": render(args.main),
        "cooldown": render(args.cooldown),
    }
