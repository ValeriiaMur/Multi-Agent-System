"""Routing eval harness — offline self-test + a @live accuracy gate.

The offline tests prove the harness scores correctly and the dataset is sane.
The @live test runs the real router over the golden set and asserts an accuracy
floor; it's excluded from the default run (needs an API key) — run with:
    pytest -m live
"""
from __future__ import annotations

import pytest

from app._util import last_human_text, recent_context
from app.evals.routing import ROUTING_CASES, evaluate_routing


def _oracle(messages):
    """A perfect router: looks the expected label up from the dataset."""
    by_message = {c.message: c.expected for c in ROUTING_CASES}
    return by_message[last_human_text(messages)]


def test_harness_scores_a_perfect_router():
    report = evaluate_routing(_oracle)
    assert report.accuracy == 1.0
    assert report.failures == []
    assert report.total == len(ROUTING_CASES)


def test_harness_reports_failures():
    report = evaluate_routing(lambda _messages: "CLARIFY")  # always wrong (mostly)
    assert report.correct < report.total
    assert any(f["expected"] != "CLARIFY" for f in report.failures)


def test_dataset_covers_every_route():
    assert {c.expected for c in ROUTING_CASES} == {"COACH", "WORKOUT_GENERATE", "WORKOUT_LOG", "CLARIFY"}


@pytest.mark.live
def test_routing_accuracy_live():
    """The real router (current model) must hit the accuracy floor on the golden set."""
    from app.hub.router import route_message
    from app.llm import get_llm

    llm = get_llm()

    def route_fn(messages):
        return route_message(last_human_text(messages), llm, recent_context(messages)).route

    report = evaluate_routing(route_fn)
    assert report.accuracy >= 0.8, "\n" + report.format()
