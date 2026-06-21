from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseSettings, HttpUrl, validator


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    product_api_url: HttpUrl
    source_csv_path: Path
    source_json_path: Path
    log_level: str = "INFO"
    environment: str = "development"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @validator("source_csv_path", "source_json_path", pre=True)
    def ensure_path(cls, value: Any) -> Path:
        return Path(value)

    class Config:
        env_file = ".env"
        case_sensitive = False
