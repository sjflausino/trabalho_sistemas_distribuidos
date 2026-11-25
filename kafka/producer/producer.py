import json
import time

from confluent_kafka import Producer

BROKERS = "kafka1:9092,kafka2:9092,kafka3:9092"
TOPICO = "leituras"

LEITURAS = [
    ("Sensor-Sala", 22.5), ("Sensor-Quarto", 20.1), ("Sensor-Garagem", 18.4),
    ("Sensor-Sala", 23.0), ("Sensor-Quarto", 20.6), ("Sensor-Garagem", 18.9),
    ("Sensor-Sala", 23.5), ("Sensor-Quarto", 21.2), ("Sensor-Garagem", 19.3),
]


def confirmacao(erro, msg):
    if erro:
        print(f"Erro ao enviar: {erro}")
    else:
        print(f"Gravado -> {msg.key().decode()} | partição {msg.partition()} | offset {msg.offset()}")


def run():
    produtor = Producer({"bootstrap.servers": BROKERS})

    print(f"=== Enviando {len(LEITURAS)} leituras para o tópico '{TOPICO}' ===")
    for sensor_id, temperatura in LEITURAS:
        valor = json.dumps({"sensor_id": sensor_id, "temperatura": temperatura})
        produtor.produce(TOPICO, key=sensor_id, value=valor, callback=confirmacao)
        produtor.poll(0)
        time.sleep(0.5)

    produtor.flush()


if __name__ == '__main__':
    run()