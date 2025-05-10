"""
Knowledge visualization module for ProductInsight.

This module provides functionality for visualizing insights, search results,
and related knowledge in various formats.
"""

import json
from typing import Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field

from product_insight.discovery.insights import Insight, InsightGroup, TrendData
from product_insight.models import SearchResult, SearchResults


class InsightVisualization(BaseModel):
    """Visualization data for insights."""
    
    title: str
    insights: List[Dict] = Field(default_factory=list)
    type: str = "bubble_chart"


class TrendVisualization(BaseModel):
    """Visualization data for trends."""
    
    title: str
    labels: List[str] = Field(default_factory=list)
    datasets: List[Dict] = Field(default_factory=list)
    type: str = "line_chart"


class ConnectionGraph(BaseModel):
    """Visualization data for entity connections."""
    
    nodes: List[Dict] = Field(default_factory=list)
    links: List[Dict] = Field(default_factory=list)


class DiscoveryVisualizer:
    """Visualizes knowledge discovery data."""
    
    @staticmethod
    def create_insight_visualization(
        insight_groups: List[InsightGroup]
    ) -> InsightVisualization:
        """Create a visualization of insights.
        
        Args:
            insight_groups: List of insight groups
            
        Returns:
            InsightVisualization for rendering
        """
        viz = InsightVisualization(
            title="Product Insights Overview"
        )
        
        # Convert insights to visualization-friendly format
        for group in insight_groups:
            for insight in group.insights:
                viz_insight = {
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "type": insight.insight_type,
                    "group": group.title,
                    "tags": insight.tags,
                    "size": 10 + (insight.confidence * 20),  # Size based on confidence
                }
                
                viz.insights.append(viz_insight)
        
        return viz
    
    @staticmethod
    def create_trend_visualization(trend_data: TrendData) -> TrendVisualization:
        """Create a visualization of trend data.
        
        Args:
            trend_data: Trend data to visualize
            
        Returns:
            TrendVisualization for rendering
        """
        viz = TrendVisualization(
            title=trend_data.title,
            labels=trend_data.time_periods
        )
        
        # Create datasets for each series
        colors = [
            "#4285F4",  # Blue
            "#DB4437",  # Red
            "#F4B400",  # Yellow
            "#0F9D58",  # Green
            "#AB47BC",  # Purple
            "#00ACC1",  # Cyan
            "#FF7043",  # Orange
        ]
        
        for i, (series_name, values) in enumerate(trend_data.series.items()):
            color_index = i % len(colors)
            
            dataset = {
                "label": series_name,
                "data": values,
                "borderColor": colors[color_index],
                "backgroundColor": colors[color_index] + "40",  # Add transparency
                "fill": False,
                "tension": 0.4  # Smooth lines
            }
            
            viz.datasets.append(dataset)
        
        return viz
    
    @staticmethod
    def create_connection_graph(
        entities: Dict[str, List[Dict]], 
        central_entity: Dict
    ) -> ConnectionGraph:
        """Create a connection graph visualization.
        
        Args:
            entities: Dictionary of related entities by type
            central_entity: The central entity for the graph
            
        Returns:
            ConnectionGraph for rendering
        """
        graph = ConnectionGraph()
        
        # Add central node
        central_node = {
            "id": central_entity["id"],
            "label": central_entity.get("title", "") or central_entity.get("name", "Entity"),
            "type": central_entity["type"],
            "size": 20,  # Larger size for central node
            "color": "#4285F4"  # Blue
        }
        
        graph.nodes.append(central_node)
        
        # Color mapping for entity types
        type_colors = {
            "feedback": "#DB4437",    # Red
            "feature": "#0F9D58",     # Green
            "objective": "#F4B400",   # Yellow
            "decision": "#AB47BC",    # Purple
            "competitor": "#00ACC1",  # Cyan
            "stakeholder": "#FF7043", # Orange
            "perspective": "#9E9E9E"  # Grey
        }
        
        # Add related entity nodes and links
        for entity_type, entity_list in entities.items():
            color = type_colors.get(entity_type, "#9E9E9E")  # Default to grey
            
            for i, entity in enumerate(entity_list):
                if i >= 10:  # Limit to 10 entities per type to avoid clutter
                    break
                
                entity_id = entity.get("id", f"{entity_type}_{i}")
                
                # Add node
                node = {
                    "id": entity_id,
                    "label": entity.get("title", "") or entity.get("name", f"{entity_type.capitalize()} {i+1}"),
                    "type": entity_type,
                    "size": 10,  # Standard size for related nodes
                    "color": color
                }
                
                graph.nodes.append(node)
                
                # Add link to central node
                link = {
                    "source": central_entity["id"],
                    "target": entity_id,
                    "type": "related",
                    "value": 1
                }
                
                graph.links.append(link)
        
        return graph
    
    @staticmethod
    def create_search_results_visualization(
        results: SearchResults
    ) -> Dict:
        """Create a visualization of search results.
        
        Args:
            results: Search results to visualize
            
        Returns:
            Dictionary with visualization data
        """
        # Group results by entity type
        results_by_type = {}
        
        for result in results.results:
            entity_type = result.entity_type
            
            if entity_type not in results_by_type:
                results_by_type[entity_type] = []
            
            results_by_type[entity_type].append({
                "id": str(result.entity_id),
                "title": result.title,
                "snippet": result.snippet,
                "score": result.relevance_score,
                "date": result.date.isoformat() if result.date else None,
                "tags": [tag.name for tag in result.tags]
            })
        
        # Return structured data for rendering
        return {
            "query": results.query,
            "total_count": results.total_count,
            "execution_time_ms": results.execution_time_ms,
            "results_by_type": results_by_type,
            "facets": results.facets
        }
    
    @staticmethod
    def insights_to_markdown(insight_groups: List[InsightGroup]) -> str:
        """Convert insights to Markdown format.
        
        Args:
            insight_groups: List of insight groups
            
        Returns:
            Markdown string
        """
        if not insight_groups:
            return "# Product Insights\n\nNo insights available."
        
        md = "# Product Insights\n\n"
        md += f"Generated: {insight_groups[0].insights[0].generated_at.strftime('%Y-%m-%d %H:%M') if insight_groups[0].insights else 'N/A'}\n\n"
        
        total_insights = sum(len(group.insights) for group in insight_groups)
        md += f"Total insights: {total_insights}\n\n"
        
        for group in insight_groups:
            md += f"## {group.title}\n\n"
            
            for insight in group.insights:
                confidence = f"{insight.confidence:.0%}" if insight.confidence is not None else "N/A"
                md += f"### {insight.title} ({confidence} confidence)\n\n"
                md += f"{insight.description}\n\n"
                
                if insight.tags:
                    md += f"**Tags:** {', '.join(insight.tags)}\n\n"
                
                # Add source entities if available and not too many
                if insight.source_entities and len(insight.source_entities) <= 5:
                    md += "**Sources:**\n\n"
                    
                    for entity in insight.source_entities:
                        entity_type = entity.get("type", "unknown")
                        
                        if entity_type == "feedback":
                            md += f"- Feedback: \"{entity.get('text', 'N/A')}\"\n"
                        elif entity_type == "feature":
                            md += f"- Feature: {entity.get('name', 'N/A')}\n"
                        elif entity_type == "objective":
                            md += f"- Objective: {entity.get('name', 'N/A')}\n"
                        elif entity_type == "decision":
                            md += f"- Decision: {entity.get('title', 'N/A')}\n"
                        elif entity_type == "stakeholder":
                            md += f"- Stakeholder: {entity.get('name', 'N/A')}\n"
                        elif entity_type == "competitor":
                            md += f"- Competitor: {entity.get('name', 'N/A')}\n"
                        elif entity_type == "feedback_cluster":
                            md += f"- Feedback Cluster: {entity.get('name', 'N/A')}\n"
                        elif entity_type == "strength" or entity_type == "concern":
                            md += f"- {entity_type.capitalize()}: {entity.get('text') or entity.get('name', 'N/A')}\n"
                        else:
                            md += f"- {entity_type.capitalize()}: {str(entity)}\n"
                    
                    md += "\n"
                
                md += "---\n\n"
        
        return md
    
    @staticmethod
    def trends_to_markdown(trends: List[TrendData]) -> str:
        """Convert trend data to Markdown format.
        
        Args:
            trends: List of trend data
            
        Returns:
            Markdown string
        """
        if not trends:
            return "# Trend Analysis\n\nNo trend data available."
        
        md = "# Trend Analysis\n\n"
        
        for trend in trends:
            md += f"## {trend.title}\n\n"
            
            # Create a table representation of the trend
            md += "| Period |"
            for series_name in trend.series.keys():
                md += f" {series_name} |"
            md += "\n"
            
            md += "|--------|"
            for _ in trend.series.keys():
                md += "--------|"
            md += "\n"
            
            for i, period in enumerate(trend.time_periods):
                md += f"| {period} |"
                
                for series_name, values in trend.series.items():
                    value = values[i] if i < len(values) else "N/A"
                    
                    # Format value based on type
                    if isinstance(value, float):
                        if "progress" in series_name.lower() or "percent" in series_name.lower():
                            formatted_value = f"{value:.1f}%"
                        else:
                            formatted_value = f"{value:.1f}"
                    else:
                        formatted_value = str(value)
                    
                    md += f" {formatted_value} |"
                
                md += "\n"
            
            md += "\n\n"
        
        return md
    
    @staticmethod
    def search_results_to_markdown(results: SearchResults) -> str:
        """Convert search results to Markdown format.
        
        Args:
            results: Search results to convert
            
        Returns:
            Markdown string
        """
        md = f"# Search Results: '{results.query}'\n\n"
        md += f"Found {results.total_count} results in {results.execution_time_ms} ms\n\n"
        
        # Group by entity type
        results_by_type = {}
        
        for result in results.results:
            entity_type = result.entity_type
            
            if entity_type not in results_by_type:
                results_by_type[entity_type] = []
            
            results_by_type[entity_type].append(result)
        
        # Generate markdown for each entity type
        for entity_type, type_results in results_by_type.items():
            md += f"## {entity_type.capitalize()} ({len(type_results)})\n\n"
            
            for result in type_results:
                md += f"### {result.title}\n\n"
                md += f"**Relevance:** {result.relevance_score:.2f}\n\n"
                md += f"{result.snippet}\n\n"
                
                if result.tags:
                    tag_names = [tag.name for tag in result.tags]
                    md += f"**Tags:** {', '.join(tag_names)}\n\n"
                
                if result.date:
                    md += f"**Date:** {result.date.strftime('%Y-%m-%d')}\n\n"
                
                md += "---\n\n"
        
        return md
    
    @staticmethod
    def insights_to_json(insight_groups: List[InsightGroup]) -> str:
        """Convert insights to JSON format.
        
        Args:
            insight_groups: List of insight groups
            
        Returns:
            JSON string
        """
        # Convert to dictionary structure suitable for JSON
        groups_dict = []
        
        for group in insight_groups:
            insights_list = []
            
            for insight in group.insights:
                insights_list.append({
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "insight_type": insight.insight_type,
                    "tags": insight.tags,
                    "generated_at": insight.generated_at.isoformat(),
                    "source_entities": insight.source_entities
                })
            
            groups_dict.append({
                "title": group.title,
                "insight_type": group.insight_type,
                "insights": insights_list
            })
        
        return json.dumps(groups_dict, indent=2)
    
    @staticmethod
    def trends_to_json(trends: List[TrendData]) -> str:
        """Convert trend data to JSON format.
        
        Args:
            trends: List of trend data
            
        Returns:
            JSON string
        """
        # Convert to dictionary structure suitable for JSON
        trends_dict = []
        
        for trend in trends:
            trends_dict.append({
                "title": trend.title,
                "time_periods": trend.time_periods,
                "series": trend.series
            })
        
        return json.dumps(trends_dict, indent=2)