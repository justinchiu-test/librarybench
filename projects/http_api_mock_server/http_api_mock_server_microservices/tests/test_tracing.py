"""Tests for Distributed Tracing System."""

import asyncio
import pytest
from datetime import datetime, timedelta, timezone

from pymockapi.models import TraceContext, Span
from pymockapi.tracing import TracingSystem


class TestTracingSystem:
    """Test TracingSystem functionality."""
    
    @pytest.fixture
    async def tracing(self):
        """Create a tracing system instance."""
        return TracingSystem()
    
    def test_generate_trace_id(self, tracing):
        """Test trace ID generation."""
        trace_id = tracing.generate_trace_id()
        
        assert len(trace_id) == 32
        assert all(c in '0123456789abcdef' for c in trace_id)
        
        # Generate multiple IDs and verify uniqueness
        ids = {tracing.generate_trace_id() for _ in range(100)}
        assert len(ids) == 100
    
    def test_generate_span_id(self, tracing):
        """Test span ID generation."""
        span_id = tracing.generate_span_id()
        
        assert len(span_id) == 16
        assert all(c in '0123456789abcdef' for c in span_id)
        
        # Generate multiple IDs and verify uniqueness
        ids = {tracing.generate_span_id() for _ in range(100)}
        assert len(ids) == 100
    
    async def test_create_trace_context(self, tracing):
        """Test creating trace context."""
        # Create new trace
        context = await tracing.create_trace_context()
        
        assert len(context.trace_id) == 32
        assert len(context.span_id) == 16
        assert context.parent_id is None
        assert context.trace_flags == "01"
        
        # Create with existing trace
        child_context = await tracing.create_trace_context(
            trace_id=context.trace_id,
            parent_span_id=context.span_id
        )
        
        assert child_context.trace_id == context.trace_id
        assert child_context.parent_id == context.span_id
        assert child_context.span_id != context.span_id
    
    async def test_start_span(self, tracing):
        """Test starting a span."""
        context = await tracing.create_trace_context()
        
        span = await tracing.start_span(
            "test-service",
            "GET /api/test",
            context,
            {"method": "GET", "path": "/api/test"}
        )
        
        assert span.trace_id == context.trace_id
        assert span.span_id == context.span_id
        assert span.parent_span_id == context.parent_id
        assert span.service_name == "test-service"
        assert span.operation_name == "GET /api/test"
        assert span.tags == {"method": "GET", "path": "/api/test"}
        assert isinstance(span.start_time, datetime)
        assert span.end_time is None
        
        # Verify span is active
        active_spans = await tracing.get_active_spans()
        assert len(active_spans) == 1
        assert active_spans[0].span_id == span.span_id
    
    async def test_end_span(self, tracing):
        """Test ending a span."""
        context = await tracing.create_trace_context()
        span = await tracing.start_span("test-service", "operation", context)
        
        # End span successfully
        await tracing.end_span(span.span_id, 200)
        
        # Verify span ended
        active_spans = await tracing.get_active_spans()
        assert len(active_spans) == 0
        
        # Get trace and verify span details
        trace_spans = await tracing.get_trace(context.trace_id)
        assert len(trace_spans) == 1
        assert trace_spans[0].end_time is not None
        assert trace_spans[0].status_code == 200
        assert trace_spans[0].error is None
    
    async def test_end_span_with_error(self, tracing):
        """Test ending a span with error."""
        context = await tracing.create_trace_context()
        span = await tracing.start_span("test-service", "operation", context)
        
        # End span with error
        await tracing.end_span(span.span_id, 500, "Internal server error")
        
        # Verify error recorded
        trace_spans = await tracing.get_trace(context.trace_id)
        assert trace_spans[0].status_code == 500
        assert trace_spans[0].error == "Internal server error"
    
    async def test_get_trace(self, tracing):
        """Test getting all spans for a trace."""
        trace_id = tracing.generate_trace_id()
        
        # Create multiple spans
        contexts = []
        for i in range(3):
            context = await tracing.create_trace_context(
                trace_id=trace_id,
                parent_span_id=contexts[-1].span_id if contexts else None
            )
            contexts.append(context)
            
            await tracing.start_span(
                f"service-{i}",
                f"operation-{i}",
                context
            )
        
        # Get trace
        spans = await tracing.get_trace(trace_id)
        assert len(spans) == 3
        
        # Verify span relationships
        assert spans[0].parent_span_id is None
        assert spans[1].parent_span_id == spans[0].span_id
        assert spans[2].parent_span_id == spans[1].span_id
    
    async def test_propagate_context(self, tracing):
        """Test context propagation."""
        original_context = await tracing.create_trace_context()
        
        # Propagate to another service
        propagated_context = await tracing.propagate_context(
            original_context,
            "downstream-service"
        )
        
        assert propagated_context.trace_id == original_context.trace_id
        assert propagated_context.parent_id == original_context.span_id
        assert propagated_context.span_id != original_context.span_id
        assert propagated_context.trace_flags == original_context.trace_flags
    
    def test_parse_traceparent_header(self, tracing):
        """Test parsing W3C traceparent header."""
        # Valid header
        header = "00-0123456789abcdef0123456789abcdef-0123456789abcdef-01"
        context = tracing.parse_traceparent_header(header)
        
        assert context is not None
        assert context.trace_id == "0123456789abcdef0123456789abcdef"
        assert context.parent_id == "0123456789abcdef"
        assert len(context.span_id) == 16  # New span ID generated
        assert context.trace_flags == "01"
        
        # Invalid headers
        invalid_headers = [
            "invalid",
            "00-invalid-0123456789abcdef-01",
            "01-0123456789abcdef0123456789abcdef-0123456789abcdef-01",  # Wrong version
            "00-0123456789abcdef0123456789abcdef-01",  # Missing part
        ]
        
        for header in invalid_headers:
            context = tracing.parse_traceparent_header(header)
            assert context is None
    
    def test_format_traceparent_header(self, tracing):
        """Test formatting trace context as W3C traceparent header."""
        context = TraceContext(
            trace_id="0123456789abcdef0123456789abcdef",
            span_id="0123456789abcdef",
            trace_flags="01"
        )
        
        header = tracing.format_traceparent_header(context)
        assert header == "00-0123456789abcdef0123456789abcdef-0123456789abcdef-01"
    
    async def test_get_trace_graph(self, tracing):
        """Test getting trace as graph structure."""
        trace_id = tracing.generate_trace_id()
        
        # Create a trace with multiple spans
        root_context = await tracing.create_trace_context(trace_id=trace_id)
        root_span = await tracing.start_span("frontend", "GET /home", root_context)
        await asyncio.sleep(0.01)
        
        api_context = await tracing.propagate_context(root_context, "api")
        api_span = await tracing.start_span("api", "GET /api/data", api_context)
        await asyncio.sleep(0.01)
        
        db_context = await tracing.propagate_context(api_context, "database")
        db_span = await tracing.start_span("database", "SELECT * FROM users", db_context)
        await asyncio.sleep(0.01)
        
        # End spans
        await tracing.end_span(db_span.span_id, 200)
        await tracing.end_span(api_span.span_id, 200)
        await tracing.end_span(root_span.span_id, 200)
        
        # Get trace graph
        graph = await tracing.get_trace_graph(trace_id)
        
        assert graph["trace_id"] == trace_id
        assert len(graph["nodes"]) == 3
        assert len(graph["edges"]) == 2
        
        # Verify nodes
        services = {node["service"] for node in graph["nodes"]}
        assert services == {"frontend", "api", "database"}
        
        # Verify all nodes have duration
        for node in graph["nodes"]:
            assert node["duration"] is not None
            assert node["duration"] > 0
    
    async def test_get_service_dependencies_from_traces(self, tracing):
        """Test extracting service dependencies from traces."""
        # Create multiple traces showing service interactions
        for _ in range(3):
            trace_id = tracing.generate_trace_id()
            
            # Frontend -> API
            ctx1 = await tracing.create_trace_context(trace_id=trace_id)
            await tracing.start_span("frontend", "operation", ctx1)
            
            ctx2 = await tracing.propagate_context(ctx1, "api")
            await tracing.start_span("api", "operation", ctx2)
            
            # API -> Database
            ctx3 = await tracing.propagate_context(ctx2, "database")
            await tracing.start_span("database", "operation", ctx3)
            
            # API -> Cache
            ctx4 = await tracing.propagate_context(ctx2, "cache")
            await tracing.start_span("cache", "operation", ctx4)
        
        # Get dependencies
        dependencies = await tracing.get_service_dependencies_from_traces()
        
        assert "frontend" in dependencies
        assert "api" in dependencies["frontend"]
        
        assert "api" in dependencies
        assert "database" in dependencies["api"]
        assert "cache" in dependencies["api"]
    
    async def test_get_trace_statistics(self, tracing):
        """Test getting trace statistics."""
        # Create traces with various scenarios
        for i in range(5):
            trace_id = tracing.generate_trace_id()
            ctx = await tracing.create_trace_context(trace_id=trace_id)
            
            # Create spans
            span1 = await tracing.start_span("service-a", "operation", ctx)
            
            ctx2 = await tracing.propagate_context(ctx, "service-b")
            span2 = await tracing.start_span("service-b", "operation", ctx2)
            
            # End spans (some with errors)
            if i % 2 == 0:
                await tracing.end_span(span2.span_id, 500, "Error")
            else:
                await tracing.end_span(span2.span_id, 200)
            
            await tracing.end_span(span1.span_id, 200)
        
        # Get statistics
        stats = await tracing.get_trace_statistics()
        
        assert stats["total_traces"] == 5
        assert stats["total_spans"] == 10
        assert stats["active_spans"] == 0
        
        assert "service-a" in stats["service_span_counts"]
        assert stats["service_span_counts"]["service-a"] == 5
        assert stats["service_span_counts"]["service-b"] == 5
        
        assert "service-b" in stats["service_error_counts"]
        assert stats["service_error_counts"]["service-b"] == 3
    
    async def test_cleanup_old_traces(self, tracing):
        """Test cleaning up old traces."""
        # Create old trace
        old_trace_id = tracing.generate_trace_id()
        ctx = await tracing.create_trace_context(trace_id=old_trace_id)
        span = await tracing.start_span("service", "operation", ctx)
        
        # Manually set old timestamp
        span.start_time = datetime.now(timezone.utc) - timedelta(hours=2)
        
        # Create recent trace
        new_trace_id = tracing.generate_trace_id()
        ctx2 = await tracing.create_trace_context(trace_id=new_trace_id)
        await tracing.start_span("service", "operation", ctx2)
        
        # Clean up traces older than 1 hour
        removed_count = await tracing.cleanup_old_traces(max_age_seconds=3600)
        
        assert removed_count == 1
        
        # Verify old trace removed
        old_trace = await tracing.get_trace(old_trace_id)
        assert len(old_trace) == 0
        
        # Verify new trace remains
        new_trace = await tracing.get_trace(new_trace_id)
        assert len(new_trace) == 1
    
    async def test_concurrent_span_operations(self, tracing):
        """Test concurrent span operations."""
        trace_id = tracing.generate_trace_id()
        
        async def create_span(i):
            ctx = await tracing.create_trace_context(trace_id=trace_id)
            span = await tracing.start_span(f"service-{i}", f"op-{i}", ctx)
            await asyncio.sleep(0.01)
            await tracing.end_span(span.span_id, 200)
        
        # Create spans concurrently
        await asyncio.gather(*[create_span(i) for i in range(10)])
        
        # Verify all spans created
        spans = await tracing.get_trace(trace_id)
        assert len(spans) == 10
        
        # Verify no active spans
        active = await tracing.get_active_spans()
        assert len(active) == 0