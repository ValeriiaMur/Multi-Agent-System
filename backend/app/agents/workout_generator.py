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
from ..tools.normalize import AMBIENT_EQUIPMENT, normalize_equipment, normalize_muscles
from ..tools.schemas import BuildWorkoutInput, SearchExercisesInput, WorkoutItem
from ..tools.search_exercises import search_exercises

GEN_PROMPT = (
    "Extract workout parameters from the user's request: target muscle groups, "
    "available equipment, desired movement patterns, total duration in minutes, "
    "any joints to avoid (injuries), and the training goal."
)
MAX_MAIN_EXERCISES = 6
MIN_MAIN_EXERCISES = 2
_GOAL_REPS = {"strength": (4, 10, 75), "endurance": (3, 15, 45), "power": (5, 5, 120)}


def _main_count(duration_minutes: int) -> int:
    """Roughly one main exercise per ~10 minutes, clamped to a sane range."""
    return max(MIN_MAIN_EXERCISES, min(MAX_MAIN_EXERCISES, duration_minutes // 10 + 1))


class GenerationSpec(BaseModel):
    muscle_groups: list[str] = Field(default_factory=list, description="Target muscle groups.")
    equipment: list[str] = Field(default_factory=list, description="Equipment the user has.")
    movement_patterns: list[str] = Field(default_factory=list, description="Desired patterns.")
    duration_minutes: int = Field(default=30, description="Total session length in minutes.")
    avoid_joints: list[str] = Field(default_factory=list, description="Joints to avoid loading.")
    goal: str = Field(default="strength", description="strength | endurance | power.")


def _matches(patterns: list[str], needle: str) -> bool:
    return any(needle in p.lower() for p in patterns)


def _is_warmup(e) -> bool:
    return _matches(e.movement_patterns, "mobility") or _matches(e.movement_patterns, "dynamic")


def _is_cooldown(e) -> bool:
    return (
        _matches(e.movement_patterns, "mobility - static")
        or _matches(e.movement_patterns, "stretch")
        or _matches(e.movement_patterns, "regen")
    )


def _enrich(rendered: list[dict], by_id: dict, kind: str) -> list[dict]:
    """Decorate built items with muscle data + a human-readable prescription."""
    out = []
    for it in rendered:
        ex = by_id.get(it["exercise_id"])
        if kind == "warmup":
            presc, rest = "0:45", 15
        elif kind == "cooldown":
            presc, rest = "0:30 hold", 0
        else:
            presc, rest = f"{it['sets']} × {it['reps']}", it["rest_seconds"]
        out.append(
            {
                **it,
                "muscle_groups": ex.muscle_groups if ex else [],
                "is_bilateral": ex.is_bilateral if ex else False,
                "prescription": presc,
                "rest": rest,
            }
        )
    return out


def build_generator_graph(llm, exercises=None):
    """Return a compiled StateGraph that generates a structured workout."""
    catalog = exercises if exercises is not None else load_exercises()

    def generate(state: HubState) -> dict:
        text = last_human_text(state["messages"])
        spec = llm.with_structured_output(GenerationSpec).invoke(
            [("system", GEN_PROMPT), ("human", text)]
        )
        avoid = list({*spec.avoid_joints, *state.get("avoid_joints", [])})
        # Normalize loose LLM vocab to the dataset's exact names, and treat benches/
        # racks/plates as ambient so e.g. a dumbbell session isn't filtered to nothing.
        # (movement_patterns are intentionally not used as a hard filter — they rarely
        # match the dataset's specific pattern strings and would over-exclude.)
        muscles = normalize_muscles(spec.muscle_groups)
        raw_equipment = spec.equipment or []
        user_equipment = normalize_equipment(raw_equipment)
        if user_equipment:
            search_equipment = user_equipment + sorted(AMBIENT_EQUIPMENT)
        elif raw_equipment:
            # gear we don't recognize/stock -> let search return nothing (honest recovery)
            search_equipment = raw_equipment
        else:
            search_equipment = []
        log_event("llm", "generator.spec", {"muscles": muscles, "equipment": user_equipment, "avoid": avoid})

        found = search_exercises(
            SearchExercisesInput(
                muscle_groups=muscles,
                equipment=search_equipment,
                avoid_joints=avoid,
            ),
            catalog,
        )
        # keep the session on-theme: prefer exercises that actually use the gear asked for
        if user_equipment:
            on_theme = [e for e in found if set(e.equipment_required) & set(user_equipment)]
            found = on_theme or found
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
        n_main = _main_count(spec.duration_minutes)
        chosen = sorted(found, key=lambda e: e.priority_tier or 99)[:n_main]
        sets, reps, rest = _GOAL_REPS.get(spec.goal, _GOAL_REPS["strength"])
        main_items = [
            WorkoutItem(exercise_id=e.id, sets=sets, reps=reps, rest_seconds=rest) for e in chosen
        ]
        # Real warm-up / cool-down drawn from the same catalog (never invented).
        chosen_ids = {e.id for e in chosen}
        warm = [e for e in catalog if _is_warmup(e) and e.id not in chosen_ids][:2]
        warm_ids = chosen_ids | {e.id for e in warm}
        cool = [e for e in catalog if _is_cooldown(e) and e.id not in warm_ids][:2]
        warm_items = [WorkoutItem(exercise_id=e.id, sets=1, reps=1, rest_seconds=15) for e in warm]
        cool_items = [WorkoutItem(exercise_id=e.id, sets=1, reps=1, rest_seconds=0) for e in cool]
        try:
            workout = build_workout(
                BuildWorkoutInput(
                    duration_minutes=spec.duration_minutes,
                    warmup=warm_items,
                    main=main_items,
                    cooldown=cool_items,
                ),
                catalog,
            )
        except UnknownExerciseError as exc:  # invalid tool call -> recover
            log_event("error", "build_workout", {"detail": str(exc)})
            return {
                "messages": [
                    AIMessage(content="I hit an invalid exercise reference and skipped it.")
                ],
                "workout": None,
            }

        by_id = {e.id: e for e in catalog}
        workout["warmup"] = _enrich(workout["warmup"], by_id, "warmup")
        workout["main"] = _enrich(workout["main"], by_id, "main")
        workout["cooldown"] = _enrich(workout["cooldown"], by_id, "cooldown")
        workout["meta"] = {
            "duration_min": spec.duration_minutes,
            "goal": spec.goal,
            "muscle_groups": spec.muscle_groups,
            "equipment": user_equipment or ["Any"],
            "avoid_joints": avoid,
            "empty": False,
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
