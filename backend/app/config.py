"""Environment-driven settings. Keep secrets out of code."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic")
    llm_model: str = os.getenv("LLM_MODEL", "claude-3-5-sonnet-latest")
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


def get_api_key() -> str | None:
    """Shared secret the frontend must send as X-API-Key. None disables the check."""
    return os.getenv("API_KEY") or None


def get_rate_limit_per_min() -> int:
    """Max /chat requests per client per minute. 0 disables limiting."""
    try:
        return int(os.getenv("RATE_LIMIT_PER_MIN", "30"))
    except ValueError:
        return 30
