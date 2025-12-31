"""OpenTelemetry initialization for Betterstack OTLP integration.

This module sets up full observability (logs + traces + metrics) using native
Litestar patterns and OpenTelemetry SDK defaults. All exports are non-blocking
via batch processors and fail gracefully if Betterstack is unavailable.
"""

import logging
import sys

from opentelemetry import metrics, trace  # type: ignore[import-untyped]
from opentelemetry._logs import set_logger_provider  # type: ignore[import-untyped]
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter  # type: ignore[import-untyped]
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter  # type: ignore[import-untyped]
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore[import-untyped]
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # type: ignore[import-untyped]
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor  # type: ignore[import-untyped]
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler  # type: ignore[import-untyped]
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor  # type: ignore[import-untyped]
from opentelemetry.sdk.metrics import MeterProvider  # type: ignore[import-untyped]
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader  # type: ignore[import-untyped]
from opentelemetry.sdk.resources import Resource  # type: ignore[import-untyped]
from opentelemetry.sdk.trace import TracerProvider  # type: ignore[import-untyped]
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore[import-untyped]

from app.utils.configure import ConfigProtocol

logger = logging.getLogger(__name__)

# Global references for shutdown
_tracer_provider: TracerProvider | None = None
_meter_provider: MeterProvider | None = None
_logger_provider: LoggerProvider | None = None


def create_resource(config: ConfigProtocol) -> Resource:
    """Create OpenTelemetry Resource with service metadata.

    Resources describe the entity producing telemetry data. This metadata
    appears in Betterstack and helps identify which service generated logs/traces.

    Args:
        config: Application configuration with service name, version, environment

    Returns:
        Resource instance with service.name, service.version, and environment attributes
    """
    return Resource.create(
        {
            "service.name": config.OTEL_SERVICE_NAME,
            "service.version": config.OTEL_SERVICE_VERSION,
            "deployment.environment": config.ENV,
        }
    )


def setup_tracing(config: ConfigProtocol, resource: Resource) -> TracerProvider | None:
    """Initialize distributed tracing with Betterstack OTLP exporter.

    Creates a TracerProvider with BatchSpanProcessor for non-blocking export.
    Uses OpenTelemetry SDK defaults for batch processing (5s interval, 2048 queue size).

    Args:
        config: Application configuration with Betterstack endpoint and token
        resource: OpenTelemetry resource with service metadata

    Returns:
        TracerProvider instance, or None if initialization fails
    """
    if not config.BETTERSTACK_OTLP_INGESTING_HOST or not config.BETTERSTACK_OTLP_SOURCE_TOKEN:
        logger.warning(
            "Betterstack ingesting host or token not configured. Skipping trace export. "
            "Set BETTERSTACK_OTLP_INGESTING_HOST and BETTERSTACK_OTLP_SOURCE_TOKEN to enable."
        )
        return None

    try:
        # Create OTLP HTTP span exporter
        span_exporter = OTLPSpanExporter(
            endpoint=f"https://{config.BETTERSTACK_OTLP_INGESTING_HOST}/v1/traces",
            headers={"Authorization": f"Bearer {config.BETTERSTACK_OTLP_SOURCE_TOKEN}"},
        )

        # Create tracer provider with batch processor (uses SDK defaults)
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)

        logger.info("OpenTelemetry tracing initialized (exporting to Betterstack)")
        return tracer_provider

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry tracing: {e}", exc_info=True)
        return None


def setup_metrics(config: ConfigProtocol, resource: Resource) -> MeterProvider | None:
    """Initialize metrics collection with Betterstack OTLP exporter.

    Creates a MeterProvider with PeriodicExportingMetricReader for non-blocking export.
    Uses OpenTelemetry SDK defaults for periodic export (60s interval).

    Args:
        config: Application configuration with Betterstack endpoint and token
        resource: OpenTelemetry resource with service metadata

    Returns:
        MeterProvider instance, or None if initialization fails
    """
    if not config.BETTERSTACK_OTLP_INGESTING_HOST or not config.BETTERSTACK_OTLP_SOURCE_TOKEN:
        logger.warning(
            "Betterstack ingesting host or token not configured. Skipping metrics export. "
            "Set BETTERSTACK_OTLP_INGESTING_HOST and BETTERSTACK_OTLP_SOURCE_TOKEN to enable."
        )
        return None

    try:
        # Create OTLP HTTP metric exporter
        metric_exporter = OTLPMetricExporter(
            endpoint=f"https://{config.BETTERSTACK_OTLP_INGESTING_HOST}/v1/metrics",
            headers={"Authorization": f"Bearer {config.BETTERSTACK_OTLP_SOURCE_TOKEN}"},
        )

        # Create meter provider with periodic exporting reader (uses SDK defaults)
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[PeriodicExportingMetricReader(metric_exporter)],
        )

        # Set global meter provider
        metrics.set_meter_provider(meter_provider)

        logger.info("OpenTelemetry metrics initialized (exporting to Betterstack)")
        return meter_provider

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry metrics: {e}", exc_info=True)
        return None


def setup_logging(config: ConfigProtocol, resource: Resource) -> LoggerProvider | None:
    """Initialize logging with Betterstack OTLP exporter.

    Creates a LoggerProvider with BatchLogRecordProcessor for non-blocking export.
    Uses OpenTelemetry SDK defaults for batch processing (5s interval, 2048 queue size).

    This DOES NOT replace structlog's stdout logging - it runs in parallel.
    LoggingHandler bridges Python's standard logging to OpenTelemetry.

    Args:
        config: Application configuration with Betterstack endpoint and token
        resource: OpenTelemetry resource with service metadata

    Returns:
        LoggerProvider instance, or None if initialization fails
    """
    if not config.BETTERSTACK_OTLP_INGESTING_HOST or not config.BETTERSTACK_OTLP_SOURCE_TOKEN:
        logger.warning(
            "Betterstack ingesting host or token not configured. Skipping log export. "
            "Set BETTERSTACK_OTLP_INGESTING_HOST and BETTERSTACK_OTLP_SOURCE_TOKEN to enable."
        )
        return None

    try:
        # Create OTLP HTTP log exporter
        log_exporter = OTLPLogExporter(
            endpoint=f"https://{config.BETTERSTACK_OTLP_INGESTING_HOST}/v1/logs",
            headers={"Authorization": f"Bearer {config.BETTERSTACK_OTLP_SOURCE_TOKEN}"},
        )

        # Create logger provider with batch processor (uses SDK defaults)
        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

        # Set global logger provider
        set_logger_provider(logger_provider)

        # Attach OpenTelemetry handler to root logger
        # This bridges stdlib logging to OTLP (dual output with structlog)
        handler = LoggingHandler(logger_provider=logger_provider)

        # Apply the same HealthCheckFilter to prevent noisy health check logs
        from app.logging_config import HealthCheckFilter

        handler.addFilter(HealthCheckFilter())

        logging.getLogger().addHandler(handler)

        logger.info("OpenTelemetry logging initialized (exporting to Betterstack)")
        return logger_provider

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry logging: {e}", exc_info=True)
        return None


def setup_instrumentation() -> None:
    """Enable automatic instrumentation for SQLAlchemy and httpx.

    This instruments:
    - SQLAlchemy database queries → creates spans for each query
    - httpx HTTP client requests → creates spans for outbound API calls

    Litestar's OpenTelemetryPlugin handles HTTP request instrumentation automatically.
    """
    try:
        # Instrument SQLAlchemy for database query tracing
        SQLAlchemyInstrumentor().instrument()

        # Instrument httpx for outbound HTTP request tracing
        HTTPXClientInstrumentor().instrument()

        logger.info("Auto-instrumentation enabled (SQLAlchemy, httpx)")

    except Exception as e:
        logger.error(f"Failed to enable auto-instrumentation: {e}", exc_info=True)


def initialize_opentelemetry(config: ConfigProtocol) -> None:
    """Initialize OpenTelemetry SDK with Betterstack OTLP exporters.

    This is the main entry point called by the application factory before
    creating the Litestar app. Sets up global providers for traces, metrics,
    and logs, then enables auto-instrumentation.

    If OTEL_ENABLED=false, this function does nothing (no-op).

    Args:
        config: Application configuration with OTEL settings
    """
    global _tracer_provider, _meter_provider, _logger_provider

    if not config.OTEL_ENABLED:
        logger.info("OpenTelemetry disabled (OTEL_ENABLED=false)")
        return

    logger.info(f"Initializing OpenTelemetry for service: {config.OTEL_SERVICE_NAME}")

    try:
        # Create resource with service metadata
        resource = create_resource(config)

        # Set up tracing, metrics, and logging
        _tracer_provider = setup_tracing(config, resource)
        _meter_provider = setup_metrics(config, resource)
        _logger_provider = setup_logging(config, resource)

        # Enable auto-instrumentation
        setup_instrumentation()

        logger.info("OpenTelemetry initialization complete")

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}", exc_info=True)
        # Don't re-raise - fail gracefully
        sys.stderr.write(f"ERROR: OpenTelemetry initialization failed: {e}\n")


def shutdown_opentelemetry() -> None:
    """Gracefully shutdown OpenTelemetry providers and flush pending telemetry.

    This ensures all buffered spans, metrics, and logs are exported before
    the application exits. Called automatically via Litestar's on_shutdown hook.
    """
    global _tracer_provider, _meter_provider, _logger_provider

    logger.info("Shutting down OpenTelemetry...")

    try:
        # Shutdown tracer provider (flushes spans)
        if _tracer_provider:
            _tracer_provider.shutdown()
            logger.info("TracerProvider shutdown complete")

        # Shutdown meter provider (flushes metrics)
        if _meter_provider:
            _meter_provider.shutdown()
            logger.info("MeterProvider shutdown complete")

        # Shutdown logger provider (flushes logs)
        if _logger_provider:
            _logger_provider.shutdown()
            logger.info("LoggerProvider shutdown complete")

    except Exception as e:
        logger.error(f"Error during OpenTelemetry shutdown: {e}", exc_info=True)
        sys.stderr.write(f"ERROR: OpenTelemetry shutdown failed: {e}\n")
