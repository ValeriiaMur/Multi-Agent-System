# PLAN — Fitness Coaching Multi-Agent System

Phased build plan for a LangGraph hub-and-spoke agent system. Every phase is
**test-first**: write the failing test (RED), make it pass with the smallest
change (GREEN), then refactor. See `AGENTS.md` for the loop agents must follow.

Provider: **Anthropic** (Claude via LangChain), kept swappable behind
`app/llm.py` + env config. Target: all core requirements **and** all stretch goals.

---

## Phase 0 — Scaffold & harness (foundation)

Goal: a repo that imports cleanly and runs a RED test suite.

- Repo layout (`backend/app`, `backend/tests`, `frontend/`), `pyproject.toml`, `.env.example`.
- `app/config.py` (env-driven settings), `app/llm.py` (`get_llm()` → Anthropic, swappable).
- `app/data.py` loads `data/exercises.json` (50 exercises) into typed records.
- `app/state.py` — typed `StateGraph` state (`TypedDict`): messages, route, confidence, scratch.
- pytest + vitest harnesses wired; CI-friendly. Fixtures stub the LLM so tests are deterministic and offline.

**Exit:** `pytest` collects and runs; suite is RED by design.

## Phase 1 — Router (critical path #1)

Goal: classify intent with **LLM structured output**, never regex/keywords.

- `app/hub/router.py`: `RouterDecision` Pydantic model `{route: COACH|WORKOUT_GENERATE|WORKOUT_LOG|CLARIFY, confidence: float, reason: str}` via `llm.with_structured_output(RouterDecision)`.
- Low-confidence handling is **explicit**: below threshold → `CLARIFY` route that asks the user to disambiguate.
- Tests (RED→GREEN): clear cases route correctly; ambiguous inputs ("I did a workout yesterday, can you adjust it?", "Bench press") fall back to `CLARIFY`.

**Exit:** router tests green; misroutes surface as low confidence, not silent failure.

## Phase 2 — Tools (Pydantic schemas)

Goal: two tools with described input schemas, independent of any agent.

- `app/tools/schemas.py`: `SearchExercisesInput`, `BuildWorkoutInput` — every field has a `description`.
- `search_exercises`: filter `exercises.json` by muscle groups, equipment, movement patterns.
- `build_workout`: assemble `{warmup, main, cooldown}` with sets/reps/rest from selected exercises.
- Tests: search filters correctly; empty-result case returns `[]` (no crash); build produces valid structure.

**Exit:** tool unit tests green; tools are pure and deterministic.

## Phase 3 — Sub-agent graphs (composed, not inlined)

Each sub-agent is its **own** `StateGraph`, compiled and composed into the hub.

- **Coach** (`agents/coach.py`): LLM Q&A grounded in exercise data; cites muscle groups/joints.
- **Workout Generator** (`agents/workout_generator.py`): tool-calling loop over `search_exercises` → `build_workout`.
- **Workout Logger** (`agents/workout_logger.py`): extracts `{exercise, sets, reps, weight}`, **fuzzy-matches** "bench press" → "Barbell Flat Bench Press", returns structured JSON.

**Exit:** each sub-agent graph has its own passing tests.

## Phase 4 — Hub composition (the StateGraph)

Goal: wire router + sub-agents into one graph with explicit edges.

- `app/hub/graph.py`: `StateGraph` with conditional edges from router node to each sub-agent; `CLARIFY` short-circuits to a clarify node.
- End-to-end happy-path tests per route.

**Exit:** full graph runs end-to-end for all three routes + clarify.

## Phase 5 — Resilience (critical path #2)

Goal: fail gracefully, never hallucinate.

- `search_exercises` no results (e.g. unavailable equipment) → generator recovers: tells the user, suggests alternatives, does not invent exercises.
- Invalid tool call (bad exercise ID / schema) → caught, retried or surfaced as a meaningful message.
- Tests assert recovery messaging and absence of fabricated exercise IDs.

**Exit:** resilience tests green; this is the second documented critical path.

## Phase 6 — Frontend (richer web UI)

Goal: demo-quality chat with visible internals.

- Vite + React + TS chat view; calls backend.
- Shows **route badge + confidence** per turn, **workout cards** (warmup/main/cooldown, sets/reps/rest), and **log entry** chips.
- Streaming tokens rendered live.
- vitest component tests for `RouteBadge`, `WorkoutCard`, `LogEntry` (RED→GREEN).

**Exit:** UI renders all three response shapes; component tests green.

## Phase 7 — Stretch goals (all)

- **Streaming**: FastAPI SSE endpoint + `astream` through the graph → live tokens in UI.
- **Multi-turn memory**: `app/memory.py` thread-scoped state via LangGraph checkpointer.
- **Injury avoidance**: filter on `joints_loaded`; user-supplied avoid-list excludes loaded joints.
- **Bilateral pairing**: auto-include `bilateral_pair_id` partner when an exercise `is_bilateral`.
- **Observability**: structured logging of every LLM call + tool invocation (`app/observability.py`), with optional Langfuse/OTel hook.

**Exit:** each stretch goal has at least one test and is demoed in the UI/transcript.

## Phase 8 — Docs, demo, submission

- README: setup, run, architecture diagram, "How I would evaluate this in production" (metrics, failure modes, monitoring).
- Recorded transcript + screenshots of the web view.
- Public GitHub repo, green CI.

---

## Critical paths chosen for required tests

1. **Router classification + low-confidence fallback** — the routing decision gates everything; a silent misroute is the worst failure mode.
2. **Workout-generator resilience** — tool-calling + recovery from empty results / bad tool calls is where hallucination and crashes are most likely.

## Risk / sequencing notes

- LLM is stubbed in tests (deterministic, offline); a small `@pytest.mark.live` set hits the real API.
- Tools and schemas land before agents so agent tests build on trusted primitives.
- Stretch goals are additive and gated behind passing core tests — never merged RED.
