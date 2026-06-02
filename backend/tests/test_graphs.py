"""Phase 3/4: sub-agent graphs + hub composition (FakeLLM, offline)."""
from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.coach import build_coach_graph
from app.agents.workout_generator import GenerationSpec, build_generator_graph
from app.agents.workout_logger import RawEntry, RawLog, build_logger_graph
from app.hub.graph import build_hub_graph
from app.hub.router import RouterDecision


def _ai_texts(state):
    return " ".join(m.content for m in state["messages"] if isinstance(m, AIMessage)).lower()


def test_coach_graph_answers(fake_llm, exercises):
    llm = fake_llm(text="The deadlift trains glutes, hamstrings and back.")
    graph = build_coach_graph(llm, exercises)
    out = graph.invoke({"messages": [HumanMessage(content="what does a deadlift work?")]})
    assert "deadlift" in _ai_texts(out)


def test_generator_graph_produces_workout(fake_llm, exercises):
    llm = fake_llm(structured_by_type={GenerationSpec: GenerationSpec(muscle_groups=["chest"])})
    graph = build_generator_graph(llm, exercises)
    out = graph.invoke({"messages": [HumanMessage(content="build me a chest day")]})
    assert out["workout"] and out["workout"]["main"]


def test_generator_recovers_on_no_results(fake_llm, exercises):
    llm = fake_llm(structured_by_type={GenerationSpec: GenerationSpec(equipment=["kettlebell-X9000"])})
    graph = build_generator_graph(llm, exercises)
    out = graph.invoke({"messages": [HumanMessage(content="kettlebell session")]})
    assert out["workout"] is None
    assert "couldn't" in _ai_texts(out) or "broaden" in _ai_texts(out)


def test_generator_respects_avoid_joints(fake_llm, exercises):
    llm = fake_llm(structured_by_type={GenerationSpec: GenerationSpec(avoid_joints=["shoulder"])})
    graph = build_generator_graph(llm, exercises)
    out = graph.invoke({"messages": [HumanMessage(content="full body, bad shoulder")]})
    ids = {it["exercise_id"] for it in out["workout"]["main"]}
    loaded = {e.id for e in exercises if "shoulder" in e.joints_loaded}
    assert ids.isdisjoint(loaded)


def test_logger_graph_extracts_and_matches(fake_llm, exercises):
    llm = fake_llm(
        structured_by_type={RawLog: RawLog(entries=[RawEntry(exercise="bench press", sets=3, reps=10, weight=185)])}
    )
    graph = build_logger_graph(llm, exercises)
    out = graph.invoke({"messages": [HumanMessage(content="did 3x10 bench at 185")]})
    entry = out["log_entries"][0]
    assert entry["matched"] and "bench" in entry["exercise"].lower()
    assert entry["weight"] == 185


def test_hub_routes_to_generate(fake_llm, exercises):
    llm = fake_llm(
        structured_by_type={
            RouterDecision: RouterDecision(route="WORKOUT_GENERATE", confidence=0.95, reason="build"),
            GenerationSpec: GenerationSpec(muscle_groups=["chest"]),
        }
    )
    graph = build_hub_graph(llm, exercises)
    out = graph.invoke({"messages": [HumanMessage(content="build me a chest workout")]})
    assert out["route"] == "WORKOUT_GENERATE"
    assert out["workout"]["main"]


def test_hub_clarifies_on_low_confidence(fake_llm, exercises):
    llm = fake_llm(
        structured_by_type={RouterDecision: RouterDecision(route="WORKOUT_LOG", confidence=0.2, reason="ambiguous")}
    )
    graph = build_hub_graph(llm, exercises)
    out = graph.invoke({"messages": [HumanMessage(content="bench press")]})
    assert out["route"] == "CLARIFY"
    assert "not sure" in _ai_texts(out)
