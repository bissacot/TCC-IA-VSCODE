from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL")
    products_api_url: str = os.getenv("PRODUCTS_API_URL")
    csv_path: str = os.getenv("CSV_PATH", "./data/sales.csv")
    customers_json: str = os.getenv("CUSTOMERS_JSON", "./data/customers.json")

settings = Settings()
