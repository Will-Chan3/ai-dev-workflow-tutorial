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
