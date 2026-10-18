package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"time"

	pb "grpc-server/pb"
	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedSensorServiceServer
}

func (s *server) EnviarLeitura(ctx context.Context, req *pb.Leitura) (*pb.Resposta, error) {
	fmt.Printf("[UNÁRIO] Recebido do Sensor: %s | Temperatura: %.2f\n", req.GetSensorId(), req.GetTemperatura())
	return &pb.Resposta{
		Sucesso:  true,
		Mensagem: "Leitura registrada com sucesso pelo Servidor Go!",
	}, nil
}

func (s *server) ObterHistorico(req *pb.Filtro, stream pb.SensorService_ObterHistoricoServer) error {
	fmt.Printf("[STREAMING] Iniciando envio de histórico para o sensor: %s\n", req.GetSensorId())
	
	temperaturas := []float32{22.5, 23.0, 23.5, 24.1, 22.8}
	for _, temp := range temperaturas {
		leitura := &pb.Leitura{
			SensorId:    req.GetSensorId(),
			Temperatura: temp,
		}
		if err := stream.Send(leitura); err != nil {
			return err
		}
		time.Sleep(1 * time.Second)
	}
	fmt.Println("[STREAMING] Finalizado.")
	return nil
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Falha ao escutar a porta: %v", err)
	}
	
	s := grpc.NewServer()
	pb.RegisterSensorServiceServer(s, &server{})
	
	fmt.Println("=== Servidor gRPC (Go) rodando na porta 50051 ===")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("Falha ao iniciar servidor: %v", err)
	}
}