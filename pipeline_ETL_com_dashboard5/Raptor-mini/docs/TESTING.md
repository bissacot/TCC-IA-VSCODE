# Testing

## Run unit tests
```powershell
pytest --cov=src tests
```

## Test coverage
- `tests/test_transform.py`
- `tests/test_quality.py`
- `tests/test_load.py`

## Notes
- `test_load.py` uses SQLite for local schema and load validation.
- Additional end-to-end tests can be added by seeding PostgreSQL and verifying dashboard data.
