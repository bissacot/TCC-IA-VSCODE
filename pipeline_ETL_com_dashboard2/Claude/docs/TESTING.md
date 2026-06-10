# Testing Documentation

## Test Structure

```
tests/
├── test_etl.py           # ETL pipeline tests
├── test_extractor.py     # Data extractor tests
├── test_transformer.py   # Data transformation tests
├── test_loader.py        # Data loader tests
└── conftest.py           # Pytest fixtures
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Test File
```bash
pytest tests/test_etl.py -v
```

### Specific Test Function
```bash
pytest tests/test_etl.py::test_extract_valid_csv -v
```

### With Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### With Markers
```bash
pytest tests/ -m "not slow" -v
```

## Test Categories

### Unit Tests

Test individual functions in isolation.

```python
def test_data_transformer_initialization():
    transformer = DataTransformer()
    assert transformer is not None
    assert transformer.quality_metrics == {}
```

### Integration Tests

Test component interactions.

```python
def test_etl_pipeline_end_to_end():
    pipeline = ETLPipeline()
    pipeline.setup_database()
    pipeline.register_data_sources(...)
    success, report, error = pipeline.run()
    assert success is True
```

### Performance Tests

Test performance characteristics.

```python
def test_large_dataset_processing():
    # Generate large dataset
    df = generate_large_dataframe(100000)
    
    # Measure transformation time
    start = time.time()
    result_df, metrics = transformer.transform_sales_data(df)
    elapsed = time.time() - start
    
    assert elapsed < 30  # Should complete in < 30 seconds
```

### Data Quality Tests

Test data validation and cleaning.

```python
def test_handle_missing_values():
    transformer = DataTransformer()
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["John", None, "Jane"],
        "value": [100.0, 200.0, None],
    })
    
    result = transformer._handle_missing_values(df)
    assert result.iloc[1]["name"] == ""
    assert result.iloc[2]["value"] == 0
```

## Fixtures

### Common Fixtures (conftest.py)

```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_csv():
    """Temporary CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,name,value\n1,test,100\n")
        temp_path = f.name
    yield temp_path
    Path(temp_path).unlink()

@pytest.fixture
def sample_dataframe():
    """Sample DataFrame."""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['A', 'B', 'C'],
        'value': [100, 200, 300]
    })
```

## Test Examples

### Extractor Tests

```python
def test_csv_extractor_valid_file(temp_csv):
    extractor = CSVExtractor(temp_csv)
    df = extractor.extract()
    assert len(df) > 0
    assert 'id' in df.columns

def test_csv_extractor_file_not_found():
    extractor = CSVExtractor('/nonexistent.csv')
    with pytest.raises(ExtractionException):
        extractor.extract()

def test_json_extractor_nested_data():
    data = {"users": [{"id": 1, "name": "John"}]}
    # Test extraction with nested path
```

### Transformer Tests

```python
def test_remove_duplicates():
    df = pd.DataFrame({
        'id': [1, 2, 1],
        'name': ['A', 'B', 'A']
    })
    result, metrics = transformer.transform_sales_data(df)
    assert metrics['duplicates_removed'] == 1

def test_data_type_conversion():
    df = pd.DataFrame({
        'quantity': ['2', '3', 'invalid'],
        'price': ['10.5', '20.0', 'x']
    })
    result = transformer._validate_and_convert_sales_types(df)
    # Check types are converted correctly
```

### Loader Tests

```python
def test_load_customers_to_database(session):
    loader = DataLoader(session)
    df = pd.DataFrame({
        'customer_id': ['C001'],
        'name': ['John'],
        'email': ['john@test.com'],
        'state': ['SP']
    })
    count = loader.load_customers(df)
    assert count == 1

def test_load_with_duplicates():
    # Test incremental mode behavior
    # Test duplicate handling
```

## Mocking

### Mock API Responses

```python
from unittest.mock import Mock, patch
import requests

@patch('requests.get')
def test_api_extractor_with_mock(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {'data': [{'id': 1}]}
    mock_get.return_value = mock_response
    
    extractor = APIExtractor('http://api.test', '/products')
    df = extractor.extract()
    assert len(df) > 0
```

### Mock Database

```python
@patch('src.database.connection.DatabaseManager.get_session')
def test_loader_with_mock_session(mock_session):
    mock_session_instance = Mock()
    mock_session.return_value = mock_session_instance
    
    loader = DataLoader()
    # Test loading logic
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest tests/ --cov=src
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Coverage Goals

- Overall: > 80%
- Critical paths: > 95%
- ETL pipeline: > 90%
- Database operations: > 85%

## Test Data Management

### Generate Test Data

```python
def generate_test_sales_data(n_records=100):
    """Generate n records of test sales data."""
    import random
    from datetime import datetime, timedelta
    
    data = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(n_records):
        data.append({
            'sale_id': f'SALE{i:06d}',
            'customer_id': f'CUST{random.randint(1, 100):04d}',
            'product_id': f'PROD{random.randint(1, 50):04d}',
            'quantity': random.randint(1, 10),
            'unit_price': random.uniform(10, 1000),
            'sale_date': start_date + timedelta(days=random.randint(0, 365))
        })
    
    return pd.DataFrame(data)
```

## Performance Benchmarking

```python
import time

def benchmark_transformation():
    df = generate_test_sales_data(10000)
    transformer = DataTransformer()
    
    start = time.time()
    result, metrics = transformer.transform_sales_data(df)
    elapsed = time.time() - start
    
    print(f"Transformed 10000 records in {elapsed:.2f}s")
    print(f"Rate: {10000/elapsed:.0f} records/second")
```

## Troubleshooting Tests

### Common Issues

**Import Errors**
```bash
# Add project to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

**Database Connection Issues**
```bash
# Use fixtures to provide mock connections
# Or set test database URL in .env
export TEST_DATABASE_URL=postgresql://...
```

**Flaky Tests**
```python
# Use pytest-retry for flaky tests
@pytest.mark.flaky(reruns=3)
def test_api_call():
    ...
```

## Test Maintenance

- Update tests when code changes
- Add tests for new features
- Remove tests for deprecated code
- Review test coverage regularly
- Refactor test code for clarity

---

Run `pytest tests/ -v` to execute all tests.
