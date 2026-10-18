import grpc
import sensor_pb2
import sensor_pb2_grpc

def run():
    # Estabelece a conexão com o servidor Go
    with grpc.insecure_channel('grpc_server:50051') as channel: 
        stub = sensor_pb2_grpc.SensorServiceStub(channel)

        print("=== Testando Chamada Unária (Síncrona) ===")
        # Bloqueia o cliente até o servidor retornar a resposta 
        resposta = stub.EnviarLeitura(sensor_pb2.Leitura(sensor_id="Sensor-Sala", temperatura=25.4))
        print(f"Resposta do Servidor: {resposta.mensagem}\n")

        print("=== Testando Chamada de Streaming (Fluxo) ===")
        # O cliente não fica bloqueado esperando o lote todo, processa assim que chega 
        respostas_stream = stub.ObterHistorico(sensor_pb2.Filtro(sensor_id="Sensor-Sala"))
        for leitura in respostas_stream:
            print(f"Recebido via Stream -> Temp: {leitura.temperatura}°C")

if __name__ == '__main__':
    run()