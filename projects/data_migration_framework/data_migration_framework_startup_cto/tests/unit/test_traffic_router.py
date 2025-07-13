"""Unit tests for Traffic Router."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import random

from pymigrate.router.traffic import TrafficRouter
from pymigrate.models.service import RouteConfig, RoutingStrategy
from pymigrate.models.config import ServiceConfig


class TestTrafficRouter:
    """Test cases for Traffic Router."""
    
    @pytest.mark.asyncio
    async def test_router_initialization(self):
        """Test traffic router initialization."""
        router = TrafficRouter()
        
        assert router._routes == {}
        assert router._distributions == []
        assert router._sticky_sessions == {}
        assert router._feature_flags == {}
        
    @pytest.mark.asyncio
    async def test_add_route(self, service_config):
        """Test adding a route configuration."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=25.0,
            sticky_sessions=True,
        )
        
        with patch.object(router.health_checker, 'register_service', new_callable=AsyncMock):
            await router.add_route(route_config, service_config)
            
            assert "user_service" in router._routes
            assert router._routes["user_service"] == route_config
            
    @pytest.mark.asyncio
    async def test_route_request_no_config(self):
        """Test routing when no configuration exists."""
        router = TrafficRouter()
        
        result = await router.route_request(
            request_id="req_123",
            service_name="unknown_service"
        )
        
        assert result["destination"] == "monolith"
        assert result["service"] is None
        assert result["reason"] == "no_route_configured"
        
    @pytest.mark.asyncio
    async def test_route_request_unhealthy_service(self, service_config):
        """Test routing when service is unhealthy."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=100.0,  # All traffic should go to service
        )
        
        await router.add_route(route_config, service_config)
        
        # Mock unhealthy service
        with patch.object(router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = False
            
            result = await router.route_request(
                request_id="req_123",
                service_name="user_service"
            )
            
            assert result["destination"] == "monolith"
            assert result["reason"] == "service_unhealthy"
            
    @pytest.mark.asyncio
    async def test_percentage_routing(self, service_config):
        """Test percentage-based routing."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=30.0,  # 30% to microservice
            sticky_sessions=False,
        )
        
        await router.add_route(route_config, service_config)
        
        # Mock healthy service
        with patch.object(router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            # Test multiple requests to verify distribution
            destinations = []
            for i in range(100):
                # Mock random to control routing
                with patch('random.uniform') as mock_random:
                    mock_random.return_value = 25.0 if i < 30 else 75.0
                    
                    result = await router.route_request(
                        request_id=f"req_{i}",
                        service_name="user_service"
                    )
                    destinations.append(result["destination"])
                    
            # Verify approximately 30% went to microservice
            microservice_count = destinations.count("microservice")
            assert microservice_count == 30
            
    @pytest.mark.asyncio
    async def test_sticky_sessions(self, service_config):
        """Test sticky session routing."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=50.0,
            sticky_sessions=True,
        )
        
        await router.add_route(route_config, service_config)
        
        with patch.object(router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            # First request for user
            with patch('random.uniform') as mock_random:
                mock_random.return_value = 25.0  # Should go to microservice
                
                result1 = await router.route_request(
                    request_id="req_1",
                    service_name="user_service",
                    user_id="user_123"
                )
                
            # Second request for same user
            result2 = await router.route_request(
                request_id="req_2",
                service_name="user_service",
                user_id="user_123"
            )
            
            # Should stick to same destination
            assert result1["destination"] == result2["destination"]
            assert result2["reason"] == "sticky_session"
            
    @pytest.mark.asyncio
    async def test_canary_routing(self, service_config):
        """Test canary deployment routing."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.CANARY,
            percentage=10.0,  # 10% canary users
        )
        
        await router.add_route(route_config, service_config)
        
        with patch.object(router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            # Test with multiple users
            canary_users = 0
            for i in range(100):
                result = await router.route_request(
                    request_id=f"req_{i}",
                    service_name="user_service",
                    user_id=f"user_{i}"
                )
                
                if result["destination"] == "microservice":
                    canary_users += 1
                    
            # Should be approximately 10% (with some variance due to hashing)
            assert 5 <= canary_users <= 15
            
    @pytest.mark.asyncio
    async def test_blue_green_routing(self, service_config):
        """Test blue-green deployment routing."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.BLUE_GREEN,
            percentage=100.0,
        )
        
        await router.add_route(route_config, service_config)
        
        with patch.object(router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            # Test blue environment (default)
            result_blue = await router.route_request(
                request_id="req_1",
                service_name="user_service"
            )
            assert result_blue["destination"] == "monolith"
            assert result_blue["reason"] == "blue_active"
            
            # Switch to green environment
            router._feature_flags["user_service_active"] = "green"
            
            result_green = await router.route_request(
                request_id="req_2",
                service_name="user_service"
            )
            assert result_green["destination"] == "microservice"
            assert result_green["reason"] == "green_active"
            
    @pytest.mark.asyncio
    async def test_feature_flag_routing(self, service_config):
        """Test feature flag based routing."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.FEATURE_FLAG,
            percentage=0.0,
            feature_flags={"enabled": True},
        )
        
        await router.add_route(route_config, service_config)
        
        with patch.object(router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            # Test with feature enabled for specific user
            request_metadata = {
                "feature_flags": {"user_service": True}
            }
            
            result = await router.route_request(
                request_id="req_1",
                service_name="user_service",
                user_id="user_123",
                request_metadata=request_metadata
            )
            
            assert result["destination"] == "microservice"
            assert result["reason"] == "feature_enabled_for_user"
            
    @pytest.mark.asyncio
    async def test_gradual_traffic_increase(self, service_config):
        """Test gradual traffic percentage increase."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=10.0,
        )
        
        await router.add_route(route_config, service_config)
        
        with patch.object(router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                await router.update_traffic_percentage(
                    "user_service",
                    new_percentage=30.0,
                    gradual=True,
                    step_size=10.0,
                    interval_seconds=1
                )
                
                # Should reach target percentage
                assert router._routes["user_service"].percentage == 30.0
                
    @pytest.mark.asyncio
    async def test_traffic_rollback(self, service_config):
        """Test traffic rollback functionality."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=50.0,
            sticky_sessions=True,
        )
        
        await router.add_route(route_config, service_config)
        
        # Add some sticky sessions
        router._sticky_sessions["user_1"] = "microservice"
        router._sticky_sessions["user_2"] = "microservice"
        
        with patch.object(router.rollback_manager, 'get_rollback_config', new_callable=AsyncMock) as mock_rollback:
            # Rollback to 0%
            rollback_config = RouteConfig(
                service_name="user_service",
                strategy=RoutingStrategy.PERCENTAGE,
                percentage=0.0,
            )
            mock_rollback.return_value = rollback_config
            
            await router.rollback_service("user_service")
            
            # Traffic should be rolled back
            assert router._routes["user_service"].percentage == 0.0
            
            # Sticky sessions should be cleared
            assert len([s for s in router._sticky_sessions.values() if s == "microservice"]) == 0
            
    @pytest.mark.asyncio
    async def test_routing_metrics(self, service_config):
        """Test routing metrics collection."""
        router = TrafficRouter()
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=25.0,
        )
        
        await router.add_route(route_config, service_config)
        
        with patch.object(router.health_checker, 'get_service_status') as mock_status:
            mock_status.return_value = {"healthy": True}
            
            metrics = router.get_routing_metrics()
            
            assert "user_service" in metrics["active_services"]
            assert metrics["total_routes"] == 1
            assert "current_distribution" in metrics
            assert "health_status" in metrics
            
    def test_current_distribution(self):
        """Test getting current traffic distribution."""
        router = TrafficRouter()
        
        # Add multiple routes
        router._routes = {
            "user_service": RouteConfig(
                service_name="user_service",
                strategy=RoutingStrategy.PERCENTAGE,
                percentage=30.0,
            ),
            "order_service": RouteConfig(
                service_name="order_service",
                strategy=RoutingStrategy.PERCENTAGE,
                percentage=20.0,
            ),
        }
        
        distribution = router.get_current_distribution()
        
        assert distribution.distributions["user_service"] == 30.0
        assert distribution.distributions["order_service"] == 20.0
        assert len(distribution.active_routes) == 2