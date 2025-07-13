"""Integration tests for the complete mock server system."""

import json
import pytest
from aiohttp import ClientSession

from pymockapi.mock_server import MockServer
from pymockapi.models import (
    ServiceMetadata,
    ServiceDependency,
    ChaosScenario,
    CircuitBreakerConfig
)


class TestMockServerIntegration:
    """Integration tests for MockServer."""
    
    @pytest.fixture
    async def server(self):
        """Create and start a mock server."""
        server = MockServer(port=8765)
        await server.start()
        yield server
        await server.stop()
    
    @pytest.fixture
    async def client(self):
        """Create an HTTP client."""
        async with ClientSession() as session:
            yield session
    
    def base_url(self, server):
        """Get base URL for the server."""
        return f"http://{server.host}:{server.port}"
    
    async def test_service_registration_flow(self, server, client):
        """Test complete service registration flow."""
        base_url = self.base_url(server)
        
        # Register a service
        service_data = {
            "service_id": "test-service",
            "name": "Test Service",
            "version": "1.0.0",
            "endpoint": "/api/test",
            "port": 8080
        }
        
        async with client.post(f"{base_url}/registry/register", json=service_data) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "registered"
        
        # Get the service
        async with client.get(f"{base_url}/registry/test-service") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["service_id"] == "test-service"
            assert data["status"] == "healthy"
        
        # List all services
        async with client.get(f"{base_url}/registry") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["total"] == 1
            assert len(data["services"]) == 1
        
        # Send heartbeat
        async with client.put(f"{base_url}/registry/test-service/heartbeat") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "success"
        
        # Deregister the service
        async with client.delete(f"{base_url}/registry/test-service") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "success"
    
    async def test_dependency_management_flow(self, server, client):
        """Test dependency management flow."""
        base_url = self.base_url(server)
        
        # Register services
        for i in range(3):
            service_data = {
                "service_id": f"service-{i}",
                "name": f"Service {i}",
                "endpoint": f"/api/v{i}",
                "port": 8080 + i
            }
            async with client.post(f"{base_url}/registry/register", json=service_data) as resp:
                assert resp.status == 200
        
        # Add dependencies
        dependency_data = {
            "from_service": "service-0",
            "to_service": "service-1",
            "required": True,
            "timeout_ms": 5000,
            "circuit_breaker_enabled": True
        }
        async with client.post(f"{base_url}/dependencies", json=dependency_data) as resp:
            assert resp.status == 200
        
        # Add another dependency
        dependency_data2 = {
            "from_service": "service-1",
            "to_service": "service-2"
        }
        async with client.post(f"{base_url}/dependencies", json=dependency_data2) as resp:
            assert resp.status == 200
        
        # Get dependencies for service-0
        async with client.get(f"{base_url}/dependencies/service-0") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert len(data["dependencies"]) == 1
            assert data["dependencies"][0]["to_service"] == "service-1"
        
        # Get dependency graph
        async with client.get(f"{base_url}/dependencies/graph") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert len(data["services"]) == 3
            assert len(data["dependencies"]) == 2
    
    async def test_circuit_breaker_flow(self, server, client):
        """Test circuit breaker functionality."""
        base_url = self.base_url(server)
        
        # Register service
        service_data = {
            "service_id": "breaker-test",
            "name": "Breaker Test",
            "endpoint": "/api/test",
            "port": 8080
        }
        async with client.post(f"{base_url}/registry/register", json=service_data) as resp:
            assert resp.status == 200
        
        # Register circuit breaker
        breaker_data = {
            "service_id": "breaker-test",
            "endpoint": "/api/test",
            "config": {
                "failure_threshold": 3,
                "success_threshold": 2,
                "timeout_seconds": 5
            }
        }
        async with client.post(f"{base_url}/circuit-breakers", json=breaker_data) as resp:
            assert resp.status == 200
        
        # Get circuit breaker states
        async with client.get(f"{base_url}/circuit-breakers") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["total"] == 1
            assert "breaker-test:/api/test" in data["circuit_breakers"]
        
        # Reset circuit breaker
        async with client.post(f"{base_url}/circuit-breakers/breaker-test/%2Fapi%2Ftest/reset") as resp:
            assert resp.status == 200
    
    async def test_tracing_flow(self, server, client):
        """Test distributed tracing flow."""
        base_url = self.base_url(server)
        
        # Register services
        for i in range(2):
            service_data = {
                "service_id": f"trace-service-{i}",
                "name": f"Trace Service {i}",
                "endpoint": f"/api/v{i}",
                "port": 8080 + i
            }
            async with client.post(f"{base_url}/registry/register", json=service_data) as resp:
                assert resp.status == 200
        
        # Configure mock responses
        for i in range(2):
            config_data = {
                "path": "*",
                "status": 200,
                "body": {"message": f"Response from service {i}"},
                "delay_ms": 10
            }
            async with client.post(
                f"{base_url}/mock/trace-service-{i}/configure",
                json=config_data
            ) as resp:
                assert resp.status == 200
        
        # Make request to first service
        async with client.get(f"{base_url}/mock/trace-service-0/test") as resp:
            assert resp.status == 200
            traceparent = resp.headers.get("traceparent")
            assert traceparent is not None
            
            # Extract trace ID
            parts = traceparent.split("-")
            trace_id = parts[1]
        
        # Make request to second service with trace propagation
        headers = {"traceparent": traceparent}
        async with client.get(
            f"{base_url}/mock/trace-service-1/test",
            headers=headers
        ) as resp:
            assert resp.status == 200
        
        # Get trace information
        async with client.get(f"{base_url}/traces/{trace_id}") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["trace_id"] == trace_id
            assert len(data["spans"]) >= 1
        
        # Get trace statistics
        async with client.get(f"{base_url}/traces") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["total_traces"] > 0
            assert data["total_spans"] > 0
    
    async def test_chaos_engineering_flow(self, server, client):
        """Test chaos engineering scenarios."""
        base_url = self.base_url(server)
        
        # Register services
        for i in range(3):
            service_data = {
                "service_id": f"chaos-service-{i}",
                "name": f"Chaos Service {i}",
                "endpoint": f"/api/v{i}",
                "port": 8080 + i
            }
            async with client.post(f"{base_url}/registry/register", json=service_data) as resp:
                assert resp.status == 200
        
        # Create dependencies for cascade testing
        deps = [
            {"from_service": "chaos-service-0", "to_service": "chaos-service-1"},
            {"from_service": "chaos-service-1", "to_service": "chaos-service-2"}
        ]
        for dep in deps:
            async with client.post(f"{base_url}/dependencies", json=dep) as resp:
                assert resp.status == 200
        
        # Create chaos event - service down
        chaos_data = {
            "scenario": "service_down",
            "target_services": ["chaos-service-1"],
            "duration_seconds": 10
        }
        async with client.post(f"{base_url}/chaos/events", json=chaos_data) as resp:
            assert resp.status == 200
            data = await resp.json()
            event_id = data["event_id"]
            assert data["scenario"] == "service_down"
        
        # Verify service is unhealthy
        async with client.get(f"{base_url}/registry/chaos-service-1") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "unhealthy"
        
        # List active chaos events
        async with client.get(f"{base_url}/chaos/events") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["total"] == 1
        
        # Stop chaos event
        async with client.delete(f"{base_url}/chaos/events/{event_id}") as resp:
            assert resp.status == 200
        
        # Verify service is healthy again
        async with client.get(f"{base_url}/registry/chaos-service-1") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "healthy"
        
        # Test cascade failure
        cascade_data = {
            "initial_service": "chaos-service-0",
            "failure_probability": 1.0,
            "max_depth": 2
        }
        async with client.post(f"{base_url}/chaos/cascade-failure", json=cascade_data) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert "chaos-service-0" in data["target_services"]
            cascade_event_id = data["event_id"]
        
        # Clean up cascade event
        async with client.delete(f"{base_url}/chaos/events/{cascade_event_id}") as resp:
            assert resp.status == 200
    
    async def test_mock_service_behavior(self, server, client):
        """Test mock service request handling."""
        base_url = self.base_url(server)
        
        # Register service
        service_data = {
            "service_id": "mock-test",
            "name": "Mock Test",
            "endpoint": "/api/test",
            "port": 8080
        }
        async with client.post(f"{base_url}/registry/register", json=service_data) as resp:
            assert resp.status == 200
        
        # Configure mock response
        config_data = {
            "path": "users",
            "status": 200,
            "body": {"users": ["alice", "bob", "charlie"]},
            "headers": {"X-Custom-Header": "test-value"},
            "delay_ms": 50
        }
        async with client.post(f"{base_url}/mock/mock-test/configure", json=config_data) as resp:
            assert resp.status == 200
        
        # Make request to mock endpoint
        import time
        start_time = time.time()
        async with client.get(f"{base_url}/mock/mock-test/users") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["users"] == ["alice", "bob", "charlie"]
            assert resp.headers.get("X-Custom-Header") == "test-value"
            assert resp.headers.get("traceparent") is not None
        
        # Verify delay was applied
        elapsed = (time.time() - start_time) * 1000
        assert elapsed >= 50
        
        # Test with chaos - network latency
        chaos_data = {
            "scenario": "network_latency",
            "target_services": ["mock-test"],
            "parameters": {"latency_ms": 100}
        }
        async with client.post(f"{base_url}/chaos/events", json=chaos_data) as resp:
            assert resp.status == 200
            data = await resp.json()
            latency_event_id = data["event_id"]
        
        # Make request with latency
        start_time = time.time()
        async with client.get(f"{base_url}/mock/mock-test/users") as resp:
            assert resp.status == 200
        
        elapsed = (time.time() - start_time) * 1000
        assert elapsed >= 150  # 50ms configured + 100ms chaos
        
        # Clean up
        async with client.delete(f"{base_url}/chaos/events/{latency_event_id}") as resp:
            assert resp.status == 200
        
        # Test with chaos - response error
        chaos_data = {
            "scenario": "response_error",
            "target_services": ["mock-test"],
            "parameters": {"error_rate": 1.0}
        }
        async with client.post(f"{base_url}/chaos/events", json=chaos_data) as resp:
            assert resp.status == 200
            data = await resp.json()
            error_event_id = data["event_id"]
        
        # Make request expecting error
        async with client.get(f"{base_url}/mock/mock-test/users") as resp:
            assert resp.status == 500
            data = await resp.json()
            assert "error" in data
        
        # Clean up
        async with client.delete(f"{base_url}/chaos/events/{error_event_id}") as resp:
            assert resp.status == 200
    
    async def test_service_mesh_scenario(self, server, client):
        """Test complete service mesh scenario with multiple services."""
        base_url = self.base_url(server)
        
        # Set up a microservices architecture:
        # frontend -> api-gateway -> [user-service, order-service] -> database
        
        services = [
            {"service_id": "frontend", "name": "Frontend", "endpoint": "/", "port": 3000},
            {"service_id": "api-gateway", "name": "API Gateway", "endpoint": "/api", "port": 8080},
            {"service_id": "user-service", "name": "User Service", "endpoint": "/users", "port": 8081},
            {"service_id": "order-service", "name": "Order Service", "endpoint": "/orders", "port": 8082},
            {"service_id": "database", "name": "Database", "endpoint": "/db", "port": 5432}
        ]
        
        # Register all services
        for service in services:
            async with client.post(f"{base_url}/registry/register", json=service) as resp:
                assert resp.status == 200
        
        # Set up dependencies
        dependencies = [
            {"from_service": "frontend", "to_service": "api-gateway"},
            {"from_service": "api-gateway", "to_service": "user-service"},
            {"from_service": "api-gateway", "to_service": "order-service"},
            {"from_service": "user-service", "to_service": "database"},
            {"from_service": "order-service", "to_service": "database"}
        ]
        
        for dep in dependencies:
            async with client.post(f"{base_url}/dependencies", json=dep) as resp:
                assert resp.status == 200
        
        # Configure mock responses
        mock_configs = [
            {"service": "frontend", "body": {"page": "home"}},
            {"service": "api-gateway", "body": {"status": "routing"}},
            {"service": "user-service", "body": {"users": ["alice", "bob"]}},
            {"service": "order-service", "body": {"orders": [{"id": 1}, {"id": 2}]}},
            {"service": "database", "body": {"records": 1000}}
        ]
        
        for config in mock_configs:
            config_data = {
                "path": "*",
                "status": 200,
                "body": config["body"]
            }
            async with client.post(
                f"{base_url}/mock/{config['service']}/configure",
                json=config_data
            ) as resp:
                assert resp.status == 200
        
        # Make requests to test the mesh
        async with client.get(f"{base_url}/mock/frontend/home") as resp:
            assert resp.status == 200
            frontend_trace = resp.headers.get("traceparent")
        
        # Simulate frontend calling api-gateway
        headers = {"traceparent": frontend_trace}
        async with client.get(f"{base_url}/mock/api-gateway/api/v1", headers=headers) as resp:
            assert resp.status == 200
            gateway_trace = resp.headers.get("traceparent")
        
        # Simulate api-gateway calling user-service
        headers = {"traceparent": gateway_trace}
        async with client.get(f"{base_url}/mock/user-service/users", headers=headers) as resp:
            assert resp.status == 200
        
        # Test cascade failure from database
        cascade_data = {
            "initial_service": "database",
            "failure_probability": 1.0,
            "max_depth": 3
        }
        async with client.post(f"{base_url}/chaos/cascade-failure", json=cascade_data) as resp:
            assert resp.status == 200
            data = await resp.json()
            affected = data["target_services"]
            cascade_event_id = data["event_id"]
        
        # Verify cascade effect
        for service_id in ["database", "user-service", "order-service"]:
            assert service_id in affected
        
        # Clean up
        async with client.delete(f"{base_url}/chaos/events/{cascade_event_id}") as resp:
            assert resp.status == 200
        
        # Verify all services healthy again
        async with client.get(f"{base_url}/registry") as resp:
            assert resp.status == 200
            data = await resp.json()
            for service in data["services"]:
                assert service["status"] == "healthy"