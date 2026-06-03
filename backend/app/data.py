"""Load and type the exercise dataset."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

_HERE = Path(__file__).resolve()
# Single source of truth, shipped inside the deployable backend. Override with
# EXERCISES_PATH if you keep the dataset elsewhere.
_CANONICAL = _HERE.parents[1] / "data" / "exercises.json"  # backend/data/exercises.json


def _resolve_data_path() -> Path:
    env = os.getenv("EXERCISES_PATH")
    return Path(env) if env else _CANONICAL


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
