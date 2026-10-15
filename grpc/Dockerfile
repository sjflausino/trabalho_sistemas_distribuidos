FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir grpcio grpcio-tools protobuf
COPY . /app
EXPOSE 50051
CMD ["python", "server/app.py"]
