# Design: E-Commerce Sales Dashboard

**Status:** Approved for planning
**Source PRD:** `prd/ecommerce-analytics.md` (Phase 1 scope only)
**Milestone tracking:** `TASKS.md` (TASK-1 through TASK-7)

## Summary

A single-page Streamlit dashboard that reads `data/sales-data.csv` and
displays Total Sales / Total Orders KPIs, a monthly sales trend line
chart, and category/region bar charts, per the PRD's Phase 1 functional
requirements (FR-1 through FR-5). Deployment to Streamlit Community
Cloud (M7) is executed by the user after merge, not part of this
implementation.

## Architecture

```
app.py              — Streamlit UI: page config, layout, calls into metrics.py, renders charts
metrics.py          — pure functions: load_sales_data(), total_sales(), total_orders(),
                       sales_by_category(), sales_by_region(), monthly_sales_trend()
tests/test_metrics.py — pytest tests against metrics.py, using small hand-built DataFrames
requirements.txt    — streamlit, pandas, plotly, pytest
venv/               — local virtual environment (gitignored, plain venv — no uv/conda)
```

`app.py` stays thin: it wires UI to `metrics.py` and holds no calculation
logic, so every number shown in the dashboard is independently testable
without running Streamlit. `load_sales_data()` is the only function
decorated with `@st.cache_data`, since it's the only one doing I/O; the
aggregation functions are cheap enough on 482 rows that caching them
would add complexity without measurable benefit.

A single `metrics.py` module (rather than splitting loading vs.
aggregation into separate files) was chosen deliberately — the project
has ~5 small functions operating on one DataFrame shape, and splitting
further would add navigation overhead without improving clarity.

## Data Flow

```
data/sales-data.csv
   → load_sales_data(path)          [pandas.read_csv, parse_dates=["date"], @st.cache_data]
   → total_sales(df) / total_orders(df)            → scalars → st.metric() KPI cards
   → sales_by_category(df) / sales_by_region(df)   → DataFrame sorted desc by total_amount → px.bar()
   → monthly_sales_trend(df)                       → DataFrame grouped by month → px.line()
```

Each aggregation function takes the loaded DataFrame and returns either
a scalar (`total_sales`, `total_orders`) or a small DataFrame shaped for
its chart:

- `sales_by_category(df)` / `sales_by_region(df)`: grouped by
  category/region, summed on `total_amount`, sorted descending.
- `monthly_sales_trend(df)`: grouped by calendar month (derived from
  `date`), summed on `total_amount`, in chronological order.

`app.py` passes these results straight to `st.metric()` and
`plotly.express` calls — no intermediate formatting logic beyond
currency/number display strings, which Streamlit and Plotly handle
natively.

## Error Handling

Minimal validation, by design: no try/except around the CSV load or
explicit column/schema checks. If `data/sales-data.csv` is missing or
malformed, pandas raises and Streamlit renders its default error
traceback. This is acceptable because the data source is a single known
file for a workshop-style project, not a user-facing upload — adding
defensive validation here would be speculative complexity the PRD
doesn't call for.

## Testing

`tests/test_metrics.py` tests only `metrics.py` — Streamlit UI isn't
meaningfully unit-testable, and the PRD's acceptance criteria concern
correct numbers, not UI internals.

- Most tests use small, hand-built DataFrames (4-6 rows spanning two
  categories, two regions, two months) with totals computed by hand and
  asserted exactly. This keeps tests fast, deterministic, and
  independent of the real dataset ever changing.
- Sorting behavior for `sales_by_category`/`sales_by_region` (must be
  descending by sales value) gets an explicit assertion, since it's easy
  to silently break.
- One integration-style test loads the real `data/sales-data.csv` and
  asserts `total_orders() == 482` and `total_sales()` is close to the
  PRD's expected ~$116,500. This catches drift against the PRD's
  "Expected Output" table without making every unit test depend on the
  real file.

## Out of Scope (per PRD Phase 2 and explicit user constraints)

- Filtering, date range selection, drill-down, auth, real-time DB,
  export, alerts (explicitly Phase 2 in the PRD)
- Defensive CSV validation / friendly error UI
- Caching of aggregation functions (only the CSV load is cached)
- Deployment automation — the user deploys manually from `main` after
  merge; this is the final, user-executed step and is not part of the
  implementation plan's own tasks

## Milestone Mapping

This design covers all of TASKS.md's milestones:

| Milestone | Covered by |
|-----------|-----------|
| TASK-1 | venv/, requirements.txt, project skeleton |
| TASK-2 | `load_sales_data()` in metrics.py |
| TASK-3 | `total_sales()`, `total_orders()` + KPI rendering in app.py |
| TASK-4 | `monthly_sales_trend()` + line chart in app.py |
| TASK-5 | `sales_by_category()`, `sales_by_region()` + bar charts in app.py |
| TASK-6 | Full pytest suite + manual verification against PRD's expected output |
| TASK-7 | User-executed deployment (out of scope for the implementation plan) |
