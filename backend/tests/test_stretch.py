"""Stretch-goal tests: bilateral pairing + observability. RED until Phase 7."""
from __future__ import annotations

from app.bilateral import expand_bilateral
from app.observability import log_event


def test_bilateral_pair_auto_included(exercises):
    ids = {e.id for e in exercises}
    # Pick a bilateral exercise whose partner is actually present in the dataset.
    bil = next(
        (e for e in exercises if e.is_bilateral and e.bilateral_pair_id in ids),
        None,
    )
    if bil is None:
        return  # no in-dataset bilateral pair to test
    out_ids = {e.id for e in expand_bilateral([bil], exercises)}
    assert bil.bilateral_pair_id in out_ids


def test_log_event_emits(capsys):
    log_event("tool", "search_exercises", {"n": 3})
    assert capsys.readouterr().out  # structured line emitted
