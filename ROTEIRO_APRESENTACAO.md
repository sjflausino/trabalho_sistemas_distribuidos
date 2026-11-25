# Roteiro de Apresentação em Vídeo: gRPC e RabbitMQ
**Disciplina:** Sistemas Distribuídos para Sistemas de Informação  
**Tempo Limite por Vídeo:** Máximo 5 minutos (rigorosamente cronometrado)  
**Composição da Nota:** 
- 50% Domínio da Teoria sobre Comunicação Distribuída
- 50% Aplicação Prática demonstrando todas as características

---

# 📹 VÍDEO 1: APRESENTAÇÃO gRPC (Tempo Total: ~4min 30s)

## 🖥️ Preparação de Tela (Antes de Começar a Gravar)
1. **Lado Esquerdo da Tela:** Terminal com os logs do servidor monitorando em tempo real:
   ```bash
   docker logs -f grpc_server
   ```
2. **Lado Direito da Tela:** Terminal pronto para executar o cliente Python:
   ```bash
   docker exec -it grpc_client python client.py
   ```
   *(Deixe o comando digitado no terminal direito, pronto para dar Enter na hora indicada).*
3. **Fundo / Aba Secundária:** Arquivo `grpc/proto/sensor.proto` aberto no VS Code.

---

## ⏱️ Cronômetro e Roteiro de Fala Passo a Passo (gRPC)

### 0:00 - 1:15 | Introdução Teórica, IDL e Interoperabilidade
* **O que Mostrar na Tela:** Mostre o arquivo `sensor.proto` no VS Code e aponte para a definição das mensagens e serviços.
* **O que Falar (Roteiro Verbal):**
  > *"Olá! Neste vídeo apresento a implementação prática do protocolo **gRPC** aplicada a um sistema de telemetria de sensores IoT em Sistemas Distribuídos.*
  >
  > *O gRPC é um framework moderno de **Remote Procedure Call (RPC)** de alto desempenho. Ao contrário do modelo REST/HTTP tradicional, que trafega texto plano via HTTP/1.1 e JSON, o gRPC opera sobre **HTTP/2**, viabilizando **multiplexação de conexões na mesma porta TCP**, compressão binária de cabeçalhos e fluxos contínuos bidirecionais.*
  >
  > *A comunicação é estritamente regida por **Contratos Fortes (IDL - Interface Definition Language)** usando **Protocol Buffers**, como vemos aqui no arquivo `sensor.proto`. O compilador `protoc` gera stubs nativos para diferentes linguagens, garantindo **Interoperabilidade Heterogênea**: neste projeto, o nosso **Servidor foi construído em Go** e o nosso **Cliente em Python**."*

---

### 1:15 - 2:30 | Chamada Unária (Síncrona)
* **O que Mostrar na Tela:** Mude para a tela dividida com os dois terminais. No terminal direito, pressione **[Enter]** para rodar:
  ```bash
  docker exec -it grpc_client python client.py
  ```
* **O que Falar (Roteiro Verbal):**
  > *(Aponte para o primeiro bloco no terminal direito e a resposta no terminal esquerdo):*  
  > *"Vamos à execução prática conteinerizada. Observem o primeiro paradigma de comunicação: a **Chamada Unária (Síncrona)** `EnviarLeitura`.*
  >
  > *O cliente Python empacotou a leitura de temperatura de 25.4°C em formato binário Protobuf, disparou a chamada remota e ficou **bloqueado**, aguardando o processamento do servidor Go pela rede.*
  >
  > *No terminal esquerdo, vemos que o servidor Go recebeu o payload binário, desserializou os tipos estáticos instantaneamente e retornou a confirmação ao cliente. Isso ilustra o princípio clássico de RPC: para o programador cliente, executar um procedimento remoto em outro processo e outra linguagem é transparente, parecendo uma função local."*

---

### 2:30 - 4:00 | Chamada por Streaming (Fluxo Contínuo Assíncrono)
* **O que Mostrar na Tela:** Aponte para as linhas de temperatura chegando uma a uma no terminal do cliente enquanto o servidor transmite.
* **O que Falar (Roteiro Verbal):**
  > *(Aponte para o segundo bloco `Testando Chamada de Streaming`):*  
  > *"O segundo paradigma implementado é a **Comunicação por Streaming do Servidor (Fluxo Contínuo)** com o método `ObterHistorico`.*
  >
  > *Diferente do modelo requisição-resposta onde o cliente precisa esperar um lote gigantesco ser montado e trafegado de uma só vez, o servidor Go estabelece um stream contínuo sobre HTTP/2 e emite cada medição assim que ela é gerada.*
  >
  > *O cliente Python consome e processa cada pacote sob demanda, sem reter todo o volume na memória. Esse paradigma é essencial em Sistemas Distribuídos para telemetria em tempo real, monitoramento de sensores e cenários com restrição de memória (Edge Computing)."*

---

### 4:00 - 4:45 | Conclusão e Domínio Teórico
* **O que Mostrar na Tela:** Exiba os dois terminais com as execuções finalizadas com sucesso.
* **O que Falar (Roteiro Verbal):**
  > *"Em conclusão, o gRPC provou ser um protocolo de alta eficiência: elimina overhead de parsing textual através do Protobuf, reduz latência de rede com a multiplexação do HTTP/2 e resolve com facilidade a barreira de tipos entre linguagens heterogêneas (Python e Go), cumprindo com excelência todos os requisitos de arquiteturas distribuídas modernas."*

---
---

# 📹 VÍDEO 2: APRESENTAÇÃO RABBITMQ (Tempo Total: ~4min 45s)

## 🖥️ Preparação de Tela (Antes de Começar a Gravar)
1. **Infraestrutura Pré-iniciada:** Certifique-se de que os containers estão rodando:
   ```bash
   docker compose up -d rabbitmq rabbitmq_consumer rabbitmq_producer
   ```
2. **Terminal 1 (Lado Esquerdo):** Monitorando o Consumidor Go:
   ```bash
   docker logs -f rabbitmq_consumer
   ```
3. **Terminal 2 (Lado Direito):** Pronto para disparar o Produtor Python:
   ```bash
   docker exec -it rabbitmq_producer python producer.py
   ```
4. **Navegador (Aba de fundo):** Aberto no painel web `http://localhost:15672` (Usuário: `admin` | Senha: `admin123`).

---

## ⏱️ Cronômetro e Roteiro de Fala Passo a Passo (RabbitMQ)

### 0:00 - 0:50 | Introdução Teórica, AMQP e Desacoplamentos
* **O que Mostrar na Tela:** Mostre o painel web em `http://localhost:15672` e depois foque na tela dividida dos terminais.
* **O que Falar (Roteiro Verbal):**
  > *"Olá! Neste vídeo apresento a implementação prática do **RabbitMQ**, utilizando o protocolo **AMQP 0-9-1** (Advanced Message Queuing Protocol).*
  >
  > *Ao contrário do gRPC, que é síncrono e baseado em chamada direta ponto-a-ponto, o RabbitMQ opera no paradigma de **Comunicação Indireta e Assíncrona mediada por Broker**. Ele assegura os três desacoplamentos fundamentais de Sistemas Distribuídos:*
  > 1. * **Desacoplamento Espacial:** Produtor e consumidor não sabem o IP nem a porta um do outro; comunicam-se apenas através do Broker.*
  > 2. * **Desacoplamento Temporal:** O produtor pode publicar mensagens mesmo que os consumidores estejam offline; os dados ficam retidos na fila.*
  > 3. * **Desacoplamento de Sincronização:** O envio da mensagem é não-bloqueante.*
  >
  > *Demonstraremos também a **Interoperabilidade**: nosso Produtor é em **Python** e nosso Consumidor em **Go**."*

---

### 0:50 - 2:05 | Tipos de Roteamento (Fanout, Direct, Topic)
* **O que Mostrar na Tela:** No terminal direito, dê **[Enter]** em `docker exec -it rabbitmq_producer python producer.py`. Aponte para as saídas do **Bloco 1 (Exchanges)**.
* **O que Falar (Roteiro Verbal):**
  > *(Aponte para o Bloco 1 na tela):*  
  > *"Primeiro requisito: **Tipos de Roteamento (Exchanges)**.*
  >
  > *1. **Fanout Exchange (Troca de Emissão):** Roteia mensagens para todas as filas vinculadas e **ignora completamente a chave de roteamento**. Enviamos uma chave arbitrária qualquer e as 3 filas (Email, SMS e Auditoria) receberam cópias idênticas por broadcast.*
  >
  > *2. **Direct Exchange (Troca Direta):** Roteia com base em correspondência exata de chave. A chave `info` foi entregue apenas para a fila Logs Gerais. E como diz a teoria: **se várias filas se associarem à mesma chave, funciona como fanout**. Enviamos a chave `erro` e tanto a fila Alertas quanto Logs Gerais receberam a mensagem!*
  >
  > *3. **Topic Exchange (Troca de Tópico):** Roteia por padrões com curingas (`*` para uma palavra e `#` para zero ou mais palavras). Enviamos `iot.sp.temperatura` e ela casou simultaneamente com os 3 padrões (`iot.*.temperatura`, `iot.sp.#` e `iot.#`), funcionando como fanout para as 3 filas. Já `iot.rj.pressao` casou apenas com o padrão global `iot.#`."*

---

### 2:05 - 3:00 | Balanceamento de Carga (Round-Robin Simples e Ponderado)
* **O que Mostrar na Tela:** Aponte para as saídas do **Bloco 2 (Balanceamento de Carga)**.
* **O que Falar (Roteiro Verbal):**
  > *(Aponte para o Bloco 2 na tela):*  
  > *"Segundo requisito: **Balanceamento de Carga em Filas de Trabalho**.*
  >
  > *No **Round-Robin Simples**, o broker distribui as mensagens de forma circular e alternada entre os workers: Worker-A processou 3 tarefas (50%) e Worker-B processou 3 tarefas (50%).*
  >
  > *No **Round-Robin Ponderado**, lidamos com nós computacionais heterogêneos usando `basic_qos(prefetch_count=N)`. Configuramos o Worker-Lento com peso 1 (`prefetch=1`) e o Worker-Rápido com peso 3 (`prefetch=3`). O resultado comprova: o nó de maior capacidade absorveu proporcionalmente 3 vezes mais tarefas (6 contra 2), equilibrando a vazão sem sobrecarregar o nó menor."*

---

### 3:00 - 3:55 | Persistência e Confirmações (ACK)
* **O que Mostrar na Tela:** Aponte para as saídas do **Bloco 3 (Persistência e ACK)**.
* **O que Falar (Roteiro Verbal):**
  > *(Aponte para o Bloco 3 na tela):*  
  > *"Terceiro requisito: **Persistência e Confirmações (ACK)**.*
  >
  > *Na **Persistência**, mostramos a mensagem volátil com `delivery_mode=1` (fica em RAM e é perdida se o broker reiniciar) versus a persistente com `delivery_mode=2` e fila `durable=True`, gravada em disco.*
  >
  > *Nas **Confirmações de Recebimento**, demonstramos com `auto_ack=True` (fire-and-forget): o consumidor recebeu o pagamento, simulou uma falha e a mensagem sumiu do broker, gerando **perda definitiva de dados**.*
  >
  > *Já com **confirmação manual (`auto_ack=False`)**, o Worker-1 falhou e enviou `basic_nack(requeue=True)`. O RabbitMQ detectou a falha, devolveu a mensagem para a fila e o Worker-2 recuperou o contrato com segurança enviando o `basic_ack()`, garantindo entrega confiável at-least-once."*

---

### 3:55 - 4:35 | Prioridade nas Filas e Interoperabilidade Polyglot
* **O que Mostrar na Tela:** Aponte para o **Bloco 4 (Prioridade)** e em seguida olhe para o **Terminal Esquerdo (Go)** no **Bloco 5**.
* **O que Falar (Roteiro Verbal):**
  > *(Aponte para o Bloco 4 na tela e depois para o terminal do Go no Bloco 5):*  
  > *"Quarto requisito: **Filas com Prioridade**.*
  > *A fila foi declarada com `x-max-priority: 10`. Enviamos tarefas rotineiras primeiro e a mensagem de ALERTA CRÍTICO (Prioridade 10) por último. Ao consumir, a mensagem de prioridade 10 furou a fila FIFO e foi entregue em 1º lugar!*
  >
  > *Quinto requisito: **Interoperabilidade Polyglot**.*
  > *O produtor em Python publicou uma telemetria industrial estruturada em JSON. Observem agora no terminal esquerdo: o **Consumidor em Go** conectado no broker recebeu e desserializou os dados em tempo real sobre frames binários AMQP."*

---

### 4:35 - 5:00 | Conclusão Teórica e Comparativo com Kafka
* **O que Mostrar na Tela:** Mostre o navegador com o painel do RabbitMQ com as filas zeradas e mensagens processadas.
* **O que Falar (Roteiro Verbal):**
  > *"Para concluir: diferentemente do Apache Kafka (que funciona como um log de eventos distribuído e imutável particionado em disco, onde o próprio consumidor gerencia seu ponteiro de offset para alto throughput), o RabbitMQ é um Message Broker tradicional focado em roteamento flexível por exchanges, filas inteligentes dinâmicas e confirmações individuais de tarefas. Cumprimos todos os requisitos teóricos e práticos."*

---

## 📌 Checklist Rápido de Comandos para o Dia da Gravação

### Para o Vídeo de gRPC:
```bash
# Subir ambiente:
docker compose up -d grpc_server grpc_client

# Terminal 1 (Servidor Go):
docker logs -f grpc_server

# Terminal 2 (Cliente Python):
docker exec -it grpc_client python client.py
```

### Para o Vídeo de RabbitMQ:
```bash
# Subir ambiente:
docker compose up -d rabbitmq rabbitmq_consumer rabbitmq_producer

# Terminal 1 (Consumidor Go):
docker logs -f rabbitmq_consumer

# Terminal 2 (Produtor Python com todas as demonstrações):
docker exec -it rabbitmq_producer python producer.py

# Painel Web no Navegador:
http://localhost:15672 (admin / admin123)
```
