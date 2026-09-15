# Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 Streamlit sales dashboard (KPIs, trend chart, category/region breakdowns) against `data/sales-data.csv`, per the PRD and design spec.

**Architecture:** A thin `app.py` (Streamlit UI/layout) calls into a pure-Python `metrics.py` (data loading + aggregation), which is unit-tested independently of Streamlit via `tests/test_metrics.py`.

**Tech Stack:** Python 3.11+, Streamlit, Pandas, Plotly, pytest — installed in a plain `venv/` via `requirements.txt`.

**Spec:** `docs/superpowers/specs/2026-09-14-sales-dashboard-design.md`

## Global Constraints

- Work on the existing branch `feature/sales-dashboard` (already checked out) — do not create a git worktree.
- Use a plain Python virtual environment in `venv/`, dependencies pinned in `requirements.txt` — no `uv`, no conda.
- All data calculations live in `metrics.py`, tested via `tests/test_metrics.py` with pytest. `metrics.py` imports `streamlit` only for the `@st.cache_data` decorator on `load_sales_data` — every other function is plain pandas.
- Minimal validation, by design: no try/except around CSV loading, no defensive schema checks (per the spec's Error Handling section).
- Only `load_sales_data()` is cached with `@st.cache_data`; aggregation functions are not cached.
- Every commit message is prefixed with its milestone ID (e.g. `TASK-3: ...`), per `TASKS.md`'s Definition of Done.
- Each plan task below is labeled `[Milestone: TASK-N]`, referencing `TASKS.md`. The plan's own "Plan Task 1, 2, 3..." numbering is separate from those milestone IDs — don't conflate the two when tracking progress.
- **TASK-7 (deployment) is executed manually by the user after merge.** The implementing agent must stop after Plan Task 6 and hand off — do not attempt deployment.

---

### Plan Task 1: Project Scaffolding [Milestone: TASK-1]

**Files:**
- Create: `requirements.txt`
- Create: `app.py`
- Verify: `.gitignore` (already contains `venv/` — no change expected)

**Interfaces:**
- Consumes: nothing (first task)
- Produces: a runnable `app.py` entry point; `requirements.txt` for all later tasks' dependencies

- [ ] **Step 1: Create and activate the virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

- [ ] **Step 2: Install dependencies and pin them**

```bash
pip install streamlit pandas plotly pytest
pip freeze > requirements.txt
```

- [ ] **Step 3: Confirm `venv/` is gitignored**

Run: `git check-ignore -q venv && echo IGNORED || echo NOT IGNORED`
Expected: `IGNORED` (the repo's `.gitignore` already lists `venv/`)

- [ ] **Step 4: Write the app skeleton**

```python
import streamlit as st

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")
```

Save as `app.py`.

- [ ] **Step 5: Run the app and confirm it loads**

Run: `streamlit run app.py`
Expected: browser opens to a page titled "ShopSmart Sales Dashboard" with no errors in the terminal. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 6: Commit**

```bash
git add app.py requirements.txt
git commit -m "TASK-1: Scaffold Streamlit app and pin dependencies"
```

---

### Plan Task 2: Data Loading [Milestone: TASK-2]

**Files:**
- Create: `metrics.py`
- Create: `tests/test_metrics.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `requirements.txt` environment from Plan Task 1
- Produces: `load_sales_data(path: str) -> pd.DataFrame` with columns `date, order_id, product, category, region, quantity, unit_price, total_amount` and `date` parsed as a datetime dtype — later tasks call this function to get their input DataFrame

- [ ] **Step 1: Write the failing test**

Create `tests/test_metrics.py`:

```python
import pandas as pd

from metrics import load_sales_data


def test_load_sales_data_parses_expected_columns_and_date_dtype(tmp_path):
    csv_content = (
        "date,order_id,product,category,region,quantity,unit_price,total_amount\n"
        "2024-01-03,ORD-001001,Wireless Earbuds,Audio,North,2,79.99,159.98\n"
        "2024-02-10,ORD-001002,Phone Case,Accessories,South,3,24.99,74.97\n"
    )
    csv_path = tmp_path / "sales-data.csv"
    csv_path.write_text(csv_content)

    df = load_sales_data(str(csv_path))

    expected_columns = [
        "date", "order_id", "product", "category",
        "region", "quantity", "unit_price", "total_amount",
    ]
    assert list(df.columns) == expected_columns
    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_metrics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'metrics'`

- [ ] **Step 3: Write minimal implementation**

Create `metrics.py`:

```python
import pandas as pd
import streamlit as st


@st.cache_data
def load_sales_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_metrics.py -v`
Expected: PASS. (You may see a "missing ScriptRunContext" warning — that's expected and harmless when `@st.cache_data` runs outside a live Streamlit app, e.g. under pytest.)

- [ ] **Step 5: Wire loading into the app**

Update `app.py`:

```python
import streamlit as st

from metrics import load_sales_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

df = load_sales_data("data/sales-data.csv")
```

- [ ] **Step 6: Run the app and confirm it still loads**

Run: `streamlit run app.py`
Expected: page loads with no errors in the terminal. Stop the server once confirmed.

- [ ] **Step 7: Commit**

```bash
git add metrics.py tests/test_metrics.py app.py
git commit -m "TASK-2: Load sales data from CSV"
```

---

### Plan Task 3: KPI Cards [Milestone: TASK-3]

**Files:**
- Modify: `metrics.py`
- Modify: `tests/test_metrics.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `load_sales_data()` from Plan Task 2
- Produces: `total_sales(df: pd.DataFrame) -> float`, `total_orders(df: pd.DataFrame) -> int`

- [ ] **Step 1: Write the failing tests**

Update the top of `tests/test_metrics.py`: add `import pytest`, and change the existing `from metrics import load_sales_data` line to also import the two new functions:

```python
import pytest

from metrics import load_sales_data, total_orders, total_sales
```

Then append the fixture and new tests below the existing test:

```python
@pytest.fixture
def sample_sales_df():
    return pd.DataFrame({
        "date": pd.to_datetime([
            "2024-01-03", "2024-01-10", "2024-02-05",
            "2024-02-20", "2024-03-01", "2024-03-15",
        ]),
        "order_id": ["ORD-001", "ORD-002", "ORD-003", "ORD-004", "ORD-005", "ORD-006"],
        "product": [
            "Wireless Earbuds", "Phone Case", "Smart Watch",
            "USB-C Cable", "Smart Speaker", "Fitness Tracker",
        ],
        "category": ["Audio", "Accessories", "Wearables", "Accessories", "Smart Home", "Wearables"],
        "region": ["North", "South", "East", "West", "North", "South"],
        "quantity": [2, 3, 1, 5, 1, 2],
        "unit_price": [79.99, 24.99, 299.99, 12.99, 49.99, 89.99],
        "total_amount": [159.98, 74.97, 299.99, 64.95, 49.99, 179.98],
    })


def test_total_sales_sums_total_amount_column(sample_sales_df):
    assert total_sales(sample_sales_df) == 829.86


def test_total_orders_counts_rows(sample_sales_df):
    assert total_orders(sample_sales_df) == 6
```

Note: `import pandas as pd` and the earlier `load_sales_data` test already exist in this file from Plan Task 2 — add the new imports and fixture alongside them, don't duplicate `import pandas as pd`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_metrics.py -v`
Expected: FAIL with `ImportError: cannot import name 'total_orders' from 'metrics'` (and same for `total_sales`)

- [ ] **Step 3: Write minimal implementation**

Append to `metrics.py`:

```python
def total_sales(df: pd.DataFrame) -> float:
    return df["total_amount"].sum()


def total_orders(df: pd.DataFrame) -> int:
    return len(df)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_metrics.py -v`
Expected: PASS

- [ ] **Step 5: Render the KPI cards**

Update `app.py`:

```python
import streamlit as st

from metrics import load_sales_data, total_orders, total_sales

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

df = load_sales_data("data/sales-data.csv")

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales(df):,.0f}")
col2.metric("Total Orders", f"{total_orders(df):,}")
```

- [ ] **Step 6: Run the app and confirm the KPIs render**

Run: `streamlit run app.py`
Expected: two metric cards showing "Total Sales" and "Total Orders" with formatted values, no errors. Stop the server once confirmed.

- [ ] **Step 7: Commit**

```bash
git add metrics.py tests/test_metrics.py app.py
git commit -m "TASK-3: Add Total Sales and Total Orders KPI cards"
```

---

### Plan Task 4: Sales Trend Chart [Milestone: TASK-4]

**Files:**
- Modify: `metrics.py`
- Modify: `tests/test_metrics.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `sample_sales_df` fixture from Plan Task 3
- Produces: `monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame` with columns `month` (datetime, first-of-month) and `total_amount`, sorted chronologically

- [ ] **Step 1: Write the failing test**

Append to `tests/test_metrics.py`:

```python
from metrics import monthly_sales_trend


def test_monthly_sales_trend_groups_by_month_in_chronological_order(sample_sales_df):
    trend = monthly_sales_trend(sample_sales_df)

    assert list(trend["month"]) == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-03-01"),
    ]
    assert list(trend["total_amount"]) == [234.95, 364.94, 229.97]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_metrics.py -v`
Expected: FAIL with `ImportError: cannot import name 'monthly_sales_trend' from 'metrics'`

- [ ] **Step 3: Write minimal implementation**

Append to `metrics.py`:

```python
def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    trend = df.copy()
    trend["month"] = trend["date"].dt.to_period("M").dt.to_timestamp()
    return (
        trend.groupby("month")["total_amount"]
        .sum()
        .reset_index()
        .sort_values("month")
        .reset_index(drop=True)
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_metrics.py -v`
Expected: PASS

- [ ] **Step 5: Render the trend chart**

Update `app.py`:

```python
import plotly.express as px
import streamlit as st

from metrics import load_sales_data, monthly_sales_trend, total_orders, total_sales

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

df = load_sales_data("data/sales-data.csv")

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales(df):,.0f}")
col2.metric("Total Orders", f"{total_orders(df):,}")

st.subheader("Sales Trend Over Time")
trend_df = monthly_sales_trend(df)
trend_fig = px.line(trend_df, x="month", y="total_amount", markers=True)
trend_fig.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
st.plotly_chart(trend_fig, use_container_width=True)
```

- [ ] **Step 6: Run the app and confirm the trend chart renders**

Run: `streamlit run app.py`
Expected: a line chart titled "Sales Trend Over Time" appears below the KPIs, with hoverable data points. No errors. Stop the server once confirmed.

- [ ] **Step 7: Commit**

```bash
git add metrics.py tests/test_metrics.py app.py
git commit -m "TASK-4: Add monthly sales trend chart"
```

---

### Plan Task 5: Category and Region Breakdowns [Milestone: TASK-5]

**Files:**
- Modify: `metrics.py`
- Modify: `tests/test_metrics.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `sample_sales_df` fixture from Plan Task 3
- Produces: `sales_by_category(df: pd.DataFrame) -> pd.DataFrame` (columns `category`, `total_amount`, sorted descending) and `sales_by_region(df: pd.DataFrame) -> pd.DataFrame` (columns `region`, `total_amount`, sorted descending)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_metrics.py`:

```python
from metrics import sales_by_category, sales_by_region


def test_sales_by_category_sums_and_sorts_descending(sample_sales_df):
    result = sales_by_category(sample_sales_df)

    assert list(result["category"]) == ["Wearables", "Audio", "Accessories", "Smart Home"]
    assert list(result["total_amount"]) == [479.97, 159.98, 139.92, 49.99]


def test_sales_by_region_sums_and_sorts_descending(sample_sales_df):
    result = sales_by_region(sample_sales_df)

    assert list(result["region"]) == ["East", "South", "North", "West"]
    assert list(result["total_amount"]) == [299.99, 254.95, 209.97, 64.95]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_metrics.py -v`
Expected: FAIL with `ImportError: cannot import name 'sales_by_category' from 'metrics'` (and same for `sales_by_region`)

- [ ] **Step 3: Write minimal implementation**

Append to `metrics.py`:

```python
def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")["total_amount"]
        .sum()
        .reset_index()
        .sort_values("total_amount", ascending=False)
        .reset_index(drop=True)
    )


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("region")["total_amount"]
        .sum()
        .reset_index()
        .sort_values("total_amount", ascending=False)
        .reset_index(drop=True)
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_metrics.py -v`
Expected: PASS

- [ ] **Step 5: Render the bar charts**

Update `app.py`:

```python
import plotly.express as px
import streamlit as st

from metrics import (
    load_sales_data,
    monthly_sales_trend,
    sales_by_category,
    sales_by_region,
    total_orders,
    total_sales,
)

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

df = load_sales_data("data/sales-data.csv")

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales(df):,.0f}")
col2.metric("Total Orders", f"{total_orders(df):,}")

st.subheader("Sales Trend Over Time")
trend_df = monthly_sales_trend(df)
trend_fig = px.line(trend_df, x="month", y="total_amount", markers=True)
trend_fig.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
st.plotly_chart(trend_fig, use_container_width=True)

category_col, region_col = st.columns(2)

with category_col:
    st.subheader("Sales by Category")
    category_df = sales_by_category(df)
    category_fig = px.bar(category_df, x="category", y="total_amount")
    category_fig.update_layout(xaxis_title="Category", yaxis_title="Sales ($)")
    st.plotly_chart(category_fig, use_container_width=True)

with region_col:
    st.subheader("Sales by Region")
    region_df = sales_by_region(df)
    region_fig = px.bar(region_df, x="region", y="total_amount")
    region_fig.update_layout(xaxis_title="Region", yaxis_title="Sales ($)")
    st.plotly_chart(region_fig, use_container_width=True)
```

- [ ] **Step 6: Run the app and confirm both bar charts render**

Run: `streamlit run app.py`
Expected: "Sales by Category" and "Sales by Region" bar charts appear side by side below the trend chart, each sorted highest-to-lowest. No errors. Stop the server once confirmed.

- [ ] **Step 7: Commit**

```bash
git add metrics.py tests/test_metrics.py app.py
git commit -m "TASK-5: Add category and region breakdown charts"
```

---

### Plan Task 6: Verification Against the Real Dataset [Milestone: TASK-6]

**Files:**
- Modify: `tests/test_metrics.py`

**Interfaces:**
- Consumes: `load_sales_data`, `total_sales`, `total_orders` from Plan Tasks 2-3; `data/sales-data.csv` (the real dataset)
- Produces: nothing further downstream — this is the final automated verification task

- [ ] **Step 1: Write an integration test against the real CSV**

Append to `tests/test_metrics.py`:

```python
def test_real_dataset_matches_prd_expected_output():
    df = load_sales_data("data/sales-data.csv")

    assert total_orders(df) == 482
    assert total_sales(df) == pytest.approx(116_500, rel=0.05)
```

- [ ] **Step 2: Run the full test suite**

Run: `pytest tests/test_metrics.py -v`
Expected: all tests PASS, including `test_real_dataset_matches_prd_expected_output`. If `total_orders` or `total_sales` don't match, stop and investigate `data/sales-data.csv` before proceeding — don't adjust the assertion to fit a wrong number.

- [ ] **Step 3: Manually verify against the PRD's acceptance criteria**

Run: `streamlit run app.py` and confirm each of the following (from `prd/ecommerce-analytics.md`'s Acceptance Criteria section):

- Total Sales and Total Orders are displayed prominently and correctly
- The trend line chart shows sales over time with correct data and working tooltips
- The category bar chart shows all 5 categories, sorted highest to lowest
- The region bar chart shows all 4 regions, sorted highest to lowest
- The dashboard loads with no errors or warnings in the terminal
- The layout looks clean and presentable (titles, spacing, readable labels)

Stop the server once confirmed.

- [ ] **Step 4: Commit**

```bash
git add tests/test_metrics.py
git commit -m "TASK-6: Add real-dataset integration test and complete verification pass"
```

---

### Plan Task 7: Deployment [Milestone: TASK-7] — ⚠️ USER-EXECUTED, DO NOT AUTOMATE

**This task is not part of the implementing agent's work.** When Plan Task 6 is committed and reviewed, the agent's job is done — stop here and report completion. The user will execute the following manually, after merging `feature/sales-dashboard` into `main`:

1. Merge `feature/sales-dashboard` into `main` and push `main` to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Create a new app, pointing it at the `main` branch of this repo with `app.py` as the entry point.
4. Deploy, and confirm the public URL loads the dashboard with no errors.
5. Update `TASKS.md`: check off TASK-7's acceptance criteria and move it to Done.

No checkboxes are given for this task since it is executed outside the implementation workflow.
