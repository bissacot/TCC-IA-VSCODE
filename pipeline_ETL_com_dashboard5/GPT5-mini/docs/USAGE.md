# Usage

1. Copy `.env.example` to `.env` and customize values.
2. Prepare data files under `data/` (`sales.csv`, `customers.json`).
3. Start services with Docker Compose:

```bash
docker-compose up --build
```

4. Run ETL once inside the container or locally:

```bash
python -m src.etl
```

5. Open Streamlit dashboard at `http://localhost:8501`.

6. Run tests:

```bash
pytest -q
```
