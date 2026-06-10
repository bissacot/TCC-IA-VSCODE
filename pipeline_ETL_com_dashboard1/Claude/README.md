# ETL Pipeline and Sales Dashboard

A comprehensive Enterprise Data Integration solution for sales analysis, featuring a complete ETL pipeline and interactive Streamlit dashboard with advanced analytics and reporting capabilities.

## 🎯 Features

### Core ETL Capabilities
- **Multi-source extraction**: CSV, JSON, and REST API
- **Data transformation**: Deduplication, validation, standardization
- **Quality reporting**: Comprehensive data quality metrics
- **PostgreSQL integration**: Relational database storage
- **Incremental processing**: Support for delta loads
- **Automated scheduling**: Airflow integration
- **Error handling**: Robust exception management with retry logic

### Dashboard Features
- **Real-time KPIs**: Revenue, sales count, average ticket, unique customers
- **Advanced visualizations**: Time series, categorical analysis, geographic distribution
- **Interactive filters**: Date range, state, category, product
- **Report generation**: PDF and Excel export
- **Performance optimized**: Efficient caching and data handling

### Engineering Excellence
- **Type hints** throughout codebase
- **Structured logging** with rotating file handlers
- **Unit tests** with 80%+ coverage
- **Docker support** for easy deployment
- **Environment management** via .env files
- **Clean code** following PEP 8 standards

## 📋 Project Structure

```
.
├── src/                          # Main source code
│   ├── etl/                      # ETL pipeline
│   │   ├── extractors/           # Data extraction modules
│   │   ├── transformers/         # Data transformation logic
│   │   ├── loaders/              # Database loading
│   │   ├── validators/           # Data validation
│   │   └── pipeline.py           # Main ETL orchestration
│   ├── dashboard/                # Streamlit dashboard
│   ├── database/                 # Database models and utilities
│   ├── config.py                 # Configuration management
│   ├── logger.py                 # Logging setup
│   └── utils/                    # Utility functions
├── tests/                        # Unit and integration tests
├── database/                     # SQL scripts
├── docker/                       # Docker configuration
├── airflow/                      # DAG definitions
├── docs/                         # Documentation
├── data/                         # Sample data files
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── docker-compose.yml            # Multi-container setup

```

## 🚀 Quick Start

### Local Development

1. **Clone and setup**
```bash
git clone <repository>
cd pipeline-etl-dashboard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Run ETL pipeline**
```bash
python src/etl/pipeline.py
```

4. **Start dashboard**
```bash
streamlit run src/dashboard/app.py
```

### Docker Deployment

```bash
docker-compose up -d
# Dashboard: http://localhost:8501
# PostgreSQL: localhost:5432
```

## 📊 Database Schema

### Tables
- **customers**: Customer information
- **products**: Product catalog with categories
- **sales**: Sales transactions with metrics
- **data_quality_report**: ETL quality metrics
- **incremental_load_log**: Processing history

## 🔄 Data Flow

```
CSV (Sales) ──┐
JSON (Customers) ├─> Extract ─> Transform ─> Validate ─> Load ─> PostgreSQL
API (Products) ──┘                                         └──> Data Quality Report
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_etl_pipeline.py -v
```

## 📝 Logging

Logs are stored in `logs/` directory:
- `etl.log`: ETL pipeline execution
- `dashboard.log`: Dashboard operations
- `errors.log`: Error tracking

## 🐳 Docker

### Build images
```bash
docker-compose build
```

### Start services
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f
```

### Stop services
```bash
docker-compose down
```

## 🗓️ Scheduling (Airflow)

DAGs are located in `airflow/dags/`. To run Airflow:

```bash
# Initialize Airflow
airflow db init

# Start webserver
airflow webserver

# Start scheduler
airflow scheduler
```

## 📖 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [ETL Pipeline Documentation](docs/ETL.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Dashboard Guide](docs/DASHBOARD.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🔐 Environment Variables

See [.env.example](.env.example) for all available configuration options.

## 📦 Dependencies

- **Python 3.9+**
- **PostgreSQL 12+**
- **Streamlit**: Interactive dashboard
- **Pandas**: Data manipulation
- **SQLAlchemy**: ORM
- **Airflow**: Scheduling
- **Pytest**: Testing
- **Docker**: Containerization

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check existing [issues](../../issues)
2. Review [documentation](docs/)
3. Create new issue with details

## 🎓 Architecture Highlights

- **Modular Design**: Separated concerns for extraction, transformation, and loading
- **Type Safety**: Full type hints for IDE support and runtime validation
- **Error Recovery**: Comprehensive exception handling with logging
- **Performance**: Optimized queries and caching strategies
- **Scalability**: Supports incremental processing and parallel execution
- **Testability**: Unit tests for all critical components
- **Observability**: Structured logging and monitoring

---

**Last Updated**: 2024
**Version**: 1.0.0
