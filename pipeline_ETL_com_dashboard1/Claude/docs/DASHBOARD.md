# Dashboard User Guide

## Overview

The Streamlit Dashboard provides real-time analytics and insights into sales performance with interactive visualizations and filtering capabilities.

## Accessing the Dashboard

### Local Development

```bash
streamlit run src/dashboard/app.py
```

Access at: **http://localhost:8501**

### Docker

```bash
docker-compose up dashboard
```

Access at: **http://localhost:8501**

## Dashboard Components

### 1. KPI Cards

Located at the top of the dashboard, displaying four key metrics:

#### Total Revenue
- **Metric**: Sum of all sales values
- **Format**: R$ currency
- **Delta**: Percentage change indicator
- **Usage**: Monitor overall business performance

#### Total Sales
- **Metric**: Number of completed transactions
- **Format**: Integer count
- **Delta**: Percentage change indicator
- **Usage**: Track sales volume

#### Average Ticket
- **Metric**: Mean value per transaction
- **Formula**: Total Revenue ÷ Total Sales
- **Format**: R$ currency
- **Usage**: Monitor transaction size trends

#### Unique Customers
- **Metric**: Count of distinct customers
- **Format**: Integer count
- **Delta**: Percentage change indicator
- **Usage**: Track customer base growth

### 2. Filters & Controls

Located in the left sidebar, providing multi-dimensional filtering:

#### Date Range Filter
- **Default**: Last 365 days
- **Usage**: Focus on specific time periods
- **Impact**: Applies to all visualizations

```
Example: Select Jan 1 - Dec 31, 2024
```

#### State Filter
- **Options**: All Brazilian states (SP, RJ, MG, etc.)
- **Type**: Multi-select
- **Usage**: Geographic analysis

```
Example: Select SP, RJ, MG
```

#### Category Filter
- **Options**: All product categories
- **Type**: Multi-select
- **Default**: All categories
- **Usage**: Product line analysis

```
Example: Select Electronics, Accessories
```

#### Refresh Button
- **Function**: Clear cache and reload data
- **Usage**: Ensure latest data display
- **Effect**: Retrieves fresh data from database

### 3. Revenue Trend Over Time

**Chart Type**: Line chart with markers

**Axes**:
- X-Axis: Date (Year-Month)
- Y-Axis: Revenue (R$)

**Features**:
- Hover tooltip with exact values
- Responsive to date range filter
- Zoom and pan capabilities

**Insights**:
- Identify seasonal trends
- Spot growth patterns
- Detect anomalies

```
Example:
Jan 2024: R$ 50,000
Feb 2024: R$ 65,000
Mar 2024: R$ 72,000
```

### 4. Revenue by Product Category

**Chart Type**: Pie chart

**Data**:
- Categories: All product categories
- Values: Total revenue per category
- Percentages: Category share of total revenue

**Interactions**:
- Click legend to hide/show categories
- Hover for exact values

**Use Cases**:
- Understand product mix
- Identify top-performing categories
- Spot underperforming areas

### 5. Top 10 Best-Selling Products

**Chart Type**: Horizontal bar chart

**Dimensions**:
- Y-Axis: Product name
- X-Axis: Quantity sold
- Color Scale: Revenue (blue = low, purple = high)

**Features**:
- Sorted by quantity descending
- Color represents revenue contribution
- Easy identification of star products

**Analysis**:
- Determine bestsellers
- Plan inventory
- Identify cross-sell opportunities

### 6. Sales Distribution by State

**Chart Type**: Bar chart

**Dimensions**:
- X-Axis: State code (UF)
- Y-Axis: Revenue (R$)
- Color: Number of sales (count)

**Features**:
- Sorted by revenue
- Color intensity shows transaction volume
- Hover for detailed metrics

**Geographic Insights**:
- Regional performance
- Market penetration
- Growth opportunities

### 7. Data Quality Report

**Metrics Displayed**:

| Metric | Description |
|--------|-------------|
| Total Records | All records processed in last ETL |
| Invalid Records | Records failing validation |
| Missing Values % | Percentage of null values |
| Duplicates Removed | Duplicate records detected |

**Status Indicators**:
- Last ETL Execution: Timestamp
- Execution Duration: Seconds taken

**Purpose**:
- Monitor data quality
- Identify data issues
- Track ETL health

## Using Filters

### Date Range Filter

```
1. Click "Select Date Range" in sidebar
2. Choose start date on calendar
3. Choose end date on calendar
4. Charts update automatically
```

### Multi-Select Filters

```
1. Click dropdown for State/Category
2. Select/deselect options
3. Multiple selections create OR condition
4. All visualizations update in real-time
```

### Refresh Data

```
1. Click "🔄 Refresh Data" button
2. Cache clears and database is queried
3. All visualizations update with latest data
4. Takes ~2-3 seconds
```

## Data Refresh

### Automatic Caching

- Dashboard caches data for 1 hour
- Configured by: `CACHE_TTL_SECONDS=3600`
- Improves performance for repeated queries

### Manual Refresh

- Click "🔄 Refresh Data" button to force refresh
- Useful after ETL pipeline execution
- Clears all cache and reloads data

## Performance Tips

1. **Use Date Range Filter**: Narrow time period for faster queries
2. **Limit State/Category Selection**: Fewer filters = faster results
3. **Cache Enabled**: First query is slower, subsequent queries are instant
4. **Refresh Strategically**: Only refresh when needed

## Troubleshooting

### Dashboard Not Loading

```
Problem: "Unable to fetch data"
Solution: 
- Check database connection
- Verify DATABASE_URL
- Check PostgreSQL is running
```

### Charts Show No Data

```
Problem: "No data available"
Solutions:
1. Check filters aren't too restrictive
2. Expand date range
3. Click refresh button
4. Verify ETL pipeline ran successfully
```

### Slow Performance

```
Problem: "Dashboard is slow"
Solutions:
1. Reduce time period with date filter
2. Limit state/category selection
3. Wait for cache to warm up (first query)
4. Increase CACHE_TTL_SECONDS
```

### Connection Error

```
Problem: "psycopg2.OperationalError"
Solutions:
1. Check PostgreSQL is running
2. Verify credentials in .env
3. Check network connectivity
4. Restart PostgreSQL service
```

## Export Features

### Excel Export (Coming Soon)

- Export filtered data to XLSX
- Include charts and tables
- Ready for presentations

### PDF Report (Coming Soon)

- Professional report generation
- Charts and metrics
- Company branding

## Advanced Features

### Custom Queries

Modify dashboard for custom analysis:

```python
# Edit src/dashboard/app.py
# Add new repository method
# Create new visualization

# Example: Add custom metric
custom_metric = repos["sales"].custom_query()
st.metric("Custom Metric", custom_metric)
```

### API Integration

Extend with external data:

```python
# Add API data to dashboard
import requests

response = requests.get("https://api.external.com/data")
external_data = response.json()

# Merge with database data
combined_data = merge_data(dashboard_data, external_data)
```

## Dashboard Customization

### Colors and Styling

Edit CSS in `src/dashboard/app.py`:

```python
st.markdown("""
    <style>
    .metric-value {
        color: #1f77b4;
        font-size: 32px;
    }
    </style>
""", unsafe_allow_html=True)
```

### Add New Metrics

```python
# In main() function
new_kpi = repos["sales"].calculate_custom_metric()
st.metric("Custom KPI", f"R$ {new_kpi:,.2f}")
```

### Modify Visualizations

```python
# Add new chart
fig = px.scatter(
    data,
    x="metric1",
    y="metric2",
    color="category",
    size="value"
)
st.plotly_chart(fig, use_container_width=True)
```

## Database Connection

### Connection Details

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=etl_user
DB_PASSWORD=etl_password
DB_NAME=sales_db
```

### Connection Pooling

Configured for optimal performance:
- Max connections: 20
- Overflow: 40
- Recycle: 3600 seconds

## Best Practices

1. **Regular ETL Runs**: Schedule daily to keep data fresh
2. **Monitor Quality Reports**: Watch for data anomalies
3. **Use Filters**: More focused analysis, better performance
4. **Refresh After ETL**: Click refresh after pipeline execution
5. **Document Findings**: Take screenshots and notes

## Support

For issues or feature requests:

1. Check troubleshooting section
2. Review logs in `logs/dashboard.log`
3. Check database connectivity
4. Review documentation
5. Create GitHub issue with details

## Navigation

- **Home**: Main analytics view
- **Sidebar**: Filters and controls
- **Top Section**: KPI metrics
- **Middle Section**: Visualizations
- **Bottom Section**: Quality report and export
