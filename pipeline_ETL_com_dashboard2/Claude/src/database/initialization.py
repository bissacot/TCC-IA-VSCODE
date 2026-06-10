"""
Database initialization and migration utilities.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.connection import DatabaseManager
from src.database.models import Base, Customer, Product, Sale, DataQualityMetric
from src.utils.logging_config import setup_logging
from src.utils.exceptions import DatabaseException

logger = setup_logging(__name__)


def create_all_tables() -> None:
    """Create all database tables."""
    try:
        engine = DatabaseManager.get_engine()
        logger.info("Creating all database tables...")
        
        # Drop existing tables (for development)
        # Base.metadata.drop_all(engine)
        
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise DatabaseException(f"Failed to create tables: {str(e)}")


def execute_sql_file(sql_file_path: str) -> None:
    """
    Execute SQL file against database.

    Args:
        sql_file_path: Path to SQL file
    """
    try:
        with open(sql_file_path, "r") as f:
            sql_content = f.read()
        
        session = DatabaseManager.get_session()
        try:
            # Split by semicolon and execute each statement
            statements = sql_content.split(";")
            for statement in statements:
                statement = statement.strip()
                if statement:
                    session.execute(text(statement))
            
            session.commit()
            logger.info(f"SQL file executed successfully: {sql_file_path}")
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to execute SQL file {sql_file_path}: {str(e)}")
        raise DatabaseException(f"SQL execution failed: {str(e)}")


def backup_database(backup_path: str) -> None:
    """
    Backup database (requires pg_dump).

    Args:
        backup_path: Path to save backup file
    """
    import subprocess
    from src.config import DatabaseConfig

    try:
        config = DatabaseConfig
        cmd = [
            "pg_dump",
            f"--host={config.HOST}",
            f"--port={config.PORT}",
            f"--username={config.USER}",
            f"--dbname={config.NAME}",
            f"--file={backup_path}",
        ]
        
        env = {"PGPASSWORD": config.PASSWORD}
        subprocess.run(cmd, env=env, check=True)
        logger.info(f"Database backup created: {backup_path}")
        
    except Exception as e:
        logger.error(f"Failed to backup database: {str(e)}")
        raise DatabaseException(f"Database backup failed: {str(e)}")


def get_table_statistics(session: Session) -> dict:
    """
    Get statistics for all tables.

    Args:
        session: Database session

    Returns:
        Dictionary with table statistics
    """
    try:
        stats = {}
        
        stats["customers"] = session.query(Customer).count()
        stats["products"] = session.query(Product).count()
        stats["sales"] = session.query(Sale).count()
        stats["quality_metrics"] = session.query(DataQualityMetric).count()
        
        logger.info(f"Table statistics: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get table statistics: {str(e)}")
        return {}
