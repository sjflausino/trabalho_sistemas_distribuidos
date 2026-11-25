# Apache Kafka - Telemetria de sensores IoT

Implementação com Apache Kafka no mesmo cenário dos módulos gRPC e REST: sensores enviando leituras de temperatura. O produtor foi escrito em Python e o consumidor em Go. O cluster tem 3 brokers.

## Sobre o Kafka

O Kafka é uma plataforma de mensagens distribuída baseada em um **log**: uma sequência de mensagens em que novas mensagens são sempre acrescentadas no final e nunca alteradas. As mensagens são publicadas em **tópicos**, e cada tópico é dividido em **partições**. Cada mensagem recebe, dentro da sua partição, um número sequencial chamado **offset**.

Os consumidores leem o log no seu próprio ritmo e guardam até onde já leram (o offset). Ler uma mensagem não a remove: ela continua no Kafka até expirar o tempo de retenção, que por padrão é de 7 dias.

Consumidores com o mesmo identificador formam um **consumer group**. Dentro de um grupo, cada partição é lida por apenas um consumidor, e é assim que o trabalho é dividido. Grupos diferentes são independentes: cada um recebe todas as mensagens do tópico.

Cada partição é replicada em vários brokers. Um deles é o **líder**, que recebe as gravações e leituras; os outros mantêm cópias. Se o líder cair, uma das réplicas assume.

Pelos tipos de comunicação da Aula 06, a comunicação com o Kafka é:

- persistente: as mensagens são gravadas em disco e ficam disponíveis mesmo que o consumidor não esteja em execução;
- assíncrona: o produtor não espera o consumidor, só a confirmação do broker;
- confiável: o produtor recebe confirmação da gravação e cada partição tem réplicas;
- discreta: cada mensagem é uma unidade completa (uma leitura de sensor).

Como os middlewares orientados a mensagem descritos na Aula 06, o Kafka oferece comunicação fracamente acoplada no tempo: o produtor pode enviar sem que o consumidor esteja rodando, e o consumidor pode ler depois, mesmo que o produtor já tenha terminado.

## Diferenças em relação ao RabbitMQ

O RabbitMQ (Aula 06) é um broker de mensagens baseado em **filas**. O produtor envia mensagens para uma exchange, que as coloca em uma ou mais filas, e a mensagem é removida da fila quando o consumidor confirma o recebimento. O Kafka é baseado em um **log distribuído**, em que as mensagens permanecem gravadas e cada consumidor controla a própria posição de leitura.

As comparações abaixo consideram as filas tradicionais do RabbitMQ.

| Aspecto | RabbitMQ | Kafka |
|---|---|---|
| Modelo | Fila: a mensagem sai da fila depois de consumida e confirmada | Log: a mensagem fica gravada; o consumidor apenas avança seu offset |
| Releitura | Não é possível reler uma mensagem já confirmada | Qualquer grupo pode ler o tópico desde o início, enquanto as mensagens estiverem retidas |
| Entrega | Push: o broker envia as mensagens ao consumidor | Pull: o consumidor busca as mensagens no broker |
| Roteamento | Exchanges direct, fanout, topic e headers decidem para quais filas a mensagem vai | Não há roteamento: o produtor escolhe o tópico, e a chave da mensagem define a partição |
| Divisão de carga | Consumidores de uma mesma fila recebem as mensagens em round-robin, uma a uma | Cada consumidor do grupo fica com partições inteiras; o número de consumidores ativos é limitado pelo número de partições |
| Mesma mensagem para vários consumidores | Exchange fanout, com uma fila para cada consumidor | Um consumer group para cada aplicação; todos os grupos recebem todas as mensagens |
| Ordem | Com vários consumidores na mesma fila, a ordem de processamento pode mudar | Garantida dentro de cada partição; mensagens com a mesma chave ficam sempre na mesma partição |
| Confirmação do consumidor | Ack de cada mensagem; após o ack, o broker a apaga | Commit do offset; nada é apagado |
| Prioridade | Suporta filas com prioridade | Não suporta prioridade |
| Protocolo | AMQP, padrão aberto | Protocolo binário próprio sobre TCP |
| Distribuição | Cluster de brokers; filas podem ser replicadas | Tópicos divididos em partições, cada uma replicada em vários brokers com um líder |
| Uso típico | Distribuição de tarefas e roteamento flexível de mensagens | Alto volume de eventos, histórico e reprocessamento de dados |

## Arquitetura

```text
produtor Python ──> tópico "leituras" ──> consumidores Go
                    ├── partição 0  (réplicas nos brokers 1, 2 e 3)
                    ├── partição 1  (réplicas nos brokers 1, 2 e 3)
                    └── partição 2  (réplicas nos brokers 1, 2 e 3)
```

- `kafka1`, `kafka2` e `kafka3`: três brokers no modo KRaft, em que os próprios brokers coordenam o cluster, sem Zookeeper.
- `criar_topico`: cria o tópico `leituras` com 3 partições e fator de replicação 3, e depois encerra.
- `kafka_producer`: produtor Python (biblioteca `confluent-kafka`). Envia 9 leituras de 3 sensores, usando o `sensor_id` como chave.
- `kafka_consumer`: consumidor Go (biblioteca `kafka-go`). Recebe o nome do grupo e o nome do consumidor como parâmetros.

**Interoperabilidade:** o produtor Python e o consumidor Go não compartilham código. Os dois usam bibliotecas clientes do Kafka e só precisam concordar sobre o nome do tópico e o formato JSON das mensagens. As ferramentas de linha de comando do próprio Kafka, escritas em Java, acessam o mesmo cluster.

**Distribuição:** as partições são distribuídas entre os brokers, cada um sendo líder de uma delas, e cada partição tem cópia nos três brokers. Os consumidores de um grupo dividem as partições entre si. Se um broker parar, outro assume a liderança das suas partições e o sistema continua funcionando.

## Estrutura

```text
kafka/
├── docker-compose.yml
├── producer/
│   ├── producer.py     # produtor em Python
│   └── Dockerfile
└── consumer/
    ├── main.go         # consumidor em Go
    ├── go.mod
    ├── go.sum
    └── Dockerfile
```

## Como executar

Requisito: Docker com Docker Compose. Todos os comandos são executados dentro da pasta `kafka/`. O teste usa cinco terminais.

**1. Subir o cluster (terminal 1)**

```bash
cd kafka
docker compose up --build -d
docker ps -a
```

O `up` leva cerca de 30 segundos: o produtor e o consumidor só sobem depois que os brokers estão prontos e o tópico foi criado.

Resultado esperado: `kafka1`, `kafka2`, `kafka3`, `kafka_producer` e `kafka_consumer` com status `Up`, e `kafka_criar_topico` com status `Exited (0)`.

**2. Ver como o tópico foi distribuído (terminal 1)**

```bash
docker exec kafka1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka1:9092 --describe --topic leituras
```

Resultado esperado: 3 partições, cada uma com um líder diferente (`Leader`) e réplicas nos 3 brokers (`Replicas` e `Isr`). Se um mesmo broker aparecer como líder de mais de uma partição, aguarde 10 segundos e rode o comando de novo: o Kafka redistribui os líderes automaticamente.

**3. Iniciar três consumidores no mesmo grupo (terminais 2, 3 e 4)**

Um comando em cada terminal:

```bash
docker exec -it kafka_consumer ./consumer -grupo processamento -nome consumidor-1
```

```bash
docker exec -it kafka_consumer ./consumer -grupo processamento -nome consumidor-2
```

```bash
docker exec -it kafka_consumer ./consumer -grupo processamento -nome consumidor-3
```

Cada consumidor mostra `aguardando mensagens` e o terminal fica parado: ele está esperando as mensagens chegarem. Aguarde alguns segundos para que o grupo divida as partições entre os consumidores.

**4. Enviar as leituras (terminal 1)**

```bash
docker exec -it kafka_producer python producer.py
```

Resultado esperado:

- o produtor mostra a partição e o offset de cada mensagem gravada;
- cada consumidor recebe as mensagens de uma única partição, ou seja, de um único sensor;
- as leituras de cada sensor chegam na ordem em que foram enviadas.

**5. Ler as mesmas mensagens com outro grupo (terminal 5)**

```bash
docker exec -it kafka_consumer ./consumer -grupo dashboard -nome painel
```

Resultado esperado: o consumidor `painel` recebe as 9 leituras, desde o offset 0, embora elas já tenham sido consumidas pelo grupo `processamento`. As mensagens continuam no Kafka, e cada grupo tem a sua própria posição de leitura. No RabbitMQ, essas mensagens já teriam sido removidas da fila.

**6. Simular a falha de um broker (terminal 1)**

Parar um broker:

```bash
docker stop kafka2
```

Ver o tópico de novo:

```bash
docker exec kafka1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka1:9092 --describe --topic leituras
```

Resultado esperado: a partição que era liderada pelo broker 2 passa a ter outro líder, e o broker 2 sai da lista `Isr` (réplicas sincronizadas).

Enviar novas leituras:

```bash
docker exec -it kafka_producer python producer.py
```

Resultado esperado: as mensagens são gravadas com offsets 3 a 5, e os consumidores dos terminais 2 a 5 continuam recebendo normalmente.

Religar o broker:

```bash
docker start kafka2
```

Depois de cerca de 20 segundos, ao rodar o `--describe` de novo, o broker 2 volta para a lista `Isr` e reassume a liderança da sua partição.

**7. Encerrar**

Pressione `Ctrl+C` nos terminais dos consumidores. Cada um mostra `encerrado` e devolve a linha de comando. Depois, no terminal 1, execute:

```bash
docker compose down
```