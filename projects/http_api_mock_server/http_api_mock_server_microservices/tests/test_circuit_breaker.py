"""Tests for Circuit Breaker."""

import asyncio
import pytest
from datetime import datetime, timedelta

from pymockapi.models import CircuitBreakerState, CircuitBreakerConfig
from pymockapi.circuit_breaker import CircuitBreaker, CircuitBreakerEngine


class TestCircuitBreaker:
    """Test CircuitBreaker functionality."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=1,
            half_open_max_requests=2
        )
    
    @pytest.fixture
    def breaker(self, config):
        """Create a circuit breaker instance."""
        return CircuitBreaker("test-service", "/api/test", config)
    
    async def test_initial_state(self, breaker):
        """Test circuit breaker starts in closed state."""
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        assert breaker.last_failure_time is None
    
    async def test_successful_calls(self, breaker):
        """Test successful calls don't open the breaker."""
        async def success_func():
            return "success"
        
        # Make multiple successful calls
        for _ in range(5):
            result = await breaker.call(success_func)
            assert result == "success"
        
        # Verify breaker remains closed
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
    
    async def test_failure_threshold(self, breaker):
        """Test breaker opens after failure threshold."""
        async def failing_func():
            raise Exception("Test failure")
        
        # Make failures up to threshold
        for i in range(breaker.config.failure_threshold):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
            
            if i < breaker.config.failure_threshold - 1:
                assert breaker.state == CircuitBreakerState.CLOSED
        
        # Verify breaker is now open
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count == breaker.config.failure_threshold
    
    async def test_open_state_rejection(self, breaker):
        """Test calls are rejected when breaker is open."""
        # Force breaker open
        await breaker.force_open()
        
        async def test_func():
            return "should not execute"
        
        # Verify call is rejected
        with pytest.raises(Exception) as exc_info:
            await breaker.call(test_func)
        
        assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    async def test_half_open_transition(self, breaker):
        """Test transition to half-open state after timeout."""
        async def failing_func():
            raise Exception("Test failure")
        
        # Open the breaker
        for _ in range(breaker.config.failure_threshold):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(breaker.config.timeout_seconds + 0.1)
        
        # Next call should transition to half-open
        async def success_func():
            return "success"
        
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitBreakerState.HALF_OPEN
    
    async def test_half_open_to_closed(self, breaker):
        """Test successful calls in half-open state close the breaker."""
        # Force to half-open
        await breaker._transition_to_half_open()
        
        async def success_func():
            return "success"
        
        # Make successful calls up to success threshold
        for _ in range(breaker.config.success_threshold):
            result = await breaker.call(success_func)
            assert result == "success"
        
        # Verify breaker is closed
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.success_count == 0  # Reset after transition
    
    async def test_half_open_to_open(self, breaker):
        """Test failure in half-open state reopens the breaker."""
        # Force to half-open
        await breaker._transition_to_half_open()
        
        async def failing_func():
            raise Exception("Test failure")
        
        # Single failure should reopen
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        
        assert breaker.state == CircuitBreakerState.OPEN
    
    async def test_half_open_max_requests(self, config):
        """Test half-open state respects max requests."""
        # Create breaker with config where success threshold > max requests
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=5,  # Higher than max requests
            timeout_seconds=1,
            half_open_max_requests=2
        )
        breaker = CircuitBreaker("test-service", "/api/test", config)
        
        # Force to half-open
        await breaker._transition_to_half_open()
        
        async def success_func():
            return "success"
        
        # Make max allowed requests
        for _ in range(breaker.config.half_open_max_requests):
            await breaker.call(success_func)
        
        # Next request should be rejected
        with pytest.raises(Exception) as exc_info:
            await breaker.call(success_func)
        
        assert "max requests reached" in str(exc_info.value)
    
    async def test_manual_reset(self, breaker):
        """Test manual reset of circuit breaker."""
        # Open the breaker
        await breaker.force_open()
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Manual reset
        await breaker.reset()
        
        # Verify reset
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
    
    async def test_get_state_info(self, breaker):
        """Test getting state information."""
        info = breaker.get_state_info()
        
        assert info["service_id"] == "test-service"
        assert info["endpoint"] == "/api/test"
        assert info["state"] == CircuitBreakerState.CLOSED
        assert info["failure_count"] == 0
        assert info["success_count"] == 0
        assert info["last_failure_time"] is None
        assert "last_state_change" in info
    
    async def test_concurrent_calls(self, breaker):
        """Test circuit breaker handles concurrent calls correctly."""
        call_count = 0
        
        async def counted_func():
            nonlocal call_count
            call_count += 1
            if call_count <= breaker.config.failure_threshold:
                raise Exception("Test failure")
            return "success"
        
        # Make concurrent calls
        tasks = []
        for _ in range(10):
            tasks.append(asyncio.create_task(
                breaker.call(counted_func)
            ))
        
        # Wait for all calls
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count failures and successes
        failures = sum(1 for r in results if isinstance(r, Exception))
        successes = sum(1 for r in results if r == "success")
        
        # Verify behavior (exact counts depend on timing)
        assert failures >= breaker.config.failure_threshold
        assert breaker.state in [CircuitBreakerState.OPEN, CircuitBreakerState.HALF_OPEN]


class TestCircuitBreakerEngine:
    """Test CircuitBreakerEngine functionality."""
    
    @pytest.fixture
    async def engine(self):
        """Create a circuit breaker engine instance."""
        return CircuitBreakerEngine()
    
    async def test_register_endpoint(self, engine):
        """Test registering an endpoint."""
        config = CircuitBreakerConfig()
        await engine.register_endpoint("service-1", "/api/test", config)
        
        # Verify registration
        breaker = await engine.get_breaker("service-1", "/api/test")
        assert breaker is not None
        assert breaker.service_id == "service-1"
        assert breaker.endpoint == "/api/test"
    
    async def test_unregister_endpoint(self, engine):
        """Test unregistering an endpoint."""
        await engine.register_endpoint("service-1", "/api/test")
        
        # Unregister
        await engine.unregister_endpoint("service-1", "/api/test")
        
        # Verify removal
        breaker = await engine.get_breaker("service-1", "/api/test")
        assert breaker is None
    
    async def test_call_with_breaker(self, engine):
        """Test calling function through breaker."""
        await engine.register_endpoint("service-1", "/api/test")
        
        async def test_func():
            return "success"
        
        result = await engine.call_with_breaker(
            "service-1", "/api/test", test_func
        )
        assert result == "success"
    
    async def test_call_without_breaker(self, engine):
        """Test calling function without registered breaker."""
        async def test_func():
            return "success"
        
        # Should execute directly without breaker
        result = await engine.call_with_breaker(
            "unregistered", "/api/test", test_func
        )
        assert result == "success"
    
    async def test_get_all_states(self, engine):
        """Test getting all breaker states."""
        # Register multiple endpoints
        await engine.register_endpoint("service-1", "/api/v1")
        await engine.register_endpoint("service-1", "/api/v2")
        await engine.register_endpoint("service-2", "/api/v1")
        
        # Get all states
        states = await engine.get_all_states()
        assert len(states) == 3
        
        # Verify keys
        assert "service-1:/api/v1" in states
        assert "service-1:/api/v2" in states
        assert "service-2:/api/v1" in states
    
    async def test_get_open_circuits(self, engine):
        """Test getting open circuits."""
        # Register and open some breakers
        await engine.register_endpoint("service-1", "/api/v1")
        await engine.register_endpoint("service-2", "/api/v1")
        
        breaker1 = await engine.get_breaker("service-1", "/api/v1")
        await breaker1.force_open()
        
        # Get open circuits
        open_circuits = await engine.get_open_circuits()
        assert len(open_circuits) == 1
        assert "service-1:/api/v1" in open_circuits
    
    async def test_reset_all(self, engine):
        """Test resetting all breakers."""
        # Register and open breakers
        await engine.register_endpoint("service-1", "/api/v1")
        await engine.register_endpoint("service-2", "/api/v1")
        
        breaker1 = await engine.get_breaker("service-1", "/api/v1")
        breaker2 = await engine.get_breaker("service-2", "/api/v1")
        
        await breaker1.force_open()
        await breaker2.force_open()
        
        # Reset all
        await engine.reset_all()
        
        # Verify all reset
        assert breaker1.state == CircuitBreakerState.CLOSED
        assert breaker2.state == CircuitBreakerState.CLOSED
    
    async def test_update_config(self, engine):
        """Test updating breaker configuration."""
        # Register with default config
        await engine.register_endpoint("service-1", "/api/v1")
        
        # Update config
        new_config = CircuitBreakerConfig(
            failure_threshold=10,
            success_threshold=5
        )
        await engine.update_config("service-1", "/api/v1", new_config)
        
        # Verify update
        breaker = await engine.get_breaker("service-1", "/api/v1")
        assert breaker.config.failure_threshold == 10
        assert breaker.config.success_threshold == 5
    
    def test_get_counts(self, engine):
        """Test getting breaker counts."""
        assert engine.get_breaker_count() == 0
        assert engine.get_open_breaker_count() == 0
    
    async def test_concurrent_operations(self, engine):
        """Test concurrent operations on engine."""
        # Register endpoints concurrently
        async def register(i):
            await engine.register_endpoint(f"service-{i}", "/api/v1")
        
        await asyncio.gather(*[register(i) for i in range(10)])
        
        # Verify all registered
        assert engine.get_breaker_count() == 10
        
        # Call functions concurrently
        async def call_func(i):
            async def test_func():
                return f"result-{i}"
            
            return await engine.call_with_breaker(
                f"service-{i}", "/api/v1", test_func
            )
        
        results = await asyncio.gather(*[call_func(i) for i in range(10)])
        
        # Verify all calls succeeded
        for i, result in enumerate(results):
            assert result == f"result-{i}"