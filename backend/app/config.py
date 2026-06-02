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
    """
    raw = os.getenv("ALLOWED_ORIGINS", "*")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins or ["*"]
