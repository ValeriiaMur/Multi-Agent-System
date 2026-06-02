"""Observability: structured logging + LangSmith-aware tracing decorator."""
from __future__ import annotations

import json

from app.observability import log_event, traced, tracing_enabled


def test_log_event_emits_json_line(capsys):
    log_event("tool", "search_exercises", {"n": 3})
    line = capsys.readouterr().out.strip()
    record = json.loads(line)
    assert record["kind"] == "tool"
    assert record["name"] == "search_exercises"
    assert record["n"] == 3


def test_traced_preserves_function_output():
    @traced(run_type="tool", name="adder")
    def add(a, b):
        return a + b

    # Whether or not langsmith is installed, behavior is unchanged.
    assert add(2, 3) == 5
    assert add.__name__ in ("add", "adder")  # passthrough keeps name; traceable sets it


def test_tracing_enabled_reads_env(monkeypatch):
    monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
    assert tracing_enabled() is False
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    assert tracing_enabled() is True
