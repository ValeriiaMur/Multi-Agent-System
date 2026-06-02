"""Live demo: run all three routes through the hub against the real model.

Usage (from backend/):
    export ANTHROPIC_API_KEY=sk-ant-...
    # optional: enable LangSmith tracing
    export LANGCHAIN_TRACING_V2=true LANGCHAIN_API_KEY=lsv2_... LANGCHAIN_PROJECT=fitness-coach-agents
    python -m scripts.demo

Prints the route, confidence, reply and any structured workout / log payload for
each example. With tracing enabled, the full trace tree (router -> sub-agent ->
tool spans) shows up in your LangSmith project.
"""
from __future__ import annotations

import json

from langchain_core.messages import HumanMessage

from app.hub.graph import build_hub_graph
from app.llm import get_llm
from app.memory import get_checkpointer
from app.shaping import shape_response

EXAMPLES = [
    "What muscles does a deadlift work?",
    "Build me a 30 min upper body session with dumbbells",
    "I just did 3x10 bench press at 185 lbs",
    "I did a workout yesterday, can you adjust it?",  # ambiguous -> CLARIFY
]


def main() -> None:
    graph = build_hub_graph(get_llm(), checkpointer=get_checkpointer())
    for i, msg in enumerate(EXAMPLES, start=1):
        state = graph.invoke(
            {"messages": [HumanMessage(content=msg)]},
            {"configurable": {"thread_id": f"demo-{i}"}},
        )
        out = shape_response(state)
        print("=" * 72)
        print(f"USER: {msg}")
        print(f"ROUTE: {out['route']}  (confidence={out['confidence']})")
        print(f"REPLY: {out['reply']}")
        if out["workout"]:
            print("WORKOUT:", json.dumps(out["workout"], indent=2, default=str))
        if out["log_entries"]:
            print("LOG:", json.dumps(out["log_entries"], indent=2, default=str))


if __name__ == "__main__":
    main()
