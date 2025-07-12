"""Chaos Controller for failure injection and testing."""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Callable, Any

from .models import ChaosEvent, ChaosScenario, ServiceStatus
from .service_registry import ServiceRegistry
from .circuit_breaker import CircuitBreakerEngine
from .dependency_manager import DependencyManager


class ChaosController:
    """Manages chaos engineering scenarios for testing resilience."""
    
    def __init__(
        self,
        registry: ServiceRegistry,
        circuit_breaker_engine: CircuitBreakerEngine,
        dependency_manager: DependencyManager
    ):
        self.registry = registry
        self.circuit_breaker_engine = circuit_breaker_engine
        self.dependency_manager = dependency_manager
        self._active_events: Dict[str, ChaosEvent] = {}
        self._event_handlers: Dict[ChaosScenario, List[Callable]] = {}
        self._affected_services: Dict[str, Set[str]] = {}  # service_id -> event_ids
        self._lock = asyncio.Lock()
    
    async def create_chaos_event(
        self,
        scenario: ChaosScenario,
        target_services: List[str],
        duration_seconds: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ChaosEvent:
        """Create and activate a chaos event."""
        event = ChaosEvent(
            event_id=str(uuid.uuid4()),
            scenario=scenario,
            target_services=target_services,
            duration_seconds=duration_seconds,
            parameters=parameters or {}
        )
        
        async with self._lock:
            self._active_events[event.event_id] = event
            
            # Track affected services
            for service_id in target_services:
                if service_id not in self._affected_services:
                    self._affected_services[service_id] = set()
                self._affected_services[service_id].add(event.event_id)
        
        # Apply the chaos scenario
        await self._apply_chaos_scenario(event)
        
        # Schedule cleanup if duration is specified
        if duration_seconds:
            asyncio.create_task(self._schedule_event_cleanup(event))
        
        return event
    
    async def stop_chaos_event(self, event_id: str) -> bool:
        """Stop an active chaos event."""
        async with self._lock:
            if event_id not in self._active_events:
                return False
            
            event = self._active_events[event_id]
            event.active = False
            event.end_time = datetime.now(timezone.utc)
            
            # Remove from affected services
            for service_id in event.target_services:
                if service_id in self._affected_services:
                    self._affected_services[service_id].discard(event_id)
                    if not self._affected_services[service_id]:
                        del self._affected_services[service_id]
            
            del self._active_events[event_id]
        
        # Revert the chaos scenario
        await self._revert_chaos_scenario(event)
        return True
    
    async def get_active_events(self) -> List[ChaosEvent]:
        """Get all active chaos events."""
        async with self._lock:
            return list(self._active_events.values())
    
    async def get_events_for_service(self, service_id: str) -> List[ChaosEvent]:
        """Get active chaos events affecting a service."""
        async with self._lock:
            event_ids = self._affected_services.get(service_id, set())
            return [
                self._active_events[event_id] 
                for event_id in event_ids 
                if event_id in self._active_events
            ]
    
    async def is_service_affected(self, service_id: str) -> bool:
        """Check if a service is affected by any chaos event."""
        async with self._lock:
            return service_id in self._affected_services
    
    async def simulate_cascade_failure(
        self,
        initial_service: str,
        failure_probability: float = 0.5,
        max_depth: int = 3
    ) -> ChaosEvent:
        """Simulate a cascade failure starting from one service."""
        affected_services = await self._calculate_cascade_impact(
            initial_service,
            failure_probability,
            max_depth
        )
        
        return await self.create_chaos_event(
            ChaosScenario.CASCADE_FAILURE,
            affected_services,
            parameters={
                "initial_service": initial_service,
                "failure_probability": failure_probability,
                "max_depth": max_depth
            }
        )
    
    async def _calculate_cascade_impact(
        self,
        service_id: str,
        failure_probability: float,
        max_depth: int,
        current_depth: int = 0,
        visited: Optional[Set[str]] = None
    ) -> List[str]:
        """Calculate which services would be affected by cascade failure."""
        if visited is None:
            visited = set()
        
        if current_depth >= max_depth or service_id in visited:
            return []
        
        visited.add(service_id)
        affected = [service_id]
        
        # Get services that depend on this one
        dependents = await self.dependency_manager.get_dependents(service_id)
        
        for dependent in dependents:
            if random.random() < failure_probability:
                cascade_affected = await self._calculate_cascade_impact(
                    dependent,
                    failure_probability * 0.8,  # Reduce probability as we go deeper
                    max_depth,
                    current_depth + 1,
                    visited
                )
                affected.extend(cascade_affected)
        
        return affected
    
    async def _apply_chaos_scenario(self, event: ChaosEvent):
        """Apply a chaos scenario to target services."""
        if event.scenario == ChaosScenario.SERVICE_DOWN:
            await self._apply_service_down(event)
        elif event.scenario == ChaosScenario.NETWORK_LATENCY:
            await self._apply_network_latency(event)
        elif event.scenario == ChaosScenario.NETWORK_PARTITION:
            await self._apply_network_partition(event)
        elif event.scenario == ChaosScenario.RESPONSE_ERROR:
            await self._apply_response_error(event)
        elif event.scenario == ChaosScenario.CASCADE_FAILURE:
            await self._apply_cascade_failure(event)
        
        # Call registered handlers
        if event.scenario in self._event_handlers:
            for handler in self._event_handlers[event.scenario]:
                await handler(event)
    
    async def _revert_chaos_scenario(self, event: ChaosEvent):
        """Revert a chaos scenario."""
        if event.scenario == ChaosScenario.SERVICE_DOWN:
            await self._revert_service_down(event)
        elif event.scenario == ChaosScenario.CASCADE_FAILURE:
            await self._revert_cascade_failure(event)
        # Other scenarios may not need explicit reversion
    
    async def _apply_service_down(self, event: ChaosEvent):
        """Mark services as unhealthy."""
        for service_id in event.target_services:
            await self.registry.update_service_status(
                service_id, 
                ServiceStatus.UNHEALTHY
            )
    
    async def _revert_service_down(self, event: ChaosEvent):
        """Mark services as healthy again."""
        for service_id in event.target_services:
            await self.registry.update_service_status(
                service_id, 
                ServiceStatus.HEALTHY
            )
    
    async def _apply_network_latency(self, event: ChaosEvent):
        """Apply network latency (handled by mock server)."""
        # This would be implemented in the HTTP mock server
        pass
    
    async def _apply_network_partition(self, event: ChaosEvent):
        """Simulate network partition between services."""
        # Force open circuit breakers for partitioned services
        for service_id in event.target_services:
            service = await self.registry.get_service(service_id)
            if service:
                breaker = await self.circuit_breaker_engine.get_breaker(
                    service_id, 
                    service.endpoint
                )
                if breaker:
                    await breaker.force_open()
    
    async def _apply_response_error(self, event: ChaosEvent):
        """Apply response errors (handled by mock server)."""
        # This would be implemented in the HTTP mock server
        pass
    
    async def _apply_cascade_failure(self, event: ChaosEvent):
        """Apply cascade failure by marking services unhealthy."""
        for service_id in event.target_services:
            await self.registry.update_service_status(
                service_id, 
                ServiceStatus.UNHEALTHY
            )
            
            # Force open circuit breakers
            service = await self.registry.get_service(service_id)
            if service:
                breaker = await self.circuit_breaker_engine.get_breaker(
                    service_id, 
                    service.endpoint
                )
                if breaker:
                    await breaker.force_open()
    
    async def _revert_cascade_failure(self, event: ChaosEvent):
        """Revert cascade failure."""
        for service_id in event.target_services:
            await self.registry.update_service_status(
                service_id, 
                ServiceStatus.HEALTHY
            )
            
            # Reset circuit breakers
            service = await self.registry.get_service(service_id)
            if service:
                breaker = await self.circuit_breaker_engine.get_breaker(
                    service_id, 
                    service.endpoint
                )
                if breaker:
                    await breaker.reset()
    
    async def _schedule_event_cleanup(self, event: ChaosEvent):
        """Schedule automatic cleanup of an event."""
        if event.duration_seconds:
            await asyncio.sleep(event.duration_seconds)
            await self.stop_chaos_event(event.event_id)
    
    def register_event_handler(
        self, 
        scenario: ChaosScenario, 
        handler: Callable[[ChaosEvent], Any]
    ):
        """Register a custom handler for chaos events."""
        if scenario not in self._event_handlers:
            self._event_handlers[scenario] = []
        self._event_handlers[scenario].append(handler)
    
    async def get_chaos_metrics(self) -> Dict[str, Any]:
        """Get metrics about chaos events."""
        async with self._lock:
            active_events = len(self._active_events)
            affected_services = len(self._affected_services)
            
            scenario_counts = {}
            for event in self._active_events.values():
                scenario_counts[event.scenario] = scenario_counts.get(event.scenario, 0) + 1
            
            return {
                "active_events": active_events,
                "affected_services": affected_services,
                "events_by_scenario": scenario_counts,
                "total_target_services": sum(
                    len(event.target_services) 
                    for event in self._active_events.values()
                )
            }