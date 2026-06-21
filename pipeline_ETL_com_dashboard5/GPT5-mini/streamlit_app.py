import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)

@st.cache_data
def load_data(query: str):
    engine = create_engine(settings.database_url)
    return pd.read_sql(query, engine)

st.title('Sales Dashboard')

# Filters
with st.sidebar:
    start_date = st.date_input('Start date')
    end_date = st.date_input('End date')
    state = st.selectbox('State', options=['All'])
    category = st.selectbox('Category', options=['All'])
    product = st.selectbox('Product', options=['All'])

# Data
query_sales = 'SELECT * FROM sales'
query_products = 'SELECT * FROM products'
query_customers = 'SELECT * FROM customers'

sales = load_data(query_sales)
products = load_data(query_products)
customers = load_data(query_customers)

if sales.empty:
    st.warning('No sales data found. Run ETL first.')

# KPI
total_revenue = sales['total_value'].sum()
num_sales = len(sales)
avg_ticket = total_revenue / num_sales if num_sales else 0
unique_customers = sales['customer_id'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Revenue', f"{total_revenue:.2f}")
col2.metric('Number of Sales', f"{num_sales}")
col3.metric('Avg Ticket', f"{avg_ticket:.2f}")
col4.metric('Unique Customers', f"{unique_customers}")

# Revenue by month
rev_by_month = sales.groupby(['year','month'])['total_value'].sum().reset_index()
rev_by_month['month_str'] = rev_by_month['year'].astype(str) + '-' + rev_by_month['month'].astype(str)
fig = px.line(rev_by_month, x='month_str', y='total_value', title='Revenue by Month')
st.plotly_chart(fig, use_container_width=True)

# Top products
top_products = sales.groupby('product_id')['total_value'].sum().reset_index().nlargest(10,'total_value')
fig2 = px.bar(top_products, x='product_id', y='total_value', title='Top 10 Products')
st.plotly_chart(fig2, use_container_width=True)

# Revenue by category
sales_with_prod = sales.merge(products, left_on='product_id', right_on='product_id', how='left')
rev_by_cat = sales_with_prod.groupby('category')['total_value'].sum().reset_index()
fig3 = px.pie(rev_by_cat, names='category', values='total_value', title='Revenue by Category')
st.plotly_chart(fig3, use_container_width=True)

# Sales distribution by state
by_state = sales.groupby('state')['total_value'].sum().reset_index()
fig4 = px.bar(by_state, x='state', y='total_value', title='Revenue by State')
st.plotly_chart(fig4, use_container_width=True)

# Export options
with st.expander('Exports & Reports'):
    if st.button('Export KPIs PDF'):
        from src.utils import export_kpis_pdf
        kpis = {'total_revenue': total_revenue, 'num_sales': num_sales, 'avg_ticket': avg_ticket, 'unique_customers': unique_customers}
        export_kpis_pdf(kpis, 'kpis.pdf')
        st.success('kpis.pdf generated')
    if st.button('Export Sales Excel'):
        sales.to_excel('sales_export.xlsx', index=False)
        st.success('sales_export.xlsx generated')
