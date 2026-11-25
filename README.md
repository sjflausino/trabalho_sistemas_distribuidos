# Trabalho de Sistemas Distribuídos

Este repositório contém a implementação prática de diferentes paradigmas de comunicação e middlewares para Sistemas Distribuídos, desenvolvida para a disciplina **Sistemas Distribuídos para Sistemas de Informação**.

Cada tecnologia foi estruturada em seu próprio módulo independente, contendo seu próprio `docker-compose.yml`, código-fonte (em arquiteturas poliglota Go e Python) e documentação técnica detalhada.

---

## 📁 Estrutura do Repositório

```text
trabalho_sistemas_distribuidos/
├── grpc/                  # Módulo gRPC (RPC síncrono e streaming com HTTP/2 e Protobuf)
│   ├── docker-compose.yml # Orquestração independente do gRPC
│   ├── proto/             # Contrato de interface (IDL)
│   ├── server/            # Servidor em Go
│   ├── client/            # Cliente em Python
│   └── README_GRPC.md     # Documentação detalhada do gRPC
│
├── rabbitmq/              # Módulo RabbitMQ (AMQP 0-9-1 com Message Broker)
│   ├── docker-compose.yml # Orquestração independente do RabbitMQ
│   ├── producer/          # Produtor em Python (Fanout, Direct, Topic, Work Queues)
│   ├── consumer/          # Consumidor em Go
│   └── README.md          # Documentação detalhada do RabbitMQ
│
├── kafka/                 # Módulo Apache Kafka (Log distribuído em cluster KRaft)
│   ├── docker-compose.yml # Cluster com 3 brokers Kafka, produtor e consumidor
│   ├── producer/          # Produtor em Python
│   ├── consumer/          # Consumidor em Go (Consumer Groups e Partições)
│   └── README_KAFKA.md    # Documentação detalhada do Kafka
│
├── rest/                  # Módulo REST (HTTP/1.1 com Nginx Load Balancer)
│   ├── docker-compose.yml # Nginx + 3 réplicas Go + cliente Python
│   ├── nginx/             # Configuração do balanceamento round-robin
│   ├── server/            # Servidor REST em Go
│   ├── client/            # Cliente REST em Python
│   └── README_REST.md     # Documentação detalhada do REST
│
└── ROTEIRO_APRESENTACAO.md # Roteiro para gravação e apresentação dos módulos
```

---

## 🚀 Como Executar Cada Módulo

Cada pasta possui seu próprio `docker-compose.yml`. Para rodar qualquer um dos módulos, basta navegar até o diretório correspondente e executar o Docker Compose.

### 1. gRPC (RPC e Streaming)
```bash
cd grpc
docker compose up --build -d

# Ver logs do servidor Go
docker logs -f grpc_server

# Executar cliente Python (unário + streaming)
docker exec -it grpc_client python client.py

# Parar o módulo
docker compose down
```
👉 Detalhes completos: [`grpc/README_GRPC.md`](grpc/README_GRPC.md)

---

### 2. RabbitMQ (AMQP 0-9-1)
```bash
cd rabbitmq
docker compose up --build -d

# Monitorar consumidor Go
docker logs -f rabbitmq_consumer

# Executar demonstrações no produtor Python (Fanout, Direct, Topic, Work Queues)
docker exec -it rabbitmq_producer python producer.py

# Painel Web de Gestão: http://localhost:15672 (admin / admin123)

# Parar o módulo
docker compose down
```
👉 Detalhes completos: [`rabbitmq/README.md`](rabbitmq/README.md)

---

### 3. Apache Kafka (Cluster Distribuído KRaft)
```bash
cd kafka
docker compose up --build -d

# Iniciar consumidores nos grupos (em terminais separados)
docker exec -it kafka_consumer ./consumer -grupo processamento -nome consumidor-1

# Disparar envio de leituras pelo produtor Python
docker exec -it kafka_producer python producer.py

# Parar o módulo
docker compose down
```
👉 Detalhes completos: [`kafka/README_KAFKA.md`](kafka/README_KAFKA.md)

---

### 4. REST (Nginx + Balanceamento de Carga)
```bash
cd rest
docker compose up --build -d

# Acompanhar logs das 3 réplicas
docker compose logs -f rest_server_1 rest_server_2 rest_server_3

# Executar cliente Python
docker exec -it rest_client python client.py

# Parar o módulo
docker compose down
```
👉 Detalhes completos: [`rest/README_REST.md`](rest/README_REST.md)
