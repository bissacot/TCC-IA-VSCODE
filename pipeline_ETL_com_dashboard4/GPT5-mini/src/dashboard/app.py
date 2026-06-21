from typing import Optional
import streamlit as st
import pandas as pd
import sqlalchemy
from pathlib import Path
from ..config import get_settings
from ..load import get_engine
from ..logger import logger


@st.cache_data
def load_sales_data(query: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df


def build_query(filters: dict) -> str:
    q = "SELECT * FROM sales"
    clauses = []
    if filters.get('start_date'):
        clauses.append(f"sale_date >= '{filters['start_date']}'")
    if filters.get('end_date'):
        clauses.append(f"sale_date <= '{filters['end_date']}'")
    if filters.get('state') and filters['state'] != 'All':
        clauses.append(f"state = '{filters['state']}'")
    if clauses:
        q += ' WHERE ' + ' AND '.join(clauses)
    return q


def main():
    st.title("Sales Dashboard")
    st.sidebar.header("Filters")
    start = st.sidebar.date_input("Start date")
    end = st.sidebar.date_input("End date")
    state = st.sidebar.selectbox("State", options=["All"])

    filters = {'start_date': start, 'end_date': end, 'state': state}
    query = build_query(filters)
    df = load_sales_data(query)

    if df.empty:
        st.warning("No sales data available")
        return

    total_revenue = df['total_value'].sum()
    num_sales = len(df)
    avg_ticket = df['total_value'].mean()
    unique_customers = df['customer_id'].nunique()

    st.metric("Total revenue", f"${total_revenue:,.2f}")
    st.metric("Number of sales", f"{num_sales}")
    st.metric("Avg. ticket", f"${avg_ticket:,.2f}")
    st.metric("Unique customers", f"{unique_customers}")

    st.subheader("Revenue by month")
    df['month'] = pd.to_datetime(df['sale_date']).dt.to_period('M')
    rev_by_month = df.groupby('month')['total_value'].sum().reset_index()
    rev_by_month['month'] = rev_by_month['month'].astype(str)
    st.bar_chart(rev_by_month.rename(columns={'month':'index'}).set_index('month'))

    st.subheader("Top 10 Products")
    top = df.groupby('product_id')['quantity'].sum().nlargest(10).reset_index()
    st.table(top)


if __name__ == '__main__':
    main()
