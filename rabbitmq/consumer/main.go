package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

type MensagemTelemetria struct {
	ID        string  `json:"id_transacao"`
	Origem    string  `json:"origem"`
	Evento    string  `json:"evento"`
	Timestamp string  `json:"timestamp"`
	Valor     float64 `json:"valor"`
}

func getEnv(key, fallback string) string {
	if val, ok := os.LookupEnv(key); ok {
		return val
	}
	return fallback
}

func main() {
	host := getEnv("RABBITMQ_HOST", "rabbitmq")
	port := getEnv("RABBITMQ_PORT", "5672")
	user := getEnv("RABBITMQ_USER", "admin")
	pass := getEnv("RABBITMQ_PASS", "admin123")

	url := fmt.Sprintf("amqp://%s:%s@%s:%s/", user, pass, host, port)

	fmt.Println("=== Consumidor RabbitMQ (Go) Inicializado ===")
	fmt.Printf("Aguardando conexao com o broker em %s:%s...\n", host, port)

	var conn *amqp.Connection
	var err error
	for i := 1; i <= 20; i++ {
		conn, err = amqp.Dial(url)
		if err == nil {
			break
		}
		time.Sleep(2 * time.Second)
	}
	if err != nil {
		log.Fatalf("Erro fatal ao conectar no RabbitMQ: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("Erro ao abrir canal: %v", err)
	}
	defer ch.Close()

	// 1. Fila de Interoperabilidade (Python -> Go)
	qPolyglot, err := ch.QueueDeclare(
		"fila_interoperabilidade_polyglot",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("Erro ao declarar fila: %v", err)
	}

	msgsPolyglot, err := ch.Consume(
		qPolyglot.Name,
		"go_consumer_worker",
		true, // auto-ack
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("Erro ao registrar consumo: %v", err)
	}

	fmt.Printf("[PRONTO] Consumidor Go ouvindo na fila '%s'!\n", qPolyglot.Name)
	fmt.Println("Aguardando mensagens enviadas pelo Produtor Python...")
	fmt.Println("-------------------------------------------------------------------")

	// Loop infinito de consumo
	for msg := range msgsPolyglot {
		var t MensagemTelemetria
		if err := json.Unmarshal(msg.Body, &t); err == nil {
			fmt.Printf("[Go Consumer - RECEBIDO] ID: %s | Origem: %s | Evento: %s | Valor: R$ %.2f\n",
				t.ID, t.Origem, t.Evento, t.Valor)
		} else {
			fmt.Printf("[Go Consumer - RECEBIDO BRUTO] %s\n", string(msg.Body))
		}
	}
}
