FROM golang:alpine

WORKDIR /app

COPY go.mod ./
RUN go mod download || true

COPY . .
RUN go mod tidy
RUN go build -o rabbitmq-consumer main.go

CMD ["./rabbitmq-consumer"]
