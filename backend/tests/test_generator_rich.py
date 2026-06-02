"""Coverage for the enriched generator output the UI depends on."""
from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.agents.workout_generator import GenerationSpec, build_generator_graph


def _run(fake_llm, exercises, spec):
    graph = build_generator_graph(fake_llm(structured_by_type={GenerationSpec: spec}), exercises)
    return graph.invoke({"messages": [HumanMessage(content="build me a session")]})


def test_main_items_are_enriched(fake_llm, exercises):
    out = _run(fake_llm, exercises, GenerationSpec(muscle_groups=["chest"]))
    item = out["workout"]["main"][0]
    for key in ("exercise_id", "name", "prescription", "rest", "muscle_groups", "is_bilateral"):
        assert key in item
    assert isinstance(item["muscle_groups"], list)


def test_meta_block_present(fake_llm, exercises):
    out = _run(fake_llm, exercises, GenerationSpec(muscle_groups=["chest"], goal="power"))
    meta = out["workout"]["meta"]
    assert meta["goal"] == "power"
    assert meta["empty"] is False


def test_warmup_and_cooldown_populated(fake_llm, exercises):
    out = _run(fake_llm, exercises, GenerationSpec(muscle_groups=["chest"]))
    assert out["workout"]["warmup"], "expected at least one warmup item"
    assert out["workout"]["cooldown"], "expected at least one cooldown item"


def test_goal_rep_scheme_applied(fake_llm, exercises):
    out = _run(fake_llm, exercises, GenerationSpec(muscle_groups=["chest"], goal="power"))
    main = out["workout"]["main"][0]
    assert (main["sets"], main["reps"]) == (5, 5)  # power scheme


def test_main_size_scales_with_duration(fake_llm, exercises):
    short = _run(fake_llm, exercises, GenerationSpec(duration_minutes=12))
    long = _run(fake_llm, exercises, GenerationSpec(duration_minutes=60))
    assert len(short["workout"]["main"]) < len(long["workout"]["main"])
