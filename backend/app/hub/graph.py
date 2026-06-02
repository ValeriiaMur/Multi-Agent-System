"""Hub StateGraph composing the router and sub-agent graphs."""
from __future__ import annotations

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from .._util import last_human_text
from ..agents.coach import build_coach_graph
from ..agents.workout_generator import build_generator_graph
from ..agents.workout_logger import build_logger_graph
from ..observability import log_event
from ..state import HubState
from .router import route_message

CLARIFY_TEXT = (
    "I'm not sure what you'd like — are you asking a training question, want me to "
    "build a workout, or logging one you already did? A little more detail helps."
)


def build_hub_graph(llm, exercises=None, checkpointer=None):
    """Return the compiled hub StateGraph.

    Router node sets the route; conditional edges dispatch to the coach, generator,
    or logger sub-graphs (each composed as a node, not inlined). Low-confidence
    routing short-circuits to a CLARIFY node.
    """
    coach = build_coach_graph(llm, exercises)
    generator = build_generator_graph(llm, exercises)
    logger = build_logger_graph(llm, exercises)

    def router(state: HubState) -> dict:
        decision = route_message(last_human_text(state["messages"]), llm)
        log_event("router", "route", {"route": decision.route, "confidence": decision.confidence})
        return {
            "route": decision.route,
            "confidence": decision.confidence,
            "reason": decision.reason,
        }

    def clarify(state: HubState) -> dict:
        return {"messages": [AIMessage(content=CLARIFY_TEXT)]}

    def pick(state: HubState) -> str:
        return state["route"]

    g = StateGraph(HubState)
    g.add_node("router", router)
    g.add_node("COACH", coach)
    g.add_node("WORKOUT_GENERATE", generator)
    g.add_node("WORKOUT_LOG", logger)
    g.add_node("CLARIFY", clarify)

    g.add_edge(START, "router")
    g.add_conditional_edges(
        "router",
        pick,
        {
            "COACH": "COACH",
            "WORKOUT_GENERATE": "WORKOUT_GENERATE",
            "WORKOUT_LOG": "WORKOUT_LOG",
            "CLARIFY": "CLARIFY",
        },
    )
    for node in ("COACH", "WORKOUT_GENERATE", "WORKOUT_LOG", "CLARIFY"):
        g.add_edge(node, END)

    return g.compile(checkpointer=checkpointer)
