# Usa uma imagem oficial e leve do Go
FROM golang:1.22-alpine

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependência do Go primeiro
COPY server/go.mod server/go.sum ./
RUN go mod download

# Copia todo o código fonte do servidor para o container
COPY server/ .

# Compila o executável do servidor gRPC
RUN go build -o grpc-server main.go

# Expõe a porta usada pelo gRPC
EXPOSE 50051

# Comando para iniciar o servidor
CMD ["./grpc-server"]