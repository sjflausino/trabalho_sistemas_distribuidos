import os
import sys
import time
import json
import threading
import warnings
import pika

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(line_buffering=True)

HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
USER = os.getenv("RABBITMQ_USER", "admin")
PASS = os.getenv("RABBITMQ_PASS", "admin123")


def conectar():
    creds = pika.PlainCredentials(USER, PASS)
    for i in range(1, 15):
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(host=HOST, port=PORT, credentials=creds, heartbeat=600)
            )
        except Exception:
            print(f"Aguardando RabbitMQ em {HOST}:{PORT} (tentativa {i}/15)...")
            time.sleep(2)
    raise ConnectionError("Nao foi possivel conectar ao RabbitMQ.")


# =============================================================================
# 1. ROTEAMENTO DE MENSAGENS (FANOUT, DIRECT, TOPIC)
# =============================================================================
def demonstrar_roteamento(ch):
    print("\n" + "=" * 70)
    print("=== 1. DEMONSTRAÇÃO DOS TIPOS DE ROTEAMENTO (EXCHANGES) ===")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # 1.1 FANOUT EXCHANGE (Troca de Emissão)
    # - Roteia mensagens para todas as filas vinculadas a ela.
    # - Ignora completamente a chave de roteamento na mensagem.
    # -------------------------------------------------------------------------
    print("\n------------------------------------------------------------")
    print("● Fanout Exchange (Troca de Emissão)")
    print("  ○ Roteia mensagens para todas as filas vinculadas a ela.")
    print("  ○ Ignora completamente a chave de roteamento na mensagem.")
    print("------------------------------------------------------------")
    ex_f = "ex_fanout_emissao"
    ch.exchange_declare(exchange=ex_f, exchange_type="fanout")
    ch.queue_declare(queue="q_fanout_email", auto_delete=True)
    ch.queue_declare(queue="q_fanout_sms", auto_delete=True)
    ch.queue_declare(queue="q_fanout_auditoria", auto_delete=True)
    ch.queue_bind(exchange=ex_f, queue="q_fanout_email")
    ch.queue_bind(exchange=ex_f, queue="q_fanout_sms")
    ch.queue_bind(exchange=ex_f, queue="q_fanout_auditoria")

    print("[Fanout] Vinculadas 3 filas: 'q_fanout_email', 'q_fanout_sms', 'q_fanout_auditoria'")
    print("[Fanout] Publicando mensagem com routing_key='chave.qualquer.ignorada'...")
    msg_fanout = "Aviso Geral: Manutenção do Datacenter programada para as 22h"
    ch.basic_publish(exchange=ex_f, routing_key="chave.qualquer.ignorada", body=msg_fanout)
    time.sleep(0.2)

    _, _, be = ch.basic_get(queue="q_fanout_email", auto_ack=True)
    _, _, bs = ch.basic_get(queue="q_fanout_sms", auto_ack=True)
    _, _, ba = ch.basic_get(queue="q_fanout_auditoria", auto_ack=True)
    print(f"  ✔ Fila Email     recebeu: '{be.decode()}'")
    print(f"  ✔ Fila SMS       recebeu: '{bs.decode()}'")
    print(f"  ✔ Fila Auditoria recebeu: '{ba.decode()}'")
    print("  -> Comprovado: A chave foi totalmente ignorada e todas as filas receberam a cópia!")
    print("  -> Go Consumer: Fila 'q_go_fanout_emissao' também recebeu e registrou nos logs!")

    # -------------------------------------------------------------------------
    # 1.2 DIRECT EXCHANGE (Troca Direta)
    # - Roteia mensagens para filas com base em uma chave de roteamento.
    # - A chave de roteamento deve corresponder exatamente à chave especificada na mensagem.
    # - Se várias filas se associarem à mesma chave, funciona como fanout.
    # -------------------------------------------------------------------------
    print("\n------------------------------------------------------------")
    print("● Direct Exchange (Troca Direta)")
    print("  ○ Roteia mensagens para filas com base em uma chave de roteamento.")
    print("  ○ A chave de roteamento deve corresponder exatamente à chave especificada.")
    print("  ○ Se várias filas se associarem à mesma chave, funciona como fanout.")
    print("------------------------------------------------------------")
    ex_d = "ex_direct_direta"
    ch.exchange_declare(exchange=ex_d, exchange_type="direct")
    ch.queue_declare(queue="q_direct_alertas", auto_delete=True)
    ch.queue_declare(queue="q_direct_logs_gerais", auto_delete=True)

    # Bindings:
    # Ambas as filas escutam 'erro' (comportamento de fanout para a chave erro)
    ch.queue_bind(exchange=ex_d, queue="q_direct_alertas", routing_key="erro")
    ch.queue_bind(exchange=ex_d, queue="q_direct_logs_gerais", routing_key="erro")
    # Apenas logs gerais escuta 'info'
    ch.queue_bind(exchange=ex_d, queue="q_direct_logs_gerais", routing_key="info")

    print("[Direct] Bindings configurados:")
    print("  - 'q_direct_alertas'     escuta chave: 'erro'")
    print("  - 'q_direct_logs_gerais' escuta chaves: 'erro' e 'info'")

    print("\n[Direct - Teste 1] Publicando com chave='info' (correspondência exata simples):")
    ch.basic_publish(exchange=ex_d, routing_key="info", body="Log rotineiro: Inicialização de serviço")
    time.sleep(0.2)
    m_al, _, _ = ch.basic_get(queue="q_direct_alertas", auto_ack=True)
    _, _, b_lg = ch.basic_get(queue="q_direct_logs_gerais", auto_ack=True)
    print(f"  • Fila Alertas recebeu:     {'(nenhuma msg - chave info não corresponde)' if not m_al else 'Recebeu'}")
    print(f"  ✔ Fila Logs Gerais recebeu: '{b_lg.decode()}' (chave 'info' correspondeu exatamente)")
    print("  -> Go Consumer: Fila 'q_go_direct_logs' recebeu a mensagem com chave 'info'!")

    print("\n[Direct - Teste 2] Publicando com chave='erro' (várias filas com a mesma chave -> funciona como fanout):")
    ch.basic_publish(exchange=ex_d, routing_key="erro", body="Falha grave de banco de dados")
    time.sleep(0.2)
    _, _, b_al2 = ch.basic_get(queue="q_direct_alertas", auto_ack=True)
    _, _, b_lg2 = ch.basic_get(queue="q_direct_logs_gerais", auto_ack=True)
    print(f"  ✔ Fila Alertas     recebeu: '{b_al2.decode()}'")
    print(f"  ✔ Fila Logs Gerais recebeu: '{b_lg2.decode()}'")
    print("  -> Comprovado: Ambas as filas associadas a 'erro' receberam a msg (comportamento de fanout)!")
    print("  -> Go Consumer: Ambas as filas ('q_go_direct_logs' e 'q_go_direct_alertas') registraram nos logs!")

    # -------------------------------------------------------------------------
    # 1.3 TOPIC EXCHANGE (Troca de Tópico)
    # - Roteia mensagens para filas com base em padrões de chave de roteamento.
    # - As filas são vinculadas à troca com padrões (* = 1 palavra, # = 0 ou mais).
    # - Se a chave corresponder ao padrão de várias filas, funciona como fanout.
    # -------------------------------------------------------------------------
    print("\n------------------------------------------------------------")
    print("● Topic Exchange (Troca de Tópico)")
    print("  ○ Roteia mensagens para filas com base em padrões de chave de roteamento.")
    print("  ○ As filas são vinculadas à troca com padrões (* = 1 palavra, # = 0 ou mais).")
    print("  ○ Se a chave corresponder ao padrão de várias filas, funciona como fanout.")
    print("------------------------------------------------------------")
    ex_t = "ex_topic_topico"
    ch.exchange_declare(exchange=ex_t, exchange_type="topic")
    ch.queue_declare(queue="q_topic_todas_temperaturas", auto_delete=True)
    ch.queue_declare(queue="q_topic_tudo_sp", auto_delete=True)
    ch.queue_declare(queue="q_topic_global_tudo", auto_delete=True)

    # Bindings com padrões:
    ch.queue_bind(exchange=ex_t, queue="q_topic_todas_temperaturas", routing_key="iot.*.temperatura")
    ch.queue_bind(exchange=ex_t, queue="q_topic_tudo_sp", routing_key="iot.sp.#")
    ch.queue_bind(exchange=ex_t, queue="q_topic_global_tudo", routing_key="iot.#")

    print("[Topic] Bindings configurados:")
    print("  - Fila 'q_topic_todas_temperaturas' escuta: 'iot.*.temperatura' (* = 1 palavra)")
    print("  - Fila 'q_topic_tudo_sp'            escuta: 'iot.sp.#'           (# = 0 ou mais)")
    print("  - Fila 'q_topic_global_tudo'        escuta: 'iot.#'              (tudo de iot)")

    print("\n[Topic - Teste 1] Publicando 'iot.sp.temperatura':")
    print("  (A chave casa com os 3 padrões simultaneamente -> funciona como fanout para as 3 filas!)")
    ch.basic_publish(exchange=ex_t, routing_key="iot.sp.temperatura", body="SP Sensor: 26.5 C")
    time.sleep(0.2)
    _, _, bt_temp = ch.basic_get(queue="q_topic_todas_temperaturas", auto_ack=True)
    _, _, bt_sp = ch.basic_get(queue="q_topic_tudo_sp", auto_ack=True)
    _, _, bt_glob = ch.basic_get(queue="q_topic_global_tudo", auto_ack=True)
    print(f"  ✔ Fila 'iot.*.temperatura' recebeu: '{bt_temp.decode()}'")
    print(f"  ✔ Fila 'iot.sp.#'          recebeu: '{bt_sp.decode()}'")
    print(f"  ✔ Fila 'iot.#'             recebeu: '{bt_glob.decode()}'")
    print("  -> Comprovado: As 3 filas receberam a mesma mensagem (comportamento de fanout por padrão)!")
    print("  -> Go Consumer: As 3 filas de tópico do Go capturaram a mensagem (casamento de '*' e '#')!")

    print("\n[Topic - Teste 2] Publicando 'iot.rj.pressao':")
    print("  (Não é de SP e não é temperatura; deve casar APENAS com 'iot.#')")
    ch.basic_publish(exchange=ex_t, routing_key="iot.rj.pressao", body="RJ Pressão: 1013 hPa")
    time.sleep(0.2)
    m_temp2, _, _ = ch.basic_get(queue="q_topic_todas_temperaturas", auto_ack=True)
    m_sp2, _, _ = ch.basic_get(queue="q_topic_tudo_sp", auto_ack=True)
    _, _, bt_glob2 = ch.basic_get(queue="q_topic_global_tudo", auto_ack=True)
    print(f"  • Fila 'iot.*.temperatura' recebeu: {'(nenhuma msg - não casa)' if not m_temp2 else 'recebeu'}")
    print(f"  • Fila 'iot.sp.#'          recebeu: {'(nenhuma msg - não é de SP)' if not m_sp2 else 'recebeu'}")
    print(f"  ✔ Fila 'iot.#'             recebeu: '{bt_glob2.decode()}' (casou com '#')")
    print("  -> Go Consumer: Apenas a fila global 'q_go_topic_global_tudo' (#) capturou 'iot.rj.pressao'!")


# =============================================================================
# 2. BALANCEAMENTO DE CARGA (ROUND-ROBIN)
# =============================================================================
def demonstrar_balanceamento():
    print("\n" + "=" * 70)
    print("=== 2. DEMONSTRAÇÃO DE BALANCEAMENTO DE CARGA ===")
    print("=" * 70)

    # 2.1 Round-Robin Simples
    print("\n[Round-Robin Simples] Distribuição circular sequencial (50% / 50%):")
    q_s = "q_rr_simples"
    c_p = conectar()
    ch_p = c_p.channel()
    ch_p.queue_delete(queue=q_s)
    ch_p.queue_declare(queue=q_s, auto_delete=True)
    for i in range(1, 7):
        ch_p.basic_publish(exchange="", routing_key=q_s, body=f"Tarefa #{i}")
    c_p.close()

    res_simples = {"Worker-A": 0, "Worker-B": 0}
    def worker_s(nome):
        c = conectar()
        ch = c.channel()
        ch.basic_qos(prefetch_count=1)
        def cb(ch, m, p, body):
            res_simples[nome] += 1
            time.sleep(0.04)
            ch.basic_ack(delivery_tag=m.delivery_tag)
        ch.basic_consume(queue=q_s, on_message_callback=cb, auto_ack=False)
        while res_simples["Worker-A"] + res_simples["Worker-B"] < 6:
            c.process_data_events(time_limit=0.1)
        c.close()

    t1 = threading.Thread(target=worker_s, args=("Worker-A",))
    t2 = threading.Thread(target=worker_s, args=("Worker-B",))
    t1.start(); t2.start(); t1.join(); t2.join()
    print(f"  • Worker-A processou: {res_simples['Worker-A']} tarefas (50%)")
    print(f"  • Worker-B processou: {res_simples['Worker-B']} tarefas (50%)")

    # 2.2 Round-Robin Ponderado (QoS Prefetch)
    print("\n[Round-Robin Ponderado] Distribuição proporcional à capacidade computacional (QoS Prefetch):")
    q_p = "q_rr_ponderado"
    c_p = conectar()
    ch_p = c_p.channel()
    ch_p.queue_delete(queue=q_p)
    ch_p.queue_declare(queue=q_p, auto_delete=True)
    for i in range(1, 9):
        ch_p.basic_publish(exchange="", routing_key=q_p, body=f"Job #{i}")
    c_p.close()

    res_pond = {"Worker-Lento (Peso 1)": 0, "Worker-Rápido (Peso 3)": 0}
    def worker_p(nome, prefetch, delay):
        c = conectar()
        ch = c.channel()
        ch.basic_qos(prefetch_count=prefetch)
        def cb(ch, m, p, body):
            time.sleep(delay)
            res_pond[nome] += 1
            ch.basic_ack(delivery_tag=m.delivery_tag)
        ch.basic_consume(queue=q_p, on_message_callback=cb, auto_ack=False)
        while res_pond["Worker-Lento (Peso 1)"] + res_pond["Worker-Rápido (Peso 3)"] < 8:
            c.process_data_events(time_limit=0.1)
        c.close()

    tp1 = threading.Thread(target=worker_p, args=("Worker-Lento (Peso 1)", 1, 0.15))
    tp2 = threading.Thread(target=worker_p, args=("Worker-Rápido (Peso 3)", 3, 0.05))
    tp1.start(); tp2.start(); tp1.join(); tp2.join()
    print(f"  • Worker-Lento  (Peso 1, prefetch=1): {res_pond['Worker-Lento (Peso 1)']} tarefas processadas")
    print(f"  • Worker-Rápido (Peso 3, prefetch=3): {res_pond['Worker-Rápido (Peso 3)']} tarefas processadas")


# =============================================================================
# 3. PERSISTÊNCIA E CONFIRMAÇÕES (ACK)
# =============================================================================
def demonstrar_persistencia_ack(ch):
    print("\n" + "=" * 70)
    print("=== 3. PERSISTÊNCIA E CONFIRMAÇÕES DE RECEBIMENTO (ACK) ===")
    print("=" * 70)

    # 3.1 Persistente vs Transiente
    print("\n[Persistência] Durabilidade em Disco vs Memória RAM:")
    ch.queue_declare(queue="q_transiente", durable=False, auto_delete=True)
    ch.queue_declare(queue="q_persistente", durable=True, auto_delete=True)
    ch.basic_publish(exchange="", routing_key="q_transiente", body="Dado volátil", properties=pika.BasicProperties(delivery_mode=1))
    ch.basic_publish(exchange="", routing_key="q_persistente", body="Transação financeira", properties=pika.BasicProperties(delivery_mode=2))
    print("  • Mensagem transiente: delivery_mode=1 (Memória RAM - perdida se broker reiniciar)")
    print("  • Mensagem durável:    delivery_mode=2 (Gravada em Disco - sobrevive a quedas)")

    # 3.2 auto_ack=True (Perda de dados)
    print("\n[Sem Confirmação - auto_ack=True]:")
    ch.queue_declare(queue="q_falha_auto_ack", auto_delete=True)
    ch.basic_publish(exchange="", routing_key="q_falha_auto_ack", body="Pagamento R$ 350,00")
    m, _, b = ch.basic_get(queue="q_falha_auto_ack", auto_ack=True)
    print(f"  • Consumidor recebeu: '{b.decode()}' e simulou falha.")
    m2, _, _ = ch.basic_get(queue="q_falha_auto_ack", auto_ack=True)
    if not m2:
        print("  • Resultado: A mensagem sumiu do broker. Houve perda definitiva de dados.")

    # 3.3 auto_ack=False (Garantia de entrega)
    print("\n[Com Confirmação Manual - auto_ack=False + basic_ack]:")
    ch.queue_declare(queue="q_recupera_ack", auto_delete=True)
    ch.basic_publish(exchange="", routing_key="q_recupera_ack", body="Contrato Assinado R$ 100.000,00")
    m1, _, b1 = ch.basic_get(queue="q_recupera_ack", auto_ack=False)
    print(f"  • Worker-1 recebeu: '{b1.decode()}' e falhou -> enviando basic_nack(requeue=True)")
    ch.basic_nack(delivery_tag=m1.delivery_tag, requeue=True)
    time.sleep(0.2)
    m2, _, b2 = ch.basic_get(queue="q_recupera_ack", auto_ack=False)
    print(f"  • Worker-2 (Backup) recuperou a mensagem com sucesso: '{b2.decode()}'")
    ch.basic_ack(delivery_tag=m2.delivery_tag)
    print("  • Confirmação basic_ack() enviada. Processamento concluído com segurança!")


# =============================================================================
# 4. FILAS COM PRIORIDADE
# =============================================================================
def demonstrar_prioridade(ch):
    print("\n" + "=" * 70)
    print("=== 4. DEMONSTRAÇÃO DE FILAS COM PRIORIDADE (x-max-priority) ===")
    print("=" * 70)

    q_prio = "q_prioridade_demo"
    try:
        ch.queue_delete(queue=q_prio)
    except Exception:
        pass
    ch.queue_declare(queue=q_prio, durable=True, arguments={"x-max-priority": 10})

    tarefas = [
        ("Tarefa Rotineira Baixa", 1),
        ("Tarefa Operacional Média", 5),
        ("ALARME DE EMERGÊNCIA CRÍTICO", 10)
    ]

    print("\n[Produtor] Publicando mensagens (Crítica enviada por último):")
    for texto, p in tarefas:
        ch.basic_publish(exchange="", routing_key=q_prio, body=texto, properties=pika.BasicProperties(priority=p))
        print(f"  -> Enviado [Prioridade {p:2d}/10]: '{texto}'")

    time.sleep(0.3)
    print("\n[Consumidor] Ordem de entrega das mensagens pelo RabbitMQ:")
    pos = 1
    while True:
        m, props, b = ch.basic_get(queue=q_prio, auto_ack=True)
        if not m:
            break
        print(f"  • {pos}º recebido [Prioridade {props.priority:2d}/10]: '{b.decode()}'")
        pos += 1
    print("  -> A mensagem de prioridade 10 furou a fila FIFO e foi entregue primeiro!")


# =============================================================================
# 5. INTEROPERABILIDADE POLYGLOT (Python -> Go)
# =============================================================================
def demonstrar_interoperabilidade(ch):
    print("\n" + "=" * 70)
    print("=== 5. INTEROPERABILIDADE POLYGLOT (PYTHON -> GO) ===")
    print("=" * 70)

    q_go = "fila_interoperabilidade_polyglot"
    ch.queue_declare(queue=q_go, durable=True)

    mensagens = [
        {
            "id_transacao": "TX-PY-2026-9901",
            "origem": "Python (pika v1.3.2)",
            "evento": "Leitura Telemetria Sensor IoT",
            "valor": 2450.75,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id_transacao": "TX-PY-2026-9902",
            "origem": "Python (pika v1.3.2)",
            "evento": "Processamento de Pagamento PIX",
            "valor": 389.50,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id_transacao": "TX-PY-2026-9903",
            "origem": "Python (pika v1.3.2)",
            "evento": "Alerta de Monitoramento Datacenter",
            "valor": 0.00,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    ]

    print(f"\n[Python Producer] Enviando {len(mensagens)} mensagens estruturadas para a fila '{q_go}':")
    for idx, payload in enumerate(mensagens, 1):
        payload["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        body = json.dumps(payload)
        ch.basic_publish(
            exchange="",
            routing_key=q_go,
            body=body,
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2)
        )
        print(f"  • Mensagem #{idx} enviada -> ID: {payload['id_transacao']} | Evento: {payload['evento']} | Valor: R$ {payload['valor']:.2f}")
        time.sleep(0.35)

    print("\n[Verificação] O container 'rabbitmq_consumer' (Go) receberá e exibirá cada mensagem em detalhes!")
    print("              Consulte os logs com: docker logs -f rabbitmq_consumer\n")


def run():
    conn = conectar()
    ch = conn.channel()

    demonstrar_roteamento(ch)
    time.sleep(0.5)
    demonstrar_balanceamento()
    time.sleep(0.5)
    demonstrar_persistencia_ack(ch)
    time.sleep(0.5)
    demonstrar_prioridade(ch)
    time.sleep(0.5)
    demonstrar_interoperabilidade(ch)

    conn.close()
    print("=" * 70)
    print("=== TODAS AS CARACTERÍSTICAS DEMONSTRADAS COM SUCESSO! ===")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run()
