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
