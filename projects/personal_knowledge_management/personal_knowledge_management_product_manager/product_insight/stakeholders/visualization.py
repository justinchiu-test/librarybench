"""
Stakeholder visualization module for ProductInsight.

This module provides functionality for visualizing stakeholder data in various formats,
including maps, matrices, and networks.
"""

import json
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from pydantic import BaseModel, Field

from product_insight.models import (
    Feature,
    InfluenceEnum,
    Stakeholder,
    StakeholderPerspective,
    StakeholderRoleEnum,
    StrategicObjective,
)
from product_insight.stakeholders.manager import (
    StakeholderAlignment,
    StakeholderGroup,
    StakeholderNetwork,
)


class StakeholderMatrixItem(BaseModel):
    """Item in a stakeholder matrix."""
    
    id: str
    name: str
    role: str
    influence: str
    position_x: float
    position_y: float
    organization: Optional[str] = None


class StakeholderMatrix(BaseModel):
    """Two-dimensional matrix of stakeholders."""
    
    x_axis: str
    y_axis: str
    items: List[StakeholderMatrixItem] = Field(default_factory=list)


class StakeholderHeatmapItem(BaseModel):
    """Item in a stakeholder heatmap."""
    
    id: str
    name: str
    x_axis_value: str
    y_axis_value: str
    heat_value: float


class StakeholderHeatmap(BaseModel):
    """Heatmap of stakeholder data."""
    
    x_axis: str
    y_axis: str
    x_values: List[str] = Field(default_factory=list)
    y_values: List[str] = Field(default_factory=list)
    items: List[StakeholderHeatmapItem] = Field(default_factory=list)


class StakeholderVisualizer:
    """Visualizes stakeholder data."""
    
    @staticmethod
    def create_influence_interest_matrix(
        stakeholders: List[Stakeholder], feature_id: Optional[UUID] = None
    ) -> StakeholderMatrix:
        """Create an influence/interest matrix.
        
        Args:
            stakeholders: List of stakeholders to include
            feature_id: Optional feature ID to measure interest for
            
        Returns:
            StakeholderMatrix with stakeholders positioned by influence and interest
        """
        matrix = StakeholderMatrix(
            x_axis="Interest",
            y_axis="Influence"
        )
        
        # Map influence levels to y positions
        influence_positions = {
            InfluenceEnum.HIGH: 0.8,
            InfluenceEnum.MEDIUM: 0.5,
            InfluenceEnum.LOW: 0.2
        }
        
        for stakeholder in stakeholders:
            # Calculate interest
            interest = 0.5  # Default
            
            if feature_id:
                # Use specific feature preference if available
                interest = stakeholder.feature_preferences.get(feature_id, 0.5)
            elif stakeholder.feature_preferences:
                # Use average of all feature preferences
                interest = sum(stakeholder.feature_preferences.values()) / len(stakeholder.feature_preferences)
            
            # Create matrix item
            item = StakeholderMatrixItem(
                id=str(stakeholder.id),
                name=stakeholder.name,
                role=stakeholder.role.value,
                influence=stakeholder.influence.value,
                position_x=interest,
                position_y=influence_positions.get(stakeholder.influence, 0.5),
                organization=stakeholder.organization
            )
            
            matrix.items.append(item)
        
        return matrix
    
    @staticmethod
    def create_alignment_matrix(
        stakeholders: List[Stakeholder], alignments: List[StakeholderAlignment]
    ) -> StakeholderMatrix:
        """Create an alignment/influence matrix.
        
        Args:
            stakeholders: List of stakeholders to include
            alignments: List of stakeholder alignments
            
        Returns:
            StakeholderMatrix with stakeholders positioned by influence and alignment
        """
        matrix = StakeholderMatrix(
            x_axis="Alignment",
            y_axis="Influence"
        )
        
        # Map influence levels to y positions
        influence_positions = {
            InfluenceEnum.HIGH: 0.8,
            InfluenceEnum.MEDIUM: 0.5,
            InfluenceEnum.LOW: 0.2
        }
        
        # Create a map of alignments for quick lookup
        alignment_map = {a.stakeholder_id: a.overall_alignment for a in alignments}
        
        for stakeholder in stakeholders:
            # Get alignment
            alignment = alignment_map.get(stakeholder.id, 0.5)
            
            # Create matrix item
            item = StakeholderMatrixItem(
                id=str(stakeholder.id),
                name=stakeholder.name,
                role=stakeholder.role.value,
                influence=stakeholder.influence.value,
                position_x=alignment,
                position_y=influence_positions.get(stakeholder.influence, 0.5),
                organization=stakeholder.organization
            )
            
            matrix.items.append(item)
        
        return matrix
    
    @staticmethod
    def create_feature_preference_heatmap(
        stakeholders: List[Stakeholder], features: List[Feature]
    ) -> StakeholderHeatmap:
        """Create a heatmap of feature preferences.
        
        Args:
            stakeholders: List of stakeholders to include
            features: List of features to include
            
        Returns:
            StakeholderHeatmap with stakeholder feature preferences
        """
        heatmap = StakeholderHeatmap(
            x_axis="Feature",
            y_axis="Stakeholder"
        )
        
        # Set axis values
        heatmap.x_values = [feature.name for feature in features]
        heatmap.y_values = [stakeholder.name for stakeholder in stakeholders]
        
        # Create heatmap items
        for stakeholder in stakeholders:
            for feature in features:
                # Get preference
                preference = stakeholder.feature_preferences.get(feature.id, 0.0)
                
                # Create heatmap item
                item = StakeholderHeatmapItem(
                    id=f"{stakeholder.id}_{feature.id}",
                    name=f"{stakeholder.name} - {feature.name}",
                    x_axis_value=feature.name,
                    y_axis_value=stakeholder.name,
                    heat_value=preference
                )
                
                heatmap.items.append(item)
        
        return heatmap
    
    @staticmethod
    def create_perspective_heatmap(
        perspectives: List[StakeholderPerspective],
        stakeholders: List[Stakeholder],
        topics: List[str]
    ) -> StakeholderHeatmap:
        """Create a heatmap of stakeholder perspectives on topics.
        
        Args:
            perspectives: List of stakeholder perspectives
            stakeholders: List of stakeholders
            topics: List of topics
            
        Returns:
            StakeholderHeatmap with stakeholder perspectives
        """
        heatmap = StakeholderHeatmap(
            x_axis="Topic",
            y_axis="Stakeholder"
        )
        
        # Set axis values
        heatmap.x_values = topics
        heatmap.y_values = [stakeholder.name for stakeholder in stakeholders]
        
        # Create a stakeholder lookup
        stakeholder_map = {str(s.id): s for s in stakeholders}
        
        # Create perspective lookup grouped by stakeholder and topic
        perspective_map = {}
        for perspective in perspectives:
            stakeholder_id = str(perspective.stakeholder_id)
            if stakeholder_id not in perspective_map:
                perspective_map[stakeholder_id] = {}
            
            perspective_map[stakeholder_id][perspective.topic] = perspective
        
        # Map sentiment to heat value
        sentiment_values = {
            "very_negative": 0.0,
            "negative": 0.25,
            "neutral": 0.5,
            "positive": 0.75,
            "very_positive": 1.0
        }
        
        # Create heatmap items
        for stakeholder in stakeholders:
            stakeholder_id = str(stakeholder.id)
            stakeholder_perspectives = perspective_map.get(stakeholder_id, {})
            
            for topic in topics:
                # Get perspective sentiment
                perspective = stakeholder_perspectives.get(topic)
                heat_value = 0.5  # Default to neutral
                
                if perspective:
                    heat_value = sentiment_values.get(perspective.sentiment.value, 0.5)
                
                # Create heatmap item
                item = StakeholderHeatmapItem(
                    id=f"{stakeholder_id}_{topic.replace(' ', '_')}",
                    name=f"{stakeholder.name} - {topic}",
                    x_axis_value=topic,
                    y_axis_value=stakeholder.name,
                    heat_value=heat_value
                )
                
                heatmap.items.append(item)
        
        return heatmap
    
    @staticmethod
    def stakeholder_matrix_to_json(matrix: StakeholderMatrix) -> str:
        """Convert a stakeholder matrix to JSON format.
        
        Args:
            matrix: StakeholderMatrix to convert
            
        Returns:
            JSON string
        """
        return json.dumps(matrix.model_dump(), indent=2)
    
    @staticmethod
    def stakeholder_heatmap_to_json(heatmap: StakeholderHeatmap) -> str:
        """Convert a stakeholder heatmap to JSON format.
        
        Args:
            heatmap: StakeholderHeatmap to convert
            
        Returns:
            JSON string
        """
        return json.dumps(heatmap.model_dump(), indent=2)
    
    @staticmethod
    def stakeholder_network_to_json(network: StakeholderNetwork) -> str:
        """Convert a stakeholder network to JSON format.
        
        Args:
            network: StakeholderNetwork to convert
            
        Returns:
            JSON string
        """
        return json.dumps(network.model_dump(), indent=2)
    
    @staticmethod
    def influence_interest_matrix_to_markdown(matrix: StakeholderMatrix) -> str:
        """Convert an influence/interest matrix to Markdown format.
        
        Args:
            matrix: StakeholderMatrix to convert
            
        Returns:
            Markdown string
        """
        md = "# Stakeholder Influence/Interest Matrix\n\n"
        
        # Create quadrants
        high_influence_high_interest = []
        high_influence_low_interest = []
        low_influence_high_interest = []
        low_influence_low_interest = []
        
        for item in matrix.items:
            if item.position_y >= 0.5 and item.position_x >= 0.5:
                high_influence_high_interest.append(item)
            elif item.position_y >= 0.5 and item.position_x < 0.5:
                high_influence_low_interest.append(item)
            elif item.position_y < 0.5 and item.position_x >= 0.5:
                low_influence_high_interest.append(item)
            else:
                low_influence_low_interest.append(item)
        
        # High Influence, High Interest
        md += "## High Influence, High Interest (Manage Closely)\n\n"
        if high_influence_high_interest:
            md += "| Stakeholder | Role | Organization | Interest |\n"
            md += "|-------------|------|--------------|----------|\n"
            
            for item in sorted(high_influence_high_interest, key=lambda i: i.name):
                organization = item.organization or "N/A"
                interest = f"{item.position_x:.2f}"
                md += f"| {item.name} | {item.role} | {organization} | {interest} |\n"
        else:
            md += "No stakeholders in this quadrant.\n"
        
        md += "\n"
        
        # High Influence, Low Interest
        md += "## High Influence, Low Interest (Keep Satisfied)\n\n"
        if high_influence_low_interest:
            md += "| Stakeholder | Role | Organization | Interest |\n"
            md += "|-------------|------|--------------|----------|\n"
            
            for item in sorted(high_influence_low_interest, key=lambda i: i.name):
                organization = item.organization or "N/A"
                interest = f"{item.position_x:.2f}"
                md += f"| {item.name} | {item.role} | {organization} | {interest} |\n"
        else:
            md += "No stakeholders in this quadrant.\n"
        
        md += "\n"
        
        # Low Influence, High Interest
        md += "## Low Influence, High Interest (Keep Informed)\n\n"
        if low_influence_high_interest:
            md += "| Stakeholder | Role | Organization | Interest |\n"
            md += "|-------------|------|--------------|----------|\n"
            
            for item in sorted(low_influence_high_interest, key=lambda i: i.name):
                organization = item.organization or "N/A"
                interest = f"{item.position_x:.2f}"
                md += f"| {item.name} | {item.role} | {organization} | {interest} |\n"
        else:
            md += "No stakeholders in this quadrant.\n"
        
        md += "\n"
        
        # Low Influence, Low Interest
        md += "## Low Influence, Low Interest (Monitor)\n\n"
        if low_influence_low_interest:
            md += "| Stakeholder | Role | Organization | Interest |\n"
            md += "|-------------|------|--------------|----------|\n"
            
            for item in sorted(low_influence_low_interest, key=lambda i: i.name):
                organization = item.organization or "N/A"
                interest = f"{item.position_x:.2f}"
                md += f"| {item.name} | {item.role} | {organization} | {interest} |\n"
        else:
            md += "No stakeholders in this quadrant.\n"
        
        return md
    
    @staticmethod
    def stakeholder_alignment_to_markdown(alignments: List[StakeholderAlignment]) -> str:
        """Convert stakeholder alignments to Markdown format.
        
        Args:
            alignments: List of StakeholderAlignment to convert
            
        Returns:
            Markdown string
        """
        if not alignments:
            return "# Stakeholder Alignment\n\nNo alignment data available."
        
        md = "# Stakeholder Alignment\n\n"
        
        # Extract objective names from the first alignment
        objective_ids = list(alignments[0].alignment_scores.keys())
        
        # Create the table header
        md += "| Stakeholder | " + " | ".join(objective_ids) + " | Overall |\n"
        md += "|-------------|" + "".join("-----|" for _ in range(len(objective_ids) + 1)) + "\n"
        
        # Add each stakeholder row
        for alignment in alignments:
            row = f"| {alignment.stakeholder_name} |"
            
            for obj_id in objective_ids:
                score = alignment.alignment_scores.get(obj_id, 0.0)
                row += f" {score:.2f} |"
            
            row += f" {alignment.overall_alignment:.2f} |"
            md += row + "\n"
        
        return md
    
    @staticmethod
    def stakeholder_groups_to_markdown(groups: List[StakeholderGroup]) -> str:
        """Convert stakeholder groups to Markdown format.
        
        Args:
            groups: List of StakeholderGroup to convert
            
        Returns:
            Markdown string
        """
        md = "# Stakeholder Groups\n\n"
        
        for group in sorted(groups, key=lambda g: g.name):
            md += f"## {group.name}\n\n"
            
            if group.description:
                md += f"{group.description}\n\n"
            
            md += f"**Number of stakeholders:** {len(group.stakeholder_ids)}\n\n"
        
        return md
    
    @staticmethod
    def create_stakeholder_profile_markdown(
        stakeholder: Stakeholder, 
        perspectives: Optional[List[StakeholderPerspective]] = None
    ) -> str:
        """Create a detailed Markdown profile for a stakeholder.
        
        Args:
            stakeholder: Stakeholder to profile
            perspectives: Optional list of stakeholder perspectives
            
        Returns:
            Markdown string
        """
        md = f"# Stakeholder Profile: {stakeholder.name}\n\n"
        
        # Basic information
        md += "## Basic Information\n\n"
        
        if stakeholder.organization:
            md += f"**Organization:** {stakeholder.organization}\n\n"
        
        md += f"**Role:** {stakeholder.role.value}\n\n"
        md += f"**Influence:** {stakeholder.influence.value}\n\n"
        
        if stakeholder.email:
            md += f"**Email:** {stakeholder.email}\n\n"
        
        # Key concerns
        if stakeholder.key_concerns:
            md += "## Key Concerns\n\n"
            for concern in stakeholder.key_concerns:
                md += f"- {concern}\n"
            md += "\n"
        
        # Communication preferences
        if stakeholder.communication_preferences:
            md += "## Communication Preferences\n\n"
            md += f"{stakeholder.communication_preferences}\n\n"
        
        # Feature preferences
        if stakeholder.feature_preferences:
            md += "## Feature Preferences\n\n"
            md += "| Feature | Preference |\n"
            md += "|---------|------------|\n"
            
            # Sort by preference (high to low)
            sorted_preferences = sorted(
                stakeholder.feature_preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for feature_id, preference in sorted_preferences:
                md += f"| Feature {feature_id} | {preference:.2f} |\n"
            
            md += "\n"
        
        # Objective alignment
        if stakeholder.objective_alignment:
            md += "## Objective Alignment\n\n"
            md += "| Objective | Alignment |\n"
            md += "|-----------|------------|\n"
            
            # Sort by alignment (high to low)
            sorted_alignment = sorted(
                stakeholder.objective_alignment.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for objective_id, alignment in sorted_alignment:
                md += f"| Objective {objective_id} | {alignment:.2f} |\n"
            
            md += "\n"
        
        # Perspectives
        if perspectives:
            md += "## Perspectives\n\n"
            
            # Sort by date (newest first)
            sorted_perspectives = sorted(
                perspectives,
                key=lambda p: p.date_recorded,
                reverse=True
            )
            
            for perspective in sorted_perspectives:
                md += f"### {perspective.topic}\n\n"
                md += f"**Date:** {perspective.date_recorded.strftime('%Y-%m-%d')}\n\n"
                md += f"**Sentiment:** {perspective.sentiment.value}\n\n"
                md += f"**Perspective:**\n\n{perspective.perspective}\n\n"
                
                if perspective.context:
                    md += f"**Context:**\n\n{perspective.context}\n\n"
                
                md += "---\n\n"
        
        # Engagement history
        if stakeholder.engagement_history:
            md += "## Engagement History\n\n"
            
            for entry in reversed(stakeholder.engagement_history):
                md += f"- {entry}\n"
            
            md += "\n"
        
        # Notes
        if stakeholder.notes:
            md += "## Notes\n\n"
            md += f"{stakeholder.notes}\n\n"

        return md


def create_alignment_chart(stakeholders: List[Stakeholder], alignments: List[StakeholderAlignment]) -> str:
    """Create a stakeholder alignment chart.

    Args:
        stakeholders: List of stakeholders to include
        alignments: List of stakeholder alignments

    Returns:
        Markdown string with the alignment chart
    """
    visualizer = StakeholderVisualizer()
    return visualizer.stakeholder_alignment_to_markdown(alignments)


def create_stakeholder_map(stakeholders: List[Stakeholder], feature_id: Optional[UUID] = None) -> str:
    """Create a stakeholder influence/interest map.

    Args:
        stakeholders: List of stakeholders to include
        feature_id: Optional feature ID to measure interest for

    Returns:
        Markdown string with the stakeholder map
    """
    visualizer = StakeholderVisualizer()
    matrix = visualizer.create_influence_interest_matrix(stakeholders, feature_id)
    return visualizer.influence_interest_matrix_to_markdown(matrix)


def create_perspective_heatmap(
    perspectives: List[StakeholderPerspective],
    stakeholders: List[Stakeholder],
    topics: List[str]
) -> str:
    """Create a stakeholder perspective heatmap visualization.

    Args:
        perspectives: List of stakeholder perspectives
        stakeholders: List of stakeholders
        topics: List of topics

    Returns:
        JSON string with the perspective heatmap
    """
    visualizer = StakeholderVisualizer()
    heatmap = visualizer.create_perspective_heatmap(perspectives, stakeholders, topics)
    return visualizer.stakeholder_heatmap_to_json(heatmap)