# Tasks

This file tracks all work for the E-Commerce Analytics Dashboard (see `prd/ecommerce-analytics.md`).

## Definition of Done

A milestone can move to Done only when:

- All of its acceptance criteria are checked off
- The app runs locally with `streamlit run app.py` with no errors or warnings
- Changes are committed with the milestone ID (e.g. `TASK-3`) in the commit message

## To Do

### TASK-4: Sales trend chart
Add a line chart showing sales over time.
- [ ] Line chart renders with time on the x-axis and sales amount on the y-axis
- [ ] Interactive tooltips show exact values on hover
- [ ] Commit:

### TASK-5: Category and region breakdowns
Add bar charts for sales by category and sales by region.
- [ ] Category bar chart shows all 5 categories, sorted highest to lowest, with Electronics on top
- [ ] Region bar chart shows all 4 regions, sorted highest to lowest
- [ ] Both charts have interactive tooltips with exact values
- [ ] Commit:

### TASK-6: Testing and refinement
Verify the dashboard against the PRD's acceptance criteria and clean up presentation.
- [ ] Dashboard runs end-to-end with no errors or warnings
- [ ] All values match expected calculations from the CSV
- [ ] Layout and labels are clear and suitable for an executive presentation
- [ ] Commit:

### TASK-7: Deployment to Streamlit Community Cloud
Deploy the dashboard so it is publicly accessible via a shareable URL.
- [ ] App is deployed and reachable at a public Streamlit Community Cloud URL
- [ ] Deployed app matches local behavior with no errors
- [ ] Commit:

## In Progress

### TASK-3: KPI cards implementation
Display Total Sales and Total Orders as prominent KPI cards.
- [ ] Total Sales displayed as formatted currency (e.g. $116,500)
- [ ] Total Orders displayed as a formatted count
- [ ] Values match expected output from the PRD (~$116,500 sales, 482 orders)
- [ ] Commit:

## Done

### TASK-1: Environment setup and project initialization
Set up the Python project structure and install dependencies (Streamlit, Pandas, Plotly).
- [x] Project structure created (app.py, data/, requirements.txt)
- [x] Dependencies install cleanly and `streamlit run app.py` renders a blank/placeholder page
- [x] Commit: d213142
- Notes: Clean — scaffold code was correct as generated. One environment gotcha hit while testing: the very first `streamlit run app.py` on this machine failed (exit 255) on Streamlit's interactive first-run "enter your email" onboarding prompt, which blocks non-interactive shells. Fixed locally by writing an empty `~/.streamlit/credentials.toml` (a machine-level config file, not part of the repo) — not a code change.

### TASK-2: Data loading and basic structure
Load `sales-data.csv` into a Pandas DataFrame and validate its structure.
- [x] CSV loads without errors and columns match the data specification (date, order_id, product, category, region, quantity, unit_price, total_amount)
- [x] Date column is parsed as a proper datetime type
- [x] Commit: 8dca655
- Notes: Added `metrics.py` with `load_sales_data()`, tested via TDD in `tests/test_metrics.py`. Hit one project-setup gap not covered by the plan: pytest's default import mode scopes `sys.path` to `tests/` (no `__init__.py`), so `from metrics import load_sales_data` failed with `ModuleNotFoundError` even after `metrics.py` was created. Fixed by adding an empty root-level `conftest.py`, which pytest always adds to `sys.path` when collecting it — a one-time repo setup fix, not a recurring issue.
