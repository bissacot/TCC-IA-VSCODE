"""
Database connection and session management.

Provides a PostgreSQL connection pool and session management utilities.
"""

from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2 import pool, sql

from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from src.utils import LoggerConfig, DatabaseException


logger = LoggerConfig.get_logger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections."""

    _connection_pool: Optional[pool.SimpleConnectionPool] = None

    @classmethod
    def initialize(cls, min_connections: int = 1, max_connections: int = 10) -> None:
        """
        Initialize connection pool.

        Args:
            min_connections: Minimum number of connections in pool
            max_connections: Maximum number of connections in pool

        Raises:
            DatabaseException: If connection pool creation fails
        """
        try:
            cls._connection_pool = pool.SimpleConnectionPool(
                min_connections,
                max_connections,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            logger.info("Database connection pool initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise DatabaseException(f"Connection pool initialization failed: {e}")

    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator:
        """
        Get a connection from the pool.

        Yields:
            Database connection

        Raises:
            DatabaseException: If no connection available
        """
        if cls._connection_pool is None:
            cls.initialize()

        connection = None
        try:
            connection = cls._connection_pool.getconn()
            yield connection
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseException(f"Connection error: {e}")
        finally:
            if connection:
                cls._connection_pool.putconn(connection)

    @classmethod
    @contextmanager
    def get_cursor(cls) -> Generator:
        """
        Get a cursor with automatic connection management.

        Yields:
            Database cursor
        """
        with cls.get_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor
                connection.commit()
            except psycopg2.Error as e:
                connection.rollback()
                logger.error(f"Database cursor error: {e}")
                raise DatabaseException(f"Cursor error: {e}")
            finally:
                cursor.close()

    @classmethod
    def close_all(cls) -> None:
        """Close all connections in the pool."""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            logger.info("Database connection pool closed")
