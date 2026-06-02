# AGENTS.md — Operating instructions for coding agents

This repo is built **test-driven, red-green-refactor**, for both backend (BE)
and frontend (FE). Read this before writing any code. `PLAN.md` defines the
phases; this file defines the loop and the rules.

## The non-negotiable loop (RED → GREEN → REFACTOR)

For **every** change, in this order:

1. **RED** — Write or extend a test that expresses the desired behavior. Run it. It MUST fail, and fail for the right reason (assertion, not import/collection error). A test that passes immediately means it tests nothing new — fix the test.
2. **GREEN** — Write the *smallest* amount of production code that makes the test pass. No extra features, no speculative abstraction. Run the suite; it must be green.
3. **REFACTOR** — Clean up names, dedupe, extract helpers. Tests stay green throughout. No behavior change in this step.

Never write production code without a failing test demanding it. Never commit on RED. Never mark a task complete while any test fails.

## Workflow rules

- One behavior per cycle. Small commits: `test:` (RED) then `feat:`/`fix:` (GREEN) then `refactor:`.
- If a test is hard to write, the design is probably wrong — fix the seam before the code.
- Bugs get a failing regression test first, then the fix.
- Stretch goals follow the same loop and are only merged once core tests are green.
- Keep tests deterministic and offline by default (stub the LLM). Real-API tests are marked and opt-in.

## Backend (Python / pytest)

- Tooling: `pytest`, `pytest-asyncio`. Run: `pytest -q` from `backend/`.
- Structure mirrors source: `backend/tests/test_<module>.py`.
- **LLM is injected, never imported inline.** Tests pass a fake chat model (a `FakeListChatModel` or a stub returning canned `with_structured_output` objects) so routing/extraction are deterministic.
- Tools are pure functions with **Pydantic input schemas** — unit-test them with no LLM at all.
- Each LangGraph sub-agent is its own compiled `StateGraph`; test it in isolation before testing the composed hub.
- Mark real-provider tests `@pytest.mark.live`; they are excluded from the default run (`-m "not live"`).
- Required critical-path tests (must always exist and pass):
  - `test_router.py` — clear routes classify correctly; ambiguous inputs fall back to `CLARIFY` via low confidence.
  - `test_resilience.py` — empty `search_exercises` results recover without hallucinating; invalid tool calls are caught.

### BE red-green example

```
# RED: tests/test_tools.py
def test_search_exercises_empty_when_equipment_absent(exercises):
    out = search_exercises(SearchExercisesInput(equipment=["kettlebell-X"]), exercises)
    assert out == []          # fails: function not implemented yet

# GREEN: app/tools/search_exercises.py
def search_exercises(args, exercises):
    return [e for e in exercises if not args.equipment
            or set(args.equipment) & set(e.equipment_required)]
```

## Frontend (React + TS / vitest)

- Tooling: `vitest` + `@testing-library/react`. Run: `npm test` from `frontend/`.
- Component test files live in `frontend/tests/*.test.tsx`.
- Test behavior the user sees, not implementation details: render → query by role/text → assert.
- The backend API client is mocked in component tests (`vi.mock`); no network in unit tests.
- Required component tests: `RouteBadge` (shows route + confidence), `WorkoutCard` (renders warmup/main/cooldown with sets/reps/rest), `LogEntry` (renders parsed sets×reps@weight).

### FE red-green example

```
// RED: tests/RouteBadge.test.tsx
it("shows route and confidence", () => {
  render(<RouteBadge route="COACH" confidence={0.91} />);
  expect(screen.getByText(/COACH/)).toBeInTheDocument();
  expect(screen.getByText(/91%/)).toBeInTheDocument();   // fails: stub renders nothing
});
```

## Keep the system-design diagram current

`docs/system-design.svg` is the canonical architecture picture. Whenever a change
**materially** alters the system, review the SVG and update it in the same change:

- A new node, edge, route, or sub-agent in the hub graph.
- A new or removed service / external dependency (e.g. a datastore, queue, provider).
- A new API endpoint or a changed request/response contract the UI relies on.
- A change to a cross-cutting concern shown on the diagram (LLM provider, memory, observability).

Internal-only refactors that don't change the boxes or arrows (renames, rep-scheme
tweaks, added tests) do **not** require a diagram edit — but still glance at it to
confirm it's accurate. If you edit the SVG, keep the `<title>`/`<desc>` and the
legend in sync, and re-state the one-line summary in your response.

## Definition of done (per task)

- New behavior is covered by a test that was RED before the code existed.
- `pytest -m "not live"` and `npm test` both green.
- No fabricated data paths (e.g. agents never invent exercise IDs not in the dataset).
- Public-facing behavior demoable in the web UI or transcript.
- `docs/system-design.svg` reviewed; updated if the architecture changed materially.

## Conventions

- Python: type hints everywhere, `ruff` clean, Pydantic v2 models for all tool inputs and structured outputs.
- TS: strict mode, no `any` in component props.
- Config via env (`.env`), never hardcoded keys. `ANTHROPIC_API_KEY`, `LLM_MODEL` (default a Claude model), `LLM_PROVIDER` (default `anthropic`, swappable).
- Commit messages: conventional commits; the `test:` commit precedes its `feat:`/`fix:`.
