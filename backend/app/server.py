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
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .shaping import shape_response

app = FastAPI(title="Fitness Coach Agents")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    avoid_joints: list[str] = []


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
    state = get_graph().invoke(
        {"messages": [HumanMessage(content=req.message)], "avoid_joints": req.avoid_joints},
        _config(req.thread_id),
    )
    return shape_response(state)


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
