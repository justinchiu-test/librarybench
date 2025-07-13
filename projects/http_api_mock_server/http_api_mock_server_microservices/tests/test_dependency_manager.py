"""Tests for Dependency Manager."""

import pytest

from pymockapi.models import ServiceDependency, ServiceGraph, ServiceMetadata
from pymockapi.dependency_manager import DependencyManager


class TestDependencyManager:
    """Test DependencyManager functionality."""
    
    @pytest.fixture
    async def manager(self):
        """Create a dependency manager instance."""
        return DependencyManager()
    
    @pytest.fixture
    def sample_dependency(self):
        """Create a sample dependency."""
        return ServiceDependency(
            from_service="service-a",
            to_service="service-b"
        )
    
    async def test_add_service(self, manager):
        """Test adding a service."""
        await manager.add_service("service-1", {"version": "1.0"})
        
        # Verify service is added
        assert manager.get_service_count() == 1
    
    async def test_remove_service(self, manager):
        """Test removing a service."""
        # Add services and dependencies
        await manager.add_service("service-1")
        await manager.add_service("service-2")
        await manager.add_service("service-3")
        
        dep1 = ServiceDependency(from_service="service-1", to_service="service-2")
        dep2 = ServiceDependency(from_service="service-2", to_service="service-3")
        dep3 = ServiceDependency(from_service="service-1", to_service="service-3")
        
        await manager.add_dependency(dep1)
        await manager.add_dependency(dep2)
        await manager.add_dependency(dep3)
        
        # Remove service-2
        await manager.remove_service("service-2")
        
        # Verify service removed
        assert manager.get_service_count() == 2
        
        # Verify dependencies cleaned up
        service1_deps = await manager.get_dependencies("service-1")
        assert len(service1_deps) == 1  # Only dep to service-3 remains
        assert service1_deps[0].to_service == "service-3"
    
    async def test_add_dependency(self, manager, sample_dependency):
        """Test adding a dependency."""
        await manager.add_dependency(sample_dependency)
        
        # Verify dependency added
        deps = await manager.get_dependencies(sample_dependency.from_service)
        assert len(deps) == 1
        assert deps[0].from_service == sample_dependency.from_service
        assert deps[0].to_service == sample_dependency.to_service
        
        # Verify nodes added
        assert manager.get_service_count() == 2
    
    async def test_remove_dependency(self, manager, sample_dependency):
        """Test removing a dependency."""
        await manager.add_dependency(sample_dependency)
        
        # Remove dependency
        await manager.remove_dependency(
            sample_dependency.from_service,
            sample_dependency.to_service
        )
        
        # Verify dependency removed
        deps = await manager.get_dependencies(sample_dependency.from_service)
        assert len(deps) == 0
        
        # Verify nodes still exist
        assert manager.get_service_count() == 2
    
    async def test_get_dependencies(self, manager):
        """Test getting dependencies for a service."""
        # Add multiple dependencies
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-1", to_service="service-3"),
            ServiceDependency(from_service="service-2", to_service="service-3"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Get dependencies for service-1
        service1_deps = await manager.get_dependencies("service-1")
        assert len(service1_deps) == 2
        assert all(d.from_service == "service-1" for d in service1_deps)
        
        # Get dependencies for service-2
        service2_deps = await manager.get_dependencies("service-2")
        assert len(service2_deps) == 1
        assert service2_deps[0].to_service == "service-3"
    
    async def test_get_dependents(self, manager):
        """Test getting services that depend on a service."""
        # Create dependency graph
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-3"),
            ServiceDependency(from_service="service-2", to_service="service-3"),
            ServiceDependency(from_service="service-3", to_service="service-4"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Get dependents of service-3
        dependents = await manager.get_dependents("service-3")
        assert len(dependents) == 2
        assert set(dependents) == {"service-1", "service-2"}
        
        # Get dependents of service-1 (should be none)
        dependents = await manager.get_dependents("service-1")
        assert len(dependents) == 0
    
    async def test_circular_dependency_detection(self, manager):
        """Test circular dependency detection."""
        # Create non-circular dependencies
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-2", to_service="service-3"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Check no circular dependency
        has_cycle = await manager.has_circular_dependency()
        assert has_cycle is False
        
        # Add circular dependency
        circular_dep = ServiceDependency(from_service="service-3", to_service="service-1")
        await manager.add_dependency(circular_dep)
        
        # Check circular dependency detected
        has_cycle = await manager.has_circular_dependency()
        assert has_cycle is True
    
    async def test_get_circular_dependencies(self, manager):
        """Test getting circular dependencies."""
        # Create multiple circular dependencies
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-2", to_service="service-3"),
            ServiceDependency(from_service="service-3", to_service="service-1"),
            ServiceDependency(from_service="service-3", to_service="service-4"),
            ServiceDependency(from_service="service-4", to_service="service-5"),
            ServiceDependency(from_service="service-5", to_service="service-3"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Get circular dependencies
        cycles = await manager.get_circular_dependencies()
        assert len(cycles) > 0
        
        # Verify we found the expected cycles
        cycle_sets = [set(cycle) for cycle in cycles]
        assert {"service-1", "service-2", "service-3"} in cycle_sets
        assert {"service-3", "service-4", "service-5"} in cycle_sets
    
    async def test_topological_order(self, manager):
        """Test getting topological order."""
        # Create DAG
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-1", to_service="service-3"),
            ServiceDependency(from_service="service-2", to_service="service-4"),
            ServiceDependency(from_service="service-3", to_service="service-4"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Get topological order
        order = await manager.get_topological_order()
        assert order is not None
        assert len(order) == 4
        
        # Verify ordering constraints
        assert order.index("service-1") < order.index("service-2")
        assert order.index("service-1") < order.index("service-3")
        assert order.index("service-2") < order.index("service-4")
        assert order.index("service-3") < order.index("service-4")
    
    async def test_topological_order_with_cycle(self, manager):
        """Test topological order returns None with cycles."""
        # Create cycle
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-2", to_service="service-1"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Get topological order (should be None)
        order = await manager.get_topological_order()
        assert order is None
    
    async def test_get_service_graph(self, manager):
        """Test getting the complete service graph."""
        # Add services with metadata
        service1 = ServiceMetadata(
            service_id="service-1",
            name="Service 1",
            endpoint="/api/v1",
            port=8080
        )
        service2 = ServiceMetadata(
            service_id="service-2",
            name="Service 2",
            endpoint="/api/v2",
            port=8081
        )
        
        await manager.add_service("service-1", {"service_metadata": service1})
        await manager.add_service("service-2", {"service_metadata": service2})
        
        # Add dependency
        dep = ServiceDependency(from_service="service-1", to_service="service-2")
        await manager.add_dependency(dep)
        
        # Get service graph
        graph = await manager.get_service_graph()
        assert len(graph.services) == 2
        assert len(graph.dependencies) == 1
    
    async def test_get_dependency_path(self, manager):
        """Test finding dependency path between services."""
        # Create graph
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-2", to_service="service-3"),
            ServiceDependency(from_service="service-3", to_service="service-4"),
            ServiceDependency(from_service="service-1", to_service="service-5"),
            ServiceDependency(from_service="service-5", to_service="service-4"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Find path
        path = await manager.get_dependency_path("service-1", "service-4")
        assert path is not None
        assert path[0] == "service-1"
        assert path[-1] == "service-4"
        
        # Find non-existent path
        path = await manager.get_dependency_path("service-4", "service-1")
        assert path is None
    
    async def test_get_all_paths(self, manager):
        """Test getting all paths between services."""
        # Create graph with multiple paths
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-2", to_service="service-4"),
            ServiceDependency(from_service="service-1", to_service="service-3"),
            ServiceDependency(from_service="service-3", to_service="service-4"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Get all paths
        paths = await manager.get_all_paths("service-1", "service-4")
        assert len(paths) == 2
        
        # Verify both paths
        path_sets = [set(path) for path in paths]
        assert {"service-1", "service-2", "service-4"} in path_sets
        assert {"service-1", "service-3", "service-4"} in path_sets
    
    async def test_get_isolated_services(self, manager):
        """Test getting isolated services."""
        # Add connected services
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-2", to_service="service-3"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Add isolated services
        await manager.add_service("isolated-1")
        await manager.add_service("isolated-2")
        
        # Get isolated services
        isolated = await manager.get_isolated_services()
        assert len(isolated) == 2
        assert set(isolated) == {"isolated-1", "isolated-2"}
    
    async def test_get_critical_services(self, manager):
        """Test getting critical services."""
        # Create hub-and-spoke pattern
        deps = [
            ServiceDependency(from_service="service-1", to_service="hub"),
            ServiceDependency(from_service="service-2", to_service="hub"),
            ServiceDependency(from_service="service-3", to_service="hub"),
            ServiceDependency(from_service="hub", to_service="service-4"),
            ServiceDependency(from_service="hub", to_service="service-5"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Get critical services
        critical = await manager.get_critical_services()
        assert len(critical) > 0
        assert critical[0][0] == "hub"  # Hub should be most critical
        assert critical[0][1] == 3  # Hub has 3 dependents
    
    async def test_validate_dependencies(self, manager):
        """Test dependency validation."""
        # Create valid dependencies
        deps = [
            ServiceDependency(from_service="service-1", to_service="service-2"),
            ServiceDependency(from_service="service-2", to_service="service-3"),
        ]
        
        for dep in deps:
            await manager.add_dependency(dep)
        
        # Validate (should be no issues)
        issues = await manager.validate_dependencies()
        assert len(issues) == 0
        
        # Add circular dependency
        circular_dep = ServiceDependency(from_service="service-3", to_service="service-1")
        await manager.add_dependency(circular_dep)
        
        # Validate (should find circular dependency)
        issues = await manager.validate_dependencies()
        assert "circular_dependencies" in issues
        assert len(issues["circular_dependencies"]) > 0
    
    def test_get_counts(self, manager):
        """Test getting service and dependency counts."""
        assert manager.get_service_count() == 0
        assert manager.get_dependency_count() == 0