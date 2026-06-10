.PHONY: help install dev-install test test-cov lint format clean docker-build docker-up docker-down etl-run dashboard-run docs

help:
	@echo "ETL Pipeline & Dashboard - Available Commands"
	@echo "============================================"
	@echo "make install       - Install dependencies"
	@echo "make dev-install   - Install with development dependencies"
	@echo "make test          - Run all tests"
	@echo "make test-cov      - Run tests with coverage report"
	@echo "make lint          - Run code linting"
	@echo "make format        - Format code with black"
	@echo "make clean         - Clean up temporary files"
	@echo "make docker-build  - Build Docker images"
	@echo "make docker-up     - Start Docker containers"
	@echo "make docker-down   - Stop Docker containers"
	@echo "make docker-logs   - View Docker logs"
	@echo "make etl-run       - Run ETL pipeline"
	@echo "make dashboard-run - Run Streamlit dashboard"
	@echo "make docs          - Build documentation"

install:
	pip install -r requirements.txt

dev-install: install
	pip install pytest pytest-cov pytest-mock black flake8 mypy

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

lint:
	flake8 src tests
	mypy src

format:
	black src tests

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	rm -rf htmlcov/
	rm -rf .coverage

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v

etl-run:
	python -m src.etl.pipeline

dashboard-run:
	streamlit run src/dashboard/app.py

db-init:
	psql -h localhost -U etl_user -d sales_db -f database/init.sql

docs:
	@echo "Documentation is available in docs/ directory"

.DEFAULT_GOAL := help
