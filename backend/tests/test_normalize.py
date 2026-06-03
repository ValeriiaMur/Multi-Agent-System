"""Vocab normalization + the generator's empty-result guardrails."""
from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.agents.workout_generator import GenerationSpec, build_generator_graph
from app.tools.normalize import normalize_equipment, normalize_muscles


def test_expands_group_muscle_terms():
    out = normalize_muscles(["upper body"])
    assert "chest" in out and "lats" in out and "upper body" not in out


def test_passes_through_exact_muscle_names():
    assert normalize_muscles(["chest", "GLUTES"]) == ["chest", "glutes"]


def test_canonicalizes_equipment_phrasing():
    assert normalize_equipment(["dumbbells"]) == ["Dumbbell"]
    assert normalize_equipment(["KettleBells"]) == ["Kettlebell"]


def test_drops_unknown_equipment():
    assert normalize_equipment(["kettlebell-X9000"]) == []


def test_generator_builds_for_upper_body_dumbbells(fake_llm, exercises):
    # the exact regression: "upper body" + "dumbbells" must NOT hit recovery
    llm = fake_llm(
        structured_by_type={
            GenerationSpec: GenerationSpec(muscle_groups=["upper body"], equipment=["dumbbells"])
        }
    )
    graph = build_generator_graph(llm, exercises)
    out = graph.invoke({"messages": [HumanMessage(content="30 min upper body with dumbbells")]})
    assert out["workout"] is not None
    main = out["workout"]["main"]
    assert main, "expected a non-empty main block"
    # at least one main movement actually uses a dumbbell
    by_id = {e.id: e for e in exercises}
    assert any("Dumbbell" in by_id[it["exercise_id"]].equipment_required for it in main)
