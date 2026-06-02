"""LLM factory. Provider is swappable; default Anthropic.

Production code never imports a concrete model directly — call get_llm() so
tests can inject a fake chat model.
"""
from __future__ import annotations

from typing import Any

from .config import settings


def get_llm(**kwargs: Any):
    """Return a LangChain chat model for the configured provider."""
    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=settings.llm_model, **kwargs)
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
