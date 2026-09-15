import pandas as pd
import pytest

from metrics import (
    load_sales_data,
    monthly_sales_trend,
    sales_by_category,
    sales_by_region,
    total_orders,
    total_sales,
)


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
    assert total_sales(sample_sales_df) == pytest.approx(829.86)


def test_total_orders_counts_rows(sample_sales_df):
    assert total_orders(sample_sales_df) == 6


def test_monthly_sales_trend_groups_by_month_in_chronological_order(sample_sales_df):
    trend = monthly_sales_trend(sample_sales_df)

    assert list(trend["month"]) == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-03-01"),
    ]
    assert list(trend["total_amount"]) == [234.95, 364.94, 229.97]


def test_sales_by_category_sums_and_sorts_descending(sample_sales_df):
    result = sales_by_category(sample_sales_df)

    assert list(result["category"]) == ["Wearables", "Audio", "Accessories", "Smart Home"]
    assert list(result["total_amount"]) == pytest.approx([479.97, 159.98, 139.92, 49.99])


def test_sales_by_region_sums_and_sorts_descending(sample_sales_df):
    result = sales_by_region(sample_sales_df)

    assert list(result["region"]) == ["East", "South", "North", "West"]
    assert list(result["total_amount"]) == [299.99, 254.95, 209.97, 64.95]


def test_real_dataset_matches_prd_expected_output():
    df = load_sales_data("data/sales-data.csv")

    assert total_orders(df) == 482
    assert total_sales(df) == pytest.approx(116_500, rel=0.05)
