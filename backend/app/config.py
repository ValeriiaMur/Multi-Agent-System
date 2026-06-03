"""Environment-driven settings. Keep secrets out of code."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic")
    # Haiku: fast + cheap, good enough for routing, extraction, and coaching prose.
    llm_model: str = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")
    router_confidence_threshold: float = float(
        os.getenv("ROUTER_CONFIDENCE_THRESHOLD", "0.6")
    )
    # Optional path for a durable conversation-memory store (sqlite). When unset,
    # memory is in-process only.
    checkpoint_db: str | None = os.getenv("CHECKPOINT_DB") or None


settings = Settings()


def get_allowed_origins() -> list[str]:
    """CORS allowlist from ALLOWED_ORIGINS (comma-separated). Defaults to ['*'].

    Read live (not frozen at import) so the server and tests see the current env.
    In production set it to the deployed frontend origin to lock CORS down.
    """
    raw = os.getenv("ALLOWED_ORIGINS", "*")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins or ["*"]


_ROLE_MODEL_DEFAULTS = {
    "router": "claude-sonnet-4-6",  # routing quality matters most; one short call
    "coach": "claude-haiku-4-5-20251001",
    "generator": "claude-haiku-4-5-20251001",
    "logger": "claude-haiku-4-5-20251001",
}


def get_model(role: str) -> str:
    """Model id for a sub-agent role.

    Precedence: <ROLE>_MODEL env  >  global LLM_MODEL env  >  per-role default.
    So routing defaults to a stronger model while prose/extraction stay on Haiku;
    set ROUTER_MODEL / COACH_MODEL / GENERATOR_MODEL / LOGGER_MODEL to override.
    """
    return (
        os.getenv(f"{role.upper()}_MODEL")
        or os.getenv("LLM_MODEL")
        or _ROLE_MODEL_DEFAULTS.get(role, "claude-haiku-4-5-20251001")
    )


def get_api_key() -> str | None:
    """Shared secret the frontend must send as X-API-Key. None disables the check."""
    return os.getenv("API_KEY") or None


def get_rate_limit_per_min() -> int:
    """Max /chat requests per client per minute. 0 disables limiting."""
    try:
        return int(os.getenv("RATE_LIMIT_PER_MIN", "30"))
    except ValueError:
        return 30
