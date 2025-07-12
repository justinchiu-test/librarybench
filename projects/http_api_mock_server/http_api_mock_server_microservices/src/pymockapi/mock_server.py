"""HTTP Mock Server for microservices testing."""

import asyncio
import json
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from aiohttp import web

from .chaos_controller import ChaosController
from .circuit_breaker import CircuitBreakerEngine
from .dependency_manager import DependencyManager
from .models import (
    ChaosScenario,
    CircuitBreakerConfig,
    ServiceDependency,
    ServiceMetadata,
    ServiceStatus,
)
from .service_registry import ServiceRegistry
from .tracing import TracingSystem


class MockServer:
    """HTTP mock server with microservices mesh capabilities."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        
        # Initialize core components
        self.registry = ServiceRegistry()
        self.dependency_manager = DependencyManager()
        self.circuit_breaker_engine = CircuitBreakerEngine()
        self.tracing_system = TracingSystem()
        self.chaos_controller = ChaosController(
            self.registry,
            self.circuit_breaker_engine,
            self.dependency_manager
        )
        
        # Web app
        self.app = web.Application()
        self._setup_routes()
        
        # Mock responses storage
        self._mock_responses: Dict[str, Dict[str, Any]] = {}
    
    def _setup_routes(self):
        """Set up HTTP routes."""
        # Service registry endpoints
        self.app.router.add_post("/registry/register", self.register_service)
        self.app.router.add_delete("/registry/{service_id}", self.deregister_service)
        self.app.router.add_get("/registry/{service_id}", self.get_service)
        self.app.router.add_get("/registry", self.list_services)
        self.app.router.add_put("/registry/{service_id}/heartbeat", self.heartbeat)
        
        # Dependency management endpoints
        self.app.router.add_post("/dependencies", self.add_dependency)
        self.app.router.add_delete("/dependencies/{from_service}/{to_service}", self.remove_dependency)
        self.app.router.add_get("/dependencies/{service_id}", self.get_dependencies)
        self.app.router.add_get("/dependencies/graph", self.get_dependency_graph)
        
        # Circuit breaker endpoints
        self.app.router.add_post("/circuit-breakers", self.register_circuit_breaker)
        self.app.router.add_get("/circuit-breakers", self.get_circuit_breaker_states)
        self.app.router.add_post("/circuit-breakers/{service_id}/{endpoint}/reset", self.reset_circuit_breaker)
        
        # Tracing endpoints
        self.app.router.add_get("/traces/{trace_id}", self.get_trace)
        self.app.router.add_get("/traces", self.get_trace_statistics)
        
        # Chaos engineering endpoints
        self.app.router.add_post("/chaos/events", self.create_chaos_event)
        self.app.router.add_delete("/chaos/events/{event_id}", self.stop_chaos_event)
        self.app.router.add_get("/chaos/events", self.list_chaos_events)
        self.app.router.add_post("/chaos/cascade-failure", self.simulate_cascade_failure)
        
        # Mock service endpoints
        self.app.router.add_post("/mock/{service_id}/configure", self.configure_mock_response)
        self.app.router.add_route("*", "/mock/{service_id}/{path:.*}", self.handle_mock_request)
    
    async def start(self):
        """Start the mock server."""
        await self.registry.start_health_checks()
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
    
    async def stop(self):
        """Stop the mock server."""
        await self.registry.stop_health_checks()
        await self.app.shutdown()
        await self.app.cleanup()
    
    # Service Registry Handlers
    
    async def register_service(self, request: web.Request) -> web.Response:
        """Register a new service."""
        data = await request.json()
        service = ServiceMetadata(**data)
        
        await self.registry.register_service(service)
        await self.dependency_manager.add_service(
            service.service_id,
            {"service_metadata": service}
        )
        
        return web.json_response({
            "status": "registered",
            "service_id": service.service_id
        })
    
    async def deregister_service(self, request: web.Request) -> web.Response:
        """Deregister a service."""
        service_id = request.match_info["service_id"]
        
        success = await self.registry.deregister_service(service_id)
        if success:
            await self.dependency_manager.remove_service(service_id)
        
        return web.json_response({
            "status": "success" if success else "not_found"
        })
    
    async def get_service(self, request: web.Request) -> web.Response:
        """Get service information."""
        service_id = request.match_info["service_id"]
        service = await self.registry.get_service(service_id)
        
        if service:
            return web.json_response(service.model_dump(mode='json'))
        return web.json_response({"error": "Service not found"}, status=404)
    
    async def list_services(self, request: web.Request) -> web.Response:
        """List all services."""
        services = await self.registry.get_all_services()
        return web.json_response({
            "services": [s.model_dump(mode='json') for s in services],
            "total": len(services)
        })
    
    async def heartbeat(self, request: web.Request) -> web.Response:
        """Update service heartbeat."""
        service_id = request.match_info["service_id"]
        success = await self.registry.heartbeat(service_id)
        
        return web.json_response({
            "status": "success" if success else "not_found"
        })
    
    # Dependency Management Handlers
    
    async def add_dependency(self, request: web.Request) -> web.Response:
        """Add a service dependency."""
        data = await request.json()
        dependency = ServiceDependency(**data)
        
        await self.dependency_manager.add_dependency(dependency)
        
        # Register circuit breaker if enabled
        if dependency.circuit_breaker_enabled:
            to_service = await self.registry.get_service(dependency.to_service)
            if to_service:
                await self.circuit_breaker_engine.register_endpoint(
                    dependency.to_service,
                    to_service.endpoint,
                    CircuitBreakerConfig()
                )
        
        return web.json_response({"status": "created"})
    
    async def remove_dependency(self, request: web.Request) -> web.Response:
        """Remove a service dependency."""
        from_service = request.match_info["from_service"]
        to_service = request.match_info["to_service"]
        
        await self.dependency_manager.remove_dependency(from_service, to_service)
        
        return web.json_response({"status": "removed"})
    
    async def get_dependencies(self, request: web.Request) -> web.Response:
        """Get dependencies for a service."""
        service_id = request.match_info["service_id"]
        dependencies = await self.dependency_manager.get_dependencies(service_id)
        
        return web.json_response({
            "service_id": service_id,
            "dependencies": [d.model_dump(mode='json') for d in dependencies]
        })
    
    async def get_dependency_graph(self, request: web.Request) -> web.Response:
        """Get the complete dependency graph."""
        graph = await self.dependency_manager.get_service_graph()
        
        return web.json_response({
            "services": [s.model_dump(mode='json') for s in graph.services],
            "dependencies": [d.model_dump(mode='json') for d in graph.dependencies]
        })
    
    # Circuit Breaker Handlers
    
    async def register_circuit_breaker(self, request: web.Request) -> web.Response:
        """Register a circuit breaker."""
        data = await request.json()
        service_id = data["service_id"]
        endpoint = data["endpoint"]
        config = CircuitBreakerConfig(**data.get("config", {}))
        
        await self.circuit_breaker_engine.register_endpoint(
            service_id,
            endpoint,
            config
        )
        
        return web.json_response({"status": "registered"})
    
    async def get_circuit_breaker_states(self, request: web.Request) -> web.Response:
        """Get all circuit breaker states."""
        states = await self.circuit_breaker_engine.get_all_states()
        
        return web.json_response({
            "circuit_breakers": states,
            "total": len(states)
        })
    
    async def reset_circuit_breaker(self, request: web.Request) -> web.Response:
        """Reset a circuit breaker."""
        service_id = request.match_info["service_id"]
        endpoint = request.match_info["endpoint"]
        
        breaker = await self.circuit_breaker_engine.get_breaker(service_id, endpoint)
        if breaker:
            await breaker.reset()
            return web.json_response({"status": "reset"})
        
        return web.json_response({"error": "Circuit breaker not found"}, status=404)
    
    # Tracing Handlers
    
    async def get_trace(self, request: web.Request) -> web.Response:
        """Get trace information."""
        trace_id = request.match_info["trace_id"]
        spans = await self.tracing_system.get_trace(trace_id)
        
        if not spans:
            return web.json_response({"error": "Trace not found"}, status=404)
        
        graph = await self.tracing_system.get_trace_graph(trace_id)
        
        return web.json_response({
            "trace_id": trace_id,
            "spans": [s.model_dump(mode='json') for s in spans],
            "graph": graph
        })
    
    async def get_trace_statistics(self, request: web.Request) -> web.Response:
        """Get tracing statistics."""
        stats = await self.tracing_system.get_trace_statistics()
        return web.json_response(stats)
    
    # Chaos Engineering Handlers
    
    async def create_chaos_event(self, request: web.Request) -> web.Response:
        """Create a chaos event."""
        data = await request.json()
        scenario = ChaosScenario(data["scenario"])
        target_services = data["target_services"]
        duration_seconds = data.get("duration_seconds")
        parameters = data.get("parameters", {})
        
        event = await self.chaos_controller.create_chaos_event(
            scenario,
            target_services,
            duration_seconds,
            parameters
        )
        
        return web.json_response(event.model_dump(mode='json'))
    
    async def stop_chaos_event(self, request: web.Request) -> web.Response:
        """Stop a chaos event."""
        event_id = request.match_info["event_id"]
        success = await self.chaos_controller.stop_chaos_event(event_id)
        
        return web.json_response({
            "status": "stopped" if success else "not_found"
        })
    
    async def list_chaos_events(self, request: web.Request) -> web.Response:
        """List active chaos events."""
        events = await self.chaos_controller.get_active_events()
        
        return web.json_response({
            "events": [e.model_dump(mode='json') for e in events],
            "total": len(events)
        })
    
    async def simulate_cascade_failure(self, request: web.Request) -> web.Response:
        """Simulate a cascade failure."""
        data = await request.json()
        initial_service = data["initial_service"]
        failure_probability = data.get("failure_probability", 0.5)
        max_depth = data.get("max_depth", 3)
        
        event = await self.chaos_controller.simulate_cascade_failure(
            initial_service,
            failure_probability,
            max_depth
        )
        
        return web.json_response(event.model_dump(mode='json'))
    
    # Mock Service Handlers
    
    async def configure_mock_response(self, request: web.Request) -> web.Response:
        """Configure mock response for a service."""
        service_id = request.match_info["service_id"]
        data = await request.json()
        
        if service_id not in self._mock_responses:
            self._mock_responses[service_id] = {}
        
        path = data.get("path", "*")
        self._mock_responses[service_id][path] = {
            "status": data.get("status", 200),
            "body": data.get("body", {}),
            "headers": data.get("headers", {}),
            "delay_ms": data.get("delay_ms", 0)
        }
        
        return web.json_response({"status": "configured"})
    
    async def handle_mock_request(self, request: web.Request) -> web.Response:
        """Handle mock service requests."""
        service_id = request.match_info["service_id"]
        path = request.match_info.get("path", "")
        
        # Extract trace context from headers
        traceparent = request.headers.get("traceparent")
        if traceparent:
            trace_context = self.tracing_system.parse_traceparent_header(traceparent)
        else:
            trace_context = await self.tracing_system.create_trace_context()
        
        # Start span for this request
        span = await self.tracing_system.start_span(
            service_id,
            f"{request.method} /{path}",
            trace_context,
            {"method": request.method, "path": path}
        )
        
        try:
            # Check if service is affected by chaos
            chaos_events = await self.chaos_controller.get_events_for_service(service_id)
            
            for event in chaos_events:
                if event.scenario == ChaosScenario.NETWORK_LATENCY:
                    delay_ms = event.parameters.get("latency_ms", 1000)
                    await asyncio.sleep(delay_ms / 1000)
                elif event.scenario == ChaosScenario.RESPONSE_ERROR:
                    error_rate = event.parameters.get("error_rate", 0.5)
                    if random.random() < error_rate:
                        await self.tracing_system.end_span(span.span_id, 500, "Chaos-induced error")
                        return web.json_response(
                            {"error": "Chaos-induced error"},
                            status=500
                        )
            
            # Check circuit breaker
            service = await self.registry.get_service(service_id)
            if not service or service.status == ServiceStatus.UNHEALTHY:
                await self.tracing_system.end_span(span.span_id, 503, "Service unavailable")
                return web.json_response(
                    {"error": "Service unavailable"},
                    status=503
                )
            
            # Get mock response
            mock_config = self._mock_responses.get(service_id, {})
            response_config = mock_config.get(path) or mock_config.get("*", {
                "status": 200,
                "body": {"message": f"Mock response from {service_id}"},
                "headers": {},
                "delay_ms": 0
            })
            
            # Apply configured delay
            if response_config["delay_ms"] > 0:
                await asyncio.sleep(response_config["delay_ms"] / 1000)
            
            # End span successfully
            await self.tracing_system.end_span(span.span_id, response_config["status"])
            
            # Build response with trace propagation
            headers = dict(response_config["headers"])
            headers["traceparent"] = self.tracing_system.format_traceparent_header(trace_context)
            
            return web.json_response(
                response_config["body"],
                status=response_config["status"],
                headers=headers
            )
            
        except Exception as e:
            await self.tracing_system.end_span(span.span_id, 500, str(e))
            return web.json_response(
                {"error": str(e)},
                status=500
            )