import pandas as pd
import streamlit as st


@st.cache_data
def load_sales_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def total_sales(df: pd.DataFrame) -> float:
    return df["total_amount"].sum()


def total_orders(df: pd.DataFrame) -> int:
    return len(df)


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
