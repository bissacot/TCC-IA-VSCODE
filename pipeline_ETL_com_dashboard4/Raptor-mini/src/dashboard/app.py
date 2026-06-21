from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

from etl.config import Settings
from etl.logger import get_logger

logger = get_logger(__name__)


def load_dataframes(engine) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sales = pd.read_sql_table("sales", engine)
    customers = pd.read_sql_table("customers", engine)
    products = pd.read_sql_table("products", engine)
    return sales, customers, products


def merge_datasets(sales: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    df = sales.merge(customers, on="customer_id", how="left").merge(products, on="product_id", how="left")
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    return df


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    min_date = df["sale_date"].min()
    max_date = df["sale_date"].max()
    start_date, end_date = st.sidebar.date_input(
        "Date range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )
    states = sorted(df["state"].dropna().unique())
    categories = sorted(df["category"].dropna().unique())
    products = sorted(df["product_name"].dropna().unique())

    selected_states = st.sidebar.multiselect("State", states, default=states)
    selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
    selected_products = st.sidebar.multiselect("Product", products, default=products)

    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    filtered_df = df[
        (df["sale_date"].dt.date >= start_date)
        & (df["sale_date"].dt.date <= end_date)
        & (df["state"].isin(selected_states))
        & (df["category"].isin(selected_categories))
        & (df["product_name"].isin(selected_products))
    ]
    return filtered_df


def render_dashboard(df: pd.DataFrame) -> None:
    st.title("Sales Analysis Dashboard")

    total_revenue = df["total_sale_value"].sum()
    total_sales = len(df)
    avg_ticket = df["total_sale_value"].mean()
    unique_customers = df["customer_id"].nunique()

    st.metric("Total Revenue", f"${total_revenue:,.2f}")
    st.metric("Number of Sales", total_sales)
    st.metric("Average Ticket Size", f"${avg_ticket:,.2f}")
    st.metric("Unique Customers", unique_customers)

    revenue_by_month = df.groupby(df["sale_date"].dt.to_period("M"))["total_sale_value"].sum().reset_index()
    revenue_by_category = df.groupby("category")["total_sale_value"].sum().reset_index()
    top_products = df.groupby("product_name")["total_sale_value"].sum().nlargest(10).reset_index()
    revenue_by_state = df.groupby("state")["total_sale_value"].sum().reset_index()
    trend = df.groupby("sale_date")["total_sale_value"].sum().reset_index()

    st.subheader("Revenue by Month")
    st.bar_chart(revenue_by_month.rename(columns={"sale_date": "Month", "total_sale_value": "Revenue"}).set_index("Month"))

    st.subheader("Revenue by Product Category")
    st.bar_chart(revenue_by_category.set_index("category"))

    st.subheader("Top 10 Best-Selling Products")
    st.bar_chart(top_products.set_index("product_name"))

    st.subheader("Sales Distribution by State")
    st.bar_chart(revenue_by_state.set_index("state"))

    st.subheader("Sales Trend Over Time")
    st.line_chart(trend.set_index("sale_date"))


def main() -> None:
    config = Settings()
    engine = create_engine(config.database_url, future=True)
    sales, customers, products = load_dataframes(engine)
    dataset = merge_datasets(sales, customers, products)
    if dataset.empty:
        st.error("No sales data available. Run the ETL first.")
        return
    filtered = filter_data(dataset)
    render_dashboard(filtered)


if __name__ == "__main__":
    main()
