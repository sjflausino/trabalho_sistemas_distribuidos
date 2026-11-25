import requests

URL = "http://rest_nginx:8080"


def run():
    print("=== POST /leituras (equivalente ao EnviarLeitura) ===")
    resposta = requests.post(f"{URL}/leituras", json={"sensor_id": "Sensor-Sala", "temperatura": 25.4})
    print(f"Status: {resposta.status_code} | Servido por: {resposta.headers['X-Servido-Por']}")
    print(f"Resposta do Servidor: {resposta.json()['mensagem']}\n")

    print("=== GET /sensores/Sensor-Sala/historico (equivalente ao ObterHistorico) ===")
    resposta = requests.get(f"{URL}/sensores/Sensor-Sala/historico")
    print(f"Status: {resposta.status_code} | Servido por: {resposta.headers['X-Servido-Por']}")
    for leitura in resposta.json():
        print(f"Recebido -> Temp: {leitura['temperatura']}°C")

    print("\n=== Distribuição: 6 requisições ao mesmo endereço ===")
    for i in range(1, 7):
        resposta = requests.get(f"{URL}/sensores/Sensor-Sala/historico")
        print(f"Requisição {i} -> servida por {resposta.headers['X-Servido-Por']}")


if __name__ == '__main__':
    run()