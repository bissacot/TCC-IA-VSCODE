"""
Data loading into PostgreSQL database.
"""

from typing import List, Dict, Any
from datetime import datetime
from src.database.connection import DatabaseConnection
from src.models.schemas import Customer, Product, Sale
from src.utils.logger import get_logger


logger = get_logger()


class DataLoader:
    """Load transformed data into PostgreSQL."""

    def __init__(self):
        self.db = DatabaseConnection()
        self.logger = get_logger()

    def load_customers(self, customers: List[Customer]) -> int:
        """Load customer data into database."""
        if not customers:
            self.logger.warning("No customers to load")
            return 0

        self.db.connect()
        
        try:
            query = """
                INSERT INTO customers 
                (customer_id, name, email, phone, address, city, state, zip_code, country, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    address = EXCLUDED.address,
                    city = EXCLUDED.city,
                    state = EXCLUDED.state,
                    zip_code = EXCLUDED.zip_code,
                    country = EXCLUDED.country,
                    updated_at = EXCLUDED.updated_at
            """

            data = [
                (
                    c.customer_id,
                    c.name,
                    c.email,
                    c.phone,
                    c.address,
                    c.city,
                    c.state,
                    c.zip_code,
                    c.country,
                    c.created_at,
                    c.updated_at,
                )
                for c in customers
            ]

            rows_affected = self.db.execute_batch(query, data)
            self.logger.info(f"Loaded {rows_affected} customer records")
            return rows_affected

        except Exception as e:
            self.logger.error(f"Error loading customers: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def load_products(self, products: List[Product]) -> int:
        """Load product data into database."""
        if not products:
            self.logger.warning("No products to load")
            return 0

        self.db.connect()
        
        try:
            query = """
                INSERT INTO products 
                (product_id, name, category, subcategory, price, description, manufacturer, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory,
                    price = EXCLUDED.price,
                    description = EXCLUDED.description,
                    manufacturer = EXCLUDED.manufacturer,
                    updated_at = EXCLUDED.updated_at
            """

            data = [
                (
                    p.product_id,
                    p.name,
                    p.category,
                    p.subcategory,
                    p.price,
                    p.description,
                    p.manufacturer,
                    p.created_at,
                    p.updated_at,
                )
                for p in products
            ]

            rows_affected = self.db.execute_batch(query, data)
            self.logger.info(f"Loaded {rows_affected} product records")
            return rows_affected

        except Exception as e:
            self.logger.error(f"Error loading products: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def load_sales(self, sales: List[Sale]) -> int:
        """Load sales data into database."""
        if not sales:
            self.logger.warning("No sales to load")
            return 0

        self.db.connect()
        
        try:
            query = """
                INSERT INTO sales 
                (sale_id, customer_id, product_id, quantity, unit_price, total_value, 
                 sale_date, year, month, quarter, state, payment_method, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sale_id) DO UPDATE SET
                    customer_id = EXCLUDED.customer_id,
                    product_id = EXCLUDED.product_id,
                    quantity = EXCLUDED.quantity,
                    unit_price = EXCLUDED.unit_price,
                    total_value = EXCLUDED.total_value,
                    sale_date = EXCLUDED.sale_date,
                    year = EXCLUDED.year,
                    month = EXCLUDED.month,
                    quarter = EXCLUDED.quarter,
                    state = EXCLUDED.state,
                    payment_method = EXCLUDED.payment_method,
                    updated_at = EXCLUDED.updated_at
            """

            data = [
                (
                    s.sale_id,
                    s.customer_id,
                    s.product_id,
                    s.quantity,
                    s.unit_price,
                    s.total_value,
                    s.sale_date,
                    s.year,
                    s.month,
                    s.quarter,
                    s.state,
                    s.payment_method,
                    s.created_at,
                    s.updated_at,
                )
                for s in sales
            ]

            rows_affected = self.db.execute_batch(query, data)
            self.logger.info(f"Loaded {rows_affected} sales records")
            return rows_affected

        except Exception as e:
            self.logger.error(f"Error loading sales: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def load_quality_report(self, report_data: Dict[str, Any]) -> int:
        """Load data quality report into database."""
        self.db.connect()
        
        try:
            query = """
                INSERT INTO data_quality_reports 
                (report_timestamp, total_records_processed, valid_records, invalid_records, 
                 duplicates_removed, missing_values_count, missing_values_percentage, 
                 data_type_errors, date_conversion_errors, processing_time_seconds, report_details)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            import json
            data = (
                report_data.get('report_timestamp'),
                report_data.get('total_records_processed', 0),
                report_data.get('valid_records', 0),
                report_data.get('invalid_records', 0),
                report_data.get('duplicates_removed', 0),
                report_data.get('missing_values_count', 0),
                report_data.get('missing_values_percentage', 0.0),
                report_data.get('data_type_errors', 0),
                report_data.get('date_conversion_errors', 0),
                report_data.get('processing_time_seconds', 0.0),
                json.dumps(report_data, default=str),
            )

            rows_affected = self.db.execute_update(query, data)
            self.logger.info(f"Quality report loaded successfully")
            return rows_affected

        except Exception as e:
            self.logger.error(f"Error loading quality report: {str(e)}")
            raise
        finally:
            self.db.disconnect()
