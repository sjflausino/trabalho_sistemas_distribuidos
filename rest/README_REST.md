# REST - Telemetria de sensores IoT

API REST para o mesmo cenário do módulo gRPC: sensores enviando leituras de temperatura. O servidor foi escrito em Go e o cliente em Python.

## Sobre o REST

REST é um estilo de arquitetura que usa o HTTP como protocolo de comunicação. Os dados são tratados como recursos identificados por URIs (por exemplo, `/sensores/Sensor-Sala/historico`). Esses recursos são manipulados pelos métodos do HTTP: GET para consultar, POST para criar, PUT para atualizar e DELETE para remover. O resultado de cada operação vem no código de status da resposta (200, 201, 400, 404 etc.). Neste projeto os dados trafegam em JSON.

O servidor não guarda estado entre requisições (stateless): cada requisição traz tudo o que é preciso para ser atendida. Por isso é possível colocar várias cópias do servidor atrás de um balanceador de carga, já que qualquer uma delas pode responder a qualquer requisição.

Pelos tipos de comunicação da Aula 06, a comunicação REST é:

- transiente: se o servidor estiver fora do ar, a requisição se perde;
- síncrona: o cliente fica bloqueado até receber a resposta;
- confiável: o HTTP funciona sobre TCP;
- discreta: cada requisição e cada resposta é uma mensagem completa.

A Aula 06 também observa que, em aplicações Web, o RPC perdeu espaço para o REST. No RPC (e no gRPC), o cliente chama procedimentos remotos por meio de stubs gerados a partir de uma IDL, que no gRPC é o arquivo `.proto`. No REST não há IDL nem stubs: cliente e servidor só precisam concordar sobre as URIs e o formato JSON. Assim, qualquer linguagem que tenha uma biblioteca HTTP consegue usar a API.

Na Aula 04, o HTTP aparece entre os protocolos usados pelos gateways IoT para se comunicar com o resto da rede, o que torna o REST uma escolha comum nesse tipo de sistema.

## Arquitetura

```text
cliente Python ──> nginx :8080 ──┬──> rest_server_1 (Go)
curl / navegador ─┘              ├──> rest_server_2 (Go)
                                 └──> rest_server_3 (Go)
```

- `rest_server_1`, `rest_server_2` e `rest_server_3`: três réplicas do mesmo servidor Go. Toda resposta traz o cabeçalho `X-Servido-Por`, usado só para mostrar qual réplica atendeu.
- `rest_nginx`: balanceador de carga com round-robin (Aula 02). É o único endereço que o cliente conhece.
- `rest_client`: cliente Python que usa apenas a biblioteca `requests`.

**Interoperabilidade:** o servidor Go usa só a biblioteca padrão (`net/http`) e o cliente Python só a `requests`. Os dois se comunicam sem nenhum código gerado, e a mesma API pode ser acessada pelo `curl` ou pelo navegador.

**Distribuição:** o cliente sempre chama o mesmo endereço e o nginx reparte as requisições entre as réplicas. O cliente não sabe quantas réplicas existem nem qual delas respondeu (transparência de localização e de replicação, Aula 01). Se uma réplica parar, o nginx passa a usar as outras e o sistema continua respondendo (falha parcial, Aula 08).

## Operações

| Método | Rota | Equivalente no gRPC | Resposta |
|---|---|---|---|
| POST | `/leituras` | `EnviarLeitura` | 201 Created (400 se o JSON for inválido) |
| GET | `/sensores/{id}/historico` | `ObterHistorico` | 200 OK com a lista de leituras |

Corpo do POST:

```json
{"sensor_id": "Sensor-Sala", "temperatura": 25.4}
```

No gRPC o histórico chega em stream, uma leitura de cada vez. No REST a lista completa vem numa única resposta.

## Estrutura

```text
rest/
├── docker-compose.yml
├── nginx/
│   └── nginx.conf      # balanceador round-robin
├── server/
│   ├── main.go         # servidor REST em Go
│   ├── go.mod
│   └── Dockerfile
└── client/
    ├── client.py       # cliente em Python
    └── Dockerfile
```

## Como executar

Requisito: Docker com Docker Compose. Todos os comandos são executados dentro da pasta `rest/`, em dois terminais.

**1. Subir os containers (terminal 1)**

```bash
cd rest
docker compose up --build -d
docker ps
```

Resultado esperado: cinco containers com status `Up`: `rest_server_1`, `rest_server_2`, `rest_server_3`, `rest_nginx` e `rest_client`.

**2. Acompanhar os logs das réplicas (terminal 2)**

```bash
docker compose logs -f rest_server_1 rest_server_2 rest_server_3
```

Cada requisição aparece no log da réplica que a atendeu.

**3. Executar o cliente Python (terminal 1)**

```bash
docker exec -it rest_client python client.py
```

Resultado esperado:

- o POST retorna `Status: 201`;
- o GET retorna `Status: 200` e as cinco temperaturas do histórico;
- as seis requisições finais se alternam entre `rest_server_1`, `rest_server_2` e `rest_server_3`.

**4. Acessar a API sem o cliente Python (terminal 1)**

```bash
curl -i http://localhost:8080/sensores/Sensor-Sala/historico
```

Resultado esperado: `HTTP/1.1 200 OK` e o histórico em JSON.

```bash
curl -i -X POST -H "Content-Type: application/json" -d '{"sensor_id":"Sensor-Quarto","temperatura":21.7}' http://localhost:8080/leituras
```

Resultado esperado: `HTTP/1.1 201 Created`.

O GET também pode ser aberto no navegador: `http://localhost:8080/sensores/Sensor-Sala/historico`.

**5. Simular a falha de uma réplica (terminal 1)**

Parar uma das réplicas:

```bash
docker stop rest_server_2
```

Executar o cliente de novo:

```bash
docker exec -it rest_client python client.py
```

Resultado esperado: todas as requisições continuam funcionando, atendidas só por `rest_server_1` e `rest_server_3`.

Religar a réplica:

```bash
docker start rest_server_2
```

**6. Encerrar**

```bash
docker compose down
```

Ao encerrar, o terminal 2 mostra `exited with code 2` para cada réplica. Esse é o código que um programa Go devolve quando é finalizado pelo Docker, e não indica erro.

## REST x gRPC

| | REST | gRPC |
|---|---|---|
| Modelo | recursos + métodos HTTP | chamada de procedimento remoto |
| Contrato | não obrigatório | obrigatório (`.proto`) |
| Código gerado | nenhum | stubs para cada linguagem |
| Formato | JSON (texto) | Protocol Buffers (binário) |
| Transporte | HTTP/1.1 neste projeto | HTTP/2 |
| Streaming | não | sim |
| Acesso por navegador/curl | direto | não direto |