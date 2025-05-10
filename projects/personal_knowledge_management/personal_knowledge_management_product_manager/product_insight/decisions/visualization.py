"""
Decision visualization module for ProductInsight.

This module provides functionality for visualizing decision data in various formats,
including timelines, trees, and relationships.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from product_insight.decisions.manager import DecisionTimeline, DecisionTree
from product_insight.models import Decision, Feature, StrategicObjective, Stakeholder


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
        # Convert to a format that can be safely serialized to JSON
        serializable_items = []

        for item in timeline_items:
            item_dict = item.model_dump()
            # Ensure all string formatting for assertions
            serializable_items.append(item_dict)

        return json.dumps(serializable_items, indent=2)
    
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


def create_decision_timeline(decisions: List[Decision]) -> Dict:
    """Create a timeline visualization of decisions.

    Args:
        decisions: List of decisions to include in the timeline

    Returns:
        Dictionary with timeline visualization data
    """
    # Sort decisions by date
    sorted_decisions = sorted(decisions, key=lambda d: d.decision_date if d.decision_date else datetime.now())

    # Determine timespan
    if sorted_decisions:
        start_date = sorted_decisions[0].decision_date if sorted_decisions[0].decision_date else datetime.now()
        end_date = sorted_decisions[-1].decision_date if sorted_decisions[-1].decision_date else datetime.now()
    else:
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

    # Create timeline entries
    timeline_entries = []
    for decision in sorted_decisions:
        # Decision date entry
        timeline_entries.append({
            "title": decision.title,
            "date": decision.decision_date.isoformat() if decision.decision_date else datetime.now().isoformat(),
            "type": "decision",
            "description": decision.description,
            "id": str(decision.id)
        })

        # Include outcome dates if available
        if decision.outcome_date:
            timeline_entries.append({
                "title": f"Outcome: {decision.title}",
                "date": decision.outcome_date.isoformat(),
                "type": "outcome",
                "description": decision.outcome_notes if decision.outcome_notes else "Decision outcome",
                "id": f"{str(decision.id)}_outcome"
            })

    # Create the timeline structure
    timeline = {
        "title": "Decision Timeline",
        "decisions": timeline_entries,
        "timespan": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }

    return timeline


def create_decision_tree(decision: Decision) -> Dict:
    """Create a tree visualization of a decision and its alternatives.

    Args:
        decision: Decision to visualize

    Returns:
        Dictionary with tree visualization data
    """
    # Create the tree structure
    tree = {
        "title": f"Decision Tree: {decision.title}",
        "main_decision": decision.title,
        "rationale": decision.rationale,
        "context": decision.context,
        "alternatives": [],
        "tags": [tag.name for tag in decision.tags]
    }

    # Add alternatives
    if decision.alternatives:
        tree["alternatives"] = [
            {
                "option": alt,
                "selected": False
            }
            for alt in decision.alternatives
        ]

    # Add related entities
    tree["related_entities"] = []

    # Add features
    if decision.feature_ids:
        tree["related_entities"].append({
            "type": "features",
            "ids": [str(fid) for fid in decision.feature_ids]
        })

    # Add objectives
    if decision.objective_ids:
        tree["related_entities"].append({
            "type": "objectives",
            "ids": [str(oid) for oid in decision.objective_ids]
        })

    return tree


def create_stakeholder_influence_chart(decision: Decision, stakeholders: List[Stakeholder]) -> Dict:
    """Create a chart showing stakeholder influence on a decision.

    Args:
        decision: Decision to visualize
        stakeholders: List of stakeholders involved in the decision

    Returns:
        Dictionary with chart visualization data
    """
    # Create the chart structure
    chart = {
        "title": f"Stakeholder Influence: {decision.title}",
        "decision": {
            "id": str(decision.id),
            "title": decision.title,
            "description": decision.description
        },
        "stakeholders": []
    }

    # Get relevant stakeholders (those who decided or provided input)
    relevant_stakeholder_ids = set(decision.decided_by)
    relevant_stakeholder_str_ids = set(decision.stakeholder_input.keys())

    # Add stakeholder data
    for stakeholder in stakeholders:
        stakeholder_id_str = str(stakeholder.id)
        if (stakeholder.id in relevant_stakeholder_ids or
            stakeholder_id_str in relevant_stakeholder_str_ids or
            not (relevant_stakeholder_ids or relevant_stakeholder_str_ids)):

            stakeholder_entry = {
                "id": stakeholder_id_str,
                "name": stakeholder.name,
                "role": stakeholder.role.value if hasattr(stakeholder, 'role') and stakeholder.role else "Unspecified",
                "influence": stakeholder.influence.value if hasattr(stakeholder, 'influence') and stakeholder.influence else "Low",
                "input": decision.stakeholder_input.get(stakeholder_id_str, "No input provided"),
                "decided": stakeholder.id in decision.decided_by
            }
            chart["stakeholders"].append(stakeholder_entry)

    return chart