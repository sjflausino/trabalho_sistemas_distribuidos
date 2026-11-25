FROM golang:1.24-alpine

WORKDIR /app

# Só a biblioteca padrão do Go: nenhuma dependência externa nem código gerado
COPY . .

RUN go build -o rest-server main.go

EXPOSE 8080

CMD ["./rest-server"]
