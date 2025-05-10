"""
Competitive visualization module for ProductInsight.

This module provides functionality for visualizing competitive analysis data
in various formats, including charts, tables, and matrices.
"""

import json
from typing import Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field

from product_insight.competitive.analysis import (
    CompetitorFeatureMatrix,
    MarketSegmentDistribution,
    PricingComparison,
)
from product_insight.models import Competitor


class CompetitiveVisualizer:
    """Visualizes competitive analysis data."""
    
    @staticmethod
    def feature_matrix_to_markdown(matrix: CompetitorFeatureMatrix) -> str:
        """Convert a feature matrix to Markdown format.
        
        Args:
            matrix: CompetitorFeatureMatrix to convert
            
        Returns:
            Markdown string
        """
        md = "# Competitive Feature Matrix\n\n"
        
        # Create the table header
        md += "| Feature | " + " | ".join(matrix.competitors) + " |\n"
        md += "|---------|" + "".join("-----|" for _ in matrix.competitors) + "\n"
        
        # Add each feature row
        for feature in matrix.features:
            row = f"| {feature} |"
            for comp in matrix.competitors:
                has_feature = matrix.matrix[comp].get(feature, False)
                mark = "✓" if has_feature else " "
                row += f" {mark} |"
            md += row + "\n"
        
        return md
    
    @staticmethod
    def feature_matrix_to_csv(matrix: CompetitorFeatureMatrix) -> str:
        """Convert a feature matrix to CSV format.
        
        Args:
            matrix: CompetitorFeatureMatrix to convert
            
        Returns:
            CSV string
        """
        # Create the header row
        csv = "Feature," + ",".join(matrix.competitors) + "\n"
        
        # Add each feature row
        for feature in matrix.features:
            row = f'"{feature}",'
            values = []
            for comp in matrix.competitors:
                has_feature = matrix.matrix[comp].get(feature, False)
                values.append("Yes" if has_feature else "No")
            row += ",".join(values)
            csv += row + "\n"
        
        return csv
    
    @staticmethod
    def feature_matrix_to_json(matrix: CompetitorFeatureMatrix) -> str:
        """Convert a feature matrix to JSON format.
        
        Args:
            matrix: CompetitorFeatureMatrix to convert
            
        Returns:
            JSON string
        """
        return json.dumps(matrix.model_dump(), indent=2)
    
    @staticmethod
    def market_segment_to_markdown(distribution: MarketSegmentDistribution) -> str:
        """Convert a market segment distribution to Markdown format.
        
        Args:
            distribution: MarketSegmentDistribution to convert
            
        Returns:
            Markdown string
        """
        md = "# Market Segment Distribution\n\n"
        
        for segment, competitors in sorted(distribution.segments.items()):
            md += f"## {segment}\n\n"
            if competitors:
                md += "- " + "\n- ".join(sorted(competitors)) + "\n\n"
            else:
                md += "No competitors in this segment.\n\n"
        
        return md
    
    @staticmethod
    def market_segment_to_json(distribution: MarketSegmentDistribution) -> str:
        """Convert a market segment distribution to JSON format.
        
        Args:
            distribution: MarketSegmentDistribution to convert
            
        Returns:
            JSON string
        """
        return json.dumps(distribution.model_dump(), indent=2)
    
    @staticmethod
    def pricing_comparison_to_markdown(comparison: PricingComparison) -> str:
        """Convert a pricing comparison to Markdown format.
        
        Args:
            comparison: PricingComparison to convert
            
        Returns:
            Markdown string
        """
        md = "# Pricing Comparison\n\n"
        
        # Create the pricing model table
        md += "## Pricing Models\n\n"
        md += "| Competitor | Pricing Model |\n"
        md += "|------------|---------------|\n"
        
        for comp in comparison.competitors:
            model = comparison.pricing_models.get(comp, "Unknown")
            md += f"| {comp} | {model} |\n"
        
        # Create detailed pricing tables if available
        if any(comparison.pricing_details.values()):
            md += "\n## Pricing Details\n\n"
            
            for comp in comparison.competitors:
                if comp in comparison.pricing_details and comparison.pricing_details[comp]:
                    md += f"### {comp}\n\n"
                    md += "| Plan | Price |\n"
                    md += "|------|-------|\n"
                    
                    for plan, price in comparison.pricing_details[comp].items():
                        md += f"| {plan} | {price} |\n"
                    
                    md += "\n"
        
        return md
    
    @staticmethod
    def feature_gaps_to_markdown(gaps: Dict[str, List[str]]) -> str:
        """Convert feature gaps to Markdown format.
        
        Args:
            gaps: Dictionary mapping competitors to feature gaps
            
        Returns:
            Markdown string
        """
        md = "# Feature Gaps Analysis\n\n"
        
        if not gaps:
            md += "No feature gaps identified.\n"
            return md
        
        for competitor, features in gaps.items():
            md += f"## {competitor}\n\n"
            if features:
                md += "Features they have that we don't:\n\n"
                md += "- " + "\n- ".join(features) + "\n\n"
            else:
                md += "No feature gaps identified for this competitor.\n\n"
        
        return md
    
    @staticmethod
    def competitive_advantages_to_markdown(advantages: Dict[str, List[str]]) -> str:
        """Convert competitive advantages to Markdown format.
        
        Args:
            advantages: Dictionary mapping competitors to competitive advantages
            
        Returns:
            Markdown string
        """
        md = "# Competitive Advantages Analysis\n\n"
        
        if not advantages:
            md += "No competitive advantages identified.\n"
            return md
        
        for competitor, features in advantages.items():
            md += f"## {competitor}\n\n"
            if features:
                md += "Features we have that they don't:\n\n"
                md += "- " + "\n- ".join(features) + "\n\n"
            else:
                md += "No competitive advantages identified against this competitor.\n\n"
        
        return md
    
    @staticmethod
    def whitespace_opportunities_to_markdown(
        opportunities: List[Tuple[str, List[str]]]
    ) -> str:
        """Convert whitespace opportunities to Markdown format.
        
        Args:
            opportunities: List of (segment, reasons) tuples
            
        Returns:
            Markdown string
        """
        md = "# Whitespace Opportunities\n\n"
        
        if not opportunities:
            md += "No whitespace opportunities identified.\n"
            return md
        
        for segment, reasons in opportunities:
            md += f"## {segment}\n\n"
            md += "Reasons this is an opportunity:\n\n"
            md += "- " + "\n- ".join(reasons) + "\n\n"
        
        return md
    
    @staticmethod
    def threat_categories_to_markdown(
        categories: Dict[str, List[Competitor]]
    ) -> str:
        """Convert threat categories to Markdown format.
        
        Args:
            categories: Dictionary mapping threat levels to competitors
            
        Returns:
            Markdown string
        """
        md = "# Competitors by Threat Level\n\n"
        
        # Define the order of categories
        order = ["high", "medium", "low", "unknown"]
        
        for level in order:
            competitors = categories.get(level, [])
            md += f"## {level.capitalize()} Threat\n\n"
            
            if not competitors:
                md += "No competitors in this category.\n\n"
                continue
            
            md += "| Competitor | Strengths | Weaknesses |\n"
            md += "|------------|-----------|------------|\n"
            
            for comp in sorted(competitors, key=lambda c: c.name):
                strengths = ", ".join(comp.strengths[:3]) if comp.strengths else "N/A"
                weaknesses = ", ".join(comp.weaknesses[:3]) if comp.weaknesses else "N/A"
                md += f"| {comp.name} | {strengths} | {weaknesses} |\n"
            
            md += "\n"
        
        return md
    
    @staticmethod
    def create_competitor_profile_markdown(competitor: Competitor) -> str:
        """Create a detailed Markdown profile for a competitor.
        
        Args:
            competitor: Competitor to profile
            
        Returns:
            Markdown string
        """
        md = f"# Competitor Profile: {competitor.name}\n\n"
        
        # Basic information
        md += "## Overview\n\n"
        if competitor.description:
            md += f"{competitor.description}\n\n"
        
        if competitor.website:
            md += f"**Website:** [{competitor.website}]({competitor.website})\n\n"
        
        # Market information
        md += "### Market Position\n\n"
        
        if competitor.market_share is not None:
            md += f"**Market Share:** {competitor.market_share:.1f}%\n\n"
        
        if competitor.target_segments:
            md += "**Target Segments:**\n\n"
            md += "- " + "\n- ".join(competitor.target_segments) + "\n\n"
        
        # Pricing
        md += "### Pricing\n\n"
        
        if competitor.pricing_model:
            md += f"**Model:** {competitor.pricing_model}\n\n"
        
        if competitor.pricing_details:
            md += f"**Details:** {competitor.pricing_details}\n\n"
        
        # Strengths and Weaknesses
        md += "## Analysis\n\n"
        
        if competitor.strengths:
            md += "### Strengths\n\n"
            md += "- " + "\n- ".join(competitor.strengths) + "\n\n"
        
        if competitor.weaknesses:
            md += "### Weaknesses\n\n"
            md += "- " + "\n- ".join(competitor.weaknesses) + "\n\n"
        
        # Feature comparison
        if competitor.feature_comparison:
            md += "### Feature Comparison\n\n"
            md += "| Feature | Status |\n"
            md += "|---------|--------|\n"
            
            for feature, has_feature in sorted(competitor.feature_comparison.items()):
                status = "✓" if has_feature else "✗"
                md += f"| {feature} | {status} |\n"
            
            md += "\n"
        
        # Detailed comparisons
        if competitor.detailed_comparisons:
            md += "### Detailed Comparisons\n\n"
            
            for feature, details in sorted(competitor.detailed_comparisons.items()):
                md += f"**{feature}:** {details}\n\n"
        
        # Threat level
        if competitor.threat_level is not None:
            level = "Low"
            if competitor.threat_level >= 0.7:
                level = "High"
            elif competitor.threat_level >= 0.4:
                level = "Medium"
            
            md += f"### Threat Assessment: {level}\n\n"
            md += f"**Score:** {competitor.threat_level:.1f}/1.0\n\n"
        
        # Notes
        if competitor.notes:
            md += "## Notes\n\n"
            md += f"{competitor.notes}\n\n"
        
        return md