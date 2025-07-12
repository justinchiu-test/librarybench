"""Circuit Breaker implementation for fault tolerance."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional, Any

from .models import CircuitBreakerState, CircuitBreakerConfig


class CircuitBreaker:
    """Circuit breaker for a single service endpoint."""
    
    def __init__(
        self, 
        service_id: str,
        endpoint: str,
        config: CircuitBreakerConfig
    ):
        self.service_id = service_id
        self.endpoint = endpoint
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.now(timezone.utc)
        self.half_open_requests = 0
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function through the circuit breaker."""
        should_increment = False
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if await self._should_attempt_reset():
                    await self._transition_to_half_open()
                else:
                    raise Exception(f"Circuit breaker is OPEN for {self.service_id}:{self.endpoint}")
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.half_open_requests >= self.config.half_open_max_requests:
                    raise Exception(f"Circuit breaker is HALF_OPEN with max requests reached")
                should_increment = True
        
        if should_increment:
            async with self._lock:
                self.half_open_requests += 1
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    await self._transition_to_closed()
            else:
                self.failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now(timezone.utc)
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                await self._transition_to_open()
            elif (self.state == CircuitBreakerState.CLOSED and 
                  self.failure_count >= self.config.failure_threshold):
                await self._transition_to_open()
    
    async def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return False
        
        timeout_delta = timedelta(seconds=self.config.timeout_seconds)
        return datetime.now(timezone.utc) - self.last_failure_time >= timeout_delta
    
    async def _transition_to_open(self):
        """Transition to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.last_state_change = datetime.now(timezone.utc)
        self.half_open_requests = 0
    
    async def _transition_to_closed(self):
        """Transition to CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = datetime.now(timezone.utc)
        self.half_open_requests = 0
    
    async def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.success_count = 0
        self.failure_count = 0
        self.last_state_change = datetime.now(timezone.utc)
        self.half_open_requests = 0
    
    async def reset(self):
        """Manually reset the circuit breaker."""
        async with self._lock:
            await self._transition_to_closed()
    
    async def force_open(self):
        """Manually open the circuit breaker."""
        async with self._lock:
            await self._transition_to_open()
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information."""
        return {
            "service_id": self.service_id,
            "endpoint": self.endpoint,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat(),
            "half_open_requests": self.half_open_requests
        }


class CircuitBreakerEngine:
    """Manages circuit breakers for all service endpoints."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._default_config = CircuitBreakerConfig()
        self._lock = asyncio.Lock()
    
    async def register_endpoint(
        self, 
        service_id: str, 
        endpoint: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """Register a new endpoint with circuit breaker."""
        key = f"{service_id}:{endpoint}"
        async with self._lock:
            if key not in self._breakers:
                self._breakers[key] = CircuitBreaker(
                    service_id, 
                    endpoint,
                    config or self._default_config
                )
    
    async def unregister_endpoint(self, service_id: str, endpoint: str):
        """Remove circuit breaker for an endpoint."""
        key = f"{service_id}:{endpoint}"
        async with self._lock:
            if key in self._breakers:
                del self._breakers[key]
    
    async def get_breaker(
        self, 
        service_id: str, 
        endpoint: str
    ) -> Optional[CircuitBreaker]:
        """Get circuit breaker for an endpoint."""
        key = f"{service_id}:{endpoint}"
        async with self._lock:
            return self._breakers.get(key)
    
    async def call_with_breaker(
        self,
        service_id: str,
        endpoint: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute a function through the appropriate circuit breaker."""
        breaker = await self.get_breaker(service_id, endpoint)
        if breaker:
            return await breaker.call(func, *args, **kwargs)
        else:
            # No breaker registered, execute directly
            return await func(*args, **kwargs)
    
    async def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get state information for all circuit breakers."""
        async with self._lock:
            return {
                key: breaker.get_state_info()
                for key, breaker in self._breakers.items()
            }
    
    async def get_open_circuits(self) -> List[str]:
        """Get all endpoints with open circuit breakers."""
        async with self._lock:
            return [
                key for key, breaker in self._breakers.items()
                if breaker.state == CircuitBreakerState.OPEN
            ]
    
    async def reset_all(self):
        """Reset all circuit breakers."""
        async with self._lock:
            for breaker in self._breakers.values():
                await breaker.reset()
    
    async def update_config(
        self,
        service_id: str,
        endpoint: str,
        config: CircuitBreakerConfig
    ):
        """Update configuration for a specific circuit breaker."""
        key = f"{service_id}:{endpoint}"
        async with self._lock:
            if key in self._breakers:
                self._breakers[key].config = config
    
    def get_breaker_count(self) -> int:
        """Get total number of registered circuit breakers."""
        return len(self._breakers)
    
    def get_open_breaker_count(self) -> int:
        """Get number of open circuit breakers."""
        return sum(
            1 for breaker in self._breakers.values()
            if breaker.state == CircuitBreakerState.OPEN
        )