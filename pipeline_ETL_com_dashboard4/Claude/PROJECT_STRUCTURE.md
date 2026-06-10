# Project Structure
.env.example              # Example environment configuration
.gitignore               # Git ignore rules
requirements.txt         # Python dependencies
README.md               # Project documentation
QUICKSTART.md          # Quick start guide

# Source Code
src/
├── __init__.py
├── etl/                # ETL Pipeline
│   ├── __init__.py
│   ├── extractor.py    # Data extraction (CSV, JSON, API)
│   ├── transformer.py  # Data transformation and cleaning
│   ├── loader.py       # Data loading to PostgreSQL
│   └── pipeline.py     # ETL orchestration
├── database/           # Database Layer
│   ├── __init__.py
│   ├── connection.py   # Database connection management
│   └── models.py       # SQLAlchemy ORM models
├── dashboard/          # Streamlit Dashboard
│   ├── __init__.py
│   └── app.py          # Dashboard application
└── utils/              # Utilities
    ├── __init__.py
    ├── logger.py       # Logging configuration
    ├── validators.py   # Data validation utilities
    └── exceptions.py   # Custom exceptions

# Configuration
config/
├── __init__.py
└── settings.py         # Application settings

# Docker
docker/
├── Dockerfile          # ETL app container
├── Dockerfile.dashboard  # Dashboard container
└── docker-compose.yml  # Multi-container orchestration

# Database Scripts
sql/
├── init_schema.sql     # Database schema initialization
└── sample_data.sql     # Sample data insertion

# Sample Data
data/
├── sales.csv           # Sample sales data
└── customers.json      # Sample customer data

# Tests
tests/
├── __init__.py
└── unit/               # Unit tests
    ├── __init__.py
    ├── test_extractor.py
    └── test_transformer.py

# Documentation
docs/
├── ARCHITECTURE.md     # System architecture documentation
├── API.md             # API documentation
├── DEPLOYMENT.md      # Deployment guide
└── TROUBLESHOOTING.md # Troubleshooting guide

# Entry Points
etl_cli.py             # CLI for running ETL
scheduler.py           # ETL scheduler for automation

# Directories Created at Runtime
logs/                  # Application logs
reports/               # Generated reports
