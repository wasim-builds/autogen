"""Tests for telemetry module."""

from autogen_core._telemetry._genai import (
    GEN_AI_AGENT_ACTION_REF,
    trace_tool_span,
)


def test_trace_tool_span_with_action_ref() -> None:
    """Test that action_ref is set on the span when provided."""
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    # Set up in-memory span exporter
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")

    with trace_tool_span("test_tool", tracer=tracer, action_ref="abc123"):
        pass

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes.get(GEN_AI_AGENT_ACTION_REF) == "abc123"


def test_trace_tool_span_without_action_ref() -> None:
    """Test that action_ref is not set on the span when not provided."""
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    # Set up in-memory span exporter
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")

    with trace_tool_span("test_tool", tracer=tracer):
        pass

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert GEN_AI_AGENT_ACTION_REF not in (spans[0].attributes or {})
