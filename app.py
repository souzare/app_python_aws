from flask import Flask, Response, jsonify
from prometheus_client import Counter, generate_latest
import random
import os
import time

app = Flask(__name__)

# Configuração controlável para simulação
SHOULD_FAIL = os.environ.get('SHOULD_FAIL', 'False') == 'True' 

# As métricas de contador devem ser definidas para a aplicação inteira
REQUESTS_TOTAL = Counter('http_requests_total', 'Total de requisições', ['method', 'endpoint', 'status'])

@app.route('/')
def home():
    endpoint = '/'
    status_code = '200' # Assume sucesso por padrão
    
    try:
        if SHOULD_FAIL:
            # Ação: Simulação de falha de 10%
            if random.random() < 0.10: 
                # É crucial levantar uma exceção para cair no bloco 'except'
                raise Exception("Falha de Processamento Intencional!")
        
        time.sleep(0.05) # Simula o tempo de processamento normal
        
        response = jsonify({"status": "OK", "message": "Serviço disponível"})
        status_code = '200'
        return response, 200
        
    except Exception:
        # 1. Ação: Define o código de status de erro
        status_code = '500'
        
        # 2. Ação: Retorna a resposta HTTP 500
        return jsonify({"status": "ERROR", "message": "Falha de serviço"}), 500
        
    finally:
        # 3. Ação: Incrementa a métrica total (capturando o status 200 ou 500)
        # É aqui que o label 'status' é setado para "500" e o Prometheus o encontra.
        REQUESTS_TOTAL.labels(method='GET', endpoint=endpoint, status=status_code).inc()

@app.route('/metrics')
def metrics():
    # Rota que o Prometheus vai "raspar" (scrape)
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    # Usando gunicorn para garantir que o ambiente seja o mais real possível
    # Certifique-se de que o Gunicorn está configurado corretamente no Dockerfile/docker-compose
    app.run(host='0.0.0.0', port=8080)