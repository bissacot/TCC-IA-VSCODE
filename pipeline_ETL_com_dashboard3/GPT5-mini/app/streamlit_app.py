import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from src.etl.config import settings

def make_engine():
    url = (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    return create_engine(url, future=True)


@st.cache_data
def load_sales(engine):
    query = "SELECT s.*, p.category, p.name as product_name, c.name as customer_name FROM sales s LEFT JOIN products p ON s.product_id=p.product_id LEFT JOIN customers c ON s.customer_id=c.customer_id"
    return pd.read_sql(query, con=engine)


def main():
    st.set_page_config(page_title="Sales Dashboard", layout="wide")
    st.title("Sales Dashboard")
    engine = make_engine()
    df = load_sales(engine)
    if df.empty:
        st.warning("No sales data available. Run ETL first.")
        return

    # Filters
    min_date = df["sale_date"].min()
    max_date = df["sale_date"].max()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date))
    state = st.sidebar.multiselect("State", options=sorted(df["state"].dropna().unique()))
    category = st.sidebar.multiselect("Category", options=sorted(df["category"].dropna().unique()))
    product = st.sidebar.multiselect("Product", options=sorted(df["product_name"].dropna().unique()))

    q = df.copy()
    if date_range and len(date_range) == 2:
        start, end = date_range
        q = q[(q["sale_date"] >= pd.to_datetime(start)) & (q["sale_date"] <= pd.to_datetime(end))]
    if state:
        q = q[q["state"].isin(state)]
    if category:
        q = q[q["category"].isin(category)]
    if product:
        q = q[q["product_name"].isin(product)]

    # KPIs
    total_revenue = q["total_value"].sum()
    num_sales = len(q)
    avg_ticket = q["total_value"].mean()
    unique_customers = q["customer_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total revenue", f"${total_revenue:,.2f}")
    col2.metric("Number of sales", f"{num_sales}")
    col3.metric("Avg ticket", f"${(avg_ticket or 0):,.2f}")
    col4.metric("Unique customers", f"{unique_customers}")

    st.subheader("Revenue by month")
    rev_month = q.groupby(["year", "month"])["total_value"].sum().reset_index()
    rev_month["date"] = pd.to_datetime(rev_month["year"].astype(str) + "-" + rev_month["month"].astype(str) + "-01")
    st.line_chart(rev_month.set_index("date")["total_value"]) 

    st.subheader("Top 10 Products")
    top = q.groupby(["product_id", "product_name"])["total_value"].sum().reset_index().nlargest(10, "total_value")
    st.bar_chart(top.set_index("product_name")["total_value"])

    st.subheader("Revenue by Category")
    cat = q.groupby("category")["total_value"].sum()
    st.bar_chart(cat)

    st.subheader("Sales distribution by state")
    st.map(q.dropna(subset=["state"]))

    st.download_button("Export Excel", data=q.to_excel(index=False, engine="openpyxl"), file_name="sales.xlsx")


if __name__ == "__main__":
    main()
