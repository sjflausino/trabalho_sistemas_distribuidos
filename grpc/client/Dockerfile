FROM python:3.10-slim

WORKDIR /app

# Instala as dependências do gRPC
RUN pip install --no-cache-dir grpcio grpcio-tools protobuf

# Copia o script Python e os stubs gerados
COPY . .

# Mantém o container ativo para execução manual durante o vídeo
CMD ["tail", "-f", "/dev/null"]