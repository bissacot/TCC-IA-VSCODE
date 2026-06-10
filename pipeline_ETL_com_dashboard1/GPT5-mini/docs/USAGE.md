# Usage

1. Copy `.env.example` to `.env` and adjust connection settings.
2. Start services with Docker Compose:

```bash
docker-compose -f docker/docker-compose.yml up --build
```

3. Load data by running ETL:

```bash
python src/app/etl/etl_runner.py --once
```

4. Open dashboard at `http://localhost:8501`
