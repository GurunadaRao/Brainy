import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import Counter, Histogram, CollectorRegistry

# 1. Initialize OpenTelemetry Tracer
resource = Resource.create(attributes={"service.name": "brainy-backend"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("brainy-tracer")

# 2. Initialize Centralized Prometheus Registry & Metrics
registry = CollectorRegistry()

REQUEST_COUNT = Counter(
    "brainy_requests_total",
    "Total HTTP requests count",
    ["method", "endpoint", "status"],
    registry=registry
)

DB_LATENCY = Histogram(
    "brainy_db_latency_seconds",
    "Database call duration in seconds",
    ["db_type", "operation"],
    registry=registry
)


def get_tracer():
    return tracer
