"""Structured logging / tracing for LLM and tool calls. STUB — Phase 7 stretch."""
from __future__ import annotations

import json
import sys
import time
from typing import Any


def log_event(kind: str, name: str, payload: dict[str, Any]) -> None:
    """Emit a structured trace event (LLM call or tool invocation) as a JSON line.

    Keeps a single, parseable log format that an exporter (Langfuse/OTel) can tail.
    """
    record = {"ts": round(time.time(), 3), "kind": kind, "name": name, **payload}
    sys.stdout.write(json.dumps(record) + "\n")
