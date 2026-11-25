FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mantém o container ativo para execução manual interativa
CMD ["tail", "-f", "/dev/null"]
