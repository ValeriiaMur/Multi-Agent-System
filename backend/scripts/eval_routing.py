"""Run the routing evals against the real model, print and SAVE a scored report.

Usage (from backend/):
    export ANTHROPIC_API_KEY=sk-ant-...
    python -m scripts.eval_routing

Scores the live router over the golden set in app/evals/routing.py — including
the context-dependent follow-ups — and prints accuracy plus any misses. It scores
the SAME model production routing uses (get_model("router")), not the global
default, so the number reflects what ships. Each run is written to
backend/evals_results/routing-<timestamp>.json so scores have a saved history
(diff across model swaps). Exits non-zero if accuracy falls below the floor, so
it can gate CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from app._util import last_human_text, recent_context
from app.config import get_model
from app.evals.routing import ROUTING_CASES, evaluate_routing
from app.hub.router import route_message
from app.llm import get_llm

ACCURACY_FLOOR = 0.8
RESULTS_DIR = Path(__file__).resolve().parent.parent / "evals_results"


def save_report(report, model: str) -> Path:
    """Persist a scored run as JSON so routing accuracy has a tracked history."""
    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "eval": "routing",
        "model": model,
        "accuracy": round(report.accuracy, 4),
        "correct": report.correct,
        "total": report.total,
        "floor": ACCURACY_FLOOR,
        "passed": report.accuracy >= ACCURACY_FLOOR,
        "failures": report.failures,
    }
    path = RESULTS_DIR / f"routing-{stamp}.json"
    path.write_text(json.dumps(record, indent=2) + "\n")
    return path


def main() -> int:
    model = get_model("router")  # score the model production actually routes with
    llm = get_llm(model)

    def route_fn(messages):
        return route_message(last_human_text(messages), llm, recent_context(messages)).route

    report = evaluate_routing(route_fn, ROUTING_CASES)
    print(f"model: {model}")
    print(report.format())

    path = save_report(report, model)
    print(f"\nsaved: {path}")

    if report.accuracy < ACCURACY_FLOOR:
        print(f"FAIL: accuracy {report.accuracy:.0%} < floor {ACCURACY_FLOOR:.0%}")
        return 1
    print(f"PASS: accuracy {report.accuracy:.0%} >= floor {ACCURACY_FLOOR:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
