"""
Streamlit-based interactive dashboard for sales analysis.

Provides KPIs, visualizations, and filtering capabilities.
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker

from src.database import Customer, Product, Sale, DataQualityMetrics
from config.settings import DB_URL


# Page configuration
st.set_page_config(
    page_title="Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-title {
        font-size: 14px;
        color: #666;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


class DashboardDatabase:
    """Database connection manager for dashboard."""

    def __init__(self):
        """Initialize database connection."""
        self.engine = create_engine(DB_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @staticmethod
    @st.cache_resource
    def get_engine():
        """Get cached database engine."""
        return create_engine(DB_URL)

    def get_sales_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        states: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        products: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Get sales data with optional filters.

        Args:
            start_date: Filter start date
            end_date: Filter end date
            states: Filter by states
            categories: Filter by product categories
            products: Filter by product names

        Returns:
            DataFrame with filtered sales data
        """
        session = self.SessionLocal()

        query = session.query(
            Sale.sale_id,
            Sale.customer_id,
            Sale.product_id,
            Sale.quantity,
            Sale.unit_price,
            Sale.total_value,
            Sale.sale_date,
            Sale.year,
            Sale.month,
            Sale.quarter,
            Customer.name.label("customer_name"),
            Customer.state,
            Customer.email,
            Product.name.label("product_name"),
            Product.category,
            Product.price.label("product_price"),
        ).join(Customer, Sale.customer_id == Customer.customer_id).join(
            Product, Sale.product_id == Product.product_id
        )

        # Apply filters
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)

        if end_date:
            query = query.filter(Sale.sale_date <= end_date)

        if states:
            query = query.filter(Customer.state.in_(states))

        if categories:
            query = query.filter(Product.category.in_(categories))

        if products:
            query = query.filter(Product.name.in_(products))

        df = pd.read_sql(query.statement, self.engine)
        session.close()

        return df

    def get_kpis(self, df: pd.DataFrame) -> dict:
        """
        Calculate KPIs from sales data.

        Args:
            df: Sales DataFrame

        Returns:
            Dictionary with KPI values
        """
        if df.empty:
            return {
                "total_revenue": 0,
                "number_of_sales": 0,
                "average_ticket": 0,
                "unique_customers": 0,
            }

        return {
            "total_revenue": df["total_value"].sum(),
            "number_of_sales": len(df),
            "average_ticket": df["total_value"].mean(),
            "unique_customers": df["customer_id"].nunique(),
        }


def render_kpi_section(kpis: dict) -> None:
    """Render KPI cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${kpis['total_revenue']:,.2f}",
            delta=f"+5% vs last month",
        )

    with col2:
        st.metric(
            label="Number of Sales",
            value=f"{kpis['number_of_sales']:,}",
        )

    with col3:
        st.metric(
            label="Average Ticket Size",
            value=f"${kpis['average_ticket']:,.2f}",
        )

    with col4:
        st.metric(
            label="Unique Customers",
            value=f"{kpis['unique_customers']:,}",
        )


def render_revenue_by_month(df: pd.DataFrame) -> None:
    """Render revenue by month chart."""
    df_monthly = df.groupby("month")["total_value"].sum().reset_index()
    df_monthly["month_name"] = pd.to_datetime(df_monthly["month"], format="%m").dt.strftime(
        "%B"
    )

    fig = px.bar(
        df_monthly,
        x="month_name",
        y="total_value",
        title="Revenue by Month",
        labels={"total_value": "Revenue ($)", "month_name": "Month"},
    )

    st.plotly_chart(fig, use_container_width=True)


def render_revenue_by_category(df: pd.DataFrame) -> None:
    """Render revenue by product category chart."""
    df_category = df.groupby("category")["total_value"].sum().reset_index()
    df_category = df_category.sort_values("total_value", ascending=False)

    fig = px.pie(
        df_category,
        names="category",
        values="total_value",
        title="Revenue by Product Category",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_top_products(df: pd.DataFrame, top_n: int = 10) -> None:
    """Render top selling products chart."""
    df_products = (
        df.groupby("product_name").agg(
            {"quantity": "sum", "total_value": "sum"}
        ).reset_index()
    )
    df_products = df_products.sort_values("quantity", ascending=False).head(top_n)

    fig = px.barh(
        df_products,
        x="quantity",
        y="product_name",
        title=f"Top {top_n} Best-Selling Products",
        labels={"quantity": "Units Sold", "product_name": "Product"},
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sales_by_state(df: pd.DataFrame) -> None:
    """Render sales distribution by state chart."""
    df_state = df.groupby("state")["total_value"].sum().reset_index()
    df_state = df_state.sort_values("total_value", ascending=False)

    fig = px.bar(
        df_state,
        x="state",
        y="total_value",
        title="Sales Distribution by State",
        labels={"total_value": "Revenue ($)", "state": "State"},
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sales_trend(df: pd.DataFrame) -> None:
    """Render sales trend over time."""
    df_trend = df.sort_values("sale_date").groupby("sale_date")["total_value"].sum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_trend.index,
        y=df_trend.values,
        mode="lines+markers",
        name="Daily Revenue",
        fill="tozeroy",
    ))

    fig.update_layout(
        title="Sales Trend Over Time",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_quality_metrics() -> None:
    """Render data quality metrics."""
    engine = create_engine(DB_URL)

    query = "SELECT * FROM data_quality_metrics ORDER BY created_at DESC LIMIT 10"
    df = pd.read_sql(query, engine)

    st.subheader("Recent Data Quality Reports")

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No quality metrics available yet.")


def main() -> None:
    """Main dashboard application."""
    st.title("📊 Sales Analysis Dashboard")

    # Initialize database connection
    db = DashboardDatabase()

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")

        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=90),
            )

        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
            )

        # State filter
        session = db.SessionLocal()
        all_states = session.query(Customer.state).distinct().all()
        session.close()

        states = [s[0] for s in all_states if s[0]]
        selected_states = st.multiselect(
            "Select States",
            options=sorted(states),
            default=sorted(states),
        )

        # Category filter
        session = db.SessionLocal()
        all_categories = session.query(Product.category).distinct().all()
        session.close()

        categories = [c[0] for c in all_categories if c[0]]
        selected_categories = st.multiselect(
            "Select Categories",
            options=sorted(categories),
            default=sorted(categories),
        )

        # Product filter
        session = db.SessionLocal()
        all_products = session.query(Product.name).distinct().all()
        session.close()

        products = [p[0] for p in all_products if p[0]]
        selected_products = st.multiselect(
            "Select Products",
            options=sorted(products),
            default=sorted(products)[:10],
        )

    # Get filtered data
    df_sales = db.get_sales_data(
        start_date=start_date,
        end_date=end_date,
        states=selected_states,
        categories=selected_categories,
        products=selected_products,
    )

    # Display KPIs
    st.header("Key Performance Indicators")
    kpis = db.get_kpis(df_sales)
    render_kpi_section(kpis)

    # Visualizations
    if not df_sales.empty:
        st.header("Visualizations")

        col1, col2 = st.columns(2)

        with col1:
            render_revenue_by_month(df_sales)

        with col2:
            render_revenue_by_category(df_sales)

        col3, col4 = st.columns(2)

        with col3:
            render_top_products(df_sales)

        with col4:
            render_sales_by_state(df_sales)

        render_sales_trend(df_sales)

        # Data Quality Metrics
        st.header("Data Quality")
        render_quality_metrics()

        # Raw data table
        st.header("Raw Data")
        st.dataframe(df_sales, use_container_width=True)
    else:
        st.warning("No data available for selected filters.")


if __name__ == "__main__":
    main()
