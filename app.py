from flask import Flask, jsonify, request
import time
import random

app = Flask(__name__)

# Rota principal (pode simular latência)
@app.route('/')
def home():
    # Simula latência ocasional para fins de demonstração do SLO
    latency = random.uniform(50, 500) # latência entre 50ms e 500ms
    if random.random() < 0.1: # 10% de chance de latência alta
        latency = random.uniform(1000, 3000) # latência entre 1s e 3s
    
    time.sleep(latency / 1000) # Dorme em segundos
    
    return jsonify({"message": "Hello from Flask on EC2!", "latency_ms": round(latency, 2)}), 200

# Rota de Status (para verificar a disponibilidade - SLI de Disponibilidade)
@app.route('/status')
def status():
    # 5% de chance de erro para fins de demonstração do SLO de Disponibilidade
    if random.random() < 0.05:
        # Simula um erro interno do servidor
        return jsonify({"error": "Internal Server Error"}), 500
    return jsonify({"status": "OK"}), 200

if __name__ == '__main__':
    # Roda em todas as interfaces para acesso externo (importante para EC2)
    app.run(host='0.0.0.0', port=5000)