FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential librdkafka-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir confluent-kafka
COPY . /app
CMD ["python", "producer/producer.py"]
