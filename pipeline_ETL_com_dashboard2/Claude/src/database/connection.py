"""
Database connection and session management.
"""

from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from src.config import DatabaseConfig
from src.utils.logging_config import setup_logging
from src.utils.exceptions import DatabaseException

logger = setup_logging(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    _engine: Engine = None
    _session_maker = None

    @classmethod
    def initialize(cls, config: DatabaseConfig = None) -> Engine:
        """
        Initialize database connection.

        Args:
            config: DatabaseConfig instance

        Returns:
            SQLAlchemy engine

        Raises:
            DatabaseException: If connection fails
        """
        if config is None:
            config = DatabaseConfig

        try:
            logger.info(f"Initializing database connection to {config.HOST}:{config.PORT}/{config.NAME}")
            
            cls._engine = create_engine(
                config.engine_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                echo=False,
                pool_pre_ping=True,
            )

            cls._session_maker = sessionmaker(bind=cls._engine)
            
            # Test connection
            with cls._engine.connect() as conn:
                logger.info("Database connection successful")
                
            return cls._engine

        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise DatabaseException(f"Database initialization failed: {str(e)}")

    @classmethod
    def get_engine(cls) -> Engine:
        """Get database engine."""
        if cls._engine is None:
            cls.initialize()
        return cls._engine

    @classmethod
    def get_session(cls) -> Session:
        """Get new database session."""
        if cls._session_maker is None:
            cls.initialize()
        return cls._session_maker()

    @classmethod
    def get_session_generator(cls) -> Generator[Session, None, None]:
        """Get session generator for dependency injection."""
        session = cls.get_session()
        try:
            yield session
        finally:
            session.close()

    @classmethod
    def close(cls) -> None:
        """Close all connections."""
        if cls._engine:
            cls._engine.dispose()
            logger.info("Database connections closed")

    @classmethod
    def health_check(cls) -> bool:
        """Check database health."""
        try:
            with cls.get_engine().connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
