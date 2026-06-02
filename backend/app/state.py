"""Typed state for the hub StateGraph."""
from __future__ import annotations

from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph.message import add_messages

Route = Literal["COACH", "WORKOUT_GENERATE", "WORKOUT_LOG", "CLARIFY"]


class HubState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    route: Route
    confidence: float
    reason: str
    # sub-agent outputs
    workout: dict[str, Any] | None
    log_entries: list[dict[str, Any]] | None
    # stretch: user constraints
    avoid_joints: list[str]
