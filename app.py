from flask import Flask
import time
import random

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

resource = Resource(attributes={
    "service.name": "demo-app"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
)
provider.add_span_processor(processor)

trace.set_tracer_provider(provider)

FlaskInstrumentor().instrument_app(app)

@app.route("/")
def home():
    delay = random.uniform(0.1, 1.5)
    time.sleep(delay)

    if random.random() < 0.2:
        return "Erro simulado!", 500

    return f"Resposta OK em {delay:.2f}s"

app.run(host="0.0.0.0", port=5000)