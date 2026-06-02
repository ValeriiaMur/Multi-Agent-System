"""LLM structured-output router. STUB — implement in Phase 1 (GREEN).

Routing MUST use llm.with_structured_output(RouterDecision), never regex or
keyword matching. Low confidence -> CLARIFY.
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
    "- COACH: questions about training, technique, anatomy, programming advice.\n"
    "- WORKOUT_GENERATE: requests to build/create/design a workout or session.\n"
    "- WORKOUT_LOG: the user reporting a workout they already performed.\n"
    "- CLARIFY: intent is ambiguous or underspecified.\n"
    "Return your confidence in [0,1]. If you are not clearly confident, say so "
    "with a low score rather than guessing."
)


def route_message(text: str, llm) -> RouterDecision:
    """Classify intent via structured output, applying the confidence threshold.

    Uses llm.with_structured_output(RouterDecision) — never regex/keywords. If the
    model's confidence is below settings.router_confidence_threshold, the effective
    route becomes CLARIFY so the system never silently misroutes.
    """
    structured = llm.with_structured_output(RouterDecision)
    decision = structured.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", text),
        ]
    )
    if decision.confidence < settings.router_confidence_threshold:
        return RouterDecision(
            route="CLARIFY",
            confidence=decision.confidence,
            reason=f"low confidence ({decision.confidence:.2f}): {decision.reason}",
        )
    return decision
