"""Tests for Service Registry."""

import asyncio
import pytest
from datetime import datetime, timedelta, timezone

from pymockapi.models import ServiceMetadata, ServiceStatus
from pymockapi.service_registry import ServiceRegistry


class TestServiceRegistry:
    """Test ServiceRegistry functionality."""
    
    @pytest.fixture
    async def registry(self):
        """Create a service registry instance."""
        registry = ServiceRegistry(health_check_interval=1)
        yield registry
        await registry.stop_health_checks()
    
    @pytest.fixture
    def sample_service(self):
        """Create a sample service."""
        return ServiceMetadata(
            service_id="test-service",
            name="Test Service",
            endpoint="/api/test",
            port=8080
        )
    
    async def test_register_service(self, registry, sample_service):
        """Test registering a service."""
        result = await registry.register_service(sample_service)
        assert result is True
        
        # Verify service is registered
        service = await registry.get_service(sample_service.service_id)
        assert service is not None
        assert service.service_id == sample_service.service_id
        assert service.name == sample_service.name
    
    async def test_register_duplicate_service(self, registry, sample_service):
        """Test registering duplicate service updates existing."""
        await registry.register_service(sample_service)
        
        # Update service
        updated_service = ServiceMetadata(
            service_id=sample_service.service_id,
            name="Updated Service",
            endpoint="/api/test",
            port=8081
        )
        
        result = await registry.register_service(updated_service)
        assert result is True
        
        # Verify update
        service = await registry.get_service(sample_service.service_id)
        assert service.name == "Updated Service"
        assert service.port == 8081
    
    async def test_deregister_service(self, registry, sample_service):
        """Test deregistering a service."""
        await registry.register_service(sample_service)
        
        result = await registry.deregister_service(sample_service.service_id)
        assert result is True
        
        # Verify service is removed
        service = await registry.get_service(sample_service.service_id)
        assert service is None
    
    async def test_deregister_nonexistent_service(self, registry):
        """Test deregistering a non-existent service."""
        result = await registry.deregister_service("non-existent")
        assert result is False
    
    async def test_get_services_by_name(self, registry):
        """Test getting services by name."""
        # Register multiple services with same name
        services = []
        for i in range(3):
            service = ServiceMetadata(
                service_id=f"service-{i}",
                name="common-service",
                endpoint=f"/api/v{i}",
                port=8080 + i
            )
            services.append(service)
            await registry.register_service(service)
        
        # Register service with different name
        other_service = ServiceMetadata(
            service_id="other-service",
            name="different-service",
            endpoint="/api/other",
            port=9000
        )
        await registry.register_service(other_service)
        
        # Get services by name
        found_services = await registry.get_services_by_name("common-service")
        assert len(found_services) == 3
        assert all(s.name == "common-service" for s in found_services)
    
    async def test_get_services_by_tag(self, registry):
        """Test getting services by tag."""
        # Register services with tags
        service1 = ServiceMetadata(
            service_id="service-1",
            name="service-1",
            endpoint="/api/v1",
            port=8080,
            tags=["production", "api"]
        )
        service2 = ServiceMetadata(
            service_id="service-2",
            name="service-2",
            endpoint="/api/v2",
            port=8081,
            tags=["development", "api"]
        )
        service3 = ServiceMetadata(
            service_id="service-3",
            name="service-3",
            endpoint="/api/v3",
            port=8082,
            tags=["production", "backend"]
        )
        
        await registry.register_service(service1)
        await registry.register_service(service2)
        await registry.register_service(service3)
        
        # Get services by tag
        api_services = await registry.get_services_by_tag("api")
        assert len(api_services) == 2
        assert all("api" in s.tags for s in api_services)
        
        production_services = await registry.get_services_by_tag("production")
        assert len(production_services) == 2
        assert all("production" in s.tags for s in production_services)
    
    async def test_get_healthy_services(self, registry):
        """Test getting healthy services."""
        # Register services with different statuses
        healthy_service = ServiceMetadata(
            service_id="healthy",
            name="healthy-service",
            endpoint="/api/healthy",
            port=8080,
            status=ServiceStatus.HEALTHY
        )
        unhealthy_service = ServiceMetadata(
            service_id="unhealthy",
            name="unhealthy-service",
            endpoint="/api/unhealthy",
            port=8081,
            status=ServiceStatus.UNHEALTHY
        )
        degraded_service = ServiceMetadata(
            service_id="degraded",
            name="degraded-service",
            endpoint="/api/degraded",
            port=8082,
            status=ServiceStatus.DEGRADED
        )
        
        await registry.register_service(healthy_service)
        await registry.register_service(unhealthy_service)
        await registry.register_service(degraded_service)
        
        # Get healthy services
        healthy_services = await registry.get_healthy_services()
        assert len(healthy_services) == 1
        assert healthy_services[0].service_id == "healthy"
    
    async def test_update_service_status(self, registry, sample_service):
        """Test updating service status."""
        await registry.register_service(sample_service)
        
        # Update status
        result = await registry.update_service_status(
            sample_service.service_id,
            ServiceStatus.DEGRADED
        )
        assert result is True
        
        # Verify update
        service = await registry.get_service(sample_service.service_id)
        assert service.status == ServiceStatus.DEGRADED
    
    async def test_update_nonexistent_service_status(self, registry):
        """Test updating status of non-existent service."""
        result = await registry.update_service_status(
            "non-existent",
            ServiceStatus.HEALTHY
        )
        assert result is False
    
    async def test_heartbeat(self, registry, sample_service):
        """Test service heartbeat."""
        await registry.register_service(sample_service)
        
        # Get initial heartbeat time
        service = await registry.get_service(sample_service.service_id)
        initial_heartbeat = service.last_heartbeat
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Send heartbeat
        result = await registry.heartbeat(sample_service.service_id)
        assert result is True
        
        # Verify heartbeat updated
        service = await registry.get_service(sample_service.service_id)
        assert service.last_heartbeat > initial_heartbeat
    
    async def test_heartbeat_nonexistent_service(self, registry):
        """Test heartbeat for non-existent service."""
        result = await registry.heartbeat("non-existent")
        assert result is False
    
    async def test_health_check_marks_unhealthy(self, registry, sample_service):
        """Test health check marks services unhealthy when heartbeat is old."""
        # Register service with old heartbeat
        sample_service.last_heartbeat = datetime.now(timezone.utc) - timedelta(minutes=5)
        await registry.register_service(sample_service)
        
        # Start health checks
        await registry.start_health_checks()
        
        # Wait for health check to run
        await asyncio.sleep(1.5)
        
        # Verify service marked unhealthy
        service = await registry.get_service(sample_service.service_id)
        assert service.status == ServiceStatus.UNHEALTHY
    
    async def test_health_check_restores_healthy(self, registry, sample_service):
        """Test health check restores healthy status after heartbeat."""
        # Register unhealthy service
        sample_service.status = ServiceStatus.UNHEALTHY
        await registry.register_service(sample_service)
        
        # Start health checks
        await registry.start_health_checks()
        
        # Send heartbeat
        await registry.heartbeat(sample_service.service_id)
        
        # Wait for health check to run
        await asyncio.sleep(1.5)
        
        # Verify service restored to healthy
        service = await registry.get_service(sample_service.service_id)
        assert service.status == ServiceStatus.HEALTHY
    
    async def test_get_all_services(self, registry):
        """Test getting all services."""
        # Register multiple services
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
        
        # Get all services
        all_services = await registry.get_all_services()
        assert len(all_services) == 5
        
        # Verify all services present
        service_ids = {s.service_id for s in all_services}
        expected_ids = {f"service-{i}" for i in range(5)}
        assert service_ids == expected_ids
    
    def test_service_count(self, registry):
        """Test service count."""
        assert registry.get_service_count() == 0
        
        # Note: This is a sync method accessing internal state
        # In a real scenario, we'd make this async or ensure thread safety
    
    def test_healthy_service_count(self, registry):
        """Test healthy service count."""
        assert registry.get_healthy_service_count() == 0
        
        # Note: This is a sync method accessing internal state
        # In a real scenario, we'd make this async or ensure thread safety
    
    async def test_concurrent_operations(self, registry):
        """Test concurrent service operations."""
        # Register services concurrently
        async def register_service(i):
            service = ServiceMetadata(
                service_id=f"service-{i}",
                name=f"service-{i}",
                endpoint=f"/api/v{i}",
                port=8080 + i
            )
            await registry.register_service(service)
        
        # Register 10 services concurrently
        await asyncio.gather(*[register_service(i) for i in range(10)])
        
        # Verify all registered
        all_services = await registry.get_all_services()
        assert len(all_services) == 10
        
        # Update statuses concurrently
        async def update_status(i):
            await registry.update_service_status(
                f"service-{i}",
                ServiceStatus.DEGRADED if i % 2 == 0 else ServiceStatus.HEALTHY
            )
        
        await asyncio.gather(*[update_status(i) for i in range(10)])
        
        # Verify updates
        healthy_services = await registry.get_healthy_services()
        assert len(healthy_services) == 5  # Only odd-numbered services