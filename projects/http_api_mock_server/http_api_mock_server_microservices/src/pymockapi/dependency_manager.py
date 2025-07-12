"""Service Dependency Manager for managing service relationships."""

import asyncio
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

from .models import ServiceDependency, ServiceGraph, ServiceMetadata


class DependencyManager:
    """Manages service dependencies and provides graph operations."""
    
    def __init__(self):
        self._graph = nx.DiGraph()
        self._dependencies: Dict[str, List[ServiceDependency]] = {}
        self._lock = asyncio.Lock()
    
    async def add_service(self, service_id: str, metadata: Optional[Dict] = None):
        """Add a service node to the dependency graph."""
        async with self._lock:
            self._graph.add_node(service_id, **(metadata or {}))
            if service_id not in self._dependencies:
                self._dependencies[service_id] = []
    
    async def remove_service(self, service_id: str):
        """Remove a service and all its dependencies."""
        async with self._lock:
            if service_id in self._graph:
                self._graph.remove_node(service_id)
            if service_id in self._dependencies:
                del self._dependencies[service_id]
            # Remove from other services' dependencies
            for deps in self._dependencies.values():
                deps[:] = [d for d in deps if d.to_service != service_id]
    
    async def add_dependency(self, dependency: ServiceDependency):
        """Add a dependency between services."""
        async with self._lock:
            # Ensure both services exist
            if dependency.from_service not in self._graph:
                self._graph.add_node(dependency.from_service)
            if dependency.to_service not in self._graph:
                self._graph.add_node(dependency.to_service)
            
            # Add edge with dependency metadata
            self._graph.add_edge(
                dependency.from_service,
                dependency.to_service,
                dependency=dependency
            )
            
            # Store in dependencies dict
            if dependency.from_service not in self._dependencies:
                self._dependencies[dependency.from_service] = []
            self._dependencies[dependency.from_service].append(dependency)
    
    async def remove_dependency(self, from_service: str, to_service: str):
        """Remove a dependency between services."""
        async with self._lock:
            if self._graph.has_edge(from_service, to_service):
                self._graph.remove_edge(from_service, to_service)
            
            if from_service in self._dependencies:
                self._dependencies[from_service] = [
                    d for d in self._dependencies[from_service]
                    if d.to_service != to_service
                ]
    
    async def get_dependencies(self, service_id: str) -> List[ServiceDependency]:
        """Get all dependencies of a service."""
        async with self._lock:
            return list(self._dependencies.get(service_id, []))
    
    async def get_dependents(self, service_id: str) -> List[str]:
        """Get all services that depend on the given service."""
        async with self._lock:
            if service_id not in self._graph:
                return []
            return list(self._graph.predecessors(service_id))
    
    async def has_circular_dependency(self) -> bool:
        """Check if the dependency graph has cycles."""
        async with self._lock:
            return not nx.is_directed_acyclic_graph(self._graph)
    
    async def get_circular_dependencies(self) -> List[List[str]]:
        """Get all circular dependencies in the graph."""
        async with self._lock:
            try:
                cycles = list(nx.simple_cycles(self._graph))
                return cycles
            except nx.NetworkXNoCycle:
                return []
    
    async def get_topological_order(self) -> Optional[List[str]]:
        """Get topological ordering of services (None if cycles exist)."""
        async with self._lock:
            try:
                return list(nx.topological_sort(self._graph))
            except nx.NetworkXUnfeasible:
                return None
    
    async def get_service_graph(self) -> ServiceGraph:
        """Get the complete service graph representation."""
        async with self._lock:
            services = []
            dependencies = []
            
            for node in self._graph.nodes():
                metadata = self._graph.nodes[node]
                if 'service_metadata' in metadata:
                    services.append(metadata['service_metadata'])
            
            for from_service, to_service, data in self._graph.edges(data=True):
                if 'dependency' in data:
                    dependencies.append(data['dependency'])
            
            return ServiceGraph(services=services, dependencies=dependencies)
    
    async def get_dependency_path(
        self, 
        from_service: str, 
        to_service: str
    ) -> Optional[List[str]]:
        """Find a dependency path between two services."""
        async with self._lock:
            try:
                path = nx.shortest_path(self._graph, from_service, to_service)
                return path
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                return None
    
    async def get_all_paths(
        self, 
        from_service: str, 
        to_service: str
    ) -> List[List[str]]:
        """Get all possible paths between two services."""
        async with self._lock:
            try:
                paths = list(nx.all_simple_paths(self._graph, from_service, to_service))
                return paths
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                return []
    
    async def get_isolated_services(self) -> List[str]:
        """Get services with no dependencies or dependents."""
        async with self._lock:
            isolated = []
            for node in self._graph.nodes():
                if (self._graph.in_degree(node) == 0 and 
                    self._graph.out_degree(node) == 0):
                    isolated.append(node)
            return isolated
    
    async def get_critical_services(self) -> List[Tuple[str, int]]:
        """Get services that many others depend on (sorted by dependents)."""
        async with self._lock:
            critical = []
            for node in self._graph.nodes():
                in_degree = self._graph.in_degree(node)
                if in_degree > 0:
                    critical.append((node, in_degree))
            critical.sort(key=lambda x: x[1], reverse=True)
            return critical
    
    async def validate_dependencies(self) -> Dict[str, List[str]]:
        """Validate the dependency graph and return issues."""
        issues = {}
        
        # Check for cycles (get_circular_dependencies handles its own locking)
        cycles = await self.get_circular_dependencies()
        if cycles:
            issues['circular_dependencies'] = [
                ' -> '.join(cycle + [cycle[0]]) for cycle in cycles
            ]
        
        # Check for missing services
        async with self._lock:
            missing_services = []
            for from_service, to_service in self._graph.edges():
                if from_service not in self._graph:
                    missing_services.append(from_service)
                if to_service not in self._graph:
                    missing_services.append(to_service)
            
            if missing_services:
                issues['missing_services'] = list(set(missing_services))
        
        return issues
    
    def get_service_count(self) -> int:
        """Get the total number of services in the graph."""
        return self._graph.number_of_nodes()
    
    def get_dependency_count(self) -> int:
        """Get the total number of dependencies."""
        return self._graph.number_of_edges()