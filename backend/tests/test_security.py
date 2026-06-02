"""Unit tests for the public-endpoint hardening helpers (offline, no network)."""
from __future__ import annotations

from app.security import RateLimiter, api_key_ok


def test_api_key_disabled_when_unset(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    assert api_key_ok(None) is True
    assert api_key_ok("anything") is True


def test_api_key_enforced_when_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "s3cret")
    assert api_key_ok("s3cret") is True
    assert api_key_ok("wrong") is False
    assert api_key_ok(None) is False


def test_rate_limiter_blocks_over_limit():
    rl = RateLimiter(window_seconds=60)
    # 3 allowed within the window, 4th blocked (same simulated clock)
    assert [rl.allow("ip", limit=3, now=0.0) for _ in range(4)] == [True, True, True, False]


def test_rate_limiter_recovers_after_window():
    rl = RateLimiter(window_seconds=60)
    assert rl.allow("ip", limit=1, now=0.0) is True
    assert rl.allow("ip", limit=1, now=10.0) is False  # still inside window
    assert rl.allow("ip", limit=1, now=61.0) is True   # window elapsed


def test_rate_limiter_is_per_key():
    rl = RateLimiter(window_seconds=60)
    assert rl.allow("a", limit=1, now=0.0) is True
    assert rl.allow("b", limit=1, now=0.0) is True  # different client unaffected
    assert rl.allow("a", limit=1, now=0.0) is False
