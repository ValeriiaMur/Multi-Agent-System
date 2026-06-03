"""Shared fixtures. LLM is faked so tests are deterministic and offline."""
from __future__ import annotations

import os

# Force the suite fully offline regardless of the developer's .env. Without this,
# a real LANGSMITH_TRACING=true / API key makes LangChain & LangGraph ship every
# run to api.smith.langchain.com — slow, non-deterministic, leaks trace data, and
# spams errors when the network is blocked. Must run before any langchain import.
for _var in ("LANGSMITH_TRACING", "LANGCHAIN_TRACING_V2"):
    os.environ[_var] = "false"
for _var in ("LANGSMITH_API_KEY", "LANGCHAIN_API_KEY", "LANGCHAIN_ENDPOINT"):
    os.environ.pop(_var, None)

import pytest

from app.data import load_exercises


@pytest.fixture
def exercises():
    return load_exercises()


class FakeStructuredLLM:
    """Stands in for llm.with_structured_output(Model): returns a canned object."""

    def __init__(self, result):
        self._result = result

    def invoke(self, _input):
        return self._result


class FakeLLM:
    """Minimal chat-model double. Configure structured/responses per test.

    - structured_result: returned for any with_structured_output() call.
    - structured_by_type: optional {Model: result} so one fake can serve the
      router (RouterDecision), generator (GenerationSpec), and logger (RawLog).
    """

    def __init__(self, structured_result=None, structured_by_type=None, text="ok"):
        self._structured_result = structured_result
        self._by_type = structured_by_type or {}
        self._text = text

    def with_structured_output(self, model):
        if model in self._by_type:
            return FakeStructuredLLM(self._by_type[model])
        return FakeStructuredLLM(self._structured_result)

    def bind_tools(self, _tools):
        return self

    def invoke(self, _input):
        from langchain_core.messages import AIMessage

        return AIMessage(content=self._text)


@pytest.fixture
def fake_llm():
    return FakeLLM
