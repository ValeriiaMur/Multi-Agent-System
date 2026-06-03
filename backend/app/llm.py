"""LLM factory. Provider is swappable; default Anthropic.

Production code never imports a concrete model directly — call get_llm() so
tests can inject a fake chat model.
"""
from __future__ import annotations

from typing import Any

from .config import settings


def get_llm(model: str | None = None, **kwargs: Any):
    """Return a LangChain chat model for the configured provider.

    Pass ``model`` to pick a specific model (e.g. per sub-agent role); defaults to
    the global LLM_MODEL setting.
    """
    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model or settings.llm_model, **kwargs)
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
