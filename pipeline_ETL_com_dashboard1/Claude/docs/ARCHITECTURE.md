# Architecture Guide

## System Overview

The ETL Pipeline and Dashboard solution is built on a modular, layered architecture designed for scalability, maintainability, and extensibility.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Data Sources                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CSV Files    │  │ JSON Files   │  │ REST APIs    │      │
│  │ (Sales)      │  │ (Customers)  │  │ (Products)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  ETL Pipeline                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Extract Layer (Extractors)                         │   │
│  │  - CSVExtractor, JSONExtractor, APIExtractor       │   │
│  └─────────────────────────────────────────────────────┘   │
│                        │                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Transform Layer (Transformers)                    │   │
│  │  - Data Validation, Cleaning, Enrichment          │   │
│  │  - Duplicate Detection, Missing Value Handling    │   │
│  │  - Derived Metric Calculation                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                        │                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Load Layer (Loaders)                              │   │
│  │  - Database Operations, Batch Insert              │   │
│  │  - Quality Report Generation                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Customers    │  │ Products     │  │ Sales        │      │
│  │ (Dimension)  │  │ (Dimension)  │  │ (Fact)       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Quality Reports & Incremental Load Logs            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Streamlit Dashboard                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  KPI Cards (Revenue, Sales, Customers)             │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  Visualizations                                    │   │
│  │  - Revenue Trends, Category Distribution          │   │
│  │  - Top Products, Geographic Analysis              │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  Filters & Controls                               │   │
│  │  - Date Range, State, Category, Product           │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  Export & Reporting                               │   │
│  │  - PDF, Excel                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Extraction Layer

**Purpose**: Unified data extraction from multiple sources

**Components**:
- `BaseExtractor`: Abstract interface for all extractors
- `CSVExtractor`: Extract sales data from CSV files
- `JSONExtractor`: Extract customer data from JSON files
- `APIExtractor`: Extract product data from REST APIs
- `ExtractorFactory`: Create appropriate extractor instances

**Design Pattern**: Strategy Pattern + Factory Pattern

```python
# Usage
csv_extractor = ExtractorFactory.create_csv_extractor(path)
api_extractor = ExtractorFactory.create_api_extractor(url)
```

### 2. Transformation Layer

**Purpose**: Data cleaning, validation, and enrichment

**Components**:
- `BaseTransformer`: Abstract interface for transformers
- `SalesTransformer`: Transform sales records
- `CustomerTransformer`: Transform customer records
- `ProductTransformer`: Transform product records
- `DataQualityMetrics`: Track data quality metrics

**Features**:
- Field validation
- Data type conversion
- Duplicate detection
- Missing value handling
- Derived metric calculation
- Date standardization

**Design Pattern**: Strategy Pattern

### 3. Loading Layer

**Purpose**: Persist data to PostgreSQL database

**Components**:
- `BaseLoader`: Abstract interface for loaders
- `CustomerLoader`: Load customer dimension
- `ProductLoader`: Load product dimension
- `SaleLoader`: Load sales fact table
- `DataQualityReportLoader`: Load quality metrics
- `ETLLoader`: Orchestrate all loaders

**Design Pattern**: Repository Pattern

### 4. Database Layer

**Purpose**: ORM models and data access

**Components**:
- `models.py`: SQLAlchemy ORM models
  - Customer, Product, Sale
  - DataQualityReport, IncrementalLoadLog
- `repository.py`: Repository pattern implementation
  - CustomerRepository, ProductRepository
  - SaleRepository, DataQualityRepository
  - IncrementalLoadRepository
- `DatabaseConnection`: Connection management

**Design Pattern**: Repository Pattern, ORM Pattern

### 5. Pipeline Orchestration

**Purpose**: Coordinate ETL workflow

**Components**:
- `ETLPipeline`: Main orchestrator
  - Extract phase
  - Transform phase
  - Load phase
  - Quality report generation

**Features**:
- Error handling and recovery
- Incremental processing support
- Detailed logging
- Performance tracking

### 6. Dashboard Layer

**Purpose**: Interactive analytics and visualization

**Components**:
- `app.py`: Streamlit application
- UI Components:
  - KPI cards
  - Plotly charts
  - Filters and controls
  - Export options

**Features**:
- Real-time data caching
- Interactive filtering
- Dynamic visualizations
- PDF/Excel export (advanced)

## Data Flow

### Extract Phase

```
Data Sources
    ↓
Extractors (Strategy pattern)
    ↓
Raw Data (List of dictionaries)
```

### Transform Phase

```
Raw Data
    ↓
Validators (Field validation, Data types)
    ↓
Cleaners (Standardization, Deduplication)
    ↓
Enrichers (Derived metrics, Calculations)
    ↓
Transformed Data with Quality Metrics
```

### Load Phase

```
Transformed Data
    ↓
Repositories (ORM models)
    ↓
PostgreSQL Database
    ↓
Quality Report
```

## Design Patterns

### 1. Strategy Pattern
Used for extractors and transformers to support multiple implementations:
- Different extraction strategies (CSV, JSON, API)
- Different transformation strategies per data type

### 2. Factory Pattern
Used for creating extractors and transformers:
- `ExtractorFactory`: Create appropriate extractor
- Encapsulates creation logic

### 3. Repository Pattern
Used for data access layer:
- Abstracts database operations
- Provides query methods
- Facilitates testing with mock repositories

### 4. Decorator Pattern
Used for logging and error handling:
- Applied to critical functions
- Enhances functionality without modification

## Layers and Responsibilities

### Configuration Layer (`config.py`)
- Environment variable management
- Configuration defaults
- Multi-environment support (dev, prod, test)

### Logging Layer (`logger.py`)
- Centralized logging setup
- Rotating file handlers
- Console output with different levels

### Database Layer (`database/`)
- ORM models definition
- Connection management
- Query execution

### ETL Layer (`etl/`)
- Data extraction
- Data transformation
- Data loading
- Pipeline orchestration

### Presentation Layer (`dashboard/`)
- Web interface
- Visualizations
- User interactions

## Scalability Considerations

### Horizontal Scaling
- Containerized with Docker
- Kubernetes-ready deployment
- Independent service scaling

### Vertical Scaling
- Connection pooling
- Query optimization
- Caching strategies

### Data Processing
- Batch processing support
- Incremental load capability
- Parallel processing potential

## Error Handling Strategy

1. **Extraction Level**
   - Validate source availability
   - Handle connection errors
   - Retry with exponential backoff

2. **Transformation Level**
   - Validate individual records
   - Log invalid data
   - Continue processing with graceful degradation

3. **Loading Level**
   - Handle database constraints
   - Transaction management
   - Rollback on critical errors

## Testing Strategy

### Unit Tests
- Test individual components
- Mock external dependencies
- Validate transformation logic

### Integration Tests
- Test component interactions
- Use test database
- Verify end-to-end flows

### Performance Tests
- Load testing
- Query performance
- ETL execution time

## Security Considerations

1. **Data Protection**
   - Encrypted password storage
   - SSL/TLS for connections
   - Input validation

2. **Access Control**
   - Database user isolation
   - API key management
   - Role-based access

3. **Audit Trail**
   - Execution logging
   - Change tracking
   - Quality reports

## Future Enhancements

- [ ] Machine learning integration for anomaly detection
- [ ] Advanced reporting engine
- [ ] Real-time streaming capability
- [ ] Multi-tenant support
- [ ] Advanced caching strategies
- [ ] Performance optimization framework
- [ ] Custom transformation plugins
- [ ] Workflow orchestration platform
