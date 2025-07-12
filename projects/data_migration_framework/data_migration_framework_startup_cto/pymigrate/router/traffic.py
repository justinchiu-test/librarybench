"""Traffic router for gradual microservices migration."""

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from uuid import uuid4
import hashlib

from pymigrate.models.service import (
    RouteConfig,
    TrafficDistribution,
    RoutingStrategy,
)
from pymigrate.models.config import ServiceConfig
from pymigrate.router.health import HealthChecker
from pymigrate.router.rollback import RollbackManager

logger = logging.getLogger(__name__)


class TrafficRouter:
    """Routes traffic between monolith and microservices during migration."""
    
    def __init__(self):
        """Initialize traffic router."""
        self.health_checker = HealthChecker()
        self.rollback_manager = RollbackManager()
        self._routes: Dict[str, RouteConfig] = {}
        self._distributions: List[TrafficDistribution] = []
        self._routing_rules: Dict[str, Callable] = {}
        self._sticky_sessions: Dict[str, str] = {}
        self._feature_flags: Dict[str, bool] = {}
        
    async def add_route(
        self,
        route_config: RouteConfig,
        service_config: ServiceConfig
    ) -> None:
        """Add a new route configuration."""
        logger.info(
            f"Adding route for service {route_config.service_name} "
            f"with {route_config.percentage}% traffic"
        )
        
        # Register service with health checker
        await self.health_checker.register_service(service_config)
        
        # Store route configuration
        self._routes[route_config.service_name] = route_config
        
        # Initialize rollback point
        await self.rollback_manager.create_checkpoint(
            route_config.service_name,
            route_config
        )
        
    async def route_request(
        self,
        request_id: str,
        service_name: str,
        user_id: Optional[str] = None,
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route a request to either monolith or microservice."""
        route_config = self._routes.get(service_name)
        
        if not route_config:
            # No route configured, use monolith
            return {
                "destination": "monolith",
                "service": None,
                "reason": "no_route_configured"
            }
            
        # Check service health
        is_healthy = await self.health_checker.is_healthy(service_name)
        
        if not is_healthy:
            logger.warning(f"Service {service_name} is unhealthy, routing to monolith")
            return {
                "destination": "monolith",
                "service": None,
                "reason": "service_unhealthy"
            }
            
        # Determine routing based on strategy
        destination = await self._determine_destination(
            route_config,
            user_id,
            request_metadata
        )
        
        # Record routing decision
        self._record_routing_decision(
            request_id,
            service_name,
            destination,
            user_id
        )
        
        return destination
        
    async def _determine_destination(
        self,
        route_config: RouteConfig,
        user_id: Optional[str],
        request_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine where to route the request."""
        strategy = route_config.strategy
        
        if strategy == RoutingStrategy.PERCENTAGE:
            return self._percentage_routing(route_config, user_id)
            
        elif strategy == RoutingStrategy.CANARY:
            return self._canary_routing(route_config, user_id)
            
        elif strategy == RoutingStrategy.BLUE_GREEN:
            return self._blue_green_routing(route_config)
            
        elif strategy == RoutingStrategy.FEATURE_FLAG:
            return self._feature_flag_routing(route_config, user_id, request_metadata)
            
        else:
            logger.error(f"Unknown routing strategy: {strategy}")
            return {
                "destination": "monolith",
                "service": None,
                "reason": "unknown_strategy"
            }
            
    def _percentage_routing(
        self,
        route_config: RouteConfig,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Route based on percentage."""
        # Check sticky session
        if route_config.sticky_sessions and user_id:
            existing_destination = self._sticky_sessions.get(user_id)
            if existing_destination:
                return {
                    "destination": existing_destination,
                    "service": route_config.service_name if existing_destination == "microservice" else None,
                    "reason": "sticky_session"
                }
                
        # Random routing based on percentage
        random_value = random.uniform(0, 100)
        
        if random_value < route_config.percentage:
            destination = "microservice"
            service = route_config.service_name
        else:
            destination = "monolith"
            service = None
            
        # Store sticky session
        if route_config.sticky_sessions and user_id:
            self._sticky_sessions[user_id] = destination
            
        return {
            "destination": destination,
            "service": service,
            "reason": "percentage_based"
        }
        
    def _canary_routing(
        self,
        route_config: RouteConfig,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Route canary users to new service."""
        if not user_id:
            return {
                "destination": "monolith",
                "service": None,
                "reason": "no_user_id"
            }
            
        # Use consistent hashing to determine canary users
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        
        # Route percentage of users to canary
        if (user_hash % 100) < route_config.percentage:
            return {
                "destination": "microservice",
                "service": route_config.service_name,
                "reason": "canary_user"
            }
        else:
            return {
                "destination": "monolith",
                "service": None,
                "reason": "non_canary_user"
            }
            
    def _blue_green_routing(
        self,
        route_config: RouteConfig
    ) -> Dict[str, Any]:
        """Route all traffic to either blue or green."""
        # Check which environment is active
        active_env = self._feature_flags.get(f"{route_config.service_name}_active", "blue")
        
        if active_env == "green" and route_config.percentage == 100:
            return {
                "destination": "microservice",
                "service": route_config.service_name,
                "reason": "green_active"
            }
        else:
            return {
                "destination": "monolith",
                "service": None,
                "reason": "blue_active"
            }
            
    def _feature_flag_routing(
        self,
        route_config: RouteConfig,
        user_id: Optional[str],
        request_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Route based on feature flags."""
        # Check global feature flag
        global_flag = route_config.feature_flags.get("enabled", False)
        
        if not global_flag:
            return {
                "destination": "monolith",
                "service": None,
                "reason": "feature_disabled"
            }
            
        # Check user-specific flags
        if user_id and request_metadata:
            user_flags = request_metadata.get("feature_flags", {})
            service_enabled = user_flags.get(route_config.service_name, False)
            
            if service_enabled:
                return {
                    "destination": "microservice",
                    "service": route_config.service_name,
                    "reason": "feature_enabled_for_user"
                }
                
        return {
            "destination": "monolith",
            "service": None,
            "reason": "feature_not_enabled_for_user"
        }
        
    def _record_routing_decision(
        self,
        request_id: str,
        service_name: str,
        destination: Dict[str, Any],
        user_id: Optional[str]
    ) -> None:
        """Record routing decision for monitoring."""
        # In a real implementation, this would write to metrics system
        logger.debug(
            f"Request {request_id} for user {user_id} routed to "
            f"{destination['destination']} (reason: {destination['reason']})"
        )
        
    async def update_traffic_percentage(
        self,
        service_name: str,
        new_percentage: float,
        gradual: bool = True,
        step_size: float = 5.0,
        interval_seconds: int = 300
    ) -> None:
        """Update traffic percentage for a service."""
        route_config = self._routes.get(service_name)
        
        if not route_config:
            raise ValueError(f"No route configured for service {service_name}")
            
        current_percentage = route_config.percentage
        
        if gradual:
            # Gradually increase/decrease traffic
            await self._gradual_traffic_shift(
                service_name,
                current_percentage,
                new_percentage,
                step_size,
                interval_seconds
            )
        else:
            # Immediate traffic shift
            route_config.percentage = new_percentage
            logger.info(
                f"Updated traffic for {service_name} from "
                f"{current_percentage}% to {new_percentage}%"
            )
            
    async def _gradual_traffic_shift(
        self,
        service_name: str,
        current: float,
        target: float,
        step_size: float,
        interval_seconds: int
    ) -> None:
        """Gradually shift traffic percentage."""
        route_config = self._routes[service_name]
        
        if current < target:
            # Increasing traffic
            while route_config.percentage < target:
                # Check health before increasing
                is_healthy = await self.health_checker.is_healthy(service_name)
                
                if not is_healthy:
                    logger.warning(
                        f"Service {service_name} unhealthy, stopping traffic increase"
                    )
                    break
                    
                new_percentage = min(
                    route_config.percentage + step_size,
                    target
                )
                route_config.percentage = new_percentage
                
                logger.info(
                    f"Increased traffic for {service_name} to {new_percentage}%"
                )
                
                # Record distribution
                await self._record_distribution()
                
                if new_percentage < target:
                    await asyncio.sleep(interval_seconds)
                    
        else:
            # Decreasing traffic
            while route_config.percentage > target:
                new_percentage = max(
                    route_config.percentage - step_size,
                    target
                )
                route_config.percentage = new_percentage
                
                logger.info(
                    f"Decreased traffic for {service_name} to {new_percentage}%"
                )
                
                # Record distribution
                await self._record_distribution()
                
                if new_percentage > target:
                    await asyncio.sleep(interval_seconds)
                    
    async def rollback_service(
        self,
        service_name: str,
        checkpoint_id: Optional[str] = None
    ) -> None:
        """Rollback traffic for a service."""
        logger.warning(f"Initiating rollback for service {service_name}")
        
        # Get rollback configuration
        rollback_config = await self.rollback_manager.get_rollback_config(
            service_name,
            checkpoint_id
        )
        
        if rollback_config:
            # Apply rollback configuration
            self._routes[service_name] = rollback_config
            
            # Clear sticky sessions for this service
            self._clear_sticky_sessions(service_name)
            
            logger.info(f"Rollback completed for service {service_name}")
        else:
            # No checkpoint, route all traffic to monolith
            if service_name in self._routes:
                self._routes[service_name].percentage = 0
                
            logger.info(f"Routed all traffic to monolith for {service_name}")
            
    def _clear_sticky_sessions(self, service_name: str) -> None:
        """Clear sticky sessions for a service."""
        # Remove sessions routing to this microservice
        to_remove = []
        for user_id, destination in self._sticky_sessions.items():
            if destination == "microservice":
                # In a real implementation, check if this session
                # belongs to the specific service
                to_remove.append(user_id)
                
        for user_id in to_remove:
            del self._sticky_sessions[user_id]
            
    async def _record_distribution(self) -> None:
        """Record current traffic distribution."""
        distributions = {}
        total_percentage = 0
        
        for service_name, route_config in self._routes.items():
            distributions[service_name] = route_config.percentage
            total_percentage += route_config.percentage
            
        # Calculate monolith percentage
        monolith_percentage = max(0, 100 - total_percentage)
        distributions["monolith"] = monolith_percentage
        
        # Create distribution record
        distribution = TrafficDistribution(
            timestamp=datetime.utcnow(),
            distributions=distributions,
            total_requests=0,  # Would be populated from metrics
            success_rate=100.0,  # Would be calculated from metrics
            average_latency_ms=0,  # Would be calculated from metrics
            error_counts={},
            active_routes=list(self._routes.values())
        )
        
        self._distributions.append(distribution)
        
    def get_current_distribution(self) -> TrafficDistribution:
        """Get current traffic distribution."""
        if self._distributions:
            return self._distributions[-1]
            
        # Create current distribution
        distributions = {}
        for service_name, route_config in self._routes.items():
            distributions[service_name] = route_config.percentage
            
        return TrafficDistribution(
            timestamp=datetime.utcnow(),
            distributions=distributions,
            total_requests=0,
            success_rate=100.0,
            average_latency_ms=0,
            error_counts={},
            active_routes=list(self._routes.values())
        )
        
    def get_routing_metrics(self) -> Dict[str, Any]:
        """Get routing metrics."""
        current_dist = self.get_current_distribution()
        
        return {
            "current_distribution": current_dist.distributions,
            "active_services": list(self._routes.keys()),
            "total_routes": len(self._routes),
            "sticky_sessions": len(self._sticky_sessions),
            "health_status": {
                service: self.health_checker.get_service_status(service)
                for service in self._routes.keys()
            }
        }
        
    async def enable_auto_scaling(
        self,
        service_name: str,
        min_percentage: float = 10.0,
        max_percentage: float = 90.0,
        scale_up_threshold: float = 0.95,
        scale_down_threshold: float = 0.7
    ) -> None:
        """Enable auto-scaling based on service health metrics."""
        # In a real implementation, this would monitor service metrics
        # and automatically adjust traffic percentage
        logger.info(
            f"Auto-scaling enabled for {service_name} "
            f"(range: {min_percentage}% - {max_percentage}%)"
        )