"""Strangler fig pattern planning module."""

import networkx as nx
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from .models import StranglerFigBoundary


class StranglerFigPlanner:
    """Plans strangler fig pattern boundaries based on dependencies."""

    def __init__(self) -> None:
        self.dependency_graph = nx.DiGraph()
        self.module_interfaces: Dict[str, Set[str]] = defaultdict(set)

    def plan_boundaries(
        self,
        dependencies: Dict[str, Set[str]],
        module_metrics: Dict[str, Dict[str, Any]] = None,
    ) -> List[StranglerFigBoundary]:
        """Plan strangler fig boundaries based on module dependencies."""
        self._build_dependency_graph(dependencies)
        self._analyze_interfaces(dependencies)

        # Find strongly connected components (potential boundaries)
        sccs = list(nx.strongly_connected_components(self.dependency_graph))

        # Find community structure (modules that work together)
        communities = self._detect_communities()

        # Generate boundaries
        boundaries = []

        # Create boundaries from strongly connected components
        for idx, scc in enumerate(sccs):
            if len(scc) > 1:  # Only consider non-trivial SCCs
                boundary = self._create_boundary_from_modules(
                    list(scc), f"scc_{idx}", dependencies, module_metrics
                )
                if boundary:
                    boundaries.append(boundary)

        # Create boundaries from communities
        for idx, community in enumerate(communities):
            if len(community) > 1:
                boundary = self._create_boundary_from_modules(
                    list(community), f"community_{idx}", dependencies, module_metrics
                )
                if boundary:
                    boundaries.append(boundary)

        # If no boundaries found, try to create boundaries based on directory structure
        if not boundaries and dependencies:
            boundaries = self._create_boundaries_from_directories(
                dependencies, module_metrics
            )

        # Sort boundaries by recommended order
        boundaries = self._prioritize_boundaries(boundaries)

        return boundaries

    def _build_dependency_graph(self, dependencies: Dict[str, Set[str]]) -> None:
        """Build a directed graph of dependencies."""
        self.dependency_graph.clear()

        for module, deps in dependencies.items():
            self.dependency_graph.add_node(module)
            for dep in deps:
                # Only add dependencies that are in our module set
                if dep in dependencies:
                    self.dependency_graph.add_edge(module, dep)

    def _analyze_interfaces(self, dependencies: Dict[str, Set[str]]) -> None:
        """Analyze module interfaces (what they expose to others)."""
        self.module_interfaces.clear()

        # For each module, find what other modules depend on it
        for module, deps in dependencies.items():
            for dep in deps:
                if dep in dependencies:  # Internal dependency
                    self.module_interfaces[dep].add(module)

    def _detect_communities(self) -> List[Set[str]]:
        """Detect communities of modules that work closely together."""
        # Convert to undirected graph for community detection
        undirected = self.dependency_graph.to_undirected()

        # Use connected components as a simple community detection
        communities = []
        for component in nx.connected_components(undirected):
            if len(component) > 1:
                communities.append(component)

        return communities

    def _create_boundary_from_modules(
        self,
        modules: List[str],
        boundary_name: str,
        dependencies: Dict[str, Set[str]],
        module_metrics: Dict[str, Dict[str, Any]] = None,
    ) -> Optional[StranglerFigBoundary]:
        """Create a strangler fig boundary from a set of modules."""
        if not modules:
            return None

        module_set = set(modules)

        # Find external dependencies
        external_deps = set()
        internal_deps = set()

        for module in modules:
            for dep in dependencies.get(module, set()):
                if dep not in module_set:
                    external_deps.add(dep)
                else:
                    internal_deps.add(dep)

        # Find API surface (modules that are used by external modules)
        api_surface = []
        for module in modules:
            if module in self.module_interfaces:
                external_users = [
                    user
                    for user in self.module_interfaces[module]
                    if user not in module_set
                ]
                if external_users:
                    api_surface.append(module)

        # Calculate isolation score
        total_deps = len(external_deps) + len(internal_deps)
        isolation_score = (
            1.0 - (len(external_deps) / total_deps) if total_deps > 0 else 1.0
        )

        # Estimate effort
        base_effort = len(modules) * 16  # Base hours per module
        dependency_effort = len(external_deps) * 8  # Hours per external dependency
        api_effort = len(api_surface) * 24  # Hours per API surface module

        # Adjust for module complexity if metrics available
        if module_metrics:
            complexity_factor = 0
            for module in modules:
                if module in module_metrics:
                    metrics = module_metrics[module]
                    complexity_factor += metrics.get("complexity", 0) / 50
            base_effort *= 1 + complexity_factor / len(modules)

        estimated_effort = base_effort + dependency_effort + api_effort

        return StranglerFigBoundary(
            boundary_name=boundary_name,
            internal_modules=modules,
            external_dependencies=list(external_deps),
            internal_dependencies=list(internal_deps),
            api_surface=api_surface,
            isolation_score=isolation_score,
            recommended_order=0,  # Will be set later
            estimated_effort_hours=estimated_effort,
        )

    def _prioritize_boundaries(
        self, boundaries: List[StranglerFigBoundary]
    ) -> List[StranglerFigBoundary]:
        """Prioritize boundaries for implementation order."""
        # Sort by isolation score (higher is better) and effort (lower is better)
        scored_boundaries = []

        for boundary in boundaries:
            # Calculate priority score
            # Higher isolation score is better (easier to extract)
            # Lower effort is better (quicker to implement)
            # Fewer external dependencies is better
            priority_score = (
                boundary.isolation_score * 100
                - boundary.estimated_effort_hours / 10
                - len(boundary.external_dependencies) * 5
            )
            scored_boundaries.append((priority_score, boundary))

        # Sort by priority score (descending)
        scored_boundaries.sort(key=lambda x: x[0], reverse=True)

        # Set recommended order
        for idx, (_, boundary) in enumerate(scored_boundaries):
            boundary.recommended_order = idx + 1

        return [boundary for _, boundary in scored_boundaries]

    def _create_boundaries_from_directories(
        self,
        dependencies: Dict[str, Set[str]],
        module_metrics: Dict[str, Dict[str, Any]] = None,
    ) -> List[StranglerFigBoundary]:
        """Create boundaries based on directory structure when no other boundaries found."""
        # Group modules by directory
        dir_modules = defaultdict(list)

        for module in dependencies.keys():
            # Get directory part of the module path
            parts = module.split("/")
            if len(parts) > 1:
                directory = parts[0]
                dir_modules[directory].append(module)
            else:
                dir_modules["root"].append(module)

        boundaries = []
        for idx, (directory, modules) in enumerate(dir_modules.items()):
            if (
                len(modules) > 1
            ):  # Only create boundaries for directories with multiple modules
                boundary = self._create_boundary_from_modules(
                    modules, f"{directory}_component", dependencies, module_metrics
                )
                if boundary:
                    boundaries.append(boundary)

        return boundaries
