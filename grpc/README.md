# Módulo gRPC: Sistema de Telemetria IoT

Este módulo demonstra a implementação do protocolo **gRPC** (gRPC Remote Procedure Calls) aplicado a um cenário de transmissão de telemetria de sensores IoT.

## 🎯 Objetivo e Domínio Teórico

O gRPC é um framework moderno de RPC (Chamada de Procedimento Remoto) de alto desempenho. O objetivo do RPC é permitir que processos chamem procedimentos em outras máquinas de forma transparente, ocultando a complexidade da troca de mensagens pela rede.

Este projeto demonstra as principais vantagens e características arquiteturais do protocolo:

1. **Interoperabilidade entre Linguagens:** 
   O sistema foi desenhado com um **Servidor em Go** e um **Cliente em Python**. O gRPC garante a comunicação perfeita entre arquiteturas diferentes através do uso de stubs gerados automaticamente, resolvendo problemas clássicos de sistemas distribuídos (como conversão de tipos de dados).
2. **Contratos Fortes (IDL):** 
   A comunicação é estritamente definida pelo arquivo `sensor.proto`. O Protocol Buffers atua como a *Interface Definition Language (IDL)* neutra da aplicação.
3. **Paradigmas de Comunicação Avançados (HTTP/2):**
   Diferente do REST tradicional (focado estritamente em requisição-resposta síncrona), o gRPC utiliza HTTP/2 para permitir multiplexação e fluxos de dados bidirecionais.

## 🛠️ Características Implementadas

No nosso arquivo de contrato (`proto/sensor.proto`), definimos o serviço `SensorService` abordando dois modelos clássicos de comunicação:

*   **Comunicação Unária (Síncrona):** `rpc EnviarLeitura`
    O cliente faz uma chamada remota enviando a leitura do sensor e fica **bloqueado** aguardando a confirmação e resposta do servidor. Representa a comunicação discreta clássica.
*   **Comunicação por Streaming (Assíncrona / Fluxo):** `rpc ObterHistorico`
    O cliente solicita um histórico e o servidor envia os dados como um fluxo contínuo (*stream*). O cliente processa cada pacote assim que chega, sem precisar esperar o lote completo (ideal para lidar com limites de memória e tempo real em sistemas distribuídos).

## 📁 Estrutura de Diretórios

```text
grpc/
├── proto/
│   └── sensor.proto        # Contrato IDL (Protocol Buffers) neutro
├── server/
│   ├── main.go             # Implementação do Servidor em Go
│   ├── Dockerfile          # Container do Servidor
│   └── pb/                 # Stubs gerados para Go
└── client/
    ├── client.py           # Implementação do Cliente em Python
    ├── Dockerfile          # Container do Cliente
    └── sensor_pb2...       # Stubs gerados para Python

```

## 🚀 Como Executar

O ambiente é 100% conteinerizado utilizando Docker Compose.

**1. Suba a infraestrutura:**
Na raiz do projeto (onde está o `docker-compose.yml`), execute:

```bash
docker compose up --build -d

```

**2. Acompanhe os logs do Servidor (Go):**
Abra um terminal e monitore o processamento do servidor em tempo real:

```bash
docker logs -f grpc_server

```

**3. Execute o Cliente (Python):**
Em outro terminal, dispare as chamadas remotas de dentro do container do cliente:

```bash
docker exec -it grpc_client python client.py

```

Você verá a resposta instantânea da chamada Síncrona (Unária) seguida da recepção cadenciada dos dados da chamada em Fluxo (Streaming).
