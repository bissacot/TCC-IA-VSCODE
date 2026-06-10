FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8501
EXPOSE 5000

CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
