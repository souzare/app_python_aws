from flask import Flask, Response, jsonify
from prometheus_client import Counter, generate_latest
import random
import os
import time

app = Flask(__name__)

# Configuração controlável (para simular o bug)
# Altere para 'True' durante a demonstração para queimar o Error Budget
SHOULD_FAIL = os.environ.get('SHOULD_FAIL', 'False') == 'True' 

# -----------------
# 1. Definindo o SLI (Indicators)
# -----------------
REQUESTS_TOTAL = Counter('http_requests_total', 'Total de requisições', ['method', 'endpoint', 'status'])
ERRORS_TOTAL = Counter('http_errors_total', 'Total de requisições com erro (5xx)', ['method', 'endpoint'])

@app.route('/')
def home():
    endpoint = '/'
    try:
        if SHOULD_FAIL:
            # Simulando uma falha que ocorre 1 em cada 10 requisições (10% de taxa de erro)
            if random.random() < 0.10: 
                raise Exception("Falha de Processamento Intencional!")
        
        # Simula o tempo de processamento normal
        time.sleep(0.05) 
        
        status_code = '200'
        response = jsonify({"status": "OK", "message": "Serviço disponível"})
        return response, 200
        
    except Exception:
        # 2. Incrementando o contador de Erro (o 'bad event' do SLI)
        ERRORS_TOTAL.labels(method='GET', endpoint=endpoint).inc()
        
        status_code = '500'
        return jsonify({"status": "ERROR", "message": "Falha de serviço"}), 500
        
    finally:
        # 3. Incrementando o contador total
        REQUESTS_TOTAL.labels(method='GET', endpoint=endpoint, status=status_code).inc()

@app.route('/metrics')
def metrics():
    # Rota que o Prometheus vai "raspar" (scrape)
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)