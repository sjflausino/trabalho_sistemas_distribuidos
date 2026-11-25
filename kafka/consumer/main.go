package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/segmentio/kafka-go"
)

type Leitura struct {
	SensorID    string  `json:"sensor_id"`
	Temperatura float64 `json:"temperatura"`
}

func main() {
	grupo := flag.String("grupo", "processamento", "consumer group")
	nome := flag.String("nome", "consumidor", "nome deste consumidor")
	flag.Parse()

	ctx, parar := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer parar()

	leitor := kafka.NewReader(kafka.ReaderConfig{
		Brokers: []string{"kafka1:9092", "kafka2:9092", "kafka3:9092"},
		Topic:   "leituras",
		GroupID: *grupo,
		StartOffset: kafka.FirstOffset,
	})
	defer leitor.Close()

	fmt.Printf("=== %s (grupo %s) aguardando mensagens ===\n", *nome, *grupo)
	for {
		msg, err := leitor.ReadMessage(ctx)
		if err != nil {
			fmt.Printf("=== %s encerrado ===\n", *nome)
			return
		}
		var leitura Leitura
		json.Unmarshal(msg.Value, &leitura)
		fmt.Printf("[%s] partição %d | offset %d | %s: %.1f°C\n",
			*nome, msg.Partition, msg.Offset, leitura.SensorID, leitura.Temperatura)
	}
}