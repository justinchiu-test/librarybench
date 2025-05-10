"""
Strategy visualization module for ProductInsight.

This module provides functionality for visualizing strategic objectives and their
relationships in various formats, including trees, tables, and dependency graphs.
"""

import json
from typing import Dict, List, Optional, Tuple, Union, cast

from pydantic import BaseModel, Field

from product_insight.models import (
    Feature,
    PriorityEnum,
    StatusEnum,
    StrategicObjective,
)
from product_insight.strategy.objective import ObjectiveProgress, ObjectiveTree


class TreeNode(BaseModel):
    """Node for tree visualizations."""
    
    id: str
    name: str
    description: Optional[str] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    children: List["TreeNode"] = Field(default_factory=list)


class DependencyLink(BaseModel):
    """Link for dependency graph visualizations."""
    
    source: str
    target: str
    type: str
    label: Optional[str] = None


class DependencyGraph(BaseModel):
    """Dependency graph visualization data."""
    
    nodes: List[Dict] = Field(default_factory=list)
    links: List[DependencyLink] = Field(default_factory=list)


class StrategyTable(BaseModel):
    """Table representation of a strategy."""
    
    objectives: List[Dict] = Field(default_factory=list)
    metrics: List[Dict] = Field(default_factory=list)
    features: List[Dict] = Field(default_factory=list)


class StrategyVisualizer:
    """Provides visualization for strategy components."""
    
    @staticmethod
    def create_objective_tree_view(tree: ObjectiveTree) -> TreeNode:
        """Create a tree visualization from an objective tree.
        
        Args:
            tree: ObjectiveTree to visualize
            
        Returns:
            TreeNode for visualization
        """
        # Create the root node
        root = TreeNode(
            id=str(tree.root.id),
            name=tree.root.name,
            description=tree.root.description,
            status=tree.root.status.value if tree.root.status else None,
            priority=tree.root.priority.value if tree.root.priority else None,
        )
        
        # Add progress if available
        if tree.root.metric_current is not None and tree.root.metric_target is not None:
            if tree.root.metric_target > 0:
                root.progress = min(
                    100.0, 
                    (tree.root.metric_current / tree.root.metric_target) * 100.0
                )
        
        # Add children recursively
        for child in tree.children:
            child_node = StrategyVisualizer.create_objective_tree_view(child)
            root.children.append(child_node)
        
        return root
    
    @staticmethod
    def create_progress_tree_view(progress: ObjectiveProgress) -> TreeNode:
        """Create a tree visualization from an objective progress.
        
        Args:
            progress: ObjectiveProgress to visualize
            
        Returns:
            TreeNode for visualization
        """
        # Create the root node
        root = TreeNode(
            id=str(progress.objective_id),
            name=progress.name,
            progress=progress.progress_percentage,
            status=progress.status.value,
            priority=progress.priority.value,
        )
        
        # Add children recursively
        for child in progress.child_progress:
            child_node = StrategyVisualizer.create_progress_tree_view(child)
            root.children.append(child_node)
        
        return root
    
    @staticmethod
    def create_dependency_graph(
        objectives: List[StrategicObjective], 
        features: Optional[List[Feature]] = None
    ) -> DependencyGraph:
        """Create a dependency graph visualization.
        
        Args:
            objectives: List of strategic objectives
            features: Optional list of features
            
        Returns:
            DependencyGraph for visualization
        """
        graph = DependencyGraph()
        
        # Create a map of objective IDs to indices
        obj_map = {str(obj.id): i for i, obj in enumerate(objectives)}
        
        # Add objective nodes
        for obj in objectives:
            graph.nodes.append({
                "id": str(obj.id),
                "name": obj.name,
                "type": "objective",
                "status": obj.status.value,
                "priority": obj.priority.value,
            })
            
            # Add parent-child links
            if obj.parent_id:
                parent_id = str(obj.parent_id)
                if parent_id in obj_map:
                    graph.links.append(DependencyLink(
                        source=parent_id,
                        target=str(obj.id),
                        type="parent-child",
                        label="parent-of"
                    ))
        
        # Add features if provided
        if features:
            for feature in features:
                graph.nodes.append({
                    "id": str(feature.id),
                    "name": feature.name,
                    "type": "feature",
                    "status": feature.status.value,
                    "priority": feature.priority_score,
                })
                
                # Add feature-objective links
                for obj_id in feature.objective_ids:
                    if str(obj_id) in obj_map:
                        graph.links.append(DependencyLink(
                            source=str(obj_id),
                            target=str(feature.id),
                            type="objective-feature",
                            label="supports"
                        ))
                
                # Add feature dependencies
                for dep_id in feature.dependencies:
                    graph.links.append(DependencyLink(
                        source=str(dep_id),
                        target=str(feature.id),
                        type="feature-dependency",
                        label="depends-on"
                    ))
        
        return graph
    
    @staticmethod
    def create_strategy_table(
        objectives: List[StrategicObjective], 
        features: Optional[List[Feature]] = None
    ) -> StrategyTable:
        """Create a tabular representation of a strategy.
        
        Args:
            objectives: List of strategic objectives
            features: Optional list of features
            
        Returns:
            StrategyTable for visualization
        """
        table = StrategyTable()
        
        # Add objectives
        for obj in objectives:
            table.objectives.append({
                "id": str(obj.id),
                "name": obj.name,
                "description": obj.description,
                "status": obj.status.value,
                "priority": obj.priority.value,
                "parent_id": str(obj.parent_id) if obj.parent_id else None,
            })
            
            # Add metrics
            if obj.metric_type:
                table.metrics.append({
                    "objective_id": str(obj.id),
                    "objective_name": obj.name,
                    "type": obj.metric_type.value,
                    "target": obj.metric_target,
                    "current": obj.metric_current,
                    "progress": (
                        (obj.metric_current / obj.metric_target) * 100.0 
                        if obj.metric_target and obj.metric_current and obj.metric_target > 0 
                        else None
                    ),
                })
        
        # Add features if provided
        if features:
            for feature in features:
                # Find associated objectives
                related_objectives = [
                    obj.name for obj in objectives 
                    if obj.id in feature.objective_ids
                ]
                
                table.features.append({
                    "id": str(feature.id),
                    "name": feature.name,
                    "description": feature.description,
                    "status": feature.status.value,
                    "effort": feature.effort_estimate,
                    "value": feature.value_estimate,
                    "priority": feature.priority_score,
                    "objectives": related_objectives,
                })
        
        return table
    
    @staticmethod
    def objective_tree_to_markdown(tree: ObjectiveTree) -> str:
        """Convert an objective tree to Markdown format.
        
        Args:
            tree: ObjectiveTree to convert
            
        Returns:
            Markdown string
        """
        def _build_tree_md(node: ObjectiveTree, depth: int = 0) -> str:
            indent = "  " * depth
            md = f"{indent}- **{node.root.name}**"
            
            # Add status and priority
            status_str = f" [{node.root.status.value}]" if node.root.status else ""
            priority_str = f" ({node.root.priority.value})" if node.root.priority else ""
            md += status_str + priority_str
            
            # Add progress information
            if node.root.metric_current is not None and node.root.metric_target is not None:
                if node.root.metric_target > 0:
                    progress = min(
                        100.0, 
                        (node.root.metric_current / node.root.metric_target) * 100.0
                    )
                    md += f" - {progress:.1f}%"
            
            # Add description on the next line if available
            if node.root.description:
                md += f"\n{indent}  {node.root.description}"
            
            # Add children
            if node.children:
                md += "\n"
                for child in node.children:
                    md += _build_tree_md(child, depth + 1)
                    md += "\n"
            
            return md
        
        return _build_tree_md(tree)
    
    @staticmethod
    def dependency_graph_to_json(graph: DependencyGraph) -> str:
        """Convert a dependency graph to JSON format.
        
        Args:
            graph: DependencyGraph to convert
            
        Returns:
            JSON string
        """
        return json.dumps({
            "nodes": graph.nodes,
            "links": [link.model_dump() for link in graph.links]
        }, indent=2)
    
    @staticmethod
    def strategy_table_to_markdown(table: StrategyTable) -> str:
        """Convert a strategy table to Markdown format.
        
        Args:
            table: StrategyTable to convert
            
        Returns:
            Markdown string
        """
        md = "# Strategic Plan\n\n"
        
        # Objectives table
        md += "## Strategic Objectives\n\n"
        md += "| ID | Name | Description | Status | Priority | Parent |\n"
        md += "|-----|-----|-------------|--------|----------|--------|\n"
        
        for obj in table.objectives:
            md += f"| {obj['id']} | {obj['name']} | {obj['description']} | {obj['status']} | {obj['priority']} | {obj['parent_id'] or '-'} |\n"
        
        # Metrics table
        if table.metrics:
            md += "\n## Metrics\n\n"
            md += "| Objective | Metric Type | Target | Current | Progress |\n"
            md += "|-----------|-------------|--------|---------|----------|\n"
            
            for metric in table.metrics:
                progress = f"{metric['progress']:.1f}%" if metric.get('progress') is not None else "-"
                md += f"| {metric['objective_name']} | {metric['type']} | {metric['target']} | {metric['current']} | {progress} |\n"
        
        # Features table
        if table.features:
            md += "\n## Features\n\n"
            md += "| ID | Name | Description | Status | Effort | Value | Priority | Objectives |\n"
            md += "|-----|-----|-------------|--------|--------|-------|----------|------------|\n"
            
            for feature in table.features:
                objectives = ", ".join(feature['objectives'])
                md += f"| {feature['id']} | {feature['name']} | {feature['description']} | {feature['status']} | {feature['effort']} | {feature['value']} | {feature['priority']} | {objectives} |\n"
        
        return md