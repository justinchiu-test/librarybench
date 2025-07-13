"""Tests for data models."""

import pytest
from datetime import datetime

from pymockapi.models import (
    ServiceMetadata,
    ServiceStatus,
    ServiceDependency,
    CircuitBreakerState,
    CircuitBreakerConfig,
    TraceContext,
    Span,
    ChaosEvent,
    ChaosScenario,
    ServiceGraph
)


class TestServiceMetadata:
    """Test ServiceMetadata model."""
    
    def test_create_service_metadata(self):
        """Test creating a service metadata instance."""
        service = ServiceMetadata(
            service_id="service-1",
            name="test-service",
            endpoint="/api/v1",
            port=8080
        )
        
        assert service.service_id == "service-1"
        assert service.name == "test-service"
        assert service.version == "1.0.0"
        assert service.endpoint == "/api/v1"
        assert service.port == 8080
        assert service.status == ServiceStatus.HEALTHY
        assert isinstance(service.registered_at, datetime)
        assert isinstance(service.last_heartbeat, datetime)
    
    def test_port_validation(self):
        """Test port validation."""
        with pytest.raises(ValueError):
            ServiceMetadata(
                service_id="service-1",
                name="test-service",
                endpoint="/api/v1",
                port=0
            )
        
        with pytest.raises(ValueError):
            ServiceMetadata(
                service_id="service-1",
                name="test-service",
                endpoint="/api/v1",
                port=65536
            )
    
    def test_service_with_metadata(self):
        """Test service with additional metadata."""
        service = ServiceMetadata(
            service_id="service-1",
            name="test-service",
            endpoint="/api/v1",
            port=8080,
            tags=["tag1", "tag2"],
            metadata={"region": "us-west", "tier": "production"}
        )
        
        assert service.tags == ["tag1", "tag2"]
        assert service.metadata == {"region": "us-west", "tier": "production"}


class TestServiceDependency:
    """Test ServiceDependency model."""
    
    def test_create_dependency(self):
        """Test creating a service dependency."""
        dep = ServiceDependency(
            from_service="service-1",
            to_service="service-2"
        )
        
        assert dep.from_service == "service-1"
        assert dep.to_service == "service-2"
        assert dep.required is True
        assert dep.timeout_ms == 5000
        assert dep.retry_count == 3
        assert dep.circuit_breaker_enabled is True
    
    def test_dependency_with_custom_config(self):
        """Test dependency with custom configuration."""
        dep = ServiceDependency(
            from_service="service-1",
            to_service="service-2",
            required=False,
            timeout_ms=10000,
            retry_count=5,
            circuit_breaker_enabled=False
        )
        
        assert dep.required is False
        assert dep.timeout_ms == 10000
        assert dep.retry_count == 5
        assert dep.circuit_breaker_enabled is False
    
    def test_timeout_validation(self):
        """Test timeout validation."""
        with pytest.raises(ValueError):
            ServiceDependency(
                from_service="service-1",
                to_service="service-2",
                timeout_ms=-1
            )


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig model."""
    
    def test_default_config(self):
        """Test default circuit breaker configuration."""
        config = CircuitBreakerConfig()
        
        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout_seconds == 60
        assert config.half_open_max_requests == 3
    
    def test_custom_config(self):
        """Test custom circuit breaker configuration."""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            success_threshold=5,
            timeout_seconds=120,
            half_open_max_requests=5
        )
        
        assert config.failure_threshold == 10
        assert config.success_threshold == 5
        assert config.timeout_seconds == 120
        assert config.half_open_max_requests == 5
    
    def test_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError):
            CircuitBreakerConfig(failure_threshold=0)
        
        with pytest.raises(ValueError):
            CircuitBreakerConfig(success_threshold=0)
        
        with pytest.raises(ValueError):
            CircuitBreakerConfig(half_open_max_requests=0)


class TestTraceContext:
    """Test TraceContext model."""
    
    def test_create_trace_context(self):
        """Test creating a trace context."""
        context = TraceContext(
            trace_id="0123456789abcdef0123456789abcdef",
            span_id="0123456789abcdef"
        )
        
        assert context.trace_id == "0123456789abcdef0123456789abcdef"
        assert context.span_id == "0123456789abcdef"
        assert context.parent_id is None
        assert context.trace_flags == "01"
        assert context.trace_state is None
    
    def test_trace_id_validation(self):
        """Test trace ID validation."""
        # Test invalid length
        with pytest.raises(ValueError):
            TraceContext(
                trace_id="0123456789abcdef",
                span_id="0123456789abcdef"
            )
        
        # Test invalid characters
        with pytest.raises(ValueError):
            TraceContext(
                trace_id="0123456789abcdef0123456789abcdeg",
                span_id="0123456789abcdef"
            )
    
    def test_span_id_validation(self):
        """Test span ID validation."""
        # Test invalid length
        with pytest.raises(ValueError):
            TraceContext(
                trace_id="0123456789abcdef0123456789abcdef",
                span_id="0123456789"
            )
        
        # Test invalid characters
        with pytest.raises(ValueError):
            TraceContext(
                trace_id="0123456789abcdef0123456789abcdef",
                span_id="0123456789abcdeg"
            )
    
    def test_case_normalization(self):
        """Test that IDs are normalized to lowercase."""
        context = TraceContext(
            trace_id="0123456789ABCDEF0123456789ABCDEF",
            span_id="0123456789ABCDEF"
        )
        
        assert context.trace_id == "0123456789abcdef0123456789abcdef"
        assert context.span_id == "0123456789abcdef"


class TestSpan:
    """Test Span model."""
    
    def test_create_span(self):
        """Test creating a span."""
        span = Span(
            trace_id="0123456789abcdef0123456789abcdef",
            span_id="0123456789abcdef",
            service_name="test-service",
            operation_name="GET /api/v1"
        )
        
        assert span.trace_id == "0123456789abcdef0123456789abcdef"
        assert span.span_id == "0123456789abcdef"
        assert span.parent_span_id is None
        assert span.service_name == "test-service"
        assert span.operation_name == "GET /api/v1"
        assert isinstance(span.start_time, datetime)
        assert span.end_time is None
        assert span.status_code == 200
        assert span.error is None
    
    def test_span_with_parent(self):
        """Test span with parent."""
        span = Span(
            trace_id="0123456789abcdef0123456789abcdef",
            span_id="0123456789abcdef",
            parent_span_id="fedcba9876543210",
            service_name="test-service",
            operation_name="GET /api/v1"
        )
        
        assert span.parent_span_id == "fedcba9876543210"
    
    def test_span_with_error(self):
        """Test span with error."""
        span = Span(
            trace_id="0123456789abcdef0123456789abcdef",
            span_id="0123456789abcdef",
            service_name="test-service",
            operation_name="GET /api/v1",
            status_code=500,
            error="Internal server error"
        )
        
        assert span.status_code == 500
        assert span.error == "Internal server error"


class TestChaosEvent:
    """Test ChaosEvent model."""
    
    def test_create_chaos_event(self):
        """Test creating a chaos event."""
        event = ChaosEvent(
            event_id="event-1",
            scenario=ChaosScenario.SERVICE_DOWN,
            target_services=["service-1", "service-2"]
        )
        
        assert event.event_id == "event-1"
        assert event.scenario == ChaosScenario.SERVICE_DOWN
        assert event.target_services == ["service-1", "service-2"]
        assert event.duration_seconds is None
        assert event.parameters == {}
        assert isinstance(event.start_time, datetime)
        assert event.end_time is None
        assert event.active is True
    
    def test_chaos_event_with_duration(self):
        """Test chaos event with duration."""
        event = ChaosEvent(
            event_id="event-1",
            scenario=ChaosScenario.NETWORK_LATENCY,
            target_services=["service-1"],
            duration_seconds=300,
            parameters={"latency_ms": 1000}
        )
        
        assert event.duration_seconds == 300
        assert event.parameters == {"latency_ms": 1000}


class TestServiceGraph:
    """Test ServiceGraph model."""
    
    def test_create_service_graph(self):
        """Test creating a service graph."""
        services = [
            ServiceMetadata(
                service_id="service-1",
                name="service-1",
                endpoint="/api/v1",
                port=8080
            ),
            ServiceMetadata(
                service_id="service-2",
                name="service-2",
                endpoint="/api/v2",
                port=8081
            )
        ]
        
        dependencies = [
            ServiceDependency(
                from_service="service-1",
                to_service="service-2"
            )
        ]
        
        graph = ServiceGraph(services=services, dependencies=dependencies)
        
        assert len(graph.services) == 2
        assert len(graph.dependencies) == 1
    
    def test_get_dependencies_for_service(self):
        """Test getting dependencies for a service."""
        dependencies = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-1", to_service="service-3"),
            ServiceDependency(from_service="service-2", to_service="service-3")
        ]
        
        graph = ServiceGraph(services=[], dependencies=dependencies)
        
        service1_deps = graph.get_dependencies_for_service("service-1")
        assert len(service1_deps) == 2
        assert all(dep.from_service == "service-1" for dep in service1_deps)
        
        service2_deps = graph.get_dependencies_for_service("service-2")
        assert len(service2_deps) == 1
        assert service2_deps[0].to_service == "service-3"
    
    def test_get_dependents_of_service(self):
        """Test getting dependents of a service."""
        dependencies = [
            ServiceDependency(from_service="service-1", to_service="service-3"),
            ServiceDependency(from_service="service-2", to_service="service-3"),
            ServiceDependency(from_service="service-3", to_service="service-4")
        ]
        
        graph = ServiceGraph(services=[], dependencies=dependencies)
        
        service3_dependents = graph.get_dependents_of_service("service-3")
        assert len(service3_dependents) == 2
        assert all(dep.to_service == "service-3" for dep in service3_dependents)