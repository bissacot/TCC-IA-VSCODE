"""
Pytest configuration file for the ETL pipeline project.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Import and initialize config
    from src.utils.config import Config
    Config.ensure_directories()
    yield


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")


# Test collection options
def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add default markers
        if "test_" in item.nodeid:
            item.add_marker(pytest.mark.unit)
