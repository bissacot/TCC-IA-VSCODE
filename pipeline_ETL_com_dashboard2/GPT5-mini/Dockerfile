FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV PYTHONPATH=/app
EXPOSE 8501 5000
CMD ["bash","-lc","streamlit run src/dashboard/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
