"""Workout generator sub-agent: tool-driven StateGraph.

Flow: LLM extracts a GenerationSpec -> search_exercises -> build_workout. Recovers
when search returns [] (no hallucinated exercises) and catches invalid tool calls
(unknown exercise IDs) — Phase 5 resilience.
"""
from __future__ import annotations

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from .._util import last_human_text
from ..bilateral import expand_bilateral
from ..data import load_exercises
from ..observability import log_event
from ..state import HubState
from ..tools.build_workout import UnknownExerciseError, build_workout
from ..tools.schemas import BuildWorkoutInput, SearchExercisesInput, WorkoutItem
from ..tools.search_exercises import search_exercises

GEN_PROMPT = (
    "Extract workout parameters from the user's request: target muscle groups, "
    "available equipment, desired movement patterns, total duration in minutes, "
    "and any joints to avoid (injuries)."
)
MAX_MAIN_EXERCISES = 5


class GenerationSpec(BaseModel):
    muscle_groups: list[str] = Field(default_factory=list, description="Target muscle groups.")
    equipment: list[str] = Field(default_factory=list, description="Equipment the user has.")
    movement_patterns: list[str] = Field(default_factory=list, description="Desired patterns.")
    duration_minutes: int = Field(default=30, description="Total session length in minutes.")
    avoid_joints: list[str] = Field(default_factory=list, description="Joints to avoid loading.")


def build_generator_graph(llm, exercises=None):
    """Return a compiled StateGraph that generates a structured workout."""
    catalog = exercises if exercises is not None else load_exercises()

    def generate(state: HubState) -> dict:
        text = last_human_text(state["messages"])
        spec = llm.with_structured_output(GenerationSpec).invoke(
            [("system", GEN_PROMPT), ("human", text)]
        )
        avoid = list({*spec.avoid_joints, *state.get("avoid_joints", [])})
        log_event("llm", "generator.spec", {"muscles": spec.muscle_groups, "avoid": avoid})

        found = search_exercises(
            SearchExercisesInput(
                muscle_groups=spec.muscle_groups,
                equipment=spec.equipment,
                movement_patterns=spec.movement_patterns,
                avoid_joints=avoid,
            ),
            catalog,
        )
        log_event("tool", "search_exercises", {"n": len(found)})

        if not found:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "I couldn't find exercises matching that request in the "
                            "library. Could you broaden the equipment or muscle groups?"
                        )
                    )
                ],
                "workout": None,
            }

        found = expand_bilateral(found, catalog)  # stretch: bilateral pairing
        chosen = sorted(found, key=lambda e: e.priority_tier or 99)[:MAX_MAIN_EXERCISES]
        items = [
            WorkoutItem(exercise_id=e.id, sets=3, reps=10, rest_seconds=90) for e in chosen
        ]
        try:
            workout = build_workout(
                BuildWorkoutInput(duration_minutes=spec.duration_minutes, main=items), catalog
            )
        except UnknownExerciseError as exc:  # invalid tool call -> recover
            log_event("error", "build_workout", {"detail": str(exc)})
            return {
                "messages": [
                    AIMessage(content="I hit an invalid exercise reference and skipped it.")
                ],
                "workout": None,
            }

        log_event("tool", "build_workout", {"main": len(workout["main"])})
        return {
            "messages": [AIMessage(content="Here's a workout built from your library.")],
            "workout": workout,
        }

    g = StateGraph(HubState)
    g.add_node("generate", generate)
    g.add_edge(START, "generate")
    g.add_edge("generate", END)
    return g.compile()
