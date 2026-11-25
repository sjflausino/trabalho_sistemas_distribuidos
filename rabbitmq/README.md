# Módulo RabbitMQ: Sistema de Mensageria Distribuída (AMQP)

Este módulo demonstra a implementação do protocolo **AMQP 0-9-1** (Advanced Message Queuing Protocol) utilizando o **RabbitMQ** como message broker distribuído.

---

## 🎯 1. Objetivo e Domínio Teórico

Diferente do gRPC e REST (focados em chamadas remotas e requisição-resposta diretas), o RabbitMQ opera no paradigma de **Comunicação Indireta e Assíncrona mediada por Broker**.

Este projeto demonstra as principais vantagens e características arquiteturais do protocolo:

1. **Interoperabilidade entre Linguagens (Sistemas Poliglotas):**
   O sistema foi desenhado com um **Consumidor em Go** e um **Produtor em Python**. O protocolo AMQP 0-9-1 padroniza os frames binários sobre TCP, permitindo a troca transparente de dados entre linguagens de paradigmas distintos (Python interpretado e Go compilado nativo).
2. **Desacoplamento em Três Dimensões:**
   - **Espacial:** Produtores e consumidores não conhecem o IP/porta um do outro; ambos apenas conhecem o broker.
   - **Temporal:** O produtor pode publicar mensagens mesmo que o consumidor esteja offline. As mensagens ficam salvas na fila até o consumo.
   - **Sincronização:** O produtor publica a mensagem e continua seu fluxo sem ficar bloqueado aguardando o processamento do consumidor.
3. **Garantia de Entrega e Tolerância a Falhas:**
   Mecanismos nativos de confirmação manual (*acknowledgments*) e persistência em disco garantem confiabilidade (*at-least-once delivery*).

---

## 🛠️ 2. Características Implementadas: Roteamento de Mensagens

No nosso script de demonstração (`producer/producer.py`), cobrimos os 3 tipos fundamentais de trocas (Exchanges) com foco em suas propriedades:

### ● Fanout Exchange (Troca de Emissão)
- **Roteia mensagens para todas as filas vinculadas a ela.**
- **Ignora completamente a chave de roteamento** na mensagem.
- *Demonstração prática:* Vinculamos 3 filas (`Email`, `SMS`, `Auditoria`). O produtor publica com uma chave arbitrária qualquer; todas as 3 filas recebem cópias idênticas.

### ● Direct Exchange (Troca Direta)
- **Roteia mensagens para filas com base em uma chave de roteamento.**
- A chave de roteamento deve **corresponder exatamente** à chave especificada na mensagem.
- **Propriedade fundamental:** *Se várias filas se associarem à mesma chave, funciona como fanout.*
- *Demonstração prática:*
  - Mensagem com chave `info` vai apenas para a fila de `Logs Gerais`.
  - Mensagem com chave `erro` vai para `Alertas` E para `Logs Gerais` (comportamento de **fanout** para a chave `erro`).

### ● Topic Exchange (Troca de Tópico)
- **Roteia mensagens para filas com base em padrões de chave de roteamento.**
- As filas são vinculadas à troca com uma chave de roteamento que inclui padrões:
  - `*` (asterisco): substitui exatamente **uma** palavra.
  - `#` (cardeal): substitui **zero ou mais** palavras.
- **Propriedade fundamental:** *Se a chave corresponder ao padrão de várias filas, funciona como fanout.*
- *Demonstração prática:*
  - Fila 1 escuta `iot.*.temperatura`
  - Fila 2 escuta `iot.sp.#`
  - Fila 3 escuta `iot.#`
  - A mensagem `iot.sp.temperatura` corresponde aos padrões das 3 filas simultaneamente, sendo entregue a todas elas (**funciona como fanout**).
  - A mensagem `iot.rj.pressao` casa apenas com o padrão global `iot.#`.

---

## ⚙️ 3. Outras Características Demonstradas no Produtor

* **Balanceamento de Carga (Work Queues):**
  - **Round-Robin Simples:** Distribuição circular sequencial e uniforme (50% / 50%).
  - **Round-Robin Ponderado:** Controle de fluxo proporcional à capacidade computacional do nó via `basic_qos(prefetch_count=N)`.
* **Persistência e Confirmações (ACK):**
  - **Transiente vs Persistente:** Fila e mensagem voláteis em RAM (`delivery_mode=1`) vs salvas em Disco (`delivery_mode=2`).
  - **auto_ack=True:** Simula crash com perda definitiva de mensagem no broker.
  - **auto_ack=False:** Simula falha do worker onde o broker reenfileira a mensagem (`basic_nack(requeue=True)`) para outro nó recuperar com `basic_ack()`.
* **Filas com Prioridade (`x-max-priority`):**
  - Mensagens com prioridades de 1 a 10 furam a fila FIFO convencional, entregando emergências em primeiro lugar.
* **Comunicação Cruzada Python -> Go:**
  - O produtor Python envia mensagens estruturadas em JSON que são processadas em tempo real pelo consumidor Go.

---

## 📁 4. Estrutura de Diretórios

```text
rabbitmq/
├── docker-compose.yml      # Configuração Docker Compose independente do RabbitMQ
├── consumer/
│   ├── main.go             # Implementação do Consumidor em Go
│   ├── Dockerfile          # Container do Consumidor
│   └── go.mod              # Módulo Go e driver amqp091-go
├── producer/
│   ├── producer.py         # Implementação do Produtor e Demonstrações em Python
│   ├── Dockerfile          # Container do Produtor
│   └── requirements.txt    # Dependência Python (pika)
└── README.md
```

---

## 🚀 5. Como Executar

O ambiente é 100% conteinerizado utilizando Docker Compose. Todos os comandos devem ser executados dentro da pasta `rabbitmq/`.

**Passo 1: Navegue até o diretório e suba a infraestrutura:**

```bash
cd rabbitmq
docker compose up --build -d
```

---

**Passo 2: Acompanhe os logs do Consumidor (Go):**
Abra um terminal e monitore o consumidor em Go em tempo real:

```bash
docker logs -f rabbitmq_consumer
```

O consumidor exibirá logs estruturados detalhando em tempo real:
- **Demonstração Fanout:** Confirmação de recebimento em broadcast com a chave de roteamento ignorada;
- **Demonstração Direct:** Entrega seletiva por chave exata (`info`) e comportamento de Fanout para chaves compartilhadas (`erro`);
- **Demonstração Topic:** Validação de padrões de tópicos com curingas `*` (1 palavra) e `#` (0 ou mais palavras);
- **Interoperabilidade Polyglot:** Metadados AMQP, decodificação JSON, cálculo de latência e payload formatado;
- **Confirmação Manual (`ACK`):** Todas as mensagens são confirmadas explicitamente pelo Go.

---

**Passo 3: Execute o Produtor (Python):**
Em outro terminal, dispare as demonstrações:

```bash
docker exec -it rabbitmq_producer python producer.py
```

Você verá a saída detalhada com cada tipo de roteamento (Fanout, Direct, Topic) e suas regras no terminal do produtor, e a recepção detalhada das mensagens no terminal do Go!

---

**Passo 4: Painel Web de Gestão (Opcional):**
- **URL:** [http://localhost:15672](http://localhost:15672)
- **Usuário:** `admin`
- **Senha:** `admin123`

---

**Passo 5: Encerrar os containers:**
```bash
docker compose down
```
