import pandas as pd
import pytest

from metrics import load_sales_data, total_orders, total_sales


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
