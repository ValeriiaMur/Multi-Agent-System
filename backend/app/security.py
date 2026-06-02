"""Lightweight public-endpoint hardening: shared-secret key + per-IP rate limit.

Both are env-driven and disabled by default, so local dev and the offline test
suite keep working without configuration. Enable in production via API_KEY and
RATE_LIMIT_PER_MIN. The rate limiter is in-process (per replica) — fine for a
single instance / demo; use a shared store (Redis) if you scale horizontally.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request, status

from .config import get_api_key, get_rate_limit_per_min


def api_key_ok(provided: str | None) -> bool:
    """True if the key check is disabled or the provided key matches."""
    expected = get_api_key()
    return expected is None or provided == expected


def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """FastAPI dependency: enforce the shared secret when API_KEY is set.

    Accepts the key from the X-API-Key header or an ?api_key= query param (the
    latter so the EventSource stream, which can't set headers, can authenticate).
    """
    provided = x_api_key or request.query_params.get("api_key")
    if not api_key_ok(provided):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")


class RateLimiter:
    """Fixed-window-ish per-key limiter over a sliding `window` of seconds."""

    def __init__(self, window_seconds: float = 60.0) -> None:
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        dq = self._hits[key]
        cutoff = now - self.window
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= limit:
            return False
        dq.append(now)
        return True


_limiter = RateLimiter()


def _client_ip(request: Request) -> str:
    """Real client IP. Behind a proxy (Railway) prefer the first X-Forwarded-For
    hop; fall back to the socket peer."""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(request: Request) -> None:
    """FastAPI dependency: 429 when a client exceeds RATE_LIMIT_PER_MIN."""
    limit = get_rate_limit_per_min()
    if limit <= 0:
        return  # disabled
    if not _limiter.allow(_client_ip(request), limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="rate limit exceeded; please slow down",
        )
