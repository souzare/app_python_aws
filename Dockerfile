FROM python:3.11-slim

WORKDIR /app
COPY app.py .

RUN pip install flask opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

CMD ["python", "app.py"]