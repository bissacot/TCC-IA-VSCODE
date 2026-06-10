"""Data loader for PostgreSQL."""

from typing import List, Tuple, Optional
import pandas as pd
from src.loaders.database import DatabaseManager
from src.utils.logger import logger
from src.utils.exceptions import LoadingException, DatabaseException
from src.utils.config import DatabaseConfig


class DataLoader:
    """Loads transformed data into PostgreSQL."""
    
    def __init__(self, db_config: DatabaseConfig):
        """
        Initialize data loader.
        
        Args:
            db_config: Database configuration
        """
        self.db_manager = DatabaseManager(db_config)
    
    def load_customers(self, df: pd.DataFrame, incremental: bool = False) -> int:
        """
        Load customer data into database.
        
        Args:
            df: Customer DataFrame
            incremental: Use incremental loading
        
        Returns:
            Number of loaded records
        """
        try:
            logger.info(f"Loading {len(df)} customer records")
            
            # Prepare data
            data = []
            for _, row in df.iterrows():
                data.append((
                    row.get('customer_id', ''),
                    row.get('name', ''),
                    row.get('email', ''),
                    row.get('phone'),
                    row.get('city'),
                    row.get('state'),
                    row.get('country'),
                    row.get('registration_date')
                ))
            
            query = """
                INSERT INTO customers 
                (customer_id, name, email, phone, city, state, country, registration_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) 
                DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    city = EXCLUDED.city,
                    state = EXCLUDED.state,
                    country = EXCLUDED.country,
                    registration_date = EXCLUDED.registration_date
            """
            
            rows_affected = self.db_manager.execute_batch(query, data)
            logger.info(f"Successfully loaded {rows_affected} customer records")
            return rows_affected
        
        except Exception as e:
            logger.error(f"Customer loading failed: {str(e)}")
            raise LoadingException(f"Customer load error: {str(e)}")
    
    def load_products(self, df: pd.DataFrame, incremental: bool = False) -> int:
        """
        Load product data into database.
        
        Args:
            df: Product DataFrame
            incremental: Use incremental loading
        
        Returns:
            Number of loaded records
        """
        try:
            logger.info(f"Loading {len(df)} product records")
            
            # Prepare data
            data = []
            for _, row in df.iterrows():
                data.append((
                    row.get('product_id', ''),
                    row.get('name', ''),
                    row.get('category', ''),
                    float(row.get('price', 0)),
                    row.get('description'),
                    row.get('sku')
                ))
            
            query = """
                INSERT INTO products 
                (product_id, name, category, price, description, sku)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) 
                DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    price = EXCLUDED.price,
                    description = EXCLUDED.description,
                    sku = EXCLUDED.sku
            """
            
            rows_affected = self.db_manager.execute_batch(query, data)
            logger.info(f"Successfully loaded {rows_affected} product records")
            return rows_affected
        
        except Exception as e:
            logger.error(f"Product loading failed: {str(e)}")
            raise LoadingException(f"Product load error: {str(e)}")
    
    def load_sales(self, df: pd.DataFrame, incremental: bool = False) -> int:
        """
        Load sales data into database.
        
        Args:
            df: Sales DataFrame
            incremental: Use incremental loading
        
        Returns:
            Number of loaded records
        """
        try:
            logger.info(f"Loading {len(df)} sales records")
            
            # Prepare data
            data = []
            for _, row in df.iterrows():
                data.append((
                    row.get('sale_id', ''),
                    row.get('customer_id', ''),
                    row.get('product_id', ''),
                    int(row.get('quantity', 0)),
                    float(row.get('unit_price', 0)),
                    float(row.get('total_value', 0)),
                    row.get('sale_date'),
                    int(row.get('sale_year', 0)),
                    int(row.get('sale_month', 0)),
                    int(row.get('sale_quarter', 0))
                ))
            
            query = """
                INSERT INTO sales 
                (sale_id, customer_id, product_id, quantity, unit_price, total_value, 
                 sale_date, sale_year, sale_month, sale_quarter)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sale_id) 
                DO UPDATE SET
                    quantity = EXCLUDED.quantity,
                    unit_price = EXCLUDED.unit_price,
                    total_value = EXCLUDED.total_value,
                    sale_date = EXCLUDED.sale_date,
                    sale_year = EXCLUDED.sale_year,
                    sale_month = EXCLUDED.sale_month,
                    sale_quarter = EXCLUDED.sale_quarter
            """
            
            rows_affected = self.db_manager.execute_batch(query, data)
            logger.info(f"Successfully loaded {rows_affected} sales records")
            return rows_affected
        
        except Exception as e:
            logger.error(f"Sales loading failed: {str(e)}")
            raise LoadingException(f"Sales load error: {str(e)}")
    
    def close(self) -> None:
        """Close database connections."""
        self.db_manager.close()
