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
    """True when LangSmith tracing is switched on via env."""
    return os.getenv("LANGCHAIN_TRACING_V2", "").lower() in ("1", "true", "yes")


def log_event(kind: str, name: str, payload: dict[str, Any]) -> None:
    """Emit a structured trace event (LLM call or tool invocation) as a JSON line."""
    record = {"ts": round(time.time(), 3), "kind": kind, "name": name, **payload}
    sys.stdout.write(json.dumps(record, default=str) + "\n")


def traced(run_type: str = "tool", name: str | None = None) -> Callable[[F], F]:
    """Decorator: register the function as a LangSmith span when available.

    No-op passthrough when langsmith is not installed.
    """

    def decorator(fn: F) -> F:
        if _HAS_LANGSMITH:
            return _ls_traceable(run_type=run_type, name=name or fn.__name__)(fn)
        return fn

    return decorator
