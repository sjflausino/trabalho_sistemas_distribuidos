package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"sync"
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

var (
	logMutex   sync.Mutex
	msgCounter int
)

func getEnv(key, fallback string) string {
	if val, ok := os.LookupEnv(key); ok {
		return val
	}
	return fallback
}

func formatDeliveryMode(mode uint8) string {
	switch mode {
	case 2:
		return "2 (Persistente - Gravado em Disco)"
	case 1:
		return "1 (Transiente - Memória RAM)"
	default:
		return fmt.Sprintf("%d (Padrão)", mode)
	}
}

func logRoutingMessage(categoria, exchange, routingKey, queueName, regra string, msg amqp.Delivery) {
	logMutex.Lock()
	defer logMutex.Unlock()

	msgCounter++
	now := time.Now().Format("2006-01-02 15:04:05")

	fmt.Println()
	fmt.Println("================================================================================")
	fmt.Printf(" [Go Consumer] %s | Msg #%d | %s\n", categoria, msgCounter, now)
	fmt.Println("================================================================================")
	fmt.Printf(" • Exchange          : %s\n", exchange)
	fmt.Printf(" • Routing Key Usada : %s\n", routingKey)
	fmt.Printf(" • Fila do Go        : %s\n", queueName)
	fmt.Printf(" • Conteúdo Recebido : %q\n", string(msg.Body))
	fmt.Printf(" • Regra AMQP        : %s\n", regra)
	fmt.Println("--------------------------------------------------------------------------------")
	fmt.Printf(" [STATUS] Processado e confirmado com sucesso (ACK)! Total acumulado: %d msg(s)\n", msgCounter)
	fmt.Println("================================================================================")
}

func logTelemetryMessage(msg amqp.Delivery) {
	logMutex.Lock()
	defer logMutex.Unlock()

	msgCounter++
	now := time.Now().Format("2006-01-02 15:04:05")

	exchangeName := msg.Exchange
	if exchangeName == "" {
		exchangeName = "(Default / Nameless Exchange)"
	}

	contentType := msg.ContentType
	if contentType == "" {
		contentType = "application/json"
	}

	fmt.Println()
	fmt.Println("================================================================================")
	fmt.Printf(" [Go Consumer] 🚀 [5. INTEROPERABILIDADE POLYGLOT] | Msg #%d | %s\n", msgCounter, now)
	fmt.Println("================================================================================")
	fmt.Println(" [METADADOS AMQP]")
	fmt.Printf("   • Fila / Routing Key : %s\n", msg.RoutingKey)
	fmt.Printf("   • Exchange           : %s\n", exchangeName)
	fmt.Printf("   • Content-Type       : %s\n", contentType)
	fmt.Printf("   • Modo de Entrega    : %s\n", formatDeliveryMode(msg.DeliveryMode))
	fmt.Printf("   • Delivery Tag       : %d\n", msg.DeliveryTag)
	fmt.Printf("   • Redelivered        : %t\n", msg.Redelivered)
	fmt.Printf("   • Tamanho do Payload : %d bytes\n", len(msg.Body))
	fmt.Println("--------------------------------------------------------------------------------")

	var t MensagemTelemetria
	if err := json.Unmarshal(msg.Body, &t); err == nil && (t.ID != "" || t.Evento != "") {
		fmt.Println(" [DADOS DO NEGÓCIO - JSON DECODIFICADO]")
		fmt.Printf("   • ID da Transação    : %s\n", t.ID)
		fmt.Printf("   • Origem da Mensagem : %s\n", t.Origem)
		fmt.Printf("   • Tipo de Evento     : %s\n", t.Evento)
		fmt.Printf("   • Timestamp Emissão  : %s\n", t.Timestamp)
		fmt.Printf("   • Valor Financeiro   : R$ %.2f\n", t.Valor)

		if t.Timestamp != "" {
			if tEmit, err := time.Parse("2006-01-02 15:04:05", t.Timestamp); err == nil {
				dur := time.Since(tEmit).Round(time.Millisecond)
				fmt.Printf("   • Latência Trânsito  : ~%v\n", dur)
			}
		}

		fmt.Println("--------------------------------------------------------------------------------")
		fmt.Println(" [PAYLOAD JSON FORMATADO]")
		var prettyJSON bytes.Buffer
		if err := json.Indent(&prettyJSON, msg.Body, "   ", "  "); err == nil {
			fmt.Printf("   %s\n", prettyJSON.String())
		} else {
			fmt.Printf("   %s\n", string(msg.Body))
		}
	} else {
		fmt.Println(" [PAYLOAD BRUTO]")
		var prettyJSON bytes.Buffer
		if err := json.Indent(&prettyJSON, msg.Body, "   ", "  "); err == nil {
			fmt.Printf("   %s\n", prettyJSON.String())
		} else {
			fmt.Printf("   %s\n", string(msg.Body))
		}
	}

	fmt.Println("--------------------------------------------------------------------------------")
	fmt.Printf(" [STATUS] Processado e confirmado com sucesso (ACK)! Total acumulado: %d msg(s)\n", msgCounter)
	fmt.Println("================================================================================")
}

func startConsumer(conn *amqp.Connection, queueName, consumerTag string, handler func(msg amqp.Delivery)) {
	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("Erro ao abrir canal para %s: %v", queueName, err)
	}

	msgs, err := ch.Consume(
		queueName,
		consumerTag,
		false, // manual ACK
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("Erro ao registrar consumo na fila %s: %v", queueName, err)
	}

	go func() {
		for msg := range msgs {
			handler(msg)
			_ = msg.Ack(false)
		}
	}()
}

func main() {
	host := getEnv("RABBITMQ_HOST", "rabbitmq")
	port := getEnv("RABBITMQ_PORT", "5672")
	user := getEnv("RABBITMQ_USER", "admin")
	pass := getEnv("RABBITMQ_PASS", "admin123")

	url := fmt.Sprintf("amqp://%s:%s@%s:%s/", user, pass, host, port)

	fmt.Println("================================================================================")
	fmt.Println("              🐰 CONSUMIDOR RABBITMQ (GO - AMQP 0-9-1) 🐰                       ")
	fmt.Println("================================================================================")
	fmt.Printf("Aguardando conexao com o broker RabbitMQ em %s:%s...\n", host, port)

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

	setupCh, err := conn.Channel()
	if err != nil {
		log.Fatalf("Erro ao abrir canal de configuracao: %v", err)
	}
	defer setupCh.Close()

	// -------------------------------------------------------------------------
	// 1. Declarar Exchanges de Demonstração
	// -------------------------------------------------------------------------
	if err := setupCh.ExchangeDeclare("ex_fanout_emissao", "fanout", false, false, false, false, nil); err != nil {
		log.Fatalf("Erro ao declarar exchange fanout: %v", err)
	}
	if err := setupCh.ExchangeDeclare("ex_direct_direta", "direct", false, false, false, false, nil); err != nil {
		log.Fatalf("Erro ao declarar exchange direct: %v", err)
	}
	if err := setupCh.ExchangeDeclare("ex_topic_topico", "topic", false, false, false, false, nil); err != nil {
		log.Fatalf("Erro ao declarar exchange topic: %v", err)
	}

	// -------------------------------------------------------------------------
	// 2. Filas de Roteamento Fanout
	// -------------------------------------------------------------------------
	qFanoutGo, err := setupCh.QueueDeclare("q_go_fanout_emissao", false, false, false, false, nil)
	if err != nil {
		log.Fatalf("Erro ao declarar fila fanout: %v", err)
	}
	if err := setupCh.QueueBind(qFanoutGo.Name, "", "ex_fanout_emissao", false, nil); err != nil {
		log.Fatalf("Erro ao vincular fila fanout: %v", err)
	}

	// -------------------------------------------------------------------------
	// 3. Filas de Roteamento Direct
	// -------------------------------------------------------------------------
	qDirectLogs, err := setupCh.QueueDeclare("q_go_direct_logs", false, false, false, false, nil)
	if err != nil {
		log.Fatalf("Erro ao declarar fila direct logs: %v", err)
	}
	_ = setupCh.QueueBind(qDirectLogs.Name, "info", "ex_direct_direta", false, nil)
	_ = setupCh.QueueBind(qDirectLogs.Name, "erro", "ex_direct_direta", false, nil)

	qDirectAlertas, err := setupCh.QueueDeclare("q_go_direct_alertas", false, false, false, false, nil)
	if err != nil {
		log.Fatalf("Erro ao declarar fila direct alertas: %v", err)
	}
	_ = setupCh.QueueBind(qDirectAlertas.Name, "erro", "ex_direct_direta", false, nil)

	// -------------------------------------------------------------------------
	// 4. Filas de Roteamento Topic
	// -------------------------------------------------------------------------
	qTopicTemp, err := setupCh.QueueDeclare("q_go_topic_temperaturas", false, false, false, false, nil)
	if err != nil {
		log.Fatalf("Erro ao declarar fila topic temp: %v", err)
	}
	_ = setupCh.QueueBind(qTopicTemp.Name, "iot.*.temperatura", "ex_topic_topico", false, nil)

	qTopicSp, err := setupCh.QueueDeclare("q_go_topic_tudo_sp", false, false, false, false, nil)
	if err != nil {
		log.Fatalf("Erro ao declarar fila topic sp: %v", err)
	}
	_ = setupCh.QueueBind(qTopicSp.Name, "iot.sp.#", "ex_topic_topico", false, nil)

	qTopicGlobal, err := setupCh.QueueDeclare("q_go_topic_global_tudo", false, false, false, false, nil)
	if err != nil {
		log.Fatalf("Erro ao declarar fila topic global: %v", err)
	}
	_ = setupCh.QueueBind(qTopicGlobal.Name, "iot.#", "ex_topic_topico", false, nil)

	// -------------------------------------------------------------------------
	// 5. Fila de Interoperabilidade Polyglot (JSON)
	// -------------------------------------------------------------------------
	qPolyglot, err := setupCh.QueueDeclare("fila_interoperabilidade_polyglot", true, false, false, false, nil)
	if err != nil {
		log.Fatalf("Erro ao declarar fila polyglot: %v", err)
	}

	// -------------------------------------------------------------------------
	// 6. Iniciar Consumidores Assíncronos
	// -------------------------------------------------------------------------
	startConsumer(conn, qFanoutGo.Name, "go_worker_fanout", func(msg amqp.Delivery) {
		logRoutingMessage(
			"📢 [1.1 ROTEAMENTO FANOUT - Troca de Emissão]",
			"ex_fanout_emissao",
			msg.RoutingKey,
			qFanoutGo.Name,
			"A chave de roteamento foi TOTALMENTE IGNORADA! A mensagem foi entregue em broadcast a todas as filas vinculadas.",
			msg,
		)
	})

	startConsumer(conn, qDirectLogs.Name, "go_worker_direct_logs", func(msg amqp.Delivery) {
		regra := fmt.Sprintf("Correspondência EXATA da chave '%s' com a fila de logs gerais.", msg.RoutingKey)
		if msg.RoutingKey == "erro" {
			regra = "A chave 'erro' casou tanto com logs quanto com alertas (comportamento de FANOUT para a mesma chave)!"
		}
		logRoutingMessage(
			"🎯 [1.2 ROTEAMENTO DIRECT - Troca Direta]",
			"ex_direct_direta",
			msg.RoutingKey,
			qDirectLogs.Name,
			regra,
			msg,
		)
	})

	startConsumer(conn, qDirectAlertas.Name, "go_worker_direct_alertas", func(msg amqp.Delivery) {
		logRoutingMessage(
			"🎯 [1.2 ROTEAMENTO DIRECT - Troca Direta / Alertas Críticos]",
			"ex_direct_direta",
			msg.RoutingKey,
			qDirectAlertas.Name,
			"Correspondência EXATA da chave 'erro' na fila exclusiva de alertas!",
			msg,
		)
	})

	startConsumer(conn, qTopicTemp.Name, "go_worker_topic_temp", func(msg amqp.Delivery) {
		logRoutingMessage(
			"🌐 [1.3 ROTEAMENTO TOPIC - Padrão 'iot.*.temperatura']",
			"ex_topic_topico",
			msg.RoutingKey,
			qTopicTemp.Name,
			"Casamento com curinga '*' (substitui exatamente 1 palavra central, ex: 'sp').",
			msg,
		)
	})

	startConsumer(conn, qTopicSp.Name, "go_worker_topic_sp", func(msg amqp.Delivery) {
		logRoutingMessage(
			"🌐 [1.3 ROTEAMENTO TOPIC - Padrão 'iot.sp.#']",
			"ex_topic_topico",
			msg.RoutingKey,
			qTopicSp.Name,
			"Casamento com curinga '#' (substitui zero ou mais palavras com prefixo 'iot.sp').",
			msg,
		)
	})

	startConsumer(conn, qTopicGlobal.Name, "go_worker_topic_global", func(msg amqp.Delivery) {
		regra := "Casamento com curinga '#' no padrão global 'iot.#' (captura qualquer mensagem sob o domínio iot)."
		if msg.RoutingKey == "iot.rj.pressao" {
			regra = "A chave 'iot.rj.pressao' NÃO casou com temperatura nem com sp, casando APENAS com o curinga '#' global!"
		}
		logRoutingMessage(
			"🌐 [1.3 ROTEAMENTO TOPIC - Padrão Global 'iot.#']",
			"ex_topic_topico",
			msg.RoutingKey,
			qTopicGlobal.Name,
			regra,
			msg,
		)
	})

	startConsumer(conn, qPolyglot.Name, "go_worker_polyglot", func(msg amqp.Delivery) {
		logTelemetryMessage(msg)
	})

	fmt.Println("--------------------------------------------------------------------------------")
	fmt.Printf(" • Broker Conectado : %s:%s\n", host, port)
	fmt.Printf(" • Usuário AMQP     : %s\n", user)
	fmt.Println(" • Filas e Trocas Monitoradas pelo Consumidor Go:")
	fmt.Println("   [1] FANOUT : 'q_go_fanout_emissao'     <- ex_fanout_emissao (Broadcast)")
	fmt.Println("   [2] DIRECT : 'q_go_direct_logs'        <- ex_direct_direta  (chaves: 'info', 'erro')")
	fmt.Println("   [3] DIRECT : 'q_go_direct_alertas'     <- ex_direct_direta  (chave: 'erro')")
	fmt.Println("   [4] TOPIC  : 'q_go_topic_temperaturas' <- ex_topic_topico   (padrão: 'iot.*.temperatura')")
	fmt.Println("   [5] TOPIC  : 'q_go_topic_tudo_sp'      <- ex_topic_topico   (padrão: 'iot.sp.#')")
	fmt.Println("   [6] TOPIC  : 'q_go_topic_global_tudo'  <- ex_topic_topico   (padrão: 'iot.#')")
	fmt.Println("   [7] POLY   : 'fila_interoperabilidade_polyglot' (JSON estruturado Python -> Go)")
	fmt.Println("--------------------------------------------------------------------------------")
	fmt.Println(" • Status           : PRONTO - Aguardando demonstrações do Produtor Python...")
	fmt.Println("================================================================================")

	// Mantém o processo do consumidor ativo
	select {}
}
