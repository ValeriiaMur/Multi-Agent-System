"""Phase 6: API response shaping (no FastAPI import needed)."""
from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from app.shaping import shape_response


def test_shape_picks_last_ai_reply_and_fields():
    state = {
        "messages": [HumanMessage(content="hi"), AIMessage(content="here you go")],
        "route": "WORKOUT_GENERATE",
        "confidence": 0.88,
        "workout": {"main": [{"name": "Squat"}]},
        "log_entries": None,
    }
    out = shape_response(state)
    assert out["reply"] == "here you go"
    assert out["route"] == "WORKOUT_GENERATE"
    assert out["confidence"] == 0.88
    assert out["workout"]["main"][0]["name"] == "Squat"


def test_shape_handles_empty_state():
    out = shape_response({})
    assert out["reply"] == ""
    assert out["route"] is None
