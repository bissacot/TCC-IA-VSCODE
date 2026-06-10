"""
Sample data generation for testing and demonstration.
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import random


class SampleDataGenerator:
    """Generate sample data for ETL pipeline testing."""

    # Sample data
    FIRST_NAMES = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa']
    LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    STATES = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI']
    CITIES = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']
    DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'example.com', 'test.com']
    
    PRODUCT_CATEGORIES = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys', 'Food & Beverage']
    PRODUCT_SUBCATEGORIES = {
        'Electronics': ['Computers', 'Smartphones', 'Accessories', 'Audio'],
        'Clothing': ['Men', 'Women', 'Kids', 'Shoes'],
        'Home & Garden': ['Furniture', 'Decor', 'Kitchen', 'Bedding'],
        'Sports': ['Equipment', 'Apparel', 'Footwear', 'Accessories'],
        'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics'],
        'Toys': ['Action Figures', 'Board Games', 'Puzzles', 'Building Blocks'],
        'Food & Beverage': ['Groceries', 'Snacks', 'Beverages', 'Specialty Foods'],
    }
    
    MANUFACTURERS = ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E', 'Generic']
    PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Gift Card']

    @classmethod
    def generate_customers(cls, num_customers: int = 100) -> List[Dict[str, Any]]:
        """Generate sample customer data."""
        customers = []
        for i in range(num_customers):
            first_name = random.choice(cls.FIRST_NAMES)
            last_name = random.choice(cls.LAST_NAMES)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@{random.choice(cls.DOMAINS)}"
            
            customer = {
                'customer_id': f'CUST-{i+1:05d}',
                'name': f'{first_name} {last_name}',
                'email': email,
                'phone': f'{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}',
                'address': f'{random.randint(1, 999)} {random.choice(["Oak", "Maple", "Main", "First"])} Street',
                'city': random.choice(cls.CITIES),
                'state': random.choice(cls.STATES),
                'zip_code': f'{random.randint(10000, 99999)}',
                'country': 'USA',
            }
            customers.append(customer)
        
        return customers

    @classmethod
    def generate_products(cls, num_products: int = 50) -> List[Dict[str, Any]]:
        """Generate sample product data."""
        products = []
        for i in range(num_products):
            category = random.choice(cls.PRODUCT_CATEGORIES)
            subcategory = random.choice(cls.PRODUCT_SUBCATEGORIES[category])
            
            product = {
                'product_id': f'PROD-{i+1:05d}',
                'name': f'{category} Product {i+1}',
                'category': category,
                'subcategory': subcategory,
                'price': round(random.uniform(10.00, 1000.00), 2),
                'description': f'High-quality {category.lower()} product with excellent features',
                'manufacturer': random.choice(cls.MANUFACTURERS),
            }
            products.append(product)
        
        return products

    @classmethod
    def generate_sales(cls, num_sales: int = 500, customer_ids: List[str] = None, product_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Generate sample sales data."""
        if customer_ids is None or product_ids is None:
            raise ValueError("customer_ids and product_ids are required")
        
        sales = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(num_sales):
            sale_date = start_date + timedelta(days=random.randint(0, 365))
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(10.00, 500.00), 2)
            
            sale = {
                'sale_id': f'SALE-{i+1:06d}',
                'customer_id': random.choice(customer_ids),
                'product_id': random.choice(product_ids),
                'quantity': quantity,
                'unit_price': unit_price,
                'sale_date': sale_date.strftime('%Y-%m-%d'),
                'state': random.choice(cls.STATES),
                'payment_method': random.choice(cls.PAYMENT_METHODS),
            }
            sales.append(sale)
        
        return sales

    @classmethod
    def save_customers_to_json(cls, output_path: str, num_customers: int = 100) -> None:
        """Save sample customers to JSON file."""
        customers = cls.generate_customers(num_customers)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(customers, f, indent=2)
        
        print(f"Sample customers saved to {output_path}")

    @classmethod
    def save_products_to_csv(cls, output_path: str, num_products: int = 50) -> None:
        """Save sample products to CSV file."""
        products = cls.generate_products(num_products)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Note: For API, we'd normally fetch this, but generating CSV for demo
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=products[0].keys())
            writer.writeheader()
            writer.writerows(products)
        
        print(f"Sample products saved to {output_path}")

    @classmethod
    def save_sales_to_csv(cls, output_path: str, num_sales: int = 500, num_customers: int = 100, num_products: int = 50) -> None:
        """Save sample sales to CSV file."""
        # Generate supporting data
        customers = cls.generate_customers(num_customers)
        products = cls.generate_products(num_products)
        
        customer_ids = [c['customer_id'] for c in customers]
        product_ids = [p['product_id'] for p in products]
        
        sales = cls.generate_sales(num_sales, customer_ids, product_ids)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sales[0].keys())
            writer.writeheader()
            writer.writerows(sales)
        
        print(f"Sample sales saved to {output_path}")

    @classmethod
    def generate_all_sample_data(cls, data_dir: str = 'data/input') -> None:
        """Generate all sample data files."""
        print("Generating sample data...")
        
        # Generate and save data
        cls.save_customers_to_json(f'{data_dir}/customers.json', num_customers=100)
        cls.save_products_to_csv(f'{data_dir}/products.csv', num_products=50)
        cls.save_sales_to_csv(f'{data_dir}/sales.csv', num_sales=500)
        
        print("Sample data generation completed!")


if __name__ == "__main__":
    SampleDataGenerator.generate_all_sample_data()
