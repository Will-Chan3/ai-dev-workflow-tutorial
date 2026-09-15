import streamlit as st

from metrics import load_sales_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

df = load_sales_data("data/sales-data.csv")
