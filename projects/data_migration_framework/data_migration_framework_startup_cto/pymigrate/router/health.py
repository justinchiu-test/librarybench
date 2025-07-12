"""Health checking for services during migration."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from pymigrate.models.config import ServiceConfig

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status of a service."""
    healthy: bool
    last_check: datetime
    response_time_ms: float
    consecutive_failures: int
    error_message: Optional[str] = None
    
    
class HealthChecker:
    """Monitors health of services during migration."""
    
    def __init__(self):
        """Initialize health checker."""
        self._services: Dict[str, ServiceConfig] = {}
        self._health_status: Dict[str, HealthStatus] = {}
        self._check_tasks: Dict[str, asyncio.Task] = {}
        self._failure_thresholds: Dict[str, int] = {}
        
    async def register_service(
        self,
        service_config: ServiceConfig,
        failure_threshold: int = 3
    ) -> None:
        """Register a service for health monitoring."""
        logger.info(f"Registering service {service_config.name} for health checks")
        
        self._services[service_config.name] = service_config
        self._failure_thresholds[service_config.name] = failure_threshold
        
        # Initialize health status
        self._health_status[service_config.name] = HealthStatus(
            healthy=True,
            last_check=datetime.utcnow(),
            response_time_ms=0,
            consecutive_failures=0
        )
        
        # Start health check task
        task = asyncio.create_task(
            self._health_check_loop(service_config.name)
        )
        self._check_tasks[service_config.name] = task
        
    async def unregister_service(self, service_name: str) -> None:
        """Stop monitoring a service."""
        if service_name in self._check_tasks:
            self._check_tasks[service_name].cancel()
            del self._check_tasks[service_name]
            
        if service_name in self._services:
            del self._services[service_name]
            
        if service_name in self._health_status:
            del self._health_status[service_name]
            
        logger.info(f"Unregistered service {service_name}")
        
    async def is_healthy(self, service_name: str) -> bool:
        """Check if a service is healthy."""
        status = self._health_status.get(service_name)
        
        if not status:
            return False
            
        # Check if last health check is recent
        age = datetime.utcnow() - status.last_check
        if age > timedelta(seconds=60):
            # Health check is stale
            return False
            
        return status.healthy
        
    def get_service_status(self, service_name: str) -> Optional[HealthStatus]:
        """Get detailed health status for a service."""
        return self._health_status.get(service_name)
        
    async def _health_check_loop(self, service_name: str) -> None:
        """Continuous health check loop for a service."""
        service_config = self._services[service_name]
        
        while True:
            try:
                # Perform health check
                health_result = await self._perform_health_check(service_config)
                
                # Update status
                status = self._health_status[service_name]
                
                if health_result["healthy"]:
                    status.healthy = True
                    status.consecutive_failures = 0
                    status.error_message = None
                else:
                    status.consecutive_failures += 1
                    status.error_message = health_result.get("error")
                    
                    # Check failure threshold
                    if status.consecutive_failures >= self._failure_thresholds[service_name]:
                        status.healthy = False
                        logger.warning(
                            f"Service {service_name} marked unhealthy after "
                            f"{status.consecutive_failures} failures"
                        )
                        
                status.last_check = datetime.utcnow()
                status.response_time_ms = health_result.get("response_time_ms", 0)
                
                # Wait before next check
                interval = service_config.health_check_interval_ms / 1000.0
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop for {service_name}: {e}")
                await asyncio.sleep(5)  # Back off on error
                
    async def _perform_health_check(
        self,
        service_config: ServiceConfig
    ) -> Dict[str, Any]:
        """Perform a single health check."""
        start_time = datetime.utcnow()
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=service_config.timeout) as client:
                response = await client.get(
                    f"{service_config.base_url}{service_config.health_check_path}"
                )
                
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    # Parse health response
                    try:
                        health_data = response.json()
                        
                        # Check for specific health indicators
                        if isinstance(health_data, dict):
                            if health_data.get("status") == "healthy":
                                return {
                                    "healthy": True,
                                    "response_time_ms": response_time,
                                    "details": health_data
                                }
                            else:
                                return {
                                    "healthy": False,
                                    "response_time_ms": response_time,
                                    "error": f"Service reported unhealthy: {health_data}",
                                    "details": health_data
                                }
                    except:
                        # Health endpoint returned non-JSON, but 200 status
                        return {
                            "healthy": True,
                            "response_time_ms": response_time
                        }
                else:
                    return {
                        "healthy": False,
                        "response_time_ms": response_time,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            if e.__class__.__name__ == "TimeoutException":
                return {
                    "healthy": False,
                    "response_time_ms": service_config.timeout * 1000,
                    "error": "Health check timeout"
                }
            elif e.__class__.__name__ == "ConnectError":
                return {
                    "healthy": False,
                    "response_time_ms": 0,
                    "error": f"Connection error: {str(e)}"
                }
            else:
                return {
                    "healthy": False,
                    "response_time_ms": 0,
                    "error": f"Health check error: {str(e)}"
                }
            
    async def perform_dependency_check(
        self,
        service_name: str
    ) -> Dict[str, Any]:
        """Check health of service dependencies."""
        service_config = self._services.get(service_name)
        
        if not service_config:
            return {
                "healthy": False,
                "error": "Service not registered"
            }
            
        # In a real implementation, this would check:
        # - Database connections
        # - Cache availability  
        # - External API dependencies
        # - Message queue connections
        
        dependencies = {
            "database": True,
            "cache": True,
            "external_apis": True
        }
        
        all_healthy = all(dependencies.values())
        
        return {
            "healthy": all_healthy,
            "dependencies": dependencies
        }
        
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get aggregated health metrics."""
        total_services = len(self._services)
        healthy_services = sum(
            1 for status in self._health_status.values()
            if status.healthy
        )
        
        avg_response_time = 0
        if self._health_status:
            avg_response_time = sum(
                status.response_time_ms
                for status in self._health_status.values()
            ) / len(self._health_status)
            
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "average_response_time_ms": round(avg_response_time, 2),
            "services": {
                name: {
                    "healthy": status.healthy,
                    "response_time_ms": status.response_time_ms,
                    "consecutive_failures": status.consecutive_failures,
                    "last_check": status.last_check.isoformat()
                }
                for name, status in self._health_status.items()
            }
        }
        
    async def wait_for_healthy(
        self,
        service_name: str,
        timeout: int = 300
    ) -> bool:
        """Wait for a service to become healthy."""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            if await self.is_healthy(service_name):
                return True
                
            await asyncio.sleep(5)
            
        return False