import streamlit as st

from metrics import load_sales_data, total_orders, total_sales

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

df = load_sales_data("data/sales-data.csv")

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales(df):,.0f}")
col2.metric("Total Orders", f"{total_orders(df):,}")
