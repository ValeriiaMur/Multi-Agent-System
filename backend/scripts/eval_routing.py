"""Run the routing evals against the real model and print a scored report.

Usage (from backend/):
    export ANTHROPIC_API_KEY=sk-ant-...
    python -m scripts.eval_routing

Scores the live router over the golden set in app/evals/routing.py — including
the context-dependent follow-ups — and prints accuracy plus any misses. Exits
non-zero if accuracy falls below the floor, so it can gate CI.
"""
from __future__ import annotations

import sys

from app._util import last_human_text, recent_context
from app.evals.routing import evaluate_routing
from app.hub.router import route_message
from app.llm import get_llm

ACCURACY_FLOOR = 0.8


def main() -> int:
    llm = get_llm()

    def route_fn(messages):
        return route_message(last_human_text(messages), llm, recent_context(messages)).route

    report = evaluate_routing(route_fn)
    print(report.format())
    if report.accuracy < ACCURACY_FLOOR:
        print(f"\nFAIL: accuracy {report.accuracy:.0%} < floor {ACCURACY_FLOOR:.0%}")
        return 1
    print(f"\nPASS: accuracy {report.accuracy:.0%} >= floor {ACCURACY_FLOOR:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
