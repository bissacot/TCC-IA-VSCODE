from __future__ import annotations

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine
from src.config import settings
from src.utils.logging_config import configure_logging

logger = configure_logging()


@st.cache_data
def load_sales() -> pd.DataFrame:
    engine = create_engine(settings.postgres_url)
    df = pd.read_sql_table("sales", con=engine)
    return df


def main():
    st.title("Sales Dashboard")
    df = load_sales()
    if df.empty:
        st.warning("No sales data loaded yet. Run ETL first.")
        return

    # Filters
    min_date = df["sale_date"].min()
    max_date = df["sale_date"].max()
    start, end = st.date_input("Date range", [min_date, max_date])
    st.session_state.update({"start": start, "end": end})

    state = st.selectbox("State", options=["All"] + sorted(df["state"].dropna().unique().tolist()))
    category = st.selectbox("Category", options=["All"])  # join with products if needed

    mask = (pd.to_datetime(df["sale_date"]) >= pd.to_datetime(start)) & (pd.to_datetime(df["sale_date"]) <= pd.to_datetime(end))
    if state != "All":
        mask &= df["state"] == state
    dff = df[mask]

    # KPIs
    total_revenue = dff["total_value"].sum()
    num_sales = len(dff)
    avg_ticket = dff["total_value"].mean()
    unique_customers = dff["customer_id"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total revenue", f"${total_revenue:,.2f}")
    c2.metric("Number of sales", f"{num_sales}")
    c3.metric("Avg ticket", f"${avg_ticket:,.2f}")
    c4.metric("Unique customers", f"{unique_customers}")

    # Revenue by month
    rev_month = dff.groupby(dff["sale_date"].dt.to_period("M")).total_value.sum().reset_index()
    rev_month["sale_date"] = rev_month["sale_date"].dt.to_timestamp()
    chart = alt.Chart(rev_month).mark_line(point=True).encode(x="sale_date:T", y="total_value:Q")
    st.altair_chart(chart, use_container_width=True)

    # Top products
    top = dff.groupby("product_id").total_value.sum().nlargest(10).reset_index()
    st.bar_chart(top.set_index("product_id"))


if __name__ == "__main__":
    main()
