"""Service Registry implementation for dynamic service discovery."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set

from .models import ServiceMetadata, ServiceStatus


class ServiceRegistry:
    """Manages service registration and discovery."""
    
    def __init__(self, health_check_interval: int = 10):
        self._services: Dict[str, ServiceMetadata] = {}
        self._health_check_interval = health_check_interval
        self._health_check_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
    async def register_service(self, service: ServiceMetadata) -> bool:
        """Register a new service or update existing one."""
        async with self._lock:
            self._services[service.service_id] = service
            return True
    
    async def deregister_service(self, service_id: str) -> bool:
        """Remove a service from the registry."""
        async with self._lock:
            if service_id in self._services:
                del self._services[service_id]
                return True
            return False
    
    async def get_service(self, service_id: str) -> Optional[ServiceMetadata]:
        """Get a specific service by ID."""
        async with self._lock:
            return self._services.get(service_id)
    
    async def get_services_by_name(self, name: str) -> List[ServiceMetadata]:
        """Get all services with a specific name."""
        async with self._lock:
            return [s for s in self._services.values() if s.name == name]
    
    async def get_services_by_tag(self, tag: str) -> List[ServiceMetadata]:
        """Get all services with a specific tag."""
        async with self._lock:
            return [s for s in self._services.values() if tag in s.tags]
    
    async def get_healthy_services(self) -> List[ServiceMetadata]:
        """Get all healthy services."""
        async with self._lock:
            return [
                s for s in self._services.values() 
                if s.status == ServiceStatus.HEALTHY
            ]
    
    async def get_all_services(self) -> List[ServiceMetadata]:
        """Get all registered services."""
        async with self._lock:
            return list(self._services.values())
    
    async def update_service_status(
        self, 
        service_id: str, 
        status: ServiceStatus
    ) -> bool:
        """Update the status of a service."""
        async with self._lock:
            if service_id in self._services:
                self._services[service_id].status = status
                return True
            return False
    
    async def heartbeat(self, service_id: str) -> bool:
        """Update service heartbeat timestamp."""
        async with self._lock:
            if service_id in self._services:
                self._services[service_id].last_heartbeat = datetime.now(timezone.utc)
                return True
            return False
    
    async def start_health_checks(self):
        """Start background health check task."""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def stop_health_checks(self):
        """Stop background health check task."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
    
    async def _health_check_loop(self):
        """Background task to check service health."""
        while True:
            try:
                await self._check_service_health()
                await asyncio.sleep(self._health_check_interval)
            except asyncio.CancelledError:
                break
    
    async def _check_service_health(self):
        """Check health of all services based on heartbeat."""
        threshold = datetime.now(timezone.utc) - timedelta(seconds=self._health_check_interval * 3)
        
        async with self._lock:
            for service in self._services.values():
                if service.last_heartbeat < threshold:
                    if service.status != ServiceStatus.UNHEALTHY:
                        service.status = ServiceStatus.UNHEALTHY
                elif service.status == ServiceStatus.UNHEALTHY:
                    service.status = ServiceStatus.HEALTHY
    
    def get_service_count(self) -> int:
        """Get the total number of registered services."""
        return len(self._services)
    
    def get_healthy_service_count(self) -> int:
        """Get the number of healthy services."""
        return sum(
            1 for s in self._services.values() 
            if s.status == ServiceStatus.HEALTHY
        )