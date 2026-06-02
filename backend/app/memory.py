"""Multi-turn conversation memory via a LangGraph checkpointer.

Compiling the hub graph with this checkpointer makes state thread-scoped: pass a
stable thread_id in the run config and the message history persists across turns.

By default this is in-process (MemorySaver), which resets on restart/redeploy.
Set CHECKPOINT_DB to a sqlite path for memory that survives Railway redeploys;
if the sqlite saver package isn't installed, it degrades gracefully to in-memory.
"""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver

from .config import settings
from .observability import log_event


def get_checkpointer():
    """Return a checkpointer for per-thread conversation memory.

    Uses a durable sqlite store when CHECKPOINT_DB is set and the saver is
    available; otherwise an in-process MemorySaver.
    """
    db = settings.checkpoint_db
    if db:
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver

            saver = SqliteSaver.from_conn_string(db)
            # Newer langgraph returns a context manager; unwrap if so.
            enter = getattr(saver, "__enter__", None)
            saver = enter() if enter else saver
            log_event("memory", "checkpointer", {"backend": "sqlite", "db": db})
            return saver
        except Exception as exc:  # package missing or bad path -> degrade
            log_event("memory", "checkpointer_fallback", {"detail": str(exc)})
    return MemorySaver()
