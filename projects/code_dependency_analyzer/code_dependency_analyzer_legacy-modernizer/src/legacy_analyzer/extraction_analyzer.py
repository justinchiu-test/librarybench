"""Module extraction feasibility analyzer."""

import networkx as nx
from typing import Any, Dict, List, Set

from .models import ExtractionFeasibility, LegacyPattern, DatabaseCoupling


class ExtractionAnalyzer:
    """Analyzes the feasibility of extracting modules from a legacy system."""

    def __init__(self) -> None:
        self.dependency_graph = nx.DiGraph()

    def analyze_extraction_feasibility(
        self,
        module_path: str,
        dependencies: Dict[str, Set[str]],
        patterns: List[LegacyPattern],
        database_couplings: List[DatabaseCoupling],
        module_metrics: Dict[str, Dict[str, Any]] = None,
    ) -> ExtractionFeasibility:
        """Analyze how feasible it is to extract a specific module."""
        # Build dependency graph
        self._build_dependency_graph(dependencies)

        # Find dependencies that need to be broken
        deps_to_break = self._find_dependencies_to_break(module_path, dependencies)

        # Identify backward compatibility requirements
        backward_compat = self._identify_backward_compatibility(
            module_path, dependencies
        )

        # Identify risks
        risks = self._identify_risks(
            module_path, patterns, database_couplings, deps_to_break
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            module_path, deps_to_break, risks, module_metrics
        )

        # Calculate feasibility score
        feasibility_score = self._calculate_feasibility_score(
            module_path, deps_to_break, risks, patterns, database_couplings
        )

        # Estimate effort
        effort_hours = self._estimate_effort(
            module_path, deps_to_break, risks, module_metrics
        )

        return ExtractionFeasibility(
            module_path=module_path,
            feasibility_score=feasibility_score,
            dependencies_to_break=deps_to_break,
            backward_compatibility_requirements=backward_compat,
            estimated_effort_hours=effort_hours,
            risks=risks,
            recommendations=recommendations,
        )

    def analyze_multiple_modules(
        self,
        module_paths: List[str],
        dependencies: Dict[str, Set[str]],
        patterns: List[LegacyPattern],
        database_couplings: List[DatabaseCoupling],
        module_metrics: Dict[str, Dict[str, Any]] = None,
    ) -> List[ExtractionFeasibility]:
        """Analyze extraction feasibility for multiple modules."""
        results = []

        for module_path in module_paths:
            # Check if module exists in dependencies or module_metrics
            if module_path in dependencies or (
                module_metrics and module_path in module_metrics
            ):
                feasibility = self.analyze_extraction_feasibility(
                    module_path,
                    dependencies,
                    patterns,
                    database_couplings,
                    module_metrics,
                )
                results.append(feasibility)

        # Sort by feasibility score (highest first)
        results.sort(key=lambda x: x.feasibility_score, reverse=True)

        return results

    def _build_dependency_graph(self, dependencies: Dict[str, Set[str]]) -> None:
        """Build a directed graph of dependencies."""
        self.dependency_graph.clear()

        for module, deps in dependencies.items():
            self.dependency_graph.add_node(module)
            for dep in deps:
                if dep in dependencies:  # Only internal dependencies
                    self.dependency_graph.add_edge(module, dep)

    def _find_dependencies_to_break(
        self, module_path: str, dependencies: Dict[str, Set[str]]
    ) -> List[str]:
        """Find dependencies that need to be broken for extraction."""
        deps_to_break = []

        # Find circular dependencies involving this module
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            for cycle in cycles:
                if module_path in cycle:
                    # Add edges that would break the cycle
                    for i in range(len(cycle)):
                        if cycle[i] == module_path:
                            next_module = cycle[(i + 1) % len(cycle)]
                            deps_to_break.append(f"{module_path} -> {next_module}")
        except Exception:
            pass

        # Find tight couplings (bidirectional dependencies)
        module_deps = dependencies.get(module_path, set())
        for dep in module_deps:
            if dep in dependencies and module_path in dependencies[dep]:
                deps_to_break.append(f"{module_path} <-> {dep}")

        # Also check for any dependencies that create coupling
        # For auth modules, database and external service dependencies should be broken
        for dep in module_deps:
            if any(
                keyword in dep
                for keyword in ["database", "cache", "messaging", "config"]
            ):
                deps_to_break.append(f"{module_path} -> {dep}")

        return list(set(deps_to_break))  # Remove duplicates

    def _identify_backward_compatibility(
        self, module_path: str, dependencies: Dict[str, Set[str]]
    ) -> List[str]:
        """Identify backward compatibility requirements."""
        requirements = []

        # Find modules that depend on this module
        dependent_modules = []
        for module, deps in dependencies.items():
            if module_path in deps and module != module_path:
                dependent_modules.append(module)

        if dependent_modules:
            requirements.append(
                f"Maintain API compatibility for {len(dependent_modules)} dependent modules"
            )

        # Check if module is used as a library
        if module_path.endswith(("__init__.py", "api.py", "interface.py")):
            requirements.append("Preserve public API surface")

        # Check for common patterns that indicate public interfaces
        if any(
            keyword in module_path
            for keyword in ["service", "handler", "controller", "auth"]
        ):
            requirements.append("Maintain service interface compatibility")

        # For auth modules specifically
        if "auth" in module_path.lower():
            requirements.append("Preserve authentication API for existing clients")
            requirements.append("Maintain session management compatibility")

        return requirements

    def _identify_risks(
        self,
        module_path: str,
        patterns: List[LegacyPattern],
        database_couplings: List[DatabaseCoupling],
        deps_to_break: List[str],
    ) -> List[str]:
        """Identify risks associated with extracting this module."""
        risks = []

        # Check for legacy patterns affecting this module
        for pattern in patterns:
            if module_path in pattern.affected_files:
                if pattern.risk.value in ["high", "critical"]:
                    risks.append(f"{pattern.pattern_type.value}: {pattern.description}")

        # Check for database coupling
        for coupling in database_couplings:
            if module_path in coupling.coupled_modules:
                risks.append(
                    f"Database coupling with {len(coupling.coupled_modules) - 1} other modules"
                )
                if coupling.raw_sql_queries:
                    risks.append(
                        f"Contains {len(coupling.raw_sql_queries)} raw SQL queries"
                    )

        # Risk from breaking dependencies
        if len(deps_to_break) > 5:
            risks.append(f"Need to break {len(deps_to_break)} dependencies")

        # Check for test coverage (simplified check)
        if not any(
            test_indicator in module_path for test_indicator in ["test", "spec"]
        ):
            risks.append("No apparent test coverage")

        return risks

    def _generate_recommendations(
        self,
        module_path: str,
        deps_to_break: List[str],
        risks: List[str],
        module_metrics: Dict[str, Dict[str, Any]] = None,
    ) -> List[str]:
        """Generate recommendations for extraction."""
        recommendations = []

        # Recommendations based on dependencies
        if deps_to_break:
            recommendations.append("Create abstraction layer for external dependencies")
            if any("<->" in dep for dep in deps_to_break):
                recommendations.append(
                    "Introduce interface segregation to break circular dependencies"
                )

        # Recommendations based on risks
        if any("Database coupling" in risk for risk in risks):
            recommendations.append(
                "Implement repository pattern to abstract database access"
            )

        if any("raw SQL" in risk for risk in risks):
            recommendations.append("Migrate raw SQL to ORM or query builder")

        # Recommendations based on metrics
        if module_metrics and module_path in module_metrics:
            metrics = module_metrics[module_path]

            if metrics.get("lines_of_code", 0) > 500:
                recommendations.append(
                    "Consider breaking into smaller modules before extraction"
                )

            if metrics.get("complexity", 0) > 20:
                recommendations.append(
                    "Refactor to reduce complexity before extraction"
                )

        # General recommendations
        recommendations.append("Create comprehensive test suite before extraction")
        recommendations.append("Use feature flags for gradual rollout")

        return recommendations

    def _calculate_feasibility_score(
        self,
        module_path: str,
        deps_to_break: List[str],
        risks: List[str],
        patterns: List[LegacyPattern],
        database_couplings: List[DatabaseCoupling],
    ) -> float:
        """Calculate extraction feasibility score (0-1)."""
        score = 1.0

        # Penalty for dependencies to break
        score -= len(deps_to_break) * 0.05

        # Penalty for risks
        score -= (
            len(risks) * 0.09
        )  # Reduced slightly to allow > 0.9 for isolated modules

        # Penalty for legacy patterns
        pattern_penalty = 0
        for pattern in patterns:
            if module_path in pattern.affected_files:
                if pattern.difficulty.value == "critical":
                    pattern_penalty += 0.3
                elif pattern.difficulty.value == "high":
                    pattern_penalty += 0.2
                elif pattern.difficulty.value == "medium":
                    pattern_penalty += 0.1
        score -= pattern_penalty

        # Penalty for database coupling
        coupling_penalty = 0
        for coupling in database_couplings:
            if module_path in coupling.coupled_modules:
                coupling_penalty += coupling.coupling_strength * 0.2
        score -= coupling_penalty

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))

    def _estimate_effort(
        self,
        module_path: str,
        deps_to_break: List[str],
        risks: List[str],
        module_metrics: Dict[str, Dict[str, Any]] = None,
    ) -> float:
        """Estimate effort in hours for extraction."""
        base_effort = 40  # Base effort for any extraction

        # Effort for breaking dependencies
        dependency_effort = len(deps_to_break) * 8

        # Effort for addressing risks
        risk_effort = len(risks) * 16

        # Effort based on module size
        size_effort = 0
        if module_metrics and module_path in module_metrics:
            metrics = module_metrics[module_path]
            loc = metrics.get("lines_of_code", 0)
            size_effort = loc / 50  # 1 hour per 50 lines of code

            # Additional effort for complexity
            complexity = metrics.get("complexity", 0)
            size_effort += complexity * 2

        total_effort = base_effort + dependency_effort + risk_effort + size_effort

        return round(total_effort, 1)
