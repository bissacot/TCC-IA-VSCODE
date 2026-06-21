from dataclasses import dataclass
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://etl_user:etl_password@db:5432/etl_db")
    sales_csv_path: str = os.getenv("SALES_CSV_PATH", "sample_data/sales.csv")
    customers_json_path: str = os.getenv("CUSTOMERS_JSON_PATH", "sample_data/customers.json")
    product_api_url: str = os.getenv("PRODUCT_API_URL", "http://api:5000/products")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    etl_schedule_time: str = os.getenv("ETL_SCHEDULE_TIME", "02:00")
    pdf_output_path: str = os.getenv("PDF_OUTPUT_PATH", "output/etl_summary.pdf")
    excel_output_path: str = os.getenv("EXCEL_OUTPUT_PATH", "output/etl_export.xlsx")

settings = Settings()
