from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from fpdf import FPDF
from sqlalchemy import create_engine

# Ensure that the src package is discoverable when running as a Streamlit app.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from etl_app.config import settings
from etl_app.logger import get_logger

logger = get_logger(__name__)


def get_engine() -> Any:
    return create_engine(settings.db_url)


@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    engine = get_engine()
    sales = pd.read_sql("SELECT * FROM sales", engine, parse_dates=["sale_date"])
    customers = pd.read_sql("SELECT * FROM customers", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    return sales, customers, products


def build_dashboard() -> None:
    st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")
    st.title("Sales Analytics Dashboard")

    sales, customers, products = load_data()
    sales = sales.merge(customers, on="customer_id", how="left", suffixes=("", "_customer"))
    sales = sales.merge(products, on="product_id", how="left", suffixes=("", "_product"))

    min_date = sales["sale_date"].min()
    max_date = sales["sale_date"].max()
    date_range = st.sidebar.date_input("Date range", [min_date, max_date])
    state_filter = st.sidebar.multiselect("State", sorted(sales["state"].dropna().unique()))
    category_filter = st.sidebar.multiselect("Category", sorted(sales["category"].dropna().unique()))
    product_filter = st.sidebar.multiselect("Product", sorted(sales["product_name"].dropna().unique()))

    filtered = sales.copy()
    if len(date_range) == 2:
        filtered = filtered[filtered["sale_date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))]
    if state_filter:
        filtered = filtered[filtered["state"].isin(state_filter)]
    if category_filter:
        filtered = filtered[filtered["category"].isin(category_filter)]
    if product_filter:
        filtered = filtered[filtered["product_name"].isin(product_filter)]

    total_revenue = filtered["total_sale_value"].sum()
    sales_count = len(filtered)
    average_ticket = filtered["total_sale_value"].mean() if sales_count else 0
    unique_customers = filtered["customer_id"].nunique()

    st.metric("Total Revenue", f"${total_revenue:,.2f}")
    st.metric("Number of Sales", sales_count)
    st.metric("Average Ticket Size", f"${average_ticket:,.2f}")
    st.metric("Unique Customers", unique_customers)

    col1, col2 = st.columns(2)

    revenue_by_month = (
        filtered.groupby(filtered["sale_date"].dt.to_period("M"))["total_sale_value"]
        .sum()
        .reset_index()
    )
    revenue_by_month["sale_date"] = revenue_by_month["sale_date"].dt.to_timestamp()
    fig_month = px.bar(revenue_by_month, x="sale_date", y="total_sale_value", title="Revenue by Month")
    col1.plotly_chart(fig_month, use_container_width=True)

    revenue_by_category = (
        filtered.groupby("category")["total_sale_value"].sum().reset_index().sort_values("total_sale_value", ascending=False)
    )
    fig_category = px.pie(revenue_by_category, values="total_sale_value", names="category", title="Revenue by Product Category")
    col2.plotly_chart(fig_category, use_container_width=True)

    top_products = (
        filtered.groupby("product_name")[["quantity", "total_sale_value"]]
        .sum()
        .reset_index()
        .sort_values("quantity", ascending=False)
        .head(10)
    )
    st.subheader("Top 10 Best-Selling Products")
    st.dataframe(top_products)

    sales_by_state = filtered.groupby("state")["total_sale_value"].sum().reset_index()
    fig_state = px.bar(sales_by_state, x="state", y="total_sale_value", title="Sales Distribution by State")
    st.plotly_chart(fig_state, use_container_width=True)

    trend = (
        filtered.groupby(filtered["sale_date"].dt.to_period("W"))["total_sale_value"]
        .sum()
        .reset_index()
    )
    trend["sale_date"] = trend["sale_date"].dt.to_timestamp()
    fig_trend = px.line(trend, x="sale_date", y="total_sale_value", title="Sales Trends Over Time")
    st.plotly_chart(fig_trend, use_container_width=True)

    export_excel(filtered)
    export_pdf(filtered)


def export_excel(filtered: pd.DataFrame) -> None:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        filtered.to_excel(writer, sheet_name="filtered_sales", index=False)
    st.download_button(
        label="Download filtered data as Excel",
        data=buffer.getvalue(),
        file_name="sales_dashboard_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def export_pdf(filtered: pd.DataFrame) -> None:
    buffer = io.BytesIO()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Filtered Sales Overview", ln=True)
    pdf.set_font("Arial", "", 11)
    total_revenue = filtered["total_sale_value"].sum()
    sales_count = len(filtered)
    unique_customers = filtered["customer_id"].nunique()
    pdf.cell(0, 8, f"Total revenue: ${total_revenue:.2f}", ln=True)
    pdf.cell(0, 8, f"Sales count: {sales_count}", ln=True)
    pdf.cell(0, 8, f"Unique customers: {unique_customers}", ln=True)
    pdf.ln(4)
    top_products = (
        filtered.groupby("product_name")[["quantity", "total_sale_value"]]
        .sum()
        .reset_index()
        .sort_values("quantity", ascending=False)
        .head(5)
    )
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Top products", ln=True)
    pdf.set_font("Arial", "", 10)
    for _, row in top_products.iterrows():
        pdf.cell(0, 6, f"{row['product_name']} — {int(row['quantity'])} units, ${row['total_sale_value']:.2f}", ln=True)
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    st.download_button(
        label="Download summary PDF",
        data=pdf_bytes,
        file_name="sales_summary.pdf",
        mime="application/pdf",
    )


if __name__ == "__main__":
    build_dashboard()
