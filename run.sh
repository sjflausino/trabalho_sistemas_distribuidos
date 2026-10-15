#!/bin/bash
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}=== Iniciando o Ambiente de Sistemas Distribuídos ===${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Erro: Docker não encontrado.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Erro: Docker Compose não encontrado.${NC}"
    exit 1
fi

echo -e "${YELLOW}Limpando containers anteriores...${NC}"
if command -v docker compose &> /dev/null; then
    docker compose down
else
    docker-compose down
fi

echo -e "${YELLOW}Construindo e subindo os containers...${NC}"
if command -v docker compose &> /dev/null; then
    docker compose up --build -d
else
    docker-compose up --build -d
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Ambiente iniciado com sucesso!${NC}"
    docker ps
    echo -e "\n${GREEN}=== Serviços Disponíveis ===${NC}"
    echo -e "- RabbitMQ Management UI: ${YELLOW}http://localhost:15672${NC} (User: admin / Pass: admin123)"
    echo -e "- Kafka Broker:           ${YELLOW}localhost:9092${NC}"
    echo -e "- gRPC Service:           ${YELLOW}localhost:50051${NC}"
    echo -e "- REST API:               ${YELLOW}localhost:8080${NC}"
else
    echo -e "${RED}Erro ao iniciar os containers.${NC}"
    exit 1
fi
