# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A tutorial project: students build a Streamlit e-commerce sales dashboard while
practicing an agentic development workflow (PRD → `TASKS.md` → Superpowers
`brainstorming`/`writing-plans`/`executing-plans` → code → commit → push →
review → deploy). The dashboard itself (`app.py`, `metrics.py`) is the
artifact of that workflow, not the point of the repo — see `README.md` for
the full tutorial narrative and `prd/ecommerce-analytics.md` for the product
requirements the code must satisfy.

## Commands

```bash
# Activate the environment (plain venv — no uv, no conda)
source venv/bin/activate

# Run the app
streamlit run app.py

# Run the full test suite
pytest tests/test_metrics.py -v

# Run a single test
pytest tests/test_metrics.py::test_total_sales_sums_total_amount_column -v
```

`requirements.txt` is generated with `pip freeze` — after installing a new
package, regenerate it (`pip install <pkg> && pip freeze > requirements.txt`)
rather than hand-editing it.

## Architecture

- **`app.py`** is a thin Streamlit UI layer only: page config, layout, and
  calls into `metrics.py`. It holds no calculation logic — every number
  shown in the dashboard must be independently testable without running
  Streamlit.
- **`metrics.py`** holds all data loading and aggregation as plain functions
  over a single `pd.DataFrame` shape (the `sales-data.csv` schema: `date,
  order_id, product, category, region, quantity, unit_price, total_amount`).
  `load_sales_data()` is the only function decorated with `@st.cache_data`
  (it's the only one doing I/O); aggregation functions are intentionally
  *not* cached — cheap enough on this data volume that caching would add
  complexity without benefit. Keep new aggregations in this same module
  rather than splitting loading vs. aggregation into separate files — the
  project is small enough that splitting further adds navigation overhead
  without improving clarity.
- **`tests/test_metrics.py`** tests only `metrics.py`, not the Streamlit UI.
  Most tests use small, hand-built DataFrames (4-6 rows) with expected
  totals computed by hand — keeps tests fast and independent of the real
  dataset changing. One integration-style test loads the real
  `data/sales-data.csv` and checks against the PRD's expected output
  (482 orders, ~$116,500) to catch drift. `conftest.py` is an intentionally
  empty root-level file — pytest's default import mode scopes `sys.path` to
  `tests/`, so a root `conftest.py` is what makes `from metrics import ...`
  resolve during collection.
- **Error handling is minimal by design**: no try/except around the CSV
  load, no defensive schema validation. The data source is a single known
  file for a workshop project, not a user-facing upload, so pandas raising
  and Streamlit showing its default traceback is the intended behavior —
  don't add defensive validation here.

## Lessons

Rules distilled from past task notes in `TASKS.md` — check these before
re-deriving the same fix:

- Assert summed `total_amount` values with `pytest.approx()`, never `==`.
  Exact-equality float assertions have failed twice on rounding artifacts
  (e.g. `829.8600000000001 != 829.86`, `139.92000000000002 != 139.92`) —
  treat this as the default for any new test that sums currency, not a
  one-off fix. (TASK-3, TASK-5)
- Don't delete or "clean up" the empty root-level `conftest.py`. Without it,
  `from metrics import ...` fails in `tests/` with `ModuleNotFoundError`,
  because pytest's default import mode scopes `sys.path` to `tests/` (no
  `__init__.py` there). (TASK-2)
- If `streamlit run app.py` exits 255 on a fresh machine, it's Streamlit's
  interactive first-run "enter your email" onboarding prompt blocking a
  non-interactive shell — fix it at the machine level (an empty
  `~/.streamlit/credentials.toml`), not with a code or repo change. (TASK-1)
- If a session has no connected browser, say so explicitly rather than
  claiming a UI/layout acceptance criterion was visually verified — confirm
  what's actually checkable (terminal output, HTTP health checks) and note
  the gap instead. (TASK-6)

## Workflow conventions specific to this repo

- Work happens on `feature/sales-dashboard` (no per-task worktrees).
- `TASKS.md` is the milestone board (`TASK-1` … `TASK-7`, moved through To
  Do → In Progress → Done). Its own "Definition of Done" requires: all
  acceptance criteria checked off, `streamlit run app.py` runs with no
  errors/warnings, and commits reference the milestone ID.
- Every commit message is prefixed with its milestone ID (e.g. `TASK-3:
  Add Total Sales and Total Orders KPI cards`). Moving a task between board
  states is its own commit (e.g. `TASK-6: Move to In Progress`), separate
  from the commit(s) that do the actual implementation.
- The implementation plan and design doc live in
  `docs/superpowers/plans/` and `docs/superpowers/specs/` — check these for
  the reasoning behind existing architecture choices before changing them.
- `TASK-7` (deployment to Streamlit Community Cloud) is executed manually
  by the user after merging to `main`, not by an implementing agent.
