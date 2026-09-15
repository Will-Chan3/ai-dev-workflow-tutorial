import pandas as pd
import streamlit as st


@st.cache_data
def load_sales_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def total_sales(df: pd.DataFrame) -> float:
    return df["total_amount"].sum()


def total_orders(df: pd.DataFrame) -> int:
    return len(df)
