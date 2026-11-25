FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir confluent-kafka

COPY producer.py .

CMD ["tail", "-f", "/dev/null"]