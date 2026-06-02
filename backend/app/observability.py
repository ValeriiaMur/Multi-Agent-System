"""Observability: structured local logging + LangSmith-aware tracing.

Two layers:
- log_event(): always-on structured JSON lines (offline, greppable, cheap).
- traced(): wraps plain functions (our tools) as LangSmith spans when the
  langsmith package is available, so tool invocations appear nested under each
  graph node in the trace tree. When langsmith is absent it is a no-op, keeping
  tests offline and deterministic.

LangChain/LangGraph already trace LLM calls and graph nodes automatically when
LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY are set — this module adds the
tool-level spans that aren't captured otherwise.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

try:  # optional dependency
    from langsmith import traceable as _ls_traceable

    _HAS_LANGSMITH = True
except Exception:  # pragma: no cover - exercised only when langsmith absent
    _HAS_LANGSMITH = False


def tracing_enabled() -> bool:
    """True when LangSmith tracing is switched on via env.

    Honors both the modern LANGSMITH_TRACING and the legacy LANGCHAIN_TRACING_V2,
    matching what the LangChain/LangSmith SDK itself reads.
    """
    flags = (os.getenv("LANGSMITH_TRACING"), os.getenv("LANGCHAIN_TRACING_V2"))
    return any((f or "").lower() in ("1", "true", "yes") for f in flags)


def log_event(kind: str, name: str, payload: dict[str, Any]) -> None:
    """Emit a structured trace event (LLM call or tool invocation) as a JSON line."""
    record = {"ts": round(time.time(), 3), "kind": kind, "name": name, **payload}
    sys.stdout.write(json.dumps(record, default=str) + "\n")


def submit_feedback(
    run_id: str, score: float, comment: str | None = None, key: str = "user_score"
) -> bool:
    """Attach a thumbs up/down to a LangSmith run so it shows up in traces.

    Returns True if the feedback was sent. No-op (returns False) when langsmith is
    not installed or the run id is missing, so the UI degrades gracefully offline.
    """
    if not _HAS_LANGSMITH or not run_id:
        log_event("feedback", "skipped", {"run_id": run_id, "score": score})
        return False
    try:
        from langsmith import Client

        Client().create_feedback(run_id, key=key, score=score, comment=comment)
        log_event("feedback", "sent", {"run_id": run_id, "score": score})
        return True
    except Exception as exc:  # pragma: no cover - network/auth failures
        log_event("error", "feedback", {"detail": str(exc)})
        return False


def traced(run_type: str = "tool", name: str | None = None) -> Callable[[F], F]:
    """Decorator: register the function as a LangSmith span when available.

    No-op passthrough when langsmith is not installed.
    """

    def decorator(fn: F) -> F:
        if _HAS_LANGSMITH:
            return _ls_traceable(run_type=run_type, name=name or fn.__name__)(fn)
        return fn

    return decorator
