from pydantic import BaseSettings, AnyUrl
from typing import Optional


class Settings(BaseSettings):
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "salesdb"
    POSTGRES_USER: str = "salesuser"
    POSTGRES_PASSWORD: str = "changeme"

    PRODUCTS_API_URL: Optional[AnyUrl] = None
    SALES_CSV: str = "./data/sales.csv"
    CUSTOMERS_JSON: str = "./data/customers.json"

    ETL_INCREMENTAL: bool = True
    ETL_SCHEDULE_CRON: str = "0 */6 * * *"

    class Config:
        env_file = ".env"


settings = Settings()
