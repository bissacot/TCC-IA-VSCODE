from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    products_api_url: str = "https://fakestoreapi.com/products"
    csv_sales_file: str = "data/sales.csv"
    json_customers_file: str = "data/customers.json"
    etl_batch_dir: str = "data"
    incremental: bool = True
    last_run_file: str = ".lastrun"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
