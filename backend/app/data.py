"""Load and type the exercise dataset."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "exercises.json"


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
