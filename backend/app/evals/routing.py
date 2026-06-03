"""Routing evals: a labeled dataset + a tiny harness to score classification.

Routing is the highest-leverage decision in the system (a silent misroute is the
worst failure), so it gets a golden set we can score against the real model. The
harness is provider-agnostic: pass any ``route_fn(messages) -> route`` — the live
router, a heuristic, or a stub — and get an accuracy report with per-case misses.

Run against the real model:  python -m scripts.eval_routing   (needs an API key)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ..state import Route


@dataclass(frozen=True)
class RoutingCase:
    message: str
    expected: Route
    # Prior turns as (role, text) with role in {"human", "ai"}; enables follow-ups.
    history: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    note: str = ""

    def messages(self) -> list[tuple[str, str]]:
        return [*self.history, ("human", self.message)]


# Golden set — covers every route, the "act over clarify" cases, the CLARIFY
# safety net, and context-dependent follow-ups.
ROUTING_CASES: list[RoutingCase] = [
    # COACH
    RoutingCase("what muscles does a deadlift work?", "COACH"),
    RoutingCase("how do I fix my squat depth?", "COACH"),
    RoutingCase("is it better to train chest before shoulders?", "COACH"),
    # WORKOUT_GENERATE — explicit + vague-but-actionable
    RoutingCase("build me a 30 min upper body session with dumbbells", "WORKOUT_GENERATE"),
    RoutingCase("give me a leg day", "WORKOUT_GENERATE"),
    RoutingCase("next workout", "WORKOUT_GENERATE", note="vague but has a sensible default"),
    RoutingCase("what should I train today?", "WORKOUT_GENERATE"),
    # WORKOUT_LOG
    RoutingCase("I just did 3x10 bench press at 185 lbs", "WORKOUT_LOG"),
    RoutingCase("finished 5 sets of pullups and some curls", "WORKOUT_LOG"),
    # CLARIFY — genuinely unworkable
    RoutingCase("bench press", "CLARIFY", note="bare exercise name"),
    RoutingCase("idk", "CLARIFY"),
    # Follow-ups that REQUIRE conversation context
    RoutingCase(
        "make it harder",
        "WORKOUT_GENERATE",
        history=(("human", "give me a leg day"), ("ai", "Here's a workout built from your library.")),
        note="refers to the just-generated workout",
    ),
    RoutingCase(
        "why does that work the glutes?",
        "COACH",
        history=(("human", "what does a hip thrust train?"), ("ai", "It primarily targets the glutes.")),
        note="follow-up question",
    ),
]


@dataclass
class EvalReport:
    total: int
    correct: int
    failures: list[dict[str, Any]]

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    def format(self) -> str:
        lines = [f"routing accuracy: {self.correct}/{self.total} = {self.accuracy:.0%}"]
        for f in self.failures:
            lines.append(f"  ✗ {f['message']!r}: expected {f['expected']}, got {f['got']}")
        return "\n".join(lines)


def evaluate_routing(
    route_fn: Callable[[list[tuple[str, str]]], str],
    cases: list[RoutingCase] = ROUTING_CASES,
) -> EvalReport:
    """Score ``route_fn`` over the golden set. ``route_fn`` takes a message list
    (role, text tuples) and returns the chosen route string."""
    failures: list[dict[str, Any]] = []
    for c in cases:
        got = route_fn(c.messages())
        if got != c.expected:
            failures.append({"message": c.message, "expected": c.expected, "got": got, "note": c.note})
    return EvalReport(total=len(cases), correct=len(cases) - len(failures), failures=failures)
