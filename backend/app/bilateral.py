"""Bilateral pairing helper: auto-include the other-side partner for any
bilateral exercise (stretch goal)."""
from __future__ import annotations

from .data import Exercise


def expand_bilateral(selected: list[Exercise], all_exercises: list[Exercise]) -> list[Exercise]:
    """For any bilateral exercise, auto-include its bilateral_pair_id partner."""
    by_id = {e.id: e for e in all_exercises}
    out = list(selected)
    seen = {e.id for e in selected}
    for e in selected:
        if e.is_bilateral and e.bilateral_pair_id and e.bilateral_pair_id not in seen:
            partner = by_id.get(e.bilateral_pair_id)
            if partner is not None:
                out.append(partner)
                seen.add(partner.id)
    return out
