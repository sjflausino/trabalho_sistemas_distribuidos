package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

type Leitura struct {
	SensorID    string  `json:"sensor_id"`
	Temperatura float64 `json:"temperatura"`
}

type Resposta struct {
	Sucesso  bool   `json:"sucesso"`
	Mensagem string `json:"mensagem"`
}

var servidor = os.Getenv("SERVER_ID")

func responderJSON(w http.ResponseWriter, status int, corpo any) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Servido-Por", servidor)
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(corpo)
}

func enviarLeitura(w http.ResponseWriter, r *http.Request) {
	var leitura Leitura
	if err := json.NewDecoder(r.Body).Decode(&leitura); err != nil {
		responderJSON(w, http.StatusBadRequest, Resposta{false, "JSON inválido"})
		return
	}
	fmt.Printf("[%s] POST Recebido do Sensor: %s | Temperatura: %.2f\n", servidor, leitura.SensorID, leitura.Temperatura)
	responderJSON(w, http.StatusCreated, Resposta{true, "Leitura registrada com sucesso pelo Servidor Go (" + servidor + ")!"})
}

func obterHistorico(w http.ResponseWriter, r *http.Request) {
	sensorID := r.PathValue("id")
	fmt.Printf("[%s] GET Histórico do sensor: %s\n", servidor, sensorID)

	historico := []Leitura{}
	for _, temp := range []float64{22.5, 23.0, 23.5, 24.1, 22.8} {
		historico = append(historico, Leitura{SensorID: sensorID, Temperatura: temp})
	}
	responderJSON(w, http.StatusOK, historico)
}

func main() {
	http.HandleFunc("POST /leituras", enviarLeitura)
	http.HandleFunc("GET /sensores/{id}/historico", obterHistorico)

	fmt.Printf("=== Servidor REST (Go) %s rodando na porta 8080 ===\n", servidor)
	log.Fatal(http.ListenAndServe(":8080", nil))
}