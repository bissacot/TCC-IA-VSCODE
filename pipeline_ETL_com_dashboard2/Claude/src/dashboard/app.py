"""
Streamlit Dashboard for Sales Analysis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session

from src.database.connection import DatabaseManager
from src.database.models import Sale, Customer, Product, DataQualityMetric
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class SalesDashboard:
    """Sales Analytics Dashboard."""

    def __init__(self) -> None:
        """Initialize dashboard."""
        self.session: Session = DatabaseManager.get_session()
        logger.info("Initialized Sales Dashboard")

    def close(self) -> None:
        """Close database session."""
        if self.session:
            self.session.close()

    @st.cache_data(ttl=300)
    def get_sales_data(self, _start_date=None, _end_date=None, state=None, category=None, product=None):
        """
        Get sales data with optional filters.

        Args:
            _start_date: Start date filter
            _end_date: End date filter
            state: State filter
            category: Product category filter
            product: Product filter

        Returns:
            DataFrame with sales data
        """
        query = self.session.query(Sale).join(Customer).join(Product)

        if _start_date:
            query = query.filter(Sale.sale_date >= _start_date)
        if _end_date:
            query = query.filter(Sale.sale_date <= _end_date)
        if state:
            query = query.filter(Customer.state == state)
        if category:
            query = query.filter(Product.category == category)
        if product:
            query = query.filter(Product.product_id == product)

        sales = query.all()
        
        # Convert to DataFrame
        data = []
        for sale in sales:
            data.append({
                'sale_id': sale.sale_id,
                'customer_id': sale.customer_id,
                'product_id': sale.product_id,
                'customer_name': sale.customer.name,
                'state': sale.customer.state,
                'product_name': sale.product.name,
                'category': sale.product.category,
                'quantity': sale.quantity,
                'unit_price': sale.unit_price,
                'total_value': sale.total_value,
                'sale_date': sale.sale_date,
                'year': sale.year,
                'month': sale.month,
                'quarter': sale.quarter,
            })

        return pd.DataFrame(data)

    def get_kpis(self, df: pd.DataFrame) -> dict:
        """Calculate KPIs from sales data."""
        return {
            'total_revenue': df['total_value'].sum(),
            'num_sales': len(df),
            'avg_ticket': df['total_value'].mean(),
            'num_customers': df['customer_id'].nunique(),
        }

    def plot_revenue_by_month(self, df: pd.DataFrame):
        """Plot revenue by month."""
        if df.empty:
            st.warning("No data available for this period")
            return

        monthly_revenue = df.groupby([df['sale_date'].dt.to_period('M')])['total_value'].sum()
        monthly_revenue.index = monthly_revenue.index.to_timestamp()

        fig = px.line(
            x=monthly_revenue.index,
            y=monthly_revenue.values,
            markers=True,
            title="Revenue by Month",
            labels={'x': 'Month', 'y': 'Revenue (R$)'},
        )
        fig.update_layout(hovermode='x unified', height=400)
        st.plotly_chart(fig, use_container_width=True)

    def plot_revenue_by_category(self, df: pd.DataFrame):
        """Plot revenue by product category."""
        if df.empty:
            st.warning("No data available")
            return

        category_revenue = df.groupby('category')['total_value'].sum().sort_values(ascending=False)

        fig = px.bar(
            x=category_revenue.index,
            y=category_revenue.values,
            title="Revenue by Product Category",
            labels={'x': 'Category', 'y': 'Revenue (R$)'},
            color=category_revenue.values,
            color_continuous_scale='Viridis',
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    def plot_top_products(self, df: pd.DataFrame, n: int = 10):
        """Plot top N best-selling products."""
        if df.empty:
            st.warning("No data available")
            return

        top_products = df.groupby('product_name')['total_value'].sum().nlargest(n)

        fig = px.barh(
            x=top_products.values,
            y=top_products.index,
            title=f"Top {n} Best-Selling Products",
            labels={'x': 'Revenue (R$)', 'y': 'Product'},
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    def plot_sales_by_state(self, df: pd.DataFrame):
        """Plot sales distribution by state."""
        if df.empty:
            st.warning("No data available")
            return

        state_sales = df.groupby('state').agg({
            'total_value': 'sum',
            'sale_id': 'count'
        }).rename(columns={'sale_id': 'num_sales'}).sort_values('total_value', ascending=False).head(10)

        fig = px.bar(
            x=state_sales.index,
            y=state_sales['total_value'],
            title="Top 10 States by Revenue",
            labels={'x': 'State', 'y': 'Revenue (R$)'},
            color=state_sales['total_value'],
            color_continuous_scale='Plasma',
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    def plot_sales_trends(self, df: pd.DataFrame):
        """Plot sales trends over time."""
        if df.empty:
            st.warning("No data available")
            return

        daily_sales = df.groupby(df['sale_date'].dt.date)['total_value'].agg(['sum', 'count'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_sales.index,
            y=daily_sales['sum'],
            mode='lines+markers',
            name='Revenue',
            yaxis='y1',
        ))
        fig.add_trace(go.Bar(
            x=daily_sales.index,
            y=daily_sales['count'],
            name='Number of Sales',
            yaxis='y2',
            opacity=0.6,
        ))

        fig.update_layout(
            title="Sales Trends Over Time",
            hovermode='x unified',
            height=400,
            yaxis=dict(title='Revenue (R$)'),
            yaxis2=dict(title='Number of Sales', overlaying='y', side='right'),
        )
        st.plotly_chart(fig, use_container_width=True)

    def plot_sales_pie(self, df: pd.DataFrame):
        """Plot sales distribution by quarter."""
        if df.empty:
            st.warning("No data available")
            return

        quarterly_sales = df.groupby('quarter')['total_value'].sum()

        fig = px.pie(
            values=quarterly_sales.values,
            names=[f'Q{int(q)}' for q in quarterly_sales.index],
            title="Sales Distribution by Quarter",
            hole=0.3,
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    def display_data_quality_report(self):
        """Display latest data quality report."""
        try:
            latest_report = self.session.query(DataQualityMetric).order_by(
                DataQualityMetric.created_at.desc()
            ).first()

            if latest_report:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Records Processed", latest_report.total_records_processed)
                with col2:
                    st.metric("Invalid Records", latest_report.invalid_records)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Missing Values %",
                        f"{latest_report.missing_values_percentage:.2f}%"
                    )
                with col2:
                    st.metric("Duplicates Removed", latest_report.duplicates_removed)

                st.metric(
                    "Transformation Time",
                    f"{latest_report.transformation_time_seconds:.2f}s"
                )

                st.write(f"**Status:** {latest_report.status}")
                st.write(f"**Last Updated:** {latest_report.created_at}")
        except Exception as e:
            logger.error(f"Error displaying quality report: {str(e)}")
            st.error("Could not load data quality report")


def run_dashboard():
    """Run the Streamlit dashboard."""
    st.set_page_config(
        page_title="Sales Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📊 Sales Analytics Dashboard")
    st.markdown("---")

    # Initialize dashboard
    dashboard = SalesDashboard()

    try:
        # Sidebar filters
        st.sidebar.header("🔍 Filters")

        # Date range filter
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now(),
        )
        start_date = date_range[0] if len(date_range) > 0 else None
        end_date = date_range[1] if len(date_range) > 1 else None

        # Get unique states
        states_df = dashboard.session.query(Customer.state).distinct().all()
        states = [row[0] for row in states_df if row[0]]
        selected_state = st.sidebar.selectbox(
            "State",
            options=["All"] + states,
        )
        state_filter = None if selected_state == "All" else selected_state

        # Get unique categories
        categories_df = dashboard.session.query(Product.category).distinct().all()
        categories = [row[0] for row in categories_df if row[0]]
        selected_category = st.sidebar.selectbox(
            "Product Category",
            options=["All"] + categories,
        )
        category_filter = None if selected_category == "All" else selected_category

        # Get sales data with filters
        sales_df = dashboard.get_sales_data(
            _start_date=start_date,
            _end_date=end_date,
            state=state_filter,
            category=category_filter,
        )

        if sales_df.empty:
            st.warning("No data available for the selected filters")
        else:
            # KPIs
            st.subheader("📈 Key Performance Indicators")
            kpis = dashboard.get_kpis(sales_df)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Total Revenue",
                    f"R$ {kpis['total_revenue']:,.2f}",
                )
            with col2:
                st.metric("Number of Sales", int(kpis['num_sales']))
            with col3:
                st.metric(
                    "Average Ticket",
                    f"R$ {kpis['avg_ticket']:,.2f}",
                )
            with col4:
                st.metric("Unique Customers", int(kpis['num_customers']))

            st.markdown("---")

            # Visualizations
            st.subheader("📊 Visualizations")

            # Row 1
            col1, col2 = st.columns(2)
            with col1:
                dashboard.plot_revenue_by_month(sales_df)
            with col2:
                dashboard.plot_revenue_by_category(sales_df)

            # Row 2
            col1, col2 = st.columns(2)
            with col1:
                dashboard.plot_top_products(sales_df, n=10)
            with col2:
                dashboard.plot_sales_by_state(sales_df)

            # Row 3
            col1, col2 = st.columns(2)
            with col1:
                dashboard.plot_sales_trends(sales_df)
            with col2:
                dashboard.plot_sales_pie(sales_df)

            # Data quality section
            st.markdown("---")
            st.subheader("🔍 Data Quality Report")
            dashboard.display_data_quality_report()

            # Raw data
            st.markdown("---")
            if st.checkbox("Show Raw Data"):
                st.subheader("Raw Sales Data")
                st.dataframe(sales_df, use_container_width=True)

    finally:
        dashboard.close()


if __name__ == "__main__":
    run_dashboard()
