from __future__ import annotations

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from app.utils.config import settings
from app.utils.logging import logger


def get_engine():
    url = (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    return create_engine(url, future=True)


@st.cache_data
def load_sales_data(query: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn)
    return df


def main():
    st.title("Sales Dashboard")

    st.sidebar.header("Filters")
    min_date = st.sidebar.date_input("Start date")
    max_date = st.sidebar.date_input("End date")

    engine = get_engine()
    query = "SELECT s.*, p.category FROM sales s LEFT JOIN products p ON s.product_id = p.product_id"
    df = load_sales_data(query)

    if not df.empty:
        df["sale_date"] = pd.to_datetime(df["sale_date"]) 
        # Apply date filter
        if min_date:
            df = df[df["sale_date"] >= pd.to_datetime(min_date)]
        if max_date:
            df = df[df["sale_date"] <= pd.to_datetime(max_date)]

        total_revenue = df["total_value"].sum()
        num_sales = len(df)
        avg_ticket = df["total_value"].mean()
        unique_customers = df["customer_id"].nunique()

        st.metric("Total Revenue", f"${total_revenue:,.2f}")
        st.metric("Number of Sales", f"{num_sales}")
        st.metric("Average Ticket", f"${avg_ticket:,.2f}")
        st.metric("Unique Customers", f"{unique_customers}")

        st.subheader("Revenue by Month")
        rev_month = df.groupby(["year", "month"])["total_value"].sum().reset_index()
        rev_month["month_year"] = pd.to_datetime(rev_month["year"].astype(str) + "-" + rev_month["month"].astype(str) + "-01")
        st.line_chart(rev_month.set_index("month_year")["total_value"]) 

        st.subheader("Top 10 Products")
        top10 = df.groupby("product_id")["total_value"].sum().nlargest(10)
        st.bar_chart(top10)

        st.subheader("Revenue by Category")
        cat = df.groupby("category")["total_value"].sum()
        st.bar_chart(cat)

        st.subheader("Sales by State")
        st.map(df.dropna(subset=["state"]))

    else:
        st.write("No data available")


if __name__ == "__main__":
    main()
