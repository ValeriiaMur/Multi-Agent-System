"""Coverage for the `reason` field and the feedback no-op path."""
from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from app.hub.graph import build_hub_graph
from app.hub.router import RouterDecision
from app.observability import submit_feedback
from app.shaping import shape_response


def test_reason_propagates_through_hub_and_shaping(fake_llm, exercises):
    llm = fake_llm(
        structured_by_type={
            RouterDecision: RouterDecision(route="COACH", confidence=0.9, reason="info question")
        },
        text="Deadlifts train the posterior chain.",
    )
    state = build_hub_graph(llm, exercises).invoke(
        {"messages": [HumanMessage(content="what does a deadlift work?")]}
    )
    assert state["reason"] == "info question"
    assert shape_response(state)["reason"] == "info question"


def test_shape_response_includes_reason_field():
    out = shape_response({"messages": [AIMessage(content="hi")], "reason": "ambiguous"})
    assert out["reason"] == "ambiguous"


def test_submit_feedback_is_noop_without_run_id():
    # No run id -> nothing to attach feedback to -> returns False, never raises.
    assert submit_feedback("", 1.0) is False
