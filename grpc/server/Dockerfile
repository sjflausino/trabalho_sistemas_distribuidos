FROM golang:alpine

WORKDIR /app

# Copia os gerenciadores de dependência e baixa os pacotes
COPY go.mod go.sum ./
RUN go mod download

# Copia o código fonte e os stubs gerados
COPY . .

# Sincroniza e limpa as dependências do go.mod automaticamente
RUN go mod tidy

# Compila o executável
RUN go build -o grpc-server main.go

EXPOSE 50051

CMD ["./grpc-server"]