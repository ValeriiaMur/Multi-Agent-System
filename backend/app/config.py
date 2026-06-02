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


settings = Settings()
