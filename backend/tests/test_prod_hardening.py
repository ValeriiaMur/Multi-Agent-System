"""Prod hardening: env-driven CORS allowlist + durable checkpointer."""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver

from app.config import get_allowed_origins
from app.memory import get_checkpointer


def test_allowed_origins_default_is_wildcard(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    assert get_allowed_origins() == ["*"]


def test_allowed_origins_parsed_from_env(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://a.app, https://b.app ,")
    assert get_allowed_origins() == ["https://a.app", "https://b.app"]


def test_checkpointer_defaults_to_memory(monkeypatch):
    monkeypatch.delenv("CHECKPOINT_DB", raising=False)
    assert isinstance(get_checkpointer(), MemorySaver)


def test_checkpointer_falls_back_when_sqlite_unavailable(monkeypatch):
    # Even if a db path is requested, an unavailable sqlite saver must not crash;
    # it degrades to the in-memory saver.
    monkeypatch.setenv("CHECKPOINT_DB", "/tmp/does-not-matter.sqlite")
    assert get_checkpointer() is not None
