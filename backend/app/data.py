"""Load and type the exercise dataset."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

_HERE = Path(__file__).resolve()
# Candidate locations, in priority order. Works whether the app is run from the
# repo root or from backend/ (e.g. Railway with a backend root directory).
_CANDIDATES = [
    _HERE.parents[1] / "data" / "exercises.json",  # backend/data/exercises.json
    _HERE.parents[2] / "data" / "exercises.json",  # <repo>/data/exercises.json
]


def _resolve_data_path() -> Path:
    env = os.getenv("EXERCISES_PATH")
    if env:
        return Path(env)
    for candidate in _CANDIDATES:
        if candidate.exists():
            return candidate
    return _CANDIDATES[0]  # default; load_exercises will raise a clear error


DATA_PATH = _resolve_data_path()


class Exercise(BaseModel):
    id: str
    name: str
    muscle_groups: list[str] = []
    joints_loaded: list[str] = []
    movement_patterns: list[str] = []
    equipment_required: list[str] = []
    priority_tier: int | None = None
    is_bilateral: bool = False
    bilateral_pair_id: str | None = None
    side: str | None = None
    supports_weight: bool = False
    is_reps: bool = False
    is_duration: bool = False
    estimated_rep_duration: float | None = None


@lru_cache(maxsize=1)
def load_exercises(path: str | None = None) -> list[Exercise]:
    p = Path(path) if path else DATA_PATH
    raw = json.loads(p.read_text())
    return [Exercise(**row) for row in raw]
