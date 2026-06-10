FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY . /app
CMD ["streamlit", "run", "src/app/dashboard/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
