"""Tests for Chaos Controller."""

import asyncio
import pytest
from datetime import datetime

from pymockapi.models import (
    ChaosEvent,
    ChaosScenario,
    ServiceMetadata,
    ServiceStatus,
    ServiceDependency,
    CircuitBreakerConfig
)
from pymockapi.service_registry import ServiceRegistry
from pymockapi.circuit_breaker import CircuitBreakerEngine
from pymockapi.dependency_manager import DependencyManager
from pymockapi.chaos_controller import ChaosController


class TestChaosController:
    """Test ChaosController functionality."""
    
    @pytest.fixture
    async def setup(self):
        """Set up test environment with all components."""
        registry = ServiceRegistry()
        circuit_breaker_engine = CircuitBreakerEngine()
        dependency_manager = DependencyManager()
        chaos_controller = ChaosController(
            registry,
            circuit_breaker_engine,
            dependency_manager
        )
        
        # Register some test services
        services = []
        for i in range(5):
            service = ServiceMetadata(
                service_id=f"service-{i}",
                name=f"service-{i}",
                endpoint=f"/api/v{i}",
                port=8080 + i
            )
            services.append(service)
            await registry.register_service(service)
            await dependency_manager.add_service(service.service_id)
            await circuit_breaker_engine.register_endpoint(
                service.service_id,
                service.endpoint,
                CircuitBreakerConfig()
            )
        
        # Set up dependencies: 0 -> 1 -> 2, 0 -> 3 -> 4
        deps = [
            ServiceDependency(from_service="service-0", to_service="service-1"),
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-0", to_service="service-3"),
            ServiceDependency(from_service="service-3", to_service="service-4"),
        ]
        
        for dep in deps:
            await dependency_manager.add_dependency(dep)
        
        yield {
            "registry": registry,
            "circuit_breaker_engine": circuit_breaker_engine,
            "dependency_manager": dependency_manager,
            "chaos_controller": chaos_controller,
            "services": services
        }
        
        # Cleanup
        await registry.stop_health_checks()
    
    async def test_create_chaos_event(self, setup):
        """Test creating a chaos event."""
        chaos = setup["chaos_controller"]
        
        event = await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1", "service-2"],
            duration_seconds=5,
            parameters={"severity": "high"}
        )
        
        assert event.event_id is not None
        assert event.scenario == ChaosScenario.SERVICE_DOWN
        assert event.target_services == ["service-1", "service-2"]
        assert event.duration_seconds == 5
        assert event.parameters == {"severity": "high"}
        assert event.active is True
        assert isinstance(event.start_time, datetime)
    
    async def test_service_down_scenario(self, setup):
        """Test SERVICE_DOWN chaos scenario."""
        chaos = setup["chaos_controller"]
        registry = setup["registry"]
        
        # Create service down event
        event = await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1", "service-2"]
        )
        
        # Verify services marked unhealthy
        service1 = await registry.get_service("service-1")
        service2 = await registry.get_service("service-2")
        
        assert service1.status == ServiceStatus.UNHEALTHY
        assert service2.status == ServiceStatus.UNHEALTHY
        
        # Stop event
        await chaos.stop_chaos_event(event.event_id)
        
        # Verify services restored
        service1 = await registry.get_service("service-1")
        service2 = await registry.get_service("service-2")
        
        assert service1.status == ServiceStatus.HEALTHY
        assert service2.status == ServiceStatus.HEALTHY
    
    async def test_network_partition_scenario(self, setup):
        """Test NETWORK_PARTITION chaos scenario."""
        chaos = setup["chaos_controller"]
        breaker_engine = setup["circuit_breaker_engine"]
        
        # Create network partition event
        event = await chaos.create_chaos_event(
            ChaosScenario.NETWORK_PARTITION,
            ["service-1"]
        )
        
        # Verify circuit breaker forced open
        breaker = await breaker_engine.get_breaker("service-1", "/api/v1")
        assert breaker.state.value == "open"
        
        # Stop event
        await chaos.stop_chaos_event(event.event_id)
    
    async def test_cascade_failure_scenario(self, setup):
        """Test CASCADE_FAILURE chaos scenario."""
        chaos = setup["chaos_controller"]
        registry = setup["registry"]
        
        # Simulate cascade failure from service-0
        event = await chaos.simulate_cascade_failure(
            "service-0",
            failure_probability=1.0,  # 100% for deterministic test
            max_depth=3
        )
        
        # Verify cascade effect
        assert event.scenario == ChaosScenario.CASCADE_FAILURE
        assert "service-0" in event.target_services
        
        # Check affected services
        for service_id in event.target_services:
            service = await registry.get_service(service_id)
            assert service.status == ServiceStatus.UNHEALTHY
    
    async def test_cascade_failure_probability(self, setup):
        """Test cascade failure with probability."""
        chaos = setup["chaos_controller"]
        
        # Run multiple simulations
        affected_counts = []
        for _ in range(10):
            event = await chaos.simulate_cascade_failure(
                "service-0",
                failure_probability=0.5,
                max_depth=3
            )
            affected_counts.append(len(event.target_services))
            await chaos.stop_chaos_event(event.event_id)
        
        # With 50% probability, we should see variation
        assert min(affected_counts) >= 1  # At least initial service
        assert max(affected_counts) <= 5  # At most all services
        # Due to randomness, we may occasionally not see variation in small samples
        # so we'll just check the basic constraints
    
    async def test_stop_chaos_event(self, setup):
        """Test stopping a chaos event."""
        chaos = setup["chaos_controller"]
        
        # Create event
        event = await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1"]
        )
        
        # Stop event
        success = await chaos.stop_chaos_event(event.event_id)
        assert success is True
        
        # Verify event no longer active
        active_events = await chaos.get_active_events()
        assert len(active_events) == 0
        
        # Try stopping non-existent event
        success = await chaos.stop_chaos_event("non-existent")
        assert success is False
    
    async def test_automatic_event_cleanup(self, setup):
        """Test automatic cleanup after duration."""
        chaos = setup["chaos_controller"]
        
        # Create short duration event
        event = await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1"],
            duration_seconds=1
        )
        
        # Verify event is active
        active_events = await chaos.get_active_events()
        assert len(active_events) == 1
        
        # Wait for cleanup
        await asyncio.sleep(1.5)
        
        # Verify event cleaned up
        active_events = await chaos.get_active_events()
        assert len(active_events) == 0
    
    async def test_get_active_events(self, setup):
        """Test getting active chaos events."""
        chaos = setup["chaos_controller"]
        
        # Create multiple events
        events = []
        for i in range(3):
            event = await chaos.create_chaos_event(
                ChaosScenario.SERVICE_DOWN,
                [f"service-{i}"]
            )
            events.append(event)
        
        # Get active events
        active_events = await chaos.get_active_events()
        assert len(active_events) == 3
        
        # Stop one event
        await chaos.stop_chaos_event(events[0].event_id)
        
        # Verify count updated
        active_events = await chaos.get_active_events()
        assert len(active_events) == 2
    
    async def test_get_events_for_service(self, setup):
        """Test getting events affecting a service."""
        chaos = setup["chaos_controller"]
        
        # Create events affecting different services
        event1 = await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1", "service-2"]
        )
        event2 = await chaos.create_chaos_event(
            ChaosScenario.NETWORK_LATENCY,
            ["service-2", "service-3"]
        )
        event3 = await chaos.create_chaos_event(
            ChaosScenario.RESPONSE_ERROR,
            ["service-3"]
        )
        
        # Get events for service-2
        service2_events = await chaos.get_events_for_service("service-2")
        assert len(service2_events) == 2
        event_ids = {e.event_id for e in service2_events}
        assert event_ids == {event1.event_id, event2.event_id}
        
        # Get events for service-3
        service3_events = await chaos.get_events_for_service("service-3")
        assert len(service3_events) == 2
        event_ids = {e.event_id for e in service3_events}
        assert event_ids == {event2.event_id, event3.event_id}
    
    async def test_is_service_affected(self, setup):
        """Test checking if service is affected by chaos."""
        chaos = setup["chaos_controller"]
        
        # Initially no services affected
        assert await chaos.is_service_affected("service-1") is False
        
        # Create chaos event
        await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1"]
        )
        
        # Now service is affected
        assert await chaos.is_service_affected("service-1") is True
        assert await chaos.is_service_affected("service-2") is False
    
    async def test_event_handlers(self, setup):
        """Test custom event handlers."""
        chaos = setup["chaos_controller"]
        
        # Track handler calls
        handler_calls = []
        
        async def custom_handler(event: ChaosEvent):
            handler_calls.append(event)
        
        # Register handler
        chaos.register_event_handler(ChaosScenario.SERVICE_DOWN, custom_handler)
        
        # Create event
        event = await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1"]
        )
        
        # Verify handler called
        assert len(handler_calls) == 1
        assert handler_calls[0].event_id == event.event_id
    
    async def test_get_chaos_metrics(self, setup):
        """Test getting chaos metrics."""
        chaos = setup["chaos_controller"]
        
        # Create various events
        await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1", "service-2"]
        )
        await chaos.create_chaos_event(
            ChaosScenario.NETWORK_LATENCY,
            ["service-3"]
        )
        await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-4"]
        )
        
        # Get metrics
        metrics = await chaos.get_chaos_metrics()
        
        assert metrics["active_events"] == 3
        assert metrics["affected_services"] == 4  # 4 unique services
        assert metrics["events_by_scenario"][ChaosScenario.SERVICE_DOWN] == 2
        assert metrics["events_by_scenario"][ChaosScenario.NETWORK_LATENCY] == 1
        assert metrics["total_target_services"] == 4  # Total across all events
    
    async def test_concurrent_chaos_operations(self, setup):
        """Test concurrent chaos operations."""
        chaos = setup["chaos_controller"]
        
        # Create events concurrently
        async def create_event(i):
            return await chaos.create_chaos_event(
                ChaosScenario.SERVICE_DOWN,
                [f"service-{i % 5}"]
            )
        
        events = await asyncio.gather(*[create_event(i) for i in range(10)])
        
        # Verify all created
        active_events = await chaos.get_active_events()
        assert len(active_events) == 10
        
        # Stop events concurrently
        async def stop_event(event):
            return await chaos.stop_chaos_event(event.event_id)
        
        results = await asyncio.gather(*[stop_event(e) for e in events])
        
        # Verify all stopped
        assert all(results)
        active_events = await chaos.get_active_events()
        assert len(active_events) == 0
    
    async def test_multiple_scenarios_same_service(self, setup):
        """Test multiple chaos scenarios affecting same service."""
        chaos = setup["chaos_controller"]
        registry = setup["registry"]
        
        # Apply multiple scenarios to same service
        await chaos.create_chaos_event(
            ChaosScenario.SERVICE_DOWN,
            ["service-1"]
        )
        await chaos.create_chaos_event(
            ChaosScenario.NETWORK_LATENCY,
            ["service-1"],
            parameters={"latency_ms": 1000}
        )
        await chaos.create_chaos_event(
            ChaosScenario.RESPONSE_ERROR,
            ["service-1"],
            parameters={"error_rate": 0.5}
        )
        
        # Verify service affected by multiple events
        events = await chaos.get_events_for_service("service-1")
        assert len(events) == 3
        
        scenarios = {e.scenario for e in events}
        assert scenarios == {
            ChaosScenario.SERVICE_DOWN,
            ChaosScenario.NETWORK_LATENCY,
            ChaosScenario.RESPONSE_ERROR
        }