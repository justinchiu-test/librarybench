"""
Prioritization visualization module for ProductInsight.

This module provides functionality for visualizing feature prioritization data
in various formats, including charts, tables, and matrices.
"""

import json
from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from product_insight.models import Feature, PriorityScoreCard, StatusEnum


class ValueEffortQuadrant(BaseModel):
    """Representation of a value/effort quadrant."""
    
    high_value_low_effort: List[Tuple[Feature, float]] = Field(default_factory=list)
    high_value_high_effort: List[Tuple[Feature, float]] = Field(default_factory=list)
    low_value_low_effort: List[Tuple[Feature, float]] = Field(default_factory=list)
    low_value_high_effort: List[Tuple[Feature, float]] = Field(default_factory=list)


class PrioritizationComparison(BaseModel):
    """Comparison of prioritization methods."""
    
    feature_id: str
    feature_name: str
    methods: Dict[str, float] = Field(default_factory=dict)


class PrioritizationTimeline(BaseModel):
    """Timeline of priority changes."""
    
    feature_id: str
    feature_name: str
    status: str
    timestamps: List[str] = Field(default_factory=list)
    scores: List[float] = Field(default_factory=list)
    methods: List[str] = Field(default_factory=list)


class PrioritizationVisualizer:
    """Visualizes feature prioritization data."""
    
    @staticmethod
    def create_value_effort_matrix(
        features: List[Feature], threshold: float = 5.0
    ) -> ValueEffortQuadrant:
        """Create a value/effort matrix.
        
        Args:
            features: List of features
            threshold: Threshold for high/low classification
            
        Returns:
            ValueEffortQuadrant with features in each quadrant
        """
        quadrant = ValueEffortQuadrant()
        
        for feature in features:
            value = feature.value_estimate or 0.0
            effort = feature.effort_estimate or 0.0
            
            if value >= threshold and effort < threshold:
                quadrant.high_value_low_effort.append((feature, feature.priority_score or 0.0))
            elif value >= threshold and effort >= threshold:
                quadrant.high_value_high_effort.append((feature, feature.priority_score or 0.0))
            elif value < threshold and effort < threshold:
                quadrant.low_value_low_effort.append((feature, feature.priority_score or 0.0))
            else:
                quadrant.low_value_high_effort.append((feature, feature.priority_score or 0.0))
        
        # Sort each quadrant by score
        for quadrant_list in [
            quadrant.high_value_low_effort,
            quadrant.high_value_high_effort,
            quadrant.low_value_low_effort,
            quadrant.low_value_high_effort
        ]:
            quadrant_list.sort(key=lambda x: x[1], reverse=True)
        
        return quadrant
    
    @staticmethod
    def create_method_comparison(
        feature: Feature, 
        scorecards: Dict[str, PriorityScoreCard]
    ) -> PrioritizationComparison:
        """Create a comparison of prioritization methods for a feature.
        
        Args:
            feature: Feature to compare
            scorecards: Dictionary mapping method names to scorecards
            
        Returns:
            PrioritizationComparison with method scores
        """
        comparison = PrioritizationComparison(
            feature_id=str(feature.id),
            feature_name=feature.name
        )
        
        for method, scorecard in scorecards.items():
            comparison.methods[method] = scorecard.total_score or 0.0
        
        return comparison
    
    @staticmethod
    def create_priority_distribution(
        features: List[Feature], 
        bins: int = 10
    ) -> Dict[str, int]:
        """Create a distribution of priority scores.
        
        Args:
            features: List of features
            bins: Number of bins in the distribution
            
        Returns:
            Dictionary mapping score ranges to counts
        """
        # Filter features with priority scores
        scored_features = [f for f in features if f.priority_score is not None]
        
        if not scored_features:
            return {}
        
        # Find min and max scores
        min_score = min(f.priority_score or 0.0 for f in scored_features)
        max_score = max(f.priority_score or 0.0 for f in scored_features)
        
        # Create bins
        bin_size = (max_score - min_score) / bins if bins > 0 and max_score > min_score else 1.0
        distribution = {}
        
        for i in range(bins):
            lower = min_score + i * bin_size
            upper = min_score + (i + 1) * bin_size
            bin_label = f"{lower:.1f}-{upper:.1f}"
            distribution[bin_label] = 0
        
        # Count features in each bin
        for feature in scored_features:
            score = feature.priority_score or 0.0
            for i in range(bins):
                lower = min_score + i * bin_size
                upper = min_score + (i + 1) * bin_size
                if lower <= score < upper or (i == bins - 1 and score == upper):
                    bin_label = f"{lower:.1f}-{upper:.1f}"
                    distribution[bin_label] = distribution.get(bin_label, 0) + 1
                    break
        
        return distribution
    
    @staticmethod
    def value_effort_matrix_to_markdown(matrix: ValueEffortQuadrant) -> str:
        """Convert a value/effort matrix to Markdown format.
        
        Args:
            matrix: ValueEffortQuadrant to convert
            
        Returns:
            Markdown string
        """
        md = "# Value/Effort Matrix\n\n"
        
        # Create the matrix
        md += "## High Value, Low Effort (Do First)\n\n"
        if matrix.high_value_low_effort:
            md += "| Feature | Value | Effort | Priority Score |\n"
            md += "|---------|-------|--------|---------------|\n"
            for feature, score in matrix.high_value_low_effort:
                md += f"| {feature.name} | {feature.value_estimate or 'N/A'} | {feature.effort_estimate or 'N/A'} | {score:.2f} |\n"
        else:
            md += "No features in this quadrant.\n"
        
        md += "\n## High Value, High Effort (Plan)\n\n"
        if matrix.high_value_high_effort:
            md += "| Feature | Value | Effort | Priority Score |\n"
            md += "|---------|-------|--------|---------------|\n"
            for feature, score in matrix.high_value_high_effort:
                md += f"| {feature.name} | {feature.value_estimate or 'N/A'} | {feature.effort_estimate or 'N/A'} | {score:.2f} |\n"
        else:
            md += "No features in this quadrant.\n"
        
        md += "\n## Low Value, Low Effort (Quick Wins)\n\n"
        if matrix.low_value_low_effort:
            md += "| Feature | Value | Effort | Priority Score |\n"
            md += "|---------|-------|--------|---------------|\n"
            for feature, score in matrix.low_value_low_effort:
                md += f"| {feature.name} | {feature.value_estimate or 'N/A'} | {feature.effort_estimate or 'N/A'} | {score:.2f} |\n"
        else:
            md += "No features in this quadrant.\n"
        
        md += "\n## Low Value, High Effort (Avoid)\n\n"
        if matrix.low_value_high_effort:
            md += "| Feature | Value | Effort | Priority Score |\n"
            md += "|---------|-------|--------|---------------|\n"
            for feature, score in matrix.low_value_high_effort:
                md += f"| {feature.name} | {feature.value_estimate or 'N/A'} | {feature.effort_estimate or 'N/A'} | {score:.2f} |\n"
        else:
            md += "No features in this quadrant.\n"
        
        return md
    
    @staticmethod
    def method_comparison_to_markdown(
        comparisons: List[PrioritizationComparison]
    ) -> str:
        """Convert method comparisons to Markdown format.
        
        Args:
            comparisons: List of PrioritizationComparison to convert
            
        Returns:
            Markdown string
        """
        if not comparisons:
            return "# Method Comparison\n\nNo comparisons available."
        
        md = "# Method Comparison\n\n"
        
        # Get all methods
        all_methods = set()
        for comp in comparisons:
            all_methods.update(comp.methods.keys())
        
        # Create the table
        md += "| Feature | " + " | ".join(all_methods) + " |\n"
        md += "|---------|" + "".join("-----|" for _ in all_methods) + "\n"
        
        for comp in comparisons:
            row = f"| {comp.feature_name} |"
            for method in all_methods:
                score = comp.methods.get(method, "N/A")
                if isinstance(score, (int, float)):
                    row += f" {score:.2f} |"
                else:
                    row += f" {score} |"
            md += row + "\n"
        
        return md
    
    @staticmethod
    def priority_distribution_to_json(distribution: Dict[str, int]) -> str:
        """Convert a priority distribution to JSON format.
        
        Args:
            distribution: Dictionary mapping score ranges to counts
            
        Returns:
            JSON string
        """
        # Convert to a format suitable for visualization
        chart_data = [
            {"range": range_label, "count": count}
            for range_label, count in distribution.items()
        ]
        
        return json.dumps(chart_data, indent=2)
    
    @staticmethod
    def create_status_distribution(features: List[Feature]) -> Dict[str, int]:
        """Create a distribution of feature statuses.
        
        Args:
            features: List of features
            
        Returns:
            Dictionary mapping status names to counts
        """
        distribution = {}
        
        for feature in features:
            status = feature.status.value if feature.status else "unknown"
            distribution[status] = distribution.get(status, 0) + 1
        
        return distribution
    
    @staticmethod
    def status_distribution_to_json(distribution: Dict[str, int]) -> str:
        """Convert a status distribution to JSON format.
        
        Args:
            distribution: Dictionary mapping status names to counts
            
        Returns:
            JSON string
        """
        # Convert to a format suitable for visualization
        chart_data = [
            {"status": status, "count": count}
            for status, count in distribution.items()
        ]
        
        return json.dumps(chart_data, indent=2)