"""Dependency analysis for database tables."""

import logging
from typing import Dict, List, Set, Tuple, Any
import networkx as nx

from pymigrate.utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyzes dependencies between database tables."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize dependency analyzer."""
        self.connection = connection
        
    async def build_dependency_graph(self) -> nx.DiGraph:
        """Build a directed graph of table dependencies."""
        graph = nx.DiGraph()
        
        # Get all tables
        tables = await self.connection.get_all_tables()
        
        # Add nodes
        for table in tables:
            graph.add_node(table)
            
        # Analyze foreign key relationships
        for table in tables:
            foreign_keys = await self.connection.get_foreign_keys(table)
            
            for fk in foreign_keys:
                referenced_table = fk["referenced_table"]
                
                # Add edge from table to referenced table
                graph.add_edge(
                    table, 
                    referenced_table,
                    constraint_name=fk["constraint_name"],
                    column=fk["column"],
                    referenced_column=fk["referenced_column"]
                )
                
        # Analyze implicit relationships (same column names, patterns)
        implicit_edges = await self._find_implicit_relationships(tables)
        for source, target, attrs in implicit_edges:
            if not graph.has_edge(source, target):
                graph.add_edge(source, target, **attrs)
                
        logger.info(
            f"Built dependency graph with {graph.number_of_nodes()} nodes "
            f"and {graph.number_of_edges()} edges"
        )
        
        return graph
        
    async def _find_implicit_relationships(
        self, 
        tables: List[str]
    ) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Find implicit relationships based on naming patterns."""
        implicit_edges = []
        
        # Get column information for all tables
        table_columns = {}
        for table in tables:
            columns = await self.connection.get_table_columns(table)
            table_columns[table] = columns
            
        # Look for common patterns
        for table1 in tables:
            for table2 in tables:
                if table1 == table2:
                    continue
                    
                # Check for common ID patterns
                for col1 in table_columns[table1]:
                    # Pattern: table1 has table2_id column
                    if col1["name"] == f"{table2}_id" or col1["name"] == f"{table2}Id":
                        implicit_edges.append((
                            table1,
                            table2,
                            {
                                "type": "implicit",
                                "reason": "naming_pattern",
                                "column": col1["name"]
                            }
                        ))
                        
        return implicit_edges
        
    async def analyze_coupling(
        self, 
        graph: nx.DiGraph
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze coupling between tables."""
        coupling_metrics = {}
        
        for node in graph.nodes():
            # Calculate metrics
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            
            # Afferent coupling (dependencies on this table)
            afferent = in_degree
            
            # Efferent coupling (this table's dependencies)
            efferent = out_degree
            
            # Instability metric
            if (efferent + afferent) > 0:
                instability = efferent / (efferent + afferent)
            else:
                instability = 0
                
            coupling_metrics[node] = {
                "afferent_coupling": afferent,
                "efferent_coupling": efferent,
                "instability": instability,
                "depends_on": list(graph.successors(node)),
                "depended_by": list(graph.predecessors(node))
            }
            
        return coupling_metrics
        
    async def find_tightly_coupled_groups(
        self, 
        graph: nx.DiGraph, 
        threshold: float = 0.7
    ) -> List[Set[str]]:
        """Find groups of tightly coupled tables."""
        # Find strongly connected components
        sccs = list(nx.strongly_connected_components(graph))
        
        # Filter out single-node components
        tightly_coupled = [scc for scc in sccs if len(scc) > 1]
        
        # Also find near-cliques using clustering
        undirected = graph.to_undirected()
        
        # Calculate clustering coefficient for each node
        clustering = nx.clustering(undirected)
        
        # Find densely connected subgraphs
        high_clustering_nodes = [
            node for node, coeff in clustering.items() 
            if coeff >= threshold
        ]
        
        # Group nearby high-clustering nodes
        if high_clustering_nodes:
            subgraph = undirected.subgraph(high_clustering_nodes)
            additional_groups = list(nx.connected_components(subgraph))
            
            for group in additional_groups:
                if len(group) > 1 and group not in tightly_coupled:
                    tightly_coupled.append(group)
                    
        return tightly_coupled
        
    async def calculate_migration_complexity(
        self, 
        graph: nx.DiGraph, 
        tables_to_migrate: List[str]
    ) -> Dict[str, Any]:
        """Calculate complexity of migrating specific tables."""
        subgraph = graph.subgraph(tables_to_migrate)
        
        # Count cross-boundary dependencies
        external_deps = 0
        for table in tables_to_migrate:
            # Dependencies going out
            for dep in graph.successors(table):
                if dep not in tables_to_migrate:
                    external_deps += 1
                    
            # Dependencies coming in
            for dep in graph.predecessors(table):
                if dep not in tables_to_migrate:
                    external_deps += 1
                    
        # Calculate metrics
        metrics = {
            "tables_count": len(tables_to_migrate),
            "internal_dependencies": subgraph.number_of_edges(),
            "external_dependencies": external_deps,
            "has_cycles": not nx.is_directed_acyclic_graph(subgraph),
            "max_depth": nx.dag_longest_path_length(subgraph) if nx.is_directed_acyclic_graph(subgraph) else -1,
            "complexity_score": external_deps / max(len(tables_to_migrate), 1)
        }
        
        return metrics