"""Streamlit Dashboard for Sales Analysis."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor
from src.utils.config import load_config_from_env
from src.loaders.database import DatabaseManager


class SalesDashboard:
    """Interactive Sales Analysis Dashboard."""
    
    def __init__(self):
        """Initialize dashboard."""
        self.config = load_config_from_env()
        self.db_manager = DatabaseManager(self.config.db_config)
        self._setup_page()
    
    def _setup_page(self):
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title="Sales Analytics Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.title("📊 Sales Analytics Dashboard")
    
    def _get_connection(self):
        """Get database connection."""
        return self.db_manager.get_connection()
    
    def _load_sales_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        state: Optional[str] = None,
        category: Optional[str] = None,
        product: Optional[str] = None
    ) -> pd.DataFrame:
        """Load filtered sales data from database."""
        query = """
            SELECT 
                s.sale_id,
                s.sale_date,
                s.total_value,
                s.quantity,
                c.state,
                p.category,
                p.name as product_name,
                c.name as customer_name
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            JOIN products p ON s.product_id = p.product_id
            WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND s.sale_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND s.sale_date <= %s"
            params.append(end_date)
        
        if state:
            query += " AND c.state = %s"
            params.append(state)
        
        if category:
            query += " AND p.category = %s"
            params.append(category)
        
        if product:
            query += " AND p.name = %s"
            params.append(product)
        
        query += " ORDER BY s.sale_date DESC"
        
        results = self.db_manager.execute_query(query, tuple(params) if params else None)
        return pd.DataFrame(results)
    
    def _load_kpi_data(self) -> Dict:
        """Load KPI data from database."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Total Revenue
            cursor.execute("SELECT COALESCE(SUM(total_value), 0) as total_revenue FROM sales")
            total_revenue = cursor.fetchone()['total_revenue']
            
            # Total Sales
            cursor.execute("SELECT COUNT(*) as total_sales FROM sales")
            total_sales = cursor.fetchone()['total_sales']
            
            # Average Ticket Size
            cursor.execute("SELECT COALESCE(AVG(total_value), 0) as avg_ticket FROM sales")
            avg_ticket = cursor.fetchone()['avg_ticket']
            
            # Unique Customers
            cursor.execute("SELECT COUNT(DISTINCT customer_id) as unique_customers FROM sales")
            unique_customers = cursor.fetchone()['unique_customers']
            
            cursor.close()
            
            return {
                'total_revenue': total_revenue,
                'total_sales': total_sales,
                'avg_ticket': avg_ticket,
                'unique_customers': unique_customers
            }
        
        finally:
            self.db_manager.return_connection(conn)
    
    def _get_filter_options(self) -> Dict[str, List]:
        """Get available filter options from database."""
        options = {}
        
        # Get states
        states_result = self.db_manager.execute_query(
            "SELECT DISTINCT state FROM customers WHERE state IS NOT NULL ORDER BY state"
        )
        options['states'] = [row['state'] for row in states_result]
        
        # Get categories
        categories_result = self.db_manager.execute_query(
            "SELECT DISTINCT category FROM products ORDER BY category"
        )
        options['categories'] = [row['category'] for row in categories_result]
        
        # Get products
        products_result = self.db_manager.execute_query(
            "SELECT DISTINCT name FROM products ORDER BY name"
        )
        options['products'] = [row['name'] for row in products_result]
        
        return options
    
    def run(self):
        """Run the dashboard."""
        # Sidebar - Filters
        st.sidebar.header("🔍 Filters")
        
        filter_options = self._get_filter_options()
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=90))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        selected_state = st.sidebar.selectbox(
            "State",
            options=["All"] + filter_options['states'],
            key="state_filter"
        )
        
        selected_category = st.sidebar.selectbox(
            "Category",
            options=["All"] + filter_options['categories'],
            key="category_filter"
        )
        
        selected_product = st.sidebar.selectbox(
            "Product",
            options=["All"] + filter_options['products'],
            key="product_filter"
        )
        
        # Load data with filters
        state_filter = None if selected_state == "All" else selected_state
        category_filter = None if selected_category == "All" else selected_category
        product_filter = None if selected_product == "All" else selected_product
        
        sales_df = self._load_sales_data(
            start_date=start_date,
            end_date=end_date,
            state=state_filter,
            category=category_filter,
            product=product_filter
        )
        
        # Display KPIs
        st.header("📈 Key Performance Indicators")
        kpi_data = self._load_kpi_data()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", f"${kpi_data['total_revenue']:,.2f}")
        with col2:
            st.metric("Total Sales", f"{kpi_data['total_sales']:,}")
        with col3:
            st.metric("Average Ticket Size", f"${kpi_data['avg_ticket']:.2f}")
        with col4:
            st.metric("Unique Customers", f"{kpi_data['unique_customers']:,}")
        
        # Visualizations
        if not sales_df.empty:
            st.header("📊 Analytics")
            
            # Revenue by Month
            col1, col2 = st.columns(2)
            with col1:
                monthly_revenue = sales_df.copy()
                monthly_revenue['sale_date'] = pd.to_datetime(monthly_revenue['sale_date'])
                monthly_revenue['month'] = monthly_revenue['sale_date'].dt.to_period('M')
                monthly_revenue = monthly_revenue.groupby('month')['total_value'].sum().reset_index()
                monthly_revenue['month'] = monthly_revenue['month'].astype(str)
                
                fig = px.bar(
                    monthly_revenue,
                    x='month',
                    y='total_value',
                    title="Revenue by Month",
                    labels={'month': 'Month', 'total_value': 'Revenue ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Revenue by Category
            with col2:
                category_revenue = sales_df.groupby('category')['total_value'].sum().reset_index()
                fig = px.pie(
                    category_revenue,
                    values='total_value',
                    names='category',
                    title="Revenue by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Top 10 Products
            col1, col2 = st.columns(2)
            with col1:
                top_products = sales_df.groupby('product_name')['quantity'].sum().nlargest(10).reset_index()
                fig = px.barh(
                    top_products,
                    y='product_name',
                    x='quantity',
                    title="Top 10 Best-Selling Products",
                    labels={'quantity': 'Quantity Sold', 'product_name': 'Product'}
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)
            
            # Sales by State
            with col2:
                state_sales = sales_df.groupby('state')['total_value'].sum().nlargest(10).reset_index()
                fig = px.bar(
                    state_sales,
                    x='state',
                    y='total_value',
                    title="Top 10 States by Revenue",
                    labels={'state': 'State', 'total_value': 'Revenue ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Sales Trend
            st.header("📈 Sales Trend Over Time")
            sales_trend = sales_df.copy()
            sales_trend['sale_date'] = pd.to_datetime(sales_trend['sale_date'])
            sales_trend = sales_trend.set_index('sale_date').resample('D')['total_value'].sum().reset_index()
            
            fig = px.line(
                sales_trend,
                x='sale_date',
                y='total_value',
                title="Daily Sales Trend",
                labels={'sale_date': 'Date', 'total_value': 'Revenue ($)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Data Table
            st.header("📋 Sales Data")
            st.dataframe(sales_df.head(100), use_container_width=True)
        
        else:
            st.warning("No data available for the selected filters")


def main():
    """Main function."""
    dashboard = SalesDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
