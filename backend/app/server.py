"""FastAPI app: chat + streaming (SSE), with thread-scoped memory.

Endpoints:
  POST /chat        -> {route, confidence, reply, workout?, log_entries?}
  GET  /chat/stream -> Server-Sent Events: token deltas then a final payload

The hub graph is built lazily so importing this module never requires an API key.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tracers.context import collect_runs
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .config import get_allowed_origins
from .observability import submit_feedback
from .shaping import shape_response

app = FastAPI(title="Fitness Coach Agents")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    """Liveness probe for Railway's healthcheck."""
    return {"status": "ok"}


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    avoid_joints: list[str] = []


class FeedbackRequest(BaseModel):
    run_id: str
    score: float  # 1 = 👍, 0 = 👎
    comment: str | None = None


@lru_cache(maxsize=1)
def get_graph():
    from .hub.graph import build_hub_graph
    from .llm import get_llm
    from .memory import get_checkpointer

    return build_hub_graph(get_llm(), checkpointer=get_checkpointer())


def _config(thread_id: str | None) -> dict:
    return {"configurable": {"thread_id": thread_id or "default"}}


@app.post("/chat")
def chat(req: ChatRequest):
    # collect_runs captures the same run id the LangSmith tracer reports, so the
    # UI can later attach 👍/👎 feedback to this exact trace.
    with collect_runs() as cb:
        state = get_graph().invoke(
            {"messages": [HumanMessage(content=req.message)], "avoid_joints": req.avoid_joints},
            _config(req.thread_id),
        )
    out = shape_response(state)
    out["run_id"] = str(cb.traced_runs[0].id) if cb.traced_runs else None
    return out


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    """Forward a thumbs up/down to LangSmith as run feedback (no-op if disabled)."""
    sent = submit_feedback(req.run_id, req.score, req.comment)
    return {"ok": sent}


@app.get("/chat/stream")
async def chat_stream(message: str, thread_id: str | None = None):
    graph = get_graph()

    async def gen():
        final: dict[str, Any] = {}
        async for kind, payload in graph.astream_events(
            {"messages": [HumanMessage(content=message)]},
            _config(thread_id),
            version="v2",
        ):
            if kind == "on_chat_model_stream":
                token = getattr(payload["data"]["chunk"], "content", "")
                if token:
                    yield {"event": "token", "data": token}
            elif kind == "on_chain_end" and payload.get("name") == "LangGraph":
                final = shape_response(payload["data"]["output"])
        yield {"event": "final", "data": json.dumps(final)}

    return EventSourceResponse(gen())
