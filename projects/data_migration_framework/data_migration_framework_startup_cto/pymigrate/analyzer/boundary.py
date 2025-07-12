"""Service boundary analyzer for microservices decomposition."""

import logging
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import defaultdict
import networkx as nx

from pymigrate.models.service import ServiceBoundary, ServiceType
from pymigrate.analyzer.dependency import DependencyAnalyzer
from pymigrate.analyzer.pattern import AccessPatternAnalyzer
from pymigrate.utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class ServiceBoundaryAnalyzer:
    """Analyzes data models to suggest optimal service boundaries."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize service boundary analyzer."""
        self.connection = connection
        self.dependency_analyzer = DependencyAnalyzer(connection)
        self.pattern_analyzer = AccessPatternAnalyzer(connection)
        self._table_graph: Optional[nx.DiGraph] = None
        
    async def analyze(self, min_confidence: float = 0.7) -> List[ServiceBoundary]:
        """Analyze database and suggest service boundaries."""
        logger.info("Starting service boundary analysis")
        
        # Build dependency graph
        self._table_graph = await self.dependency_analyzer.build_dependency_graph()
        
        # Analyze access patterns
        access_patterns = await self.pattern_analyzer.analyze_patterns()
        
        # Identify cohesive table groups
        table_groups = self._identify_cohesive_groups(access_patterns)
        
        # Generate service boundaries
        boundaries = []
        for group_name, tables in table_groups.items():
            boundary = await self._create_service_boundary(
                group_name, 
                tables, 
                access_patterns
            )
            
            if boundary.confidence_score >= min_confidence:
                boundaries.append(boundary)
                
        # Validate boundaries for circular dependencies
        boundaries = self._validate_boundaries(boundaries)
        
        logger.info(f"Identified {len(boundaries)} service boundaries")
        return boundaries
        
    def _identify_cohesive_groups(
        self, 
        access_patterns: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Identify cohesive groups of tables."""
        # Use community detection on the dependency graph
        communities = nx.community.louvain_communities(
            self._table_graph.to_undirected()
        )
        
        groups = {}
        
        # Analyze each community
        for idx, community in enumerate(communities):
            tables = list(community)
            
            # Determine service type based on table names and patterns
            service_type = self._determine_service_type(tables, access_patterns)
            
            # Create meaningful name
            if service_type != ServiceType.CUSTOM:
                group_name = service_type.value
            else:
                group_name = f"service_{idx + 1}"
                
            groups[group_name] = tables
            
        # Handle isolated tables
        all_tables = set(self._table_graph.nodes())
        grouped_tables = set()
        for tables in groups.values():
            grouped_tables.update(tables)
            
        isolated_tables = all_tables - grouped_tables
        if isolated_tables:
            groups["utility"] = list(isolated_tables)
            
        return groups
        
    def _determine_service_type(
        self, 
        tables: List[str], 
        access_patterns: Dict[str, Any]
    ) -> ServiceType:
        """Determine the type of service based on table names."""
        table_names_lower = [t.lower() for t in tables]
        
        # Check for common patterns
        if any("user" in t or "account" in t or "auth" in t for t in table_names_lower):
            return ServiceType.USER
        elif any("order" in t or "purchase" in t for t in table_names_lower):
            return ServiceType.ORDER
        elif any("inventory" in t or "stock" in t or "product" in t for t in table_names_lower):
            return ServiceType.INVENTORY
        elif any("payment" in t or "billing" in t or "invoice" in t for t in table_names_lower):
            return ServiceType.PAYMENT
        elif any("notification" in t or "email" in t or "sms" in t for t in table_names_lower):
            return ServiceType.NOTIFICATION
        elif any("analytics" in t or "metrics" in t or "report" in t for t in table_names_lower):
            return ServiceType.ANALYTICS
        else:
            return ServiceType.CUSTOM
            
    async def _create_service_boundary(
        self,
        service_name: str,
        tables: List[str],
        access_patterns: Dict[str, Any]
    ) -> ServiceBoundary:
        """Create a service boundary for a group of tables."""
        # Get relationships
        relationships = {}
        for table in tables:
            if table in self._table_graph:
                # Outgoing relationships
                outgoing = [
                    t for t in self._table_graph.successors(table)
                    if t not in tables  # External dependencies
                ]
                if outgoing:
                    relationships[table] = outgoing
                    
        # Get transaction boundaries
        transaction_boundaries = await self._identify_transaction_boundaries(tables)
        
        # Calculate estimated size
        total_size = 0
        for table in tables:
            size = await self.connection.get_table_size_mb(table)
            total_size += size
            
        # Get dependencies on other services
        dependencies = set()
        for table in tables:
            for neighbor in self._table_graph.neighbors(table):
                if neighbor not in tables:
                    # Find which service this table belongs to
                    dependencies.add(neighbor)
                    
        # Calculate confidence score
        confidence = self._calculate_confidence_score(
            tables, 
            relationships, 
            transaction_boundaries
        )
        
        # Get relevant access patterns
        service_patterns = []
        for pattern in access_patterns.get("patterns", []):
            if any(t in pattern.get("tables", []) for t in tables):
                service_patterns.append(pattern)
                
        return ServiceBoundary(
            service_name=service_name,
            service_type=self._determine_service_type(tables, access_patterns),
            tables=tables,
            relationships=relationships,
            access_patterns=service_patterns,
            estimated_size_mb=total_size,
            transaction_boundaries=transaction_boundaries,
            dependencies=dependencies,
            confidence_score=confidence
        )
        
    async def _identify_transaction_boundaries(
        self, 
        tables: List[str]
    ) -> List[str]:
        """Identify transaction boundaries within a service."""
        boundaries = []
        
        # Analyze stored procedures and functions
        procedures = await self.connection.get_stored_procedures()
        
        for proc in procedures:
            # Check if procedure accesses multiple tables in this service
            accessed_tables = await self.connection.get_procedure_tables(proc["name"])
            
            service_tables = [t for t in accessed_tables if t in tables]
            if len(service_tables) > 1:
                boundaries.append(proc["name"])
                
        return boundaries
        
    def _calculate_confidence_score(
        self,
        tables: List[str],
        relationships: Dict[str, List[str]],
        transaction_boundaries: List[str]
    ) -> float:
        """Calculate confidence score for service boundary."""
        score = 0.0
        
        # High cohesion (few external dependencies)
        total_relationships = sum(len(deps) for deps in relationships.values())
        if len(tables) > 0:
            cohesion_score = 1.0 - (total_relationships / len(tables))
            score += cohesion_score * 0.4
        else:
            score += 0.4
            
        # Transaction boundaries contained within service
        if transaction_boundaries:
            score += 0.3
            
        # Reasonable number of tables
        if 3 <= len(tables) <= 20:
            score += 0.3
        elif 1 <= len(tables) < 3:
            score += 0.15
        elif 20 < len(tables) <= 50:
            score += 0.15
            
        return min(score, 1.0)
        
    def _validate_boundaries(
        self, 
        boundaries: List[ServiceBoundary]
    ) -> List[ServiceBoundary]:
        """Validate service boundaries for issues."""
        validated = []
        
        # Check for circular dependencies between services
        service_graph = nx.DiGraph()
        
        # Build service dependency graph
        for boundary in boundaries:
            service_graph.add_node(boundary.service_name)
            
        for boundary in boundaries:
            for dep_table in boundary.dependencies:
                # Find which service owns this table
                for other in boundaries:
                    if dep_table in other.tables:
                        service_graph.add_edge(
                            boundary.service_name, 
                            other.service_name
                        )
                        
        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(service_graph))
            if cycles:
                logger.warning(f"Found circular dependencies: {cycles}")
                # In a real implementation, we might try to break cycles
                
        except nx.NetworkXNoCycle:
            pass
            
        # Validate each boundary
        for boundary in boundaries:
            issues = []
            
            # Check for too many dependencies
            if len(boundary.dependencies) > 10:
                issues.append("high_coupling")
                
            # Check for too many tables
            if len(boundary.tables) > 50:
                issues.append("too_large")
                
            # Adjust confidence based on issues
            if issues:
                boundary.confidence_score *= 0.8
                logger.warning(
                    f"Service {boundary.service_name} has issues: {issues}"
                )
                
            validated.append(boundary)
            
        return validated
        
    async def get_migration_order(
        self, 
        boundaries: List[ServiceBoundary]
    ) -> List[str]:
        """Determine optimal order for migrating services."""
        # Build dependency graph
        service_graph = nx.DiGraph()
        
        for boundary in boundaries:
            service_graph.add_node(boundary.service_name)
            
        for boundary in boundaries:
            for dep_table in boundary.dependencies:
                for other in boundaries:
                    if dep_table in other.tables and other.service_name != boundary.service_name:
                        # This service depends on other
                        service_graph.add_edge(
                            other.service_name,
                            boundary.service_name
                        )
                        
        # Topological sort for migration order
        try:
            migration_order = list(nx.topological_sort(service_graph))
        except nx.NetworkXUnfeasible:
            # Has cycles, use approximate order
            migration_order = [b.service_name for b in boundaries]
            
        return migration_order