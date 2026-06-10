FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs reports data

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD python -c "import requests; requests.get('http://localhost:8501')" || exit 1

# Default command
CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
