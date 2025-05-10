"""
Decision visualization module for ProductInsight.

This module provides functionality for visualizing decision data in various formats,
including timelines, trees, and relationships.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from product_insight.decisions.manager import DecisionTimeline, DecisionTree
from product_insight.models import Decision, Feature, StrategicObjective


class TimelineItem(BaseModel):
    """Item for timeline visualizations."""
    
    id: str
    title: str
    date: str
    type: str = "decision"
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    related_ids: List[str] = Field(default_factory=list)


class TreeNode(BaseModel):
    """Node for tree visualizations."""
    
    id: str
    name: str
    type: str
    description: Optional[str] = None
    date: Optional[str] = None
    children: List["TreeNode"] = Field(default_factory=list)


class DecisionLink(BaseModel):
    """Link for relationship visualizations."""
    
    source: str
    target: str
    type: str
    label: Optional[str] = None


class DecisionRelationshipGraph(BaseModel):
    """Relationship graph visualization data."""
    
    nodes: List[Dict] = Field(default_factory=list)
    links: List[DecisionLink] = Field(default_factory=list)


class DecisionVisualizer:
    """Visualizes decision data."""
    
    @staticmethod
    def create_timeline_view(timeline: DecisionTimeline) -> List[TimelineItem]:
        """Create a timeline visualization.
        
        Args:
            timeline: DecisionTimeline to visualize
            
        Returns:
            List of TimelineItem for visualization
        """
        timeline_items = []
        
        for date, decision in timeline.decisions:
            # Extract tags
            tags = [tag.name for tag in decision.tags]
            
            # Collect related IDs
            related_ids = []
            related_ids.extend([str(fid) for fid in decision.feature_ids])
            related_ids.extend([str(oid) for oid in decision.objective_ids])
            
            # Create the timeline item
            item = TimelineItem(
                id=str(decision.id),
                title=decision.title,
                date=date.isoformat(),
                type="decision",
                description=decision.description,
                tags=tags,
                related_ids=related_ids
            )
            
            timeline_items.append(item)
        
        return timeline_items
    
    @staticmethod
    def create_decision_tree_view(tree: DecisionTree) -> TreeNode:
        """Create a tree visualization from a decision tree.
        
        Args:
            tree: DecisionTree to visualize
            
        Returns:
            TreeNode for visualization
        """
        # Create the root node
        root = TreeNode(
            id=str(tree.root_decision.id),
            name=tree.root_decision.title,
            type="decision",
            description=tree.root_decision.description,
            date=tree.root_decision.decision_date.isoformat()
        )
        
        # Add related features as children
        for feature in tree.related_features:
            feature_node = TreeNode(
                id=str(feature.id),
                name=feature.name,
                type="feature",
                description=feature.description
            )
            root.children.append(feature_node)
        
        # Add related objectives as children
        for objective in tree.related_objectives:
            objective_node = TreeNode(
                id=str(objective.id),
                name=objective.name,
                type="objective",
                description=objective.description
            )
            root.children.append(objective_node)
        
        # Add related decisions as children
        for decision in tree.related_decisions:
            decision_node = TreeNode(
                id=str(decision.id),
                name=decision.title,
                type="decision",
                description=decision.description,
                date=decision.decision_date.isoformat()
            )
            root.children.append(decision_node)
        
        return root
    
    @staticmethod
    def create_relationship_graph(
        decisions: List[Decision],
        features: Optional[List[Feature]] = None,
        objectives: Optional[List[StrategicObjective]] = None
    ) -> DecisionRelationshipGraph:
        """Create a relationship graph visualization.
        
        Args:
            decisions: List of decisions
            features: Optional list of features
            objectives: Optional list of objectives
            
        Returns:
            DecisionRelationshipGraph for visualization
        """
        graph = DecisionRelationshipGraph()
        
        # Add decision nodes
        for decision in decisions:
            graph.nodes.append({
                "id": str(decision.id),
                "name": decision.title,
                "type": "decision",
                "date": decision.decision_date.isoformat()
            })
        
        # Add feature nodes if provided
        if features:
            for feature in features:
                graph.nodes.append({
                    "id": str(feature.id),
                    "name": feature.name,
                    "type": "feature"
                })
                
                # Add decision-feature links
                for decision in decisions:
                    if feature.id in decision.feature_ids:
                        graph.links.append(DecisionLink(
                            source=str(decision.id),
                            target=str(feature.id),
                            type="decision-feature",
                            label="affects"
                        ))
        
        # Add objective nodes if provided
        if objectives:
            for objective in objectives:
                graph.nodes.append({
                    "id": str(objective.id),
                    "name": objective.name,
                    "type": "objective"
                })
                
                # Add decision-objective links
                for decision in decisions:
                    if objective.id in decision.objective_ids:
                        graph.links.append(DecisionLink(
                            source=str(decision.id),
                            target=str(objective.id),
                            type="decision-objective",
                            label="supports"
                        ))
        
        # Add decision-decision links (based on shared features or objectives)
        for i, decision1 in enumerate(decisions):
            for decision2 in decisions[i+1:]:
                # Check for shared features
                shared_features = set(decision1.feature_ids).intersection(set(decision2.feature_ids))
                if shared_features:
                    graph.links.append(DecisionLink(
                        source=str(decision1.id),
                        target=str(decision2.id),
                        type="decision-decision",
                        label="related"
                    ))
                    continue
                
                # Check for shared objectives
                shared_objectives = set(decision1.objective_ids).intersection(set(decision2.objective_ids))
                if shared_objectives:
                    graph.links.append(DecisionLink(
                        source=str(decision1.id),
                        target=str(decision2.id),
                        type="decision-decision",
                        label="related"
                    ))
        
        return graph
    
    @staticmethod
    def timeline_to_json(timeline_items: List[TimelineItem]) -> str:
        """Convert a timeline to JSON format.
        
        Args:
            timeline_items: List of TimelineItem to convert
            
        Returns:
            JSON string
        """
        return json.dumps([item.model_dump() for item in timeline_items], indent=2)
    
    @staticmethod
    def decision_tree_to_json(tree_node: TreeNode) -> str:
        """Convert a decision tree to JSON format.
        
        Args:
            tree_node: TreeNode to convert
            
        Returns:
            JSON string
        """
        return json.dumps(tree_node.model_dump(), indent=2)
    
    @staticmethod
    def relationship_graph_to_json(graph: DecisionRelationshipGraph) -> str:
        """Convert a relationship graph to JSON format.
        
        Args:
            graph: DecisionRelationshipGraph to convert
            
        Returns:
            JSON string
        """
        return json.dumps({
            "nodes": graph.nodes,
            "links": [link.model_dump() for link in graph.links]
        }, indent=2)
    
    @staticmethod
    def decision_to_markdown(decision: Decision) -> str:
        """Convert a decision to Markdown format.
        
        Args:
            decision: Decision to convert
            
        Returns:
            Markdown string
        """
        md = f"# {decision.title}\n\n"
        
        # Add metadata
        md += f"**Date:** {decision.decision_date.strftime('%Y-%m-%d')}\n\n"
        
        if decision.tags:
            tags = ", ".join(tag.name for tag in decision.tags)
            md += f"**Tags:** {tags}\n\n"
        
        md += f"## Description\n\n{decision.description}\n\n"
        
        # Add context and rationale
        md += f"## Context\n\n{decision.context}\n\n"
        md += f"## Rationale\n\n{decision.rationale}\n\n"
        
        # Add alternatives if available
        if decision.alternatives:
            md += "## Alternatives Considered\n\n"
            for alt in decision.alternatives:
                md += f"- {alt}\n"
            md += "\n"
        
        # Add stakeholder input if available
        if decision.stakeholder_input:
            md += "## Stakeholder Input\n\n"
            for stakeholder_id, input_text in decision.stakeholder_input.items():
                md += f"- **Stakeholder {stakeholder_id}:** {input_text}\n"
            md += "\n"
        
        # Add supporting data if available
        if decision.supporting_data:
            md += "## Supporting Data\n\n"
            for data in decision.supporting_data:
                md += f"- {data}\n"
            md += "\n"
        
        # Add outcome if available
        if decision.outcome_notes:
            md += "## Outcome\n\n"
            md += f"{decision.outcome_notes}\n\n"
            
            if decision.outcome_date:
                md += f"**Outcome Date:** {decision.outcome_date.strftime('%Y-%m-%d')}\n\n"
            
            if decision.retrospective:
                md += "## Retrospective\n\n"
                md += f"{decision.retrospective}\n\n"
        
        return md
    
    @staticmethod
    def decision_tree_to_markdown(tree: DecisionTree) -> str:
        """Convert a decision tree to Markdown format.
        
        Args:
            tree: DecisionTree to convert
            
        Returns:
            Markdown string
        """
        md = f"# Decision: {tree.root_decision.title}\n\n"
        
        # Add root decision details
        md += f"**Date:** {tree.root_decision.decision_date.strftime('%Y-%m-%d')}\n\n"
        md += f"## Description\n\n{tree.root_decision.description}\n\n"
        md += f"## Context\n\n{tree.root_decision.context}\n\n"
        md += f"## Rationale\n\n{tree.root_decision.rationale}\n\n"
        
        # Add related features
        if tree.related_features:
            md += "## Related Features\n\n"
            for feature in tree.related_features:
                md += f"### {feature.name}\n\n"
                md += f"{feature.description}\n\n"
                md += f"**Status:** {feature.status.value}\n\n"
        
        # Add related objectives
        if tree.related_objectives:
            md += "## Related Objectives\n\n"
            for objective in tree.related_objectives:
                md += f"### {objective.name}\n\n"
                md += f"{objective.description}\n\n"
                md += f"**Status:** {objective.status.value}\n\n"
        
        # Add related decisions
        if tree.related_decisions:
            md += "## Related Decisions\n\n"
            for decision in tree.related_decisions:
                md += f"### {decision.title}\n\n"
                md += f"**Date:** {decision.decision_date.strftime('%Y-%m-%d')}\n\n"
                md += f"{decision.description}\n\n"
        
        return md