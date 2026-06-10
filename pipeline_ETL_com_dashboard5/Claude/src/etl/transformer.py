"""
Data transformation logic.
"""

from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
import pandas as pd
from src.utils.logger import get_logger
from src.utils.validators import Validators
from src.models.schemas import DataQualityReport, Sale, Customer, Product


logger = get_logger()


class DataTransformer:
    """Transform and clean extracted data."""

    def __init__(self):
        self.logger = get_logger()
        self.quality_report = DataQualityReport(
            report_timestamp=datetime.now()
        )

    def transform_customers(self, raw_data: List[Dict[str, Any]]) -> Tuple[List[Customer], List[Dict[str, Any]]]:
        """
        Transform and validate customer data.
        
        Returns:
            Tuple of (valid_customers, error_records)
        """
        valid_customers = []
        error_records = []

        self.logger.info(f"Transforming {len(raw_data)} customer records...")

        for idx, record in enumerate(raw_data):
            try:
                # Validate required fields
                customer_id = str(record.get('customer_id', '')).strip()
                name = str(record.get('name', '')).strip()
                email = str(record.get('email', '')).strip()

                if not customer_id or not name or not email:
                    error_records.append({
                        'index': idx,
                        'error': 'Missing required fields (customer_id, name, email)',
                        'record': record
                    })
                    self.quality_report.invalid_records += 1
                    continue

                # Validate email
                if not Validators.validate_email(email):
                    error_records.append({
                        'index': idx,
                        'error': f'Invalid email format: {email}',
                        'record': record
                    })
                    self.quality_report.invalid_records += 1
                    continue

                # Validate phone if present
                phone = record.get('phone')
                if phone and not Validators.is_null_or_empty(phone):
                    if not Validators.validate_phone(str(phone)):
                        self.logger.warning(f"Invalid phone format for customer {customer_id}: {phone}")
                    phone = str(phone).strip()
                else:
                    phone = None

                customer = Customer(
                    customer_id=customer_id,
                    name=name,
                    email=email,
                    phone=phone,
                    address=Validators.sanitize_string(record.get('address', '')),
                    city=Validators.sanitize_string(record.get('city', '')),
                    state=Validators.sanitize_string(record.get('state', '')) or None,
                    zip_code=Validators.sanitize_string(record.get('zip_code', '')),
                    country=Validators.sanitize_string(record.get('country', '')),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

                valid_customers.append(customer)
                self.quality_report.valid_records += 1

            except Exception as e:
                self.logger.error(f"Error transforming customer record {idx}: {str(e)}")
                error_records.append({
                    'index': idx,
                    'error': str(e),
                    'record': record
                })
                self.quality_report.invalid_records += 1

        self.logger.info(f"Transformed {len(valid_customers)} valid customer records")
        return valid_customers, error_records

    def transform_products(self, raw_data: List[Dict[str, Any]]) -> Tuple[List[Product], List[Dict[str, Any]]]:
        """
        Transform and validate product data.
        
        Returns:
            Tuple of (valid_products, error_records)
        """
        valid_products = []
        error_records = []

        self.logger.info(f"Transforming {len(raw_data)} product records...")

        for idx, record in enumerate(raw_data):
            try:
                # Validate required fields
                product_id = str(record.get('product_id', '')).strip()
                name = str(record.get('name', '')).strip()
                category = str(record.get('category', '')).strip()
                price_str = str(record.get('price', '')).strip()

                if not product_id or not name or not category or not price_str:
                    error_records.append({
                        'index': idx,
                        'error': 'Missing required fields (product_id, name, category, price)',
                        'record': record
                    })
                    self.quality_report.invalid_records += 1
                    continue

                # Validate price
                if not Validators.validate_numeric(price_str, allow_negative=False):
                    error_records.append({
                        'index': idx,
                        'error': f'Invalid price format: {price_str}',
                        'record': record
                    })
                    self.quality_report.invalid_records += 1
                    self.quality_report.data_type_errors += 1
                    continue

                product = Product(
                    product_id=product_id,
                    name=name,
                    category=category,
                    subcategory=Validators.sanitize_string(record.get('subcategory', '')),
                    price=float(price_str),
                    description=record.get('description'),
                    manufacturer=Validators.sanitize_string(record.get('manufacturer', '')),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

                valid_products.append(product)
                self.quality_report.valid_records += 1

            except Exception as e:
                self.logger.error(f"Error transforming product record {idx}: {str(e)}")
                error_records.append({
                    'index': idx,
                    'error': str(e),
                    'record': record
                })
                self.quality_report.invalid_records += 1

        self.logger.info(f"Transformed {len(valid_products)} valid product records")
        return valid_products, error_records

    def transform_sales(
        self,
        raw_data: List[Dict[str, Any]],
        customers: Dict[str, Customer],
        products: Dict[str, Product]
    ) -> Tuple[List[Sale], List[Dict[str, Any]]]:
        """
        Transform and validate sales data.
        
        Returns:
            Tuple of (valid_sales, error_records)
        """
        valid_sales = []
        error_records = []
        duplicates_found = set()

        self.logger.info(f"Transforming {len(raw_data)} sales records...")

        for idx, record in enumerate(raw_data):
            try:
                # Validate required fields
                sale_id = str(record.get('sale_id', '')).strip()
                customer_id = str(record.get('customer_id', '')).strip()
                product_id = str(record.get('product_id', '')).strip()
                quantity_str = str(record.get('quantity', '')).strip()
                unit_price_str = str(record.get('unit_price', '')).strip()
                sale_date_str = str(record.get('sale_date', '')).strip()

                if not sale_id or not customer_id or not product_id:
                    error_records.append({
                        'index': idx,
                        'error': 'Missing required fields (sale_id, customer_id, product_id)',
                        'record': record
                    })
                    self.quality_report.invalid_records += 1
                    continue

                # Check for duplicates
                if sale_id in duplicates_found:
                    self.logger.warning(f"Duplicate sale_id found: {sale_id}")
                    self.quality_report.duplicates_removed += 1
                    continue

                duplicates_found.add(sale_id)

                # Validate numeric fields
                if not Validators.validate_numeric(quantity_str, allow_negative=False):
                    error_records.append({
                        'index': idx,
                        'error': f'Invalid quantity format: {quantity_str}',
                        'record': record
                    })
                    self.quality_report.invalid_records += 1
                    self.quality_report.data_type_errors += 1
                    continue

                if not Validators.validate_numeric(unit_price_str, allow_negative=False):
                    error_records.append({
                        'index': idx,
                        'error': f'Invalid unit_price format: {unit_price_str}',
                        'record': record
                    })
                    self.quality_report.invalid_records += 1
                    self.quality_report.data_type_errors += 1
                    continue

                # Validate and parse date
                is_valid_date, parsed_date = Validators.validate_date_format(sale_date_str)
                if not is_valid_date:
                    error_records.append({
                        'index': idx,
                        'error': f'Invalid date format: {sale_date_str}',
                        'record': record
                    })
                    self.quality_report.invalid_records += 1
                    self.quality_report.date_conversion_errors += 1
                    continue

                # Validate customer and product exist
                if customer_id not in customers:
                    self.logger.warning(f"Customer {customer_id} not found for sale {sale_id}")
                    # Continue anyway as this might be normal in some cases
                
                if product_id not in products:
                    self.logger.warning(f"Product {product_id} not found for sale {sale_id}")
                    # Continue anyway

                quantity = int(quantity_str)
                unit_price = float(unit_price_str)
                total_value = quantity * unit_price

                sale = Sale(
                    sale_id=sale_id,
                    customer_id=customer_id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_value=total_value,
                    sale_date=parsed_date,
                    year=parsed_date.year,
                    month=parsed_date.month,
                    quarter=(parsed_date.month - 1) // 3 + 1,
                    state=Validators.sanitize_string(record.get('state', '')) or None,
                    payment_method=record.get('payment_method'),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

                valid_sales.append(sale)
                self.quality_report.valid_records += 1

            except Exception as e:
                self.logger.error(f"Error transforming sales record {idx}: {str(e)}")
                error_records.append({
                    'index': idx,
                    'error': str(e),
                    'record': record
                })
                self.quality_report.invalid_records += 1

        self.logger.info(f"Transformed {len(valid_sales)} valid sales records")
        return valid_sales, error_records

    def remove_duplicates(self, data: List[Dict[str, Any]], key_field: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Remove duplicate records based on key field.
        
        Returns:
            Tuple of (unique_data, duplicates_count)
        """
        seen_keys = set()
        unique_data = []
        duplicates_count = 0

        for record in data:
            key = record.get(key_field)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_data.append(record)
            else:
                duplicates_count += 1

        return unique_data, duplicates_count

    def calculate_missing_values_stats(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate missing values statistics."""
        if not data:
            return {}

        stats = {}
        total_fields = len(data[0]) if data else 0
        total_values = len(data) * total_fields

        for row in data:
            for field, value in row.items():
                if Validators.is_null_or_empty(value):
                    stats[field] = stats.get(field, 0) + 1

        # Convert counts to percentages
        for field in stats:
            stats[field] = (stats[field] / len(data)) * 100

        return stats
