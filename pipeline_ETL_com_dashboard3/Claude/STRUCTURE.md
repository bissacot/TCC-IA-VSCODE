# Sales ETL & Dashboard - Project Structure

## Directory Layout

```
sales_etl_dashboard/
├── src/                           # Main source code
│   ├── __init__.py
│   ├── etl_pipeline.py           # Main ETL orchestrator
│   ├── extractors/               # Data extraction modules
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base extractor
│   │   ├── csv_extractor.py      # CSV file extractor
│   │   ├── json_extractor.py     # JSON file extractor
│   │   └── api_extractor.py      # REST API extractor
│   ├── transformers/             # Data transformation modules
│   │   ├── __init__.py
│   │   └── transformer.py        # Data transformation engine
│   ├── loaders/                  # Database loading modules
│   │   ├── __init__.py
│   │   ├── database.py           # Database connection manager
│   │   └── loader.py             # Data loader
│   ├── dashboard/                # Streamlit dashboard
│   │   ├── __init__.py
│   │   └── app.py                # Dashboard application
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── logger.py             # Logging configuration
│       ├── config.py             # Configuration management
│       ├── exceptions.py         # Custom exceptions
│       ├── models.py             # Data models
│       ├── report_generator.py   # PDF/Excel report generation
│       └── scheduler.py          # ETL job scheduling
├── tests/                         # Unit tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_extractors.py
│   └── test_transformers.py
├── database/                      # Database scripts
│   ├── init.sql                  # Database initialization
│   └── sample_data.sql           # Sample data
├── data/                          # Data directory
│   ├── input/                    # Input data files
│   └── output/                   # Output reports
├── logs/                          # Log files
├── config/                        # Configuration files
│   └── etl_config.json           # ETL configuration
├── run_etl.py                    # Main ETL entry point
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── Dockerfile                    # ETL container
├── Dockerfile.streamlit          # Dashboard container
├── docker-compose.yml            # Container orchestration
├── .env.example                  # Environment variables template
└── README.md                      # Documentation
```
