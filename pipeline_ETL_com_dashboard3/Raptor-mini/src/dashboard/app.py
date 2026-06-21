from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

from etl_raptor.config import DATABASE_CONFIG


def get_connection_string() -> str:
    return DATABASE_CONFIG.dsn()


def load_sales_data(engine) -> pd.DataFrame:
    query = text(
        "SELECT s.sale_id, s.customer_id, s.sale_date, s.quantity, s.price, s.total_sale_value, "
        "s.sale_year, s.sale_month, s.sale_quarter, c.state, p.category, p.name AS product_name "
        "FROM sales s "
        "JOIN customers c ON s.customer_id = c.customer_id "
        "JOIN products p ON s.product_id = p.product_id"
    )
    return pd.read_sql(query, engine)


def main() -> None:
    st.set_page_config(page_title="Sales Dashboard", layout="wide")
    st.title("Sales Analysis Dashboard")

    engine = create_engine(get_connection_string())
    df = load_sales_data(engine)

    min_date = pd.to_datetime(df["sale_date"]).min()
    max_date = pd.to_datetime(df["sale_date"]).max()

    date_range = st.sidebar.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)
    state_filter = st.sidebar.multiselect("State", sorted(df["state"].unique()), default=sorted(df["state"].unique()))
    category_filter = st.sidebar.multiselect(
        "Category", sorted(df["category"].unique()), default=sorted(df["category"].unique())
    )
    product_filter = st.sidebar.multiselect(
        "Product", sorted(df["product_name"].unique()), default=sorted(df["product_name"].unique())
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = min_date
        end_date = max_date

    df["sale_date"] = pd.to_datetime(df["sale_date"])
    filtered = df[
        (df["sale_date"] >= pd.to_datetime(start_date))
        & (df["sale_date"] <= pd.to_datetime(end_date))
        & (df["state"].isin(state_filter))
        & (df["category"].isin(category_filter))
        & (df["product_name"].isin(product_filter))
    ]

    total_revenue = filtered["total_sale_value"].sum()
    total_sales = len(filtered)
    avg_ticket = filtered["total_sale_value"].mean() if total_sales > 0 else 0
    unique_customers = filtered["customer_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Number of Sales", total_sales)
    col3.metric("Average Ticket", f"${avg_ticket:,.2f}")
    col4.metric("Unique States", unique_customers)

    revenue_by_month = filtered.groupby(filtered["sale_date"].dt.to_period("M"))["total_sale_value"].sum().reset_index()
    revenue_by_month["sale_date"] = revenue_by_month["sale_date"].dt.to_timestamp()

    revenue_by_category = filtered.groupby("category")["total_sale_value"].sum().reset_index().sort_values("total_sale_value", ascending=False)
    top_products = filtered.groupby("product_name")["total_sale_value"].sum().reset_index().sort_values("total_sale_value", ascending=False).head(10)
    sales_by_state = filtered.groupby("state")["total_sale_value"].sum().reset_index().sort_values("total_sale_value", ascending=False)
    sales_trend = filtered.groupby(filtered["sale_date"].dt.to_period("W"))["total_sale_value"].sum().reset_index()
    sales_trend["sale_date"] = sales_trend["sale_date"].dt.to_timestamp()

    st.subheader("Revenue by Month")
    st.line_chart(revenue_by_month.rename(columns={"sale_date": "Month", "total_sale_value": "Revenue"}).set_index("Month"))

    st.subheader("Revenue by Product Category")
    st.bar_chart(revenue_by_category.rename(columns={"category": "Category", "total_sale_value": "Revenue"}).set_index("Category"))

    st.subheader("Top 10 Best-Selling Products")
    st.bar_chart(top_products.rename(columns={"product_name": "Product", "total_sale_value": "Revenue"}).set_index("Product"))

    st.subheader("Sales Distribution by State")
    st.bar_chart(sales_by_state.rename(columns={"state": "State", "total_sale_value": "Revenue"}).set_index("State"))

    st.subheader("Sales Trend")
    st.line_chart(sales_trend.rename(columns={"sale_date": "Week", "total_sale_value": "Revenue"}).set_index("Week"))


if __name__ == "__main__":
    main()
