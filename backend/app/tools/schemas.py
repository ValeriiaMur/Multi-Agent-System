"""Pydantic input schemas for tools. Every field is described."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SearchExercisesInput(BaseModel):
    muscle_groups: list[str] = Field(
        default_factory=list, description="Target muscle groups, e.g. ['chest', 'triceps']."
    )
    equipment: list[str] = Field(
        default_factory=list,
        description="Equipment the user has available; results must be satisfiable by it.",
    )
    movement_patterns: list[str] = Field(
        default_factory=list,
        description="Desired movement patterns, e.g. ['upper push - horizontal'].",
    )
    avoid_joints: list[str] = Field(
        default_factory=list,
        description="Joints to avoid loading (injury avoidance); exclude exercises loading them.",
    )


class WorkoutItem(BaseModel):
    exercise_id: str = Field(description="ID of a real exercise from the dataset.")
    sets: int = Field(description="Number of sets.")
    reps: int = Field(description="Reps per set.")
    rest_seconds: int = Field(description="Rest between sets in seconds.")


class BuildWorkoutInput(BaseModel):
    duration_minutes: int = Field(description="Total target session length in minutes.")
    main: list[WorkoutItem] = Field(description="Main-block exercises with prescription.")
    warmup: list[WorkoutItem] = Field(default_factory=list, description="Warmup items.")
    cooldown: list[WorkoutItem] = Field(default_factory=list, description="Cooldown items.")
