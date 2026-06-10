"""Database connection and operations."""

from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import execute_batch
import pandas as pd
from src.utils.logger import logger
from src.utils.exceptions import DatabaseException
from src.utils.config import DatabaseConfig


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_config: DatabaseConfig, pool_size: int = 5):
        """
        Initialize database manager.
        
        Args:
            db_config: Database configuration
            pool_size: Connection pool size
        """
        self.db_config = db_config
        self.pool_size = pool_size
        self.connection_pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Initialize connection pool."""
        try:
            self.connection_pool = SimpleConnectionPool(
                1,
                self.pool_size,
                user=self.db_config.user,
                password=self.db_config.password,
                host=self.db_config.host,
                port=self.db_config.port,
                database=self.db_config.database,
                connect_timeout=10
            )
            logger.info("Database connection pool initialized")
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise DatabaseException(f"Connection pool error: {str(e)}")
    
    def get_connection(self):
        """Get a connection from the pool."""
        if not self.connection_pool:
            raise DatabaseException("Connection pool not initialized")
        
        try:
            return self.connection_pool.getconn()
        except psycopg2.Error as e:
            logger.error(f"Failed to get connection: {str(e)}")
            raise DatabaseException(f"Failed to get connection: {str(e)}")
    
    def return_connection(self, conn) -> None:
        """Return connection to the pool."""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query.
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            List of result dictionaries
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            cursor.close()
            
            return [dict(zip(columns, row)) for row in rows]
        
        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise DatabaseException(f"Query error: {str(e)}")
        finally:
            if conn:
                self.return_connection(conn)
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            Number of affected rows
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            rows_affected = cursor.rowcount
            conn.commit()
            cursor.close()
            
            return rows_affected
        
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Update execution failed: {str(e)}")
            raise DatabaseException(f"Update error: {str(e)}")
        finally:
            if conn:
                self.return_connection(conn)
    
    def execute_batch(self, query: str, data: List[tuple], batch_size: int = 1000) -> int:
        """
        Execute batch INSERT/UPDATE operations.
        
        Args:
            query: SQL query with placeholders
            data: List of tuples with data
            batch_size: Batch size for execution
        
        Returns:
            Number of affected rows
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            total_rows = 0
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                execute_batch(cursor, query, batch)
                total_rows += cursor.rowcount
            
            conn.commit()
            cursor.close()
            
            return total_rows
        
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Batch execution failed: {str(e)}")
            raise DatabaseException(f"Batch error: {str(e)}")
        finally:
            if conn:
                self.return_connection(conn)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        try:
            result = self.execute_query(
                f"""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = %s
                )
                """,
                (table_name,)
            )
            return result[0]['exists'] if result else False
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")
