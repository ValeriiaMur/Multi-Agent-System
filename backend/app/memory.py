"""Multi-turn conversation memory via a LangGraph checkpointer.

Compiling the hub graph with this checkpointer makes state thread-scoped: pass a
stable thread_id in the run config and the message history persists across turns.
"""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer():
    """Return an in-process checkpointer for per-thread conversation memory.

    Swap for SqliteSaver/PostgresSaver in production for durable history.
    """
    return MemorySaver()
