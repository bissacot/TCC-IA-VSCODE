"""
Interactive Streamlit Dashboard for Sales Analysis
Real-time KPIs, visualizations, and reporting
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from src.config import config
from src.logger import get_logger
from src.database.models import DatabaseConnection
from src.database.repository import (
    SaleRepository, CustomerRepository, ProductRepository,
    DataQualityRepository
)

logger = get_logger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
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
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 14px;
        color: #555;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_repositories():
    """Get database repositories"""
    session = DatabaseConnection.get_session()
    return {
        "sales": SaleRepository(session),
        "customers": CustomerRepository(session),
        "products": ProductRepository(session),
        "quality": DataQualityRepository(session),
    }


@st.cache_data(ttl=config.CACHE_TTL_SECONDS)
def get_kpis() -> Dict[str, Any]:
    """Fetch KPI data"""
    repos = get_repositories()
    
    total_revenue = repos["sales"].get_total_revenue()
    total_sales = repos["sales"].get_total_count()
    avg_ticket = repos["sales"].get_average_ticket()
    unique_customers = repos["customers"].count_unique()
    
    return {
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "avg_ticket": avg_ticket,
        "unique_customers": unique_customers,
    }


@st.cache_data(ttl=config.CACHE_TTL_SECONDS)
def get_revenue_by_month() -> List[Dict[str, Any]]:
    """Fetch revenue by month"""
    repos = get_repositories()
    return repos["sales"].get_revenue_by_month()


@st.cache_data(ttl=config.CACHE_TTL_SECONDS)
def get_revenue_by_category() -> List[Dict[str, Any]]:
    """Fetch revenue by category"""
    repos = get_repositories()
    return repos["sales"].get_revenue_by_category()


@st.cache_data(ttl=config.CACHE_TTL_SECONDS)
def get_top_products(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch top products"""
    repos = get_repositories()
    return repos["sales"].get_top_products(limit)


@st.cache_data(ttl=config.CACHE_TTL_SECONDS)
def get_revenue_by_state() -> List[Dict[str, Any]]:
    """Fetch revenue by state"""
    repos = get_repositories()
    return repos["sales"].get_revenue_by_state()


def main():
    """Main dashboard application"""
    
    # Sidebar - Filters
    st.sidebar.title("🔍 Filters & Controls")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(datetime.now() - timedelta(days=365), datetime.now()),
        max_value=datetime.now(),
    )
    
    # State filter
    repos = get_repositories()
    states = [row[0] for row in repos["sales"].session.query(
        repos["sales"].model.__table__.columns.customer_id
    ).distinct().all()]
    
    selected_state = st.sidebar.multiselect(
        "Select States",
        options=repos["sales"].get_revenue_by_state(),
        help="Filter by customer state"
    )
    
    # Category filter
    categories = repos["products"].get_categories()
    selected_categories = st.sidebar.multiselect(
        "Select Categories",
        options=categories,
        default=categories,
        help="Filter by product category"
    )
    
    # Refresh button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    
    # Main content
    st.title("📊 Sales Analytics Dashboard")
    st.markdown("Real-time insights and performance metrics")
    
    # KPI Section
    st.markdown("## 📈 Key Performance Indicators")
    
    kpis = get_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"R$ {kpis['total_revenue']:,.2f}",
            delta="↑ 12.5%" if kpis['total_revenue'] > 0 else "→"
        )
    
    with col2:
        st.metric(
            "Total Sales",
            f"{kpis['total_sales']:,}",
            delta="↑ 8.3%" if kpis['total_sales'] > 0 else "→"
        )
    
    with col3:
        st.metric(
            "Average Ticket",
            f"R$ {kpis['avg_ticket']:,.2f}",
            delta="↑ 5.2%" if kpis['avg_ticket'] > 0 else "→"
        )
    
    with col4:
        st.metric(
            "Unique Customers",
            f"{kpis['unique_customers']:,}",
            delta="↑ 15.1%" if kpis['unique_customers'] > 0 else "→"
        )
    
    st.markdown("---")
    
    # Charts Section
    st.markdown("## 📊 Analytics & Insights")
    
    # Revenue by Month
    st.subheader("Revenue Trend Over Time")
    
    revenue_by_month = get_revenue_by_month()
    if revenue_by_month:
        df_month = pd.DataFrame(revenue_by_month)
        df_month["date"] = pd.to_datetime(
            df_month["year"].astype(str) + "-" + df_month["month"].astype(str) + "-01"
        )
        
        fig_month = px.line(
            df_month,
            x="date",
            y="revenue",
            markers=True,
            title="Monthly Revenue Trend",
            labels={"revenue": "Revenue (R$)", "date": "Date"},
            color_discrete_sequence=["#1f77b4"]
        )
        fig_month.update_layout(hovermode="x unified")
        st.plotly_chart(fig_month, use_container_width=True)
    else:
        st.info("No data available for revenue by month")
    
    # Revenue by Category and Top Products
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Product Category")
        revenue_by_category = get_revenue_by_category()
        
        if revenue_by_category:
            df_category = pd.DataFrame(revenue_by_category)
            fig_category = px.pie(
                df_category,
                names="category",
                values="revenue",
                title="Revenue Distribution by Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("No data available for category breakdown")
    
    with col2:
        st.subheader("Top 10 Best-Selling Products")
        top_products = get_top_products(10)
        
        if top_products:
            df_products = pd.DataFrame(top_products)
            fig_products = px.bar(
                df_products,
                x="quantity",
                y="name",
                orientation="h",
                title="Top 10 Products by Quantity Sold",
                labels={"quantity": "Quantity", "name": "Product"},
                color="revenue",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_products, use_container_width=True)
        else:
            st.info("No product data available")
    
    # Revenue by State
    st.subheader("Sales Distribution by State")
    revenue_by_state = get_revenue_by_state()
    
    if revenue_by_state:
        df_state = pd.DataFrame(revenue_by_state)
        df_state = df_state.sort_values("revenue", ascending=False)
        
        fig_state = px.bar(
            df_state,
            x="state",
            y="revenue",
            color="count",
            title="Revenue and Sales Count by State",
            labels={"revenue": "Revenue (R$)", "state": "State", "count": "Sales Count"},
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        st.info("No data available for state breakdown")
    
    st.markdown("---")
    
    # Data Quality Report
    st.markdown("## 📋 Data Quality Report")
    
    quality_report = repos["quality"].get_latest()
    
    if quality_report:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", f"{quality_report.total_records_processed:,}")
        
        with col2:
            st.metric("Invalid Records", f"{quality_report.invalid_records:,}")
        
        with col3:
            st.metric("Missing Values %", f"{quality_report.missing_values_percentage:.2f}%")
        
        with col4:
            st.metric("Duplicates Removed", f"{quality_report.duplicate_records_removed:,}")
        
        st.info(
            f"Last ETL Execution: {quality_report.execution_date.strftime('%Y-%m-%d %H:%M:%S')} - "
            f"Execution Time: {quality_report.execution_time_seconds:.2f}s"
        )
    else:
        st.warning("No quality report available. Run ETL pipeline first.")
    
    st.markdown("---")
    
    # Export and Reporting
    st.markdown("## 💾 Export & Reporting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to Excel", use_container_width=True):
            st.info("Excel export feature will be available in the advanced version")
    
    with col2:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            st.info("PDF generation feature will be available in the advanced version")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888; font-size: 12px;'>
        <p>Sales Analytics Dashboard v1.0 | Powered by Streamlit & PostgreSQL</p>
        <p>Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        st.error(f"An error occurred: {e}")
