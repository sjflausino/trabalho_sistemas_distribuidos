FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir flask requests
COPY . /app
EXPOSE 8080
CMD ["python", "server/app.py"]
