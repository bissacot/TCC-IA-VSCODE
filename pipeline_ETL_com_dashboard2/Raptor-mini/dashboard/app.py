import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://etl_user:etl_password@db:5432/etl_db")
engine = create_engine(DATABASE_URL, future=True)

@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    query = """
        SELECT
            s.sale_id,
            s.sale_date,
            s.quantity,
            s.total_sale_value,
            s.year,
            s.month,
            s.quarter,
            s.state AS sale_state,
            c.customer_id,
            c.name AS customer_name,
            c.state AS customer_state,
            p.product_id,
            p.product_name,
            p.category,
            p.unit_price
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN products p ON s.product_id = p.product_id
        ORDER BY s.sale_date
    """
    df = pd.read_sql(query, engine)
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
    states = ["All"] + sorted(df["sale_state"].dropna().unique().tolist())
    categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
    products = ["All"] + sorted(df["product_name"].dropna().unique().tolist())

    selected_state = st.sidebar.selectbox("State", states, index=0)
    selected_category = st.sidebar.selectbox("Category", categories, index=0)
    selected_product = st.sidebar.selectbox("Product", products, index=0)

    filtered = df[(df["sale_date"] >= pd.to_datetime(start_date)) & (df["sale_date"] <= pd.to_datetime(end_date))]
    if selected_state != "All":
        filtered = filtered[filtered["sale_state"] == selected_state]
    if selected_category != "All":
        filtered = filtered[filtered["category"] == selected_category]
    if selected_product != "All":
        filtered = filtered[filtered["product_name"] == selected_product]
    return filtered


def render_kpis(df: pd.DataFrame) -> None:
    revenue = df["total_sale_value"].sum()
    sales_count = df["sale_id"].nunique()
    avg_ticket = df["total_sale_value"].mean() if sales_count else 0.0
    unique_customers = df["customer_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${revenue:,.2f}")
    col2.metric("Number of Sales", sales_count)
    col3.metric("Average Ticket Size", f"${avg_ticket:,.2f}")
    col4.metric("Unique Customers", unique_customers)


def render_charts(df: pd.DataFrame) -> None:
    revenue_by_month = df.groupby(pd.Grouper(key="sale_date", freq="M"))["total_sale_value"].sum().reset_index()
    revenue_by_category = df.groupby("category")["total_sale_value"].sum().reset_index().sort_values("total_sale_value", ascending=False)
    top_products = df.groupby("product_name")["total_sale_value"].sum().reset_index().sort_values("total_sale_value", ascending=False).head(10)
    sales_by_state = df.groupby("sale_state")["total_sale_value"].sum().reset_index().sort_values("total_sale_value", ascending=False)

    st.markdown("### Revenue by Month")
    st.plotly_chart(px.line(revenue_by_month, x="sale_date", y="total_sale_value", markers=True, title="Revenue by Month"), use_container_width=True)

    st.markdown("### Revenue by Product Category")
    st.plotly_chart(px.bar(revenue_by_category, x="category", y="total_sale_value", title="Revenue by Category"), use_container_width=True)

    st.markdown("### Top 10 Best-Selling Products")
    st.plotly_chart(px.bar(top_products, x="product_name", y="total_sale_value", title="Top 10 Products"), use_container_width=True)

    st.markdown("### Sales Distribution by State")
    st.plotly_chart(px.bar(sales_by_state, x="sale_state", y="total_sale_value", title="Sales by State"), use_container_width=True)

    st.markdown("### Sales Trends Over Time")
    st.plotly_chart(px.area(revenue_by_month, x="sale_date", y="total_sale_value", title="Sales Trend"), use_container_width=True)


def main() -> None:
    st.title("Sales Analytics Dashboard")
    st.write("Interactive sales reporting with filters and KPIs.")

    df = load_data()
    filtered_df = filter_data(df)

    render_kpis(filtered_df)
    render_charts(filtered_df)

    if st.button("Refresh data"):
        st.experimental_rerun()

    st.markdown("## Raw Data")
    st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
