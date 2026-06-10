"""
Database connection and operations management.
"""

from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import DictCursor, execute_batch
from contextlib import contextmanager
from src.utils.logger import get_logger
from src.utils.config import Config


logger = get_logger()


class DatabaseConnection:
    """Manage PostgreSQL database connections."""

    def __init__(self):
        self.connection_params = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'database': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
        }
        self.connection = None
        self.logger = get_logger()

    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.logger.info("Database connection established successfully")
        except psycopg2.Error as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")

    @contextmanager
    def get_cursor(self, cursor_factory=DictCursor):
        """Get database cursor context manager."""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            self.connection.commit()
        except psycopg2.Error as e:
            self.connection.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            cursor.close()

    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or [])
                return cursor.fetchall()
        except psycopg2.Error as e:
            self.logger.error(f"Query execution error: {str(e)}")
            raise

    def execute_update(self, query: str, params: Optional[List] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or [])
                return cursor.rowcount
        except psycopg2.Error as e:
            self.logger.error(f"Update execution error: {str(e)}")
            raise

    def execute_batch(self, query: str, data: List[tuple], page_size: int = 100) -> int:
        """Execute batch insert/update."""
        try:
            with self.get_cursor() as cursor:
                execute_batch(cursor, query, data, page_size=page_size)
                return cursor.rowcount
        except psycopg2.Error as e:
            self.logger.error(f"Batch execution error: {str(e)}")
            raise

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        query = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = %s
            )
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, [table_name])
                return cursor.fetchone()[0]
        except psycopg2.Error as e:
            self.logger.error(f"Error checking table existence: {str(e)}")
            return False

    def create_schema(self, schema_sql: str) -> None:
        """Create database schema from SQL script."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(schema_sql)
            self.logger.info("Database schema created successfully")
        except psycopg2.Error as e:
            self.logger.error(f"Error creating schema: {str(e)}")
            raise

    def truncate_table(self, table_name: str, cascade: bool = False) -> None:
        """Truncate table."""
        try:
            cascade_str = "CASCADE" if cascade else "RESTRICT"
            query = f"TRUNCATE TABLE {table_name} {cascade_str}"
            with self.get_cursor() as cursor:
                cursor.execute(query)
            self.logger.info(f"Table {table_name} truncated successfully")
        except psycopg2.Error as e:
            self.logger.error(f"Error truncating table {table_name}: {str(e)}")
            raise

    def get_record_count(self, table_name: str) -> int:
        """Get row count for table."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                return cursor.fetchone()[0]
        except psycopg2.Error as e:
            self.logger.error(f"Error getting record count: {str(e)}")
            return 0
