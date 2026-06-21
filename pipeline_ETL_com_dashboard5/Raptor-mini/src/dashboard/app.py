from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

from src.etl.config import Config


def load_data(engine: Any) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sales = pd.read_sql_table("sales", engine)
    products = pd.read_sql_table("products", engine)
    customers = pd.read_sql_table("customers", engine)
    return sales, products, customers


def filter_data(sales: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    return sales


def build_dashboard() -> None:
    Config.load()
    engine = create_engine(Config.DATABASE_URL, future=True)
    sales, products, customers = load_data(engine)
    sales["sale_date"] = pd.to_datetime(sales["sale_date"])
    sales = sales.merge(products[["product_id", "product_name"]], on="product_id", how="left")

    st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")
    st.title("Sales Analytics Dashboard")

    date_min = sales["sale_date"].min()
    date_max = sales["sale_date"].max()

    with st.sidebar:
        st.header("Filters")
        date_range = st.date_input("Date range", value=(date_min.date(), date_max.date()))
        states = st.multiselect("State", sorted(sales["state"].dropna().unique()), default=sales["state"].dropna().unique().tolist())
        categories = st.multiselect("Category", sorted(sales["category"].dropna().unique()), default=sales["category"].dropna().unique().tolist())
        products_selected = st.multiselect("Product", sorted(products["product_name"].dropna().unique()), default=products["product_name"].dropna().unique().tolist())

    start_date, end_date = date_range
    filtered = sales[
        (sales["sale_date"] >= pd.to_datetime(start_date))
        & (sales["sale_date"] <= pd.to_datetime(end_date))
    ]
    if states:
        filtered = filtered[filtered["state"].isin(states)]
    if categories:
        filtered = filtered[filtered["category"].isin(categories)]
    if products_selected:
        filtered = filtered[filtered["product_name"].isin(products_selected)]

    total_revenue = filtered["total_value"].sum()
    number_of_sales = len(filtered)
    average_ticket = filtered["total_value"].mean() if number_of_sales else 0
    unique_customers = filtered["customer_id"].nunique()

    st.metric("Total Revenue", f"${total_revenue:,.2f}")
    st.metric("Number of Sales", f"{number_of_sales:,}")
    st.metric("Average Ticket", f"${average_ticket:,.2f}")
    st.metric("Unique Customers", f"{unique_customers:,}")

    revenue_by_month = (
        filtered.groupby(
            [filtered["sale_date"].dt.year.rename("year"), filtered["sale_date"].dt.month.rename("month")]
        )["total_value"]
        .sum()
        .reset_index()
    )
    revenue_by_month["month_label"] = revenue_by_month.apply(
        lambda row: f"{int(row['year']):04d}-{int(row['month']):02d}", axis=1
    )

    st.plotly_chart(px.line(revenue_by_month, x="month_label", y="total_value", title="Revenue by Month"), use_container_width=True)
    st.plotly_chart(px.bar(filtered.groupby("category")["total_value"].sum().reset_index().sort_values("total_value", ascending=False), x="category", y="total_value", title="Revenue by Category"), use_container_width=True)
    st.plotly_chart(px.bar(filtered.groupby("product_name")["total_value"].sum().reset_index().sort_values("total_value", ascending=False).head(10), x="product_name", y="total_value", title="Top 10 Products"), use_container_width=True)
    st.plotly_chart(px.bar(filtered.groupby("state")["total_value"].sum().reset_index().sort_values("total_value", ascending=False), x="state", y="total_value", title="Sales by State"), use_container_width=True)
    st.plotly_chart(px.line(filtered.groupby("sale_date")["total_value"].sum().reset_index(), x="sale_date", y="total_value", title="Sales Trend"), use_container_width=True)


def main() -> None:
    build_dashboard()


if __name__ == "__main__":
    main()
