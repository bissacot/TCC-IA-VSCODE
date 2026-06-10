# Contributing Guidelines

## Welcome! 👋

Thank you for your interest in contributing to the ETL Pipeline & Dashboard project. This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and professional
- Provide constructive feedback
- Focus on the code, not the person
- Report issues responsibly

## Getting Started

### 1. Fork the Repository

```bash
# Click "Fork" on GitHub
git clone https://github.com/your-username/pipeline-etl-dashboard.git
cd pipeline-etl-dashboard
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
make dev-install
```

## Development Workflow

### 1. Make Changes

- Follow [Code Style Guide](#code-style)
- Keep commits logical and descriptive
- Update documentation if needed

### 2. Test Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_etl_pipeline.py -v

# Check coverage
pytest tests/ --cov=src --cov-report=html
```

### 3. Code Quality Checks

```bash
# Lint code
flake8 src tests

# Type checking
mypy src

# Format code
black src tests
```

### 4. Commit Changes

```bash
git add .
git commit -m "Add feature: description of what was added"
```

**Commit Message Format**:
```
feat: Add new feature
fix: Fix bug description
docs: Update documentation
test: Add tests for feature
refactor: Refactor code section
perf: Improve performance
chore: Update dependencies
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Compare across forks
4. Provide description of changes
5. Submit PR

## Code Style Guide

### Python PEP 8

```python
# Good
def process_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process data with validation and transformation."""
    result = {}
    for item in data:
        result[item['id']] = transform_item(item)
    return result

# Bad
def processData(data):
    result = {}
    for i in data:
        result[i['id']] = transformItem(i)
    return result
```

### Type Hints

```python
# Always use type hints
from typing import List, Dict, Optional, Any

def extract_data(source_path: str) -> List[Dict[str, Any]]:
    """Extract data from source."""
    pass

def calculate_total(values: List[float]) -> float:
    """Calculate total of values."""
    return sum(values)

def find_item(items: List[Dict], key: str) -> Optional[Dict]:
    """Find item by key."""
    for item in items:
        if item.get('id') == key:
            return item
    return None
```

### Docstrings

```python
def transform_sales_data(raw_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], DataQualityMetrics]:
    """
    Transform raw sales data.
    
    Performs validation, cleaning, and enrichment on raw sales records.
    
    Args:
        raw_data: List of raw sales dictionaries
        
    Returns:
        Tuple containing:
        - List of transformed sales records
        - Data quality metrics
        
    Raises:
        ValueError: If data validation fails
        
    Example:
        >>> raw = [{"sale_id": "S001", "quantity": 2}]
        >>> transformed, metrics = transform_sales_data(raw)
        >>> len(transformed) == 1
        True
    """
    pass
```

### Naming Conventions

```python
# Classes: PascalCase
class DataQualityMetrics:
    pass

# Functions/Methods: snake_case
def validate_record(record):
    pass

# Constants: UPPER_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private/Internal: _leading_underscore
def _helper_function():
    pass
```

### Line Length

- Maximum 100 characters
- Break long lines logically

```python
# Good
result = self.repository.query_sales(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    state="SP"
)

# Bad
result = self.repository.query_sales(start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), state="SP")
```

## Testing

### Write Tests

```python
# tests/test_transformers.py

import pytest
from src.etl.transformers import SalesTransformer

class TestSalesTransformer:
    """Test SalesTransformer class."""
    
    def test_validate_record_valid(self):
        """Test validation of valid record."""
        transformer = SalesTransformer()
        record = {
            "sale_id": "S001",
            "customer_id": "C001",
            "product_id": "P001",
            "quantity": 2,
            "unit_price": 50.00,
            "sale_date": "2024-01-15"
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is True
        assert error is None
    
    def test_validate_record_missing_field(self):
        """Test validation with missing field."""
        transformer = SalesTransformer()
        record = {
            "sale_id": "S001",
            "customer_id": "C001",
            # Missing product_id
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is False
        assert "Missing" in error
```

### Test Naming

```python
# Good test names
def test_validate_record_with_valid_data():
    pass

def test_extract_raises_error_when_file_not_found():
    pass

def test_transform_removes_duplicates():
    pass

# Bad test names
def test_validate():
    pass

def test_error():
    pass

def test_it():
    pass
```

## Documentation

### Update Documentation

- Update relevant `.md` files in `docs/`
- Add docstrings to new functions
- Update README.md if adding major features
- Include code examples

### Documentation Format

```markdown
# Feature Title

## Overview
Brief description of the feature.

## Usage

### Basic Example
```python
from src.module import function

result = function(parameter)
```

### Advanced Usage
More complex examples...

## Configuration
Any configuration needed.

## See Also
- [Related Docs](path/to/docs)
```

## Pull Request Process

1. **Before Submitting**:
   - [ ] Code passes `pytest`
   - [ ] Code passes `flake8 src`
   - [ ] Code passes `mypy src`
   - [ ] Code formatted with `black src`
   - [ ] Tests added for new features
   - [ ] Documentation updated
   - [ ] Commit messages clear and descriptive

2. **PR Description**:
   ```markdown
   ## Description
   Brief description of changes.
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## How Has This Been Tested?
   Description of testing performed.
   
   ## Checklist
   - [ ] Tests pass
   - [ ] Code formatted
   - [ ] Documentation updated
   - [ ] No breaking changes
   ```

3. **Review Process**:
   - Maintainers review your PR
   - Provide feedback if needed
   - Make requested changes
   - PR is merged after approval

## Reporting Bugs

### Bug Report Template

```markdown
## Describe the Bug
Clear description of the bug.

## To Reproduce
Steps to reproduce:
1. ...
2. ...
3. ...

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: Windows 10 / macOS / Linux
- Python Version: 3.11
- Package Versions: (pip list)

## Error Message
```
Full error message and traceback
```

## Logs
Relevant log entries from `logs/` directory.

## Additional Context
Any other relevant information.
```

## Feature Requests

### Feature Request Template

```markdown
## Description
Clear description of the requested feature.

## Use Case
Why this feature is needed.

## Proposed Solution
Your suggested implementation (optional).

## Alternatives Considered
Other approaches you considered.

## Additional Context
Mockups, examples, references.
```

## Development Best Practices

### 1. Modular Code

```python
# Good: Each function has single responsibility
def validate_sales(data):
    return [validate_record(record) for record in data]

def validate_record(record):
    # Single validation responsibility
    pass

# Bad: Multiple responsibilities
def validate_and_transform_and_load(data):
    # Does too much in one function
    pass
```

### 2. Error Handling

```python
# Good: Specific error handling
try:
    data = extractor.extract()
except FileNotFoundError:
    logger.error("Data file not found")
    raise
except json.JSONDecodeError:
    logger.error("Invalid JSON format")
    raise

# Bad: Generic error handling
try:
    data = extractor.extract()
except:
    pass
```

### 3. Logging

```python
# Use structured logging
from src.logger import get_logger

logger = get_logger(__name__)

def process_data(data):
    logger.info(f"Processing {len(data)} records")
    try:
        result = transform(data)
        logger.info(f"Successfully processed {len(result)} records")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

### 4. Configuration

```python
# Use environment variables
from src.config import config

def connect_database():
    connection_string = config.get_database_url()
    return connect(connection_string)
```

## Useful Commands

```bash
# Run all checks
make lint
make test
make format

# Individual commands
pytest tests/ -v
flake8 src tests
mypy src
black src tests

# View code coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Questions?

- 📖 Check [Documentation](README.md)
- 🐛 Search [Existing Issues](../../issues)
- 💬 Create [Discussion](../../discussions)
- 📧 Contact maintainers

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page

Thank you for contributing! 🙏
