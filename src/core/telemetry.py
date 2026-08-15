"""OpenTelemetry bootstrap.

Sets up TracerProvider → OTLP exporter so every request gets a distributed trace.
Also instruments SQLAlchemy, HTTPX, Redis and Celery automatically.
"""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.core.config import Settings


def setup_telemetry(settings: Settings) -> None:
    """Initialise OTEL tracing pipeline."""
    resource = Resource.create({"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    # Auto-instrument libraries
    HTTPXClientInstrumentor().instrument()
    RedisInstrumentor().instrument()


def instrument_fastapi(app: object) -> None:
    """Instrument the FastAPI app *after* it is created."""
    FastAPIInstrumentor.instrument_app(app)  # type: ignore[arg-type]


def instrument_sqlalchemy(engine: object) -> None:
    """Instrument SQLAlchemy engine."""
    SQLAlchemyInstrumentor().instrument(engine=engine)  # type: ignore[arg-type]
