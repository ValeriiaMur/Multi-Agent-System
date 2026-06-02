"""search_exercises tool. STUB — implement in Phase 2 (GREEN)."""
from __future__ import annotations

from ..data import Exercise
from .schemas import SearchExercisesInput


def search_exercises(args: SearchExercisesInput, exercises: list[Exercise]) -> list[Exercise]:
    """Filter exercises by muscle groups, equipment, movement patterns, avoid_joints.

    Semantics:
    - muscle_groups / movement_patterns: keep if there is any overlap.
    - equipment: it is the gear the user HAS. When provided, keep an exercise
      only if it requires equipment and all of that equipment is available — so
      asking for gear the dataset doesn't have yields no results (a case the
      caller must handle gracefully).
    - avoid_joints: drop any exercise that loads a joint the user wants to avoid.

    Returns [] when nothing matches (callers must handle empty gracefully).
    """
    wanted_muscles = set(args.muscle_groups)
    wanted_patterns = set(args.movement_patterns)
    available = set(args.equipment)
    avoid = set(args.avoid_joints)

    out: list[Exercise] = []
    for e in exercises:
        if wanted_muscles and not (wanted_muscles & set(e.muscle_groups)):
            continue
        if wanted_patterns and not (wanted_patterns & set(e.movement_patterns)):
            continue
        if available:
            req = set(e.equipment_required)
            if not req or not req <= available:
                continue
        if avoid and (avoid & set(e.joints_loaded)):
            continue
        out.append(e)
    return out
