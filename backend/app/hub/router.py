"""LLM structured-output router.

Routing uses llm.with_structured_output(RouterDecision), never regex or keyword
matching. Confidence below the configured threshold is rewritten to CLARIFY so
the system never silently misroutes.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..config import settings
from ..state import Route


class RouterDecision(BaseModel):
    route: Route = Field(description="The chosen route for this user message.")
    confidence: float = Field(description="Confidence in [0,1] for the chosen route.")
    reason: str = Field(description="Short justification for the routing choice.")


SYSTEM_PROMPT = (
    "You are the router for a fitness coaching system. Classify the user's "
    "message into exactly one route:\n"
    "- COACH: questions about training, technique, anatomy, or programming advice.\n"
    "- WORKOUT_GENERATE: ANY request to build/create/design/plan a workout or "
    "session — including vague ones like 'next workout', 'what should I train "
    "today', 'give me something for legs'. A sensible default session is always "
    "possible, so these are NOT ambiguous.\n"
    "- WORKOUT_LOG: the user reporting a workout they ALREADY performed (past "
    "tense, with sets/reps/weight).\n"
    "- CLARIFY: ONLY when the message is genuinely unworkable — you cannot pick a "
    "reasonable route even with a sensible default. Prefer a concrete route when "
    "one is plausible; do not use CLARIFY merely because a detail is missing.\n\n"
    "Examples:\n"
    "- 'what muscles does a deadlift work?' -> COACH (0.97)\n"
    "- 'how do I fix my squat depth?' -> COACH (0.95)\n"
    "- 'build me a 30 min upper body session with dumbbells' -> WORKOUT_GENERATE (0.98)\n"
    "- 'next workout' -> WORKOUT_GENERATE (0.85)\n"
    "- 'what should I train today?' -> WORKOUT_GENERATE (0.9)\n"
    "- 'give me a leg day' -> WORKOUT_GENERATE (0.95)\n"
    "- 'I just did 3x10 bench at 185' -> WORKOUT_LOG (0.97)\n"
    "- 'finished 5 sets of pullups' -> WORKOUT_LOG (0.95)\n"
    "- 'bench press' -> CLARIFY (0.4)  # bare exercise name: explain it? build around it? log it?\n"
    "- 'idk' -> CLARIFY (0.3)\n\n"
    "If a 'Recent conversation' block is provided, use it to resolve follow-ups: "
    "e.g. 'make it harder' / 'another one' right after a generated workout -> "
    "WORKOUT_GENERATE; 'why?' after a coaching answer -> COACH. Always classify the "
    "'Latest message'.\n\n"
    "Return confidence in [0,1] reflecting how sure you are of the chosen route."
)


def route_message(text: str, llm, context: str = "") -> RouterDecision:
    """Classify intent via structured output, applying the confidence threshold.

    Uses llm.with_structured_output(RouterDecision) — never regex/keywords. Recent
    conversation (``context``) is included so follow-ups resolve correctly. If the
    model's confidence is below settings.router_confidence_threshold, the effective
    route becomes CLARIFY so the system never silently misroutes.
    """
    human = (
        f"Recent conversation:\n{context}\n\nLatest message: {text}" if context.strip() else text
    )
    structured = llm.with_structured_output(RouterDecision)
    decision = structured.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", human),
        ]
    )
    if decision.confidence < settings.router_confidence_threshold:
        return RouterDecision(
            route="CLARIFY",
            confidence=decision.confidence,
            reason=f"low confidence ({decision.confidence:.2f}): {decision.reason}",
        )
    return decision
