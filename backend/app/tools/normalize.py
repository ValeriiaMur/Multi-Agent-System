"""Map loose LLM-extracted vocab onto the dataset's exact muscle/equipment names.

The generator's LLM step emits human phrasing ("upper body", "dumbbells") that
won't exactly match the catalog's specific values ("chest"/"triceps"/…,
"Dumbbell"). These deterministic maps bridge that gap so search_exercises (which
is exact by design) actually returns matches. Without this, a perfectly-routed
"upper body with dumbbells" request finds nothing and falls back to recovery.
"""
from __future__ import annotations

from functools import lru_cache

from ..data import load_exercises

# Group terms → the specific muscle_groups present in the dataset.
MUSCLE_SYNONYMS: dict[str, list[str]] = {
    "upper body": ["chest", "triceps", "deltoids", "biceps", "lats", "upper back", "traps"],
    "upper": ["chest", "triceps", "deltoids", "biceps", "lats", "upper back", "traps"],
    "lower body": ["quads", "glutes", "hamstrings", "calves", "hip flexors", "hip adductors"],
    "lower": ["quads", "glutes", "hamstrings", "calves", "hip flexors"],
    "legs": ["quads", "glutes", "hamstrings", "calves", "hip flexors"],
    "leg": ["quads", "glutes", "hamstrings", "calves"],
    "push": ["chest", "triceps", "deltoids"],
    "pull": ["lats", "biceps", "upper back", "middle back"],
    "full body": ["chest", "quads", "glutes", "core", "upper back", "deltoids"],
    "total body": ["chest", "quads", "glutes", "core", "upper back", "deltoids"],
    "back": ["lats", "upper back", "middle back", "lower back"],
    "arms": ["biceps", "triceps", "forearms"],
    "arm": ["biceps", "triceps"],
    "shoulders": ["deltoids", "rotator cuff"],
    "shoulder": ["deltoids"],
    "core": ["core", "obliques"],
    "abs": ["core", "obliques"],
    "ab": ["core", "obliques"],
}

# Equipment a typical gym has lying around — shouldn't disqualify a match just
# because an exercise also rests on a bench/rack/plate/mat.
AMBIENT_EQUIPMENT: set[str] = {
    "Flat Bench",
    "Adjustable Bench - Incline",
    "Adjustable Bench - Decline",
    "Preacher Curl Bench",
    "Yoga Mat",
    "Wall",
    "Box",
    "Plate",
    "Rack",
    "Slant Board",
}

# Colloquial equipment phrasing → canonical dataset name(s).
EQUIP_SYNONYMS: dict[str, list[str]] = {
    "dumbbell": ["Dumbbell"],
    "dumbbells": ["Dumbbell"],
    "db": ["Dumbbell"],
    "barbell": ["Barbell"],
    "barbells": ["Barbell"],
    "kettlebell": ["Kettlebell"],
    "kettlebells": ["Kettlebell"],
    "kb": ["Kettlebell"],
    "band": ["Resistance Band - Loop", "Resistance Band - With Handles", "Miniband"],
    "bands": ["Resistance Band - Loop", "Resistance Band - With Handles", "Miniband"],
    "resistance band": ["Resistance Band - Loop", "Resistance Band - With Handles"],
    "resistance bands": ["Resistance Band - Loop", "Resistance Band - With Handles"],
    "cable": ["Cable Resistance Machine"],
    "cables": ["Cable Resistance Machine"],
    "machine": ["Cable Resistance Machine"],
    "pull-up bar": ["Pull-Up Bar"],
    "pullup bar": ["Pull-Up Bar"],
    "pull up bar": ["Pull-Up Bar"],
    "medicine ball": ["Medicine Ball"],
    "med ball": ["Medicine Ball"],
    "ez bar": ["EZ Bar"],
    "jump rope": ["Jump Rope"],
    "sandbag": ["Sandbag"],
    "bench": ["Flat Bench"],
}


@lru_cache(maxsize=1)
def _dataset_vocab() -> tuple[frozenset[str], dict[str, str]]:
    """(set of lowercase muscle names, {lowercase equipment: canonical})."""
    muscles: set[str] = set()
    equip: dict[str, str] = {}
    for e in load_exercises():
        muscles.update(m.lower() for m in e.muscle_groups)
        for x in e.equipment_required:
            equip[x.lower()] = x
    return frozenset(muscles), equip


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def normalize_muscles(values: list[str]) -> list[str]:
    """Expand group terms and lowercase to dataset muscle names; drop unknowns."""
    dataset_muscles, _ = _dataset_vocab()
    out: list[str] = []
    for v in values or []:
        key = " ".join(v.strip().lower().split())
        if key in MUSCLE_SYNONYMS:
            out.extend(MUSCLE_SYNONYMS[key])
        elif key in dataset_muscles:
            out.append(key)
    return _dedupe(out)


def normalize_equipment(values: list[str]) -> list[str]:
    """Canonicalize colloquial equipment to dataset names; drop unknowns."""
    _, canon = _dataset_vocab()
    out: list[str] = []
    for v in values or []:
        key = " ".join(v.strip().lower().split())
        if key in EQUIP_SYNONYMS:
            out.extend(EQUIP_SYNONYMS[key])
        elif key in canon:
            out.append(canon[key])
        elif key.endswith("s") and key[:-1] in canon:  # naive singular
            out.append(canon[key[:-1]])
    return _dedupe(out)
