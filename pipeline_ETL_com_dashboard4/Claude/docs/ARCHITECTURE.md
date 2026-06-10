# System Architecture

## Overview

The Sales ETL Dashboard is a modern, scalable ETL (Extract, Transform, Load) system with an interactive analytics dashboard. It follows a modular, layered architecture with clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interface Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Streamlit Interactive Dashboard                 │  │
│  │  • KPI Cards  • Visualizations  • Filters  • Reports    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ETL Pipeline Orchestrator                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │  Extractor   │→ │ Transformer  │→ │   Loader    │   │  │
│  │  │ (CSV/JSON/   │  │ (Clean/      │  │ (PostgreSQL)│   │  │
│  │  │  API)        │  │  Validate)   │  │             │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Data & Persistence Layer                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             PostgreSQL Database                         │  │
│  │  ┌─────────┐  ┌─────────┐  ┌────────┐  ┌────────────┐ │  │
│  │  │Customers│  │ Products│  │ Sales  │  │Quality     │ │  │
│  │  │  Table  │  │  Table  │  │ Table  │  │ Metrics    │ │  │
│  │  └─────────┘  └─────────┘  └────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Layered Architecture

### 1. **Data Source Layer**
Handles interaction with external data sources:
- **CSV Extractor**: Reads sales data from CSV files
- **JSON Extractor**: Reads customer data from JSON files
- **API Extractor**: Fetches product data from REST APIs
- Error handling and retry logic

### 2. **ETL Pipeline Layer**
Core data processing:
- **Extractor**: Multi-source data retrieval
- **Transformer**: Data cleaning, validation, and enrichment
- **Loader**: Database persistence
- **Pipeline Orchestrator**: Coordinates the entire flow

### 3. **Data Layer**
Database abstraction:
- **Connection Manager**: Handles connection pooling
- **ORM Models**: SQLAlchemy models for all entities
- **Schema**: Normalized relational schema

### 4. **Application Layer**
Business logic and utilities:
- **Logger**: Structured logging
- **Validators**: Data validation rules
- **Exceptions**: Custom error handling

### 5. **Presentation Layer**
User-facing components:
- **Streamlit Dashboard**: Interactive analytics UI
- **KPI Cards**: Key performance indicators
- **Visualizations**: Charts and graphs

## Data Flow

### ETL Execution Flow

```
1. EXTRACTION
   ├─ CSV Source → Sales Data
   ├─ JSON Source → Customer Data
   └─ API Source → Product Data
        ↓
2. TRANSFORMATION
   ├─ Data Cleaning
   │  ├─ String trimming
   │  ├─ Type conversion
   │  └─ Default value assignment
   ├─ Validation
   │  ├─ Required fields
   │  ├─ Data type checking
   │  └─ Business rules
   ├─ Duplicate Detection
   ├─ Missing Value Handling
   └─ Derived Metrics
        ↓
3. QUALITY CHECKING
   ├─ Invalid records count
   ├─ Duplicate records count
   ├─ Missing values percentage
   └─ Processing time
        ↓
4. LOADING
   ├─ Customer data → customers table
   ├─ Product data → products table
   ├─ Sales data → sales table
   └─ Metrics → quality_metrics table
        ↓
5. REPORTING
   ├─ JSON report generation
   ├─ Metrics tracking
   └─ Log output
```

### Dashboard Query Flow

```
User Interaction
     ↓
Filter Selection (Date, State, Category, Product)
     ↓
SQL Query Construction
     ↓
Database Query Execution
     ↓
Data Aggregation & Processing
     ↓
Chart Generation (Plotly)
     ↓
UI Rendering (Streamlit)
```

## Database Schema

### Entities & Relationships

```
┌─────────────────────┐
│   CUSTOMERS         │
├─────────────────────┤
│ customer_id (PK)    │
│ name                │
│ email (UNIQUE)      │
│ phone               │
│ state               │
│ city                │
│ zipcode             │
│ created_at          │
└─────────────────────┘
         ↑ (1)
         │
         │ (n)
         │
┌─────────────────────┐
│   SALES             │
├─────────────────────┤
│ sale_id (PK)        │
│ customer_id (FK)    │
│ product_id (FK)     │─────┐
│ quantity            │     │
│ unit_price          │     │
│ total_value         │     │
│ sale_date           │     │
│ year, month, quarter│     │
│ created_at          │     │
└─────────────────────┘     │
                            │ (n)
                            │
                        ┌───────────────────────┐
                        │   PRODUCTS            │
                        ├───────────────────────┤
                        │ product_id (PK)       │
                        │ name                  │
                        │ category              │
                        │ price                 │
                        │ description           │
                        │ created_at            │
                        └───────────────────────┘

┌─────────────────────────────────┐
│   DATA_QUALITY_METRICS          │
├─────────────────────────────────┤
│ metrics_id (PK)                 │
│ etl_run_id                      │
│ processed_records               │
│ invalid_records                 │
│ duplicates_removed              │
│ missing_values_percentage       │
│ processing_time_seconds         │
│ status                          │
│ created_at                      │
└─────────────────────────────────┘
```

### Indexes Strategy

**Performance Indexes**:
- `customers(email)` - Unique constraint
- `customers(state)` - Filtering by state
- `products(category)` - Filtering by category
- `products(name)` - Text search
- `sales(customer_id)` - Join optimization
- `sales(product_id)` - Join optimization
- `sales(sale_date)` - Time-based filtering
- `sales(year, month)` - Period aggregation

## Deployment Architecture

### Single-Server Deployment
```
┌─────────────────────────────────────────┐
│         Single Server                   │
│  ┌───────────────────────────────────┐  │
│  │  Python Application (ETL + API)   │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  PostgreSQL Database              │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Streamlit Dashboard              │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Docker Compose Deployment
```
┌──────────────────────────────────────────────────────┐
│           Docker Compose Network                     │
│  ┌────────────────┐  ┌────────────────┐             │
│  │  PostgreSQL    │←→│  ETL Container │             │
│  │  Container     │  └────────────────┘             │
│  │  (Port 5432)   │                                 │
│  └────────────────┘  ┌────────────────┐             │
│        ↓             │  Dashboard     │             │
│        └─────────────→│  Container     │             │
│                      │  (Port 8501)   │             │
│                      └────────────────┘             │
└──────────────────────────────────────────────────────┘
```

## Security Architecture

### Data Security
- **Credentials**: Environment variables (never in code)
- **Database**: Connection pooling with SSL option
- **API**: TLS/SSL for API calls
- **Logs**: Sensitive data masking

### Access Control
- **Authentication**: Database user authentication
- **Authorization**: Role-based access (future)
- **Auditing**: Complete operation logging

## Scalability Considerations

### Horizontal Scaling
- Stateless ETL application
- Multiple instances with shared database
- Load balancer for dashboard

### Vertical Scaling
- Connection pool optimization
- Query optimization with indexes
- Batch processing for large datasets

### Performance Optimization
- Connection pooling (min=1, max=10)
- Prepared statements
- Batch inserts
- Query result caching

## Error Handling & Resilience

### Error Management
```
Try ETL Operation
     ↓
If Error
     ├─ Log Error Details
     ├─ Increment Error Counter
     ├─ Skip Invalid Record
     ├─ Continue Processing
     └─ Generate Error Report
```

### Recovery Strategies
- **Graceful Degradation**: Continue with partial data
- **Retry Logic**: Automatic retries for transient errors
- **Rollback**: Transaction rollback on failure
- **Checkpoint**: Save state for recovery

## Monitoring & Observability

### Metrics Tracked
- Records processed/failed
- Processing duration
- Error rates
- Data quality metrics

### Logging Strategy
- **File Logs**: Persistent storage
- **Console Logs**: Real-time monitoring
- **Structured Format**: Timestamp, level, message
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR

### Dashboards & Reports
- Real-time KPI display
- Historical trend analysis
- Quality metrics tracking
- Automated report generation

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Python 3.11+ | Core application |
| Database | PostgreSQL 15 | Data persistence |
| ORM | SQLAlchemy 2.0 | Database abstraction |
| Web UI | Streamlit | Interactive dashboard |
| Visualization | Plotly | Charts & graphs |
| Scheduling | APScheduler | Job scheduling |
| Containerization | Docker | Deployment |
| Orchestration | Docker Compose | Multi-container management |
| Testing | pytest | Unit testing |

## Development Workflow

```
Code Development
     ↓
Unit Testing (pytest)
     ↓
Code Review
     ↓
Integration Testing
     ↓
Docker Build
     ↓
Docker Compose Test
     ↓
Deployment
```

## Future Enhancements

- Machine learning predictions
- Real-time data streaming
- Advanced caching layer
- Multi-tenant support
- GraphQL API
- Kubernetes deployment
- Microservices architecture
