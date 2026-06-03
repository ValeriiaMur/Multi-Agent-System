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

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage
from langchain_core.tracers.context import collect_runs
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .config import get_allowed_origins
from .observability import log_event, submit_feedback
from .security import rate_limit, require_api_key
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


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    """Log the traceback and surface the error type so a 500 isn't opaque.

    Auth (401) and rate-limit (429) are HTTPExceptions handled separately, so
    they aren't swallowed here. The common cause of a /chat error is a missing
    ANTHROPIC_API_KEY on the backend.
    """
    log_event("error", "unhandled", {"path": request.url.path, "type": type(exc).__name__, "detail": str(exc)})
    return JSONResponse(status_code=502, content={"error": type(exc).__name__, "detail": str(exc)})


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


@app.post("/chat", dependencies=[Depends(require_api_key), Depends(rate_limit)])
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


@app.post("/feedback", dependencies=[Depends(require_api_key), Depends(rate_limit)])
def feedback(req: FeedbackRequest):
    """Forward a thumbs up/down to LangSmith as run feedback (no-op if disabled)."""
    sent = submit_feedback(req.run_id, req.score, req.comment)
    return {"ok": sent}


def _chunk_text(chunk: Any) -> str:
    """Extract plain text from an LLM stream chunk (str or Anthropic blocks)."""
    content = getattr(chunk, "content", "") if chunk else ""
    if isinstance(content, list):  # Anthropic returns a list of content blocks
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return content or ""


@app.get("/chat/stream", dependencies=[Depends(require_api_key), Depends(rate_limit)])
async def chat_stream(message: str, thread_id: str | None = None):
    """Server-Sent Events: `meta` (routing decision) → `token`* (prose deltas) →
    `final` (full shaped payload + run_id). Tokens are filtered to the answering
    node so the router's structured-output tokens never leak into the text."""
    graph = get_graph()

    async def gen():
        final: dict[str, Any] = {}
        try:
            async for ev in graph.astream_events(
                {"messages": [HumanMessage(content=message)]},
                _config(thread_id),
                version="v2",
            ):
                kind = ev.get("event")
                if kind == "on_chain_end" and ev.get("name") == "router":
                    out = ev.get("data", {}).get("output") or {}
                    yield {
                        "event": "meta",
                        "data": json.dumps(
                            {
                                "route": out.get("route"),
                                "confidence": out.get("confidence"),
                                "reason": out.get("reason"),
                            }
                        ),
                    }
                elif kind == "on_chat_model_stream":
                    node = (ev.get("metadata") or {}).get("langgraph_node")
                    if node == "router":
                        continue  # never stream classification tokens
                    token = _chunk_text(ev.get("data", {}).get("chunk"))
                    if token:
                        yield {"event": "token", "data": token}
                elif kind == "on_chain_end" and ev.get("name") == "LangGraph":
                    final = shape_response(ev.get("data", {}).get("output") or {})
                    final["run_id"] = str(ev.get("run_id")) if ev.get("run_id") else None
        except Exception as exc:  # surface to the client instead of a silent hang
            log_event("error", "stream", {"detail": str(exc)})
            yield {"event": "stream_error", "data": json.dumps({"detail": str(exc)})}
            return
        yield {"event": "final", "data": json.dumps(final)}

    return EventSourceResponse(gen())
