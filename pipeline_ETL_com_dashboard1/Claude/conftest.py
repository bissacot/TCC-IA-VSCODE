"""
Pytest Configuration and Fixtures
"""

import pytest
from pathlib import Path
import os
from dotenv import load_dotenv


# Load test environment variables
env_file = Path(__file__).parent / ".env.test"
if env_file.exists():
    load_dotenv(env_file)

# Set test environment
os.environ["ENVIRONMENT"] = "testing"


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def data_dir(project_root):
    """Get data directory"""
    data_directory = project_root / "data"
    data_directory.mkdir(exist_ok=True)
    return data_directory


@pytest.fixture(scope="session")
def logs_dir(project_root):
    """Get logs directory"""
    logs_directory = project_root / "logs"
    logs_directory.mkdir(exist_ok=True)
    return logs_directory


@pytest.fixture
def sample_sales_data():
    """Sample sales data for testing"""
    return [
        {
            "sale_id": "S001",
            "customer_id": "C001",
            "product_id": "P001",
            "quantity": 2,
            "unit_price": 50.00,
            "sale_date": "2024-01-15"
        },
        {
            "sale_id": "S002",
            "customer_id": "C002",
            "product_id": "P002",
            "quantity": 1,
            "unit_price": 100.00,
            "sale_date": "2024-01-20"
        },
        {
            "sale_id": "S003",
            "customer_id": "C001",
            "product_id": "P003",
            "quantity": 3,
            "unit_price": 25.50,
            "sale_date": "2024-02-10"
        }
    ]


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return [
        {
            "customer_id": "C001",
            "name": "João Silva",
            "email": "joao@example.com",
            "phone": "(11) 98765-4321",
            "state": "SP",
            "city": "São Paulo"
        },
        {
            "customer_id": "C002",
            "name": "Maria Santos",
            "email": "maria@example.com",
            "phone": "(21) 99876-5432",
            "state": "RJ",
            "city": "Rio de Janeiro"
        }
    ]


@pytest.fixture
def sample_product_data():
    """Sample product data for testing"""
    return [
        {
            "id": "P001",
            "name": "Laptop",
            "category": "Electronics",
            "price": 3000.00,
            "description": "High-performance laptop"
        },
        {
            "id": "P002",
            "name": "Mouse",
            "category": "Electronics",
            "price": 50.00,
            "description": "Wireless mouse"
        },
        {
            "id": "P003",
            "name": "Keyboard",
            "category": "Electronics",
            "price": 150.00,
            "description": "Mechanical keyboard"
        }
    ]


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment"""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG"] = "True"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    yield
    
    # Cleanup (if needed)


# Pytest markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
