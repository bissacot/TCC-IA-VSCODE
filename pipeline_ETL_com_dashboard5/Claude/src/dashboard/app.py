"""
Streamlit Dashboard for Sales Analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import psycopg2
from src.database.connection import DatabaseConnection
from src.utils.logger import get_logger
from src.utils.config import Config


logger = get_logger()


class SalesDashboard:
    """Streamlit Sales Analytics Dashboard."""

    def __init__(self):
        self.db = DatabaseConnection()
        self.logger = get_logger()
        self.setup_page()

    def setup_page(self) -> None:
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title="Sales Analytics Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
            <style>
            .main {
                padding-top: 2rem;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 5px solid #1f77b4;
            }
            </style>
        """, unsafe_allow_html=True)

    def get_sales_data(self, filters: Dict) -> pd.DataFrame:
        """Fetch sales data with applied filters."""
        try:
            self.db.connect()
            
            query = """
                SELECT * FROM sales_summary 
                WHERE 1=1
            """
            
            params = []
            
            if filters['start_date']:
                query += " AND sale_date >= %s"
                params.append(filters['start_date'])
            
            if filters['end_date']:
                query += " AND sale_date <= %s"
                params.append(filters['end_date'])
            
            if filters['states']:
                placeholders = ','.join(['%s'] * len(filters['states']))
                query += f" AND state IN ({placeholders})"
                params.extend(filters['states'])
            
            if filters['categories']:
                placeholders = ','.join(['%s'] * len(filters['categories']))
                query += f" AND category IN ({placeholders})"
                params.extend(filters['categories'])
            
            if filters['products']:
                placeholders = ','.join(['%s'] * len(filters['products']))
                query += f" AND product_id IN ({placeholders})"
                params.extend(filters['products'])
            
            query += " ORDER BY sale_date DESC"
            
            results = self.db.execute_query(query, params)
            return pd.DataFrame(results)
        
        finally:
            self.db.disconnect()

    def get_kpis(self, df: pd.DataFrame) -> Dict:
        """Calculate KPI metrics."""
        if df.empty:
            return {
                'total_revenue': 0,
                'number_of_sales': 0,
                'average_ticket_size': 0,
                'unique_customers': 0,
            }
        
        return {
            'total_revenue': df['total_value'].sum(),
            'number_of_sales': len(df),
            'average_ticket_size': df['total_value'].mean(),
            'unique_customers': df['customer_id'].nunique(),
        }

    def render_kpi_cards(self, kpis: Dict) -> None:
        """Render KPI metric cards."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Revenue",
                value=f"${kpis['total_revenue']:,.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Number of Sales",
                value=f"{kpis['number_of_sales']:,}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Average Ticket Size",
                value=f"${kpis['average_ticket_size']:,.2f}",
                delta=None
            )
        
        with col4:
            st.metric(
                label="Unique Customers",
                value=f"{kpis['unique_customers']:,}",
                delta=None
            )

    def render_filters(self) -> Dict:
        """Render filter controls."""
        st.sidebar.header("Filters")
        
        # Date range
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.sidebar.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=90)
            )
        with col2:
            end_date = st.sidebar.date_input(
                "End Date",
                value=datetime.now()
            )
        
        # States filter
        try:
            self.db.connect()
            states_result = self.db.execute_query("SELECT DISTINCT state FROM sales WHERE state IS NOT NULL ORDER BY state")
            self.db.disconnect()
            available_states = [row['state'] for row in states_result if row['state']]
        except:
            available_states = []
        
        states = st.sidebar.multiselect(
            "States",
            options=available_states,
            default=[]
        )
        
        # Categories filter
        try:
            self.db.connect()
            categories_result = self.db.execute_query("SELECT DISTINCT category FROM products ORDER BY category")
            self.db.disconnect()
            available_categories = [row['category'] for row in categories_result if row['category']]
        except:
            available_categories = []
        
        categories = st.sidebar.multiselect(
            "Categories",
            options=available_categories,
            default=[]
        )
        
        # Products filter
        try:
            self.db.connect()
            products_result = self.db.execute_query("SELECT product_id, name FROM products ORDER BY name LIMIT 100")
            self.db.disconnect()
            available_products = {row['product_id']: row['name'] for row in products_result}
        except:
            available_products = {}
        
        products = st.sidebar.multiselect(
            "Products",
            options=list(available_products.keys()),
            format_func=lambda x: available_products.get(x, x),
            default=[]
        )
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'states': states if states else None,
            'categories': categories if categories else None,
            'products': products if products else None,
        }

    def render_revenue_by_month(self, df: pd.DataFrame) -> None:
        """Render revenue by month chart."""
        st.subheader("Revenue Trend Over Time")
        
        if df.empty:
            st.info("No data available for the selected filters")
            return
        
        # Group by month
        df['month_date'] = pd.to_datetime(df['sale_date']).dt.to_period('M')
        monthly_data = df.groupby('month_date')['total_value'].sum().reset_index()
        monthly_data['month_date'] = monthly_data['month_date'].astype(str)
        
        fig = px.line(
            monthly_data,
            x='month_date',
            y='total_value',
            markers=True,
            title="Revenue by Month",
            labels={'total_value': 'Revenue ($)', 'month_date': 'Month'}
        )
        fig.update_layout(hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

    def render_revenue_by_category(self, df: pd.DataFrame) -> None:
        """Render revenue by product category."""
        st.subheader("Revenue by Category")
        
        if df.empty:
            st.info("No data available for the selected filters")
            return
        
        category_data = df.groupby('category')['total_value'].sum().reset_index()
        category_data = category_data.sort_values('total_value', ascending=False)
        
        fig = px.pie(
            category_data,
            values='total_value',
            names='category',
            title="Revenue Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_top_products(self, df: pd.DataFrame) -> None:
        """Render top 10 best-selling products."""
        st.subheader("Top 10 Best-Selling Products")
        
        if df.empty:
            st.info("No data available for the selected filters")
            return
        
        product_data = df.groupby('product_name').agg({
            'total_value': 'sum',
            'quantity': 'sum'
        }).reset_index()
        product_data = product_data.sort_values('total_value', ascending=False).head(10)
        
        fig = px.bar(
            product_data,
            x='product_name',
            y='total_value',
            title="Top 10 Products by Revenue",
            labels={'total_value': 'Revenue ($)', 'product_name': 'Product'},
            color='quantity'
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    def render_sales_by_state(self, df: pd.DataFrame) -> None:
        """Render sales distribution by state."""
        st.subheader("Sales Distribution by State")
        
        if df.empty:
            st.info("No data available for the selected filters")
            return
        
        state_data = df.groupby('state').agg({
            'total_value': 'sum',
            'sale_id': 'count'
        }).reset_index()
        state_data.columns = ['state', 'revenue', 'number_of_sales']
        state_data = state_data.sort_values('revenue', ascending=False)
        
        fig = px.bar(
            state_data,
            x='state',
            y='revenue',
            title="Revenue by State",
            labels={'revenue': 'Revenue ($)', 'state': 'State'},
            color='number_of_sales'
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_data_table(self, df: pd.DataFrame) -> None:
        """Render detailed data table."""
        st.subheader("Sales Data Details")
        
        if df.empty:
            st.info("No data available for the selected filters")
            return
        
        # Display preview
        display_df = df[[
            'sale_id', 'customer_name', 'product_name', 'quantity',
            'unit_price', 'total_value', 'sale_date', 'state', 'category'
        ]].copy()
        
        st.dataframe(display_df, use_container_width=True, height=400)

    def run(self) -> None:
        """Run the dashboard."""
        st.title("📊 Sales Analytics Dashboard")
        
        # Render filters
        filters = self.render_filters()
        
        # Fetch and display data
        try:
            sales_data = self.get_sales_data(filters)
            
            # Display KPIs
            kpis = self.get_kpis(sales_data)
            self.render_kpi_cards(kpis)
            
            # Display visualizations
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                self.render_revenue_by_month(sales_data)
            with col2:
                self.render_revenue_by_category(sales_data)
            
            col1, col2 = st.columns(2)
            with col1:
                self.render_top_products(sales_data)
            with col2:
                self.render_sales_by_state(sales_data)
            
            st.divider()
            self.render_data_table(sales_data)
            
        except Exception as e:
            self.logger.error(f"Error running dashboard: {str(e)}")
            st.error(f"Error loading dashboard data: {str(e)}")


if __name__ == "__main__":
    dashboard = SalesDashboard()
    dashboard.run()
