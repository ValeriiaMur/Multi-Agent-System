"""Phase 7: multi-turn memory via checkpointer (offline, FakeLLM)."""
from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.hub.graph import build_hub_graph
from app.hub.router import RouterDecision
from app.memory import get_checkpointer


def test_thread_memory_accumulates_turns(fake_llm, exercises):
    llm = fake_llm(
        structured_by_type={RouterDecision: RouterDecision(route="COACH", confidence=0.9, reason="q")},
        text="Sure — happy to help.",
    )
    graph = build_hub_graph(llm, exercises, checkpointer=get_checkpointer())
    cfg = {"configurable": {"thread_id": "user-42"}}

    graph.invoke({"messages": [HumanMessage(content="what works the chest?")]}, cfg)
    state = graph.invoke({"messages": [HumanMessage(content="and the back?")]}, cfg)

    humans = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    assert len(humans) == 2  # second turn sees the first -> memory persisted


def test_separate_threads_are_isolated(fake_llm, exercises):
    llm = fake_llm(
        structured_by_type={RouterDecision: RouterDecision(route="COACH", confidence=0.9, reason="q")},
        text="ok",
    )
    graph = build_hub_graph(llm, exercises, checkpointer=get_checkpointer())
    graph.invoke({"messages": [HumanMessage(content="turn A")]}, {"configurable": {"thread_id": "a"}})
    state_b = graph.invoke(
        {"messages": [HumanMessage(content="turn B")]}, {"configurable": {"thread_id": "b"}}
    )
    humans_b = [m for m in state_b["messages"] if isinstance(m, HumanMessage)]
    assert len(humans_b) == 1  # thread b unaffected by thread a
