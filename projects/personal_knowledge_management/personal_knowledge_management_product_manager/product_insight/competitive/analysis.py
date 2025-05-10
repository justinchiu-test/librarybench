"""
Competitive analysis module for ProductInsight.

This module provides functionality for analyzing competitor products and
market positioning.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union
from uuid import UUID

from pydantic import BaseModel, Field

from product_insight.models import Competitor, Feature, Tag
from product_insight.storage import FileStorage, StorageInterface


class CompetitorFeatureMatrix(BaseModel):
    """Matrix of competitor features for comparison."""
    
    features: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    matrix: Dict[str, Dict[str, bool]] = Field(default_factory=dict)


class MarketSegmentDistribution(BaseModel):
    """Distribution of competitors across market segments."""
    
    segments: Dict[str, List[str]] = Field(default_factory=dict)
    
    def add_competitor(self, competitor_name: str, segment: str) -> None:
        """Add a competitor to a segment.
        
        Args:
            competitor_name: Name of the competitor
            segment: Market segment
        """
        if segment not in self.segments:
            self.segments[segment] = []
        
        if competitor_name not in self.segments[segment]:
            self.segments[segment].append(competitor_name)
    
    def get_segments_for_competitor(self, competitor_name: str) -> List[str]:
        """Get the segments a competitor is in.
        
        Args:
            competitor_name: Name of the competitor
            
        Returns:
            List of segment names
        """
        return [
            segment for segment, competitors in self.segments.items()
            if competitor_name in competitors
        ]


class PricingComparison(BaseModel):
    """Comparison of pricing across competitors."""
    
    competitors: List[str] = Field(default_factory=list)
    pricing_models: Dict[str, str] = Field(default_factory=dict)
    pricing_details: Dict[str, Dict[str, str]] = Field(default_factory=dict)


class CompetitiveAnalyzer:
    """Analyzes competitor products and market positioning."""
    
    def __init__(
        self,
        storage_dir: str,
        competitor_storage: Optional[StorageInterface[Competitor]] = None,
        feature_storage: Optional[StorageInterface[Feature]] = None,
    ):
        """Initialize the competitive analyzer.
        
        Args:
            storage_dir: Base directory for storing competitor data
            competitor_storage: Optional custom storage for competitors
            feature_storage: Optional custom storage for features
        """
        self.competitor_storage = competitor_storage or FileStorage(
            entity_type=Competitor,
            storage_dir=f"{storage_dir}/competitors",
            format="json"
        )
        
        self.feature_storage = feature_storage or FileStorage(
            entity_type=Feature,
            storage_dir=f"{storage_dir}/features",
            format="json"
        )
    
    def add_competitor(self, competitor: Competitor) -> Competitor:
        """Add a new competitor.
        
        Args:
            competitor: Competitor to add
            
        Returns:
            Added competitor
        """
        return self.competitor_storage.save(competitor)
    
    def update_competitor(self, competitor: Competitor) -> Competitor:
        """Update an existing competitor.
        
        Args:
            competitor: Competitor to update
            
        Returns:
            Updated competitor
        """
        return self.competitor_storage.save(competitor)
    
    def get_competitor(self, competitor_id: UUID) -> Competitor:
        """Get a competitor by ID.
        
        Args:
            competitor_id: ID of the competitor to get
            
        Returns:
            Competitor
        """
        return self.competitor_storage.get(competitor_id)
    
    def delete_competitor(self, competitor_id: UUID) -> bool:
        """Delete a competitor.
        
        Args:
            competitor_id: ID of the competitor to delete
            
        Returns:
            True if the competitor was deleted, False otherwise
        """
        return self.competitor_storage.delete(competitor_id)
    
    def get_all_competitors(self) -> List[Competitor]:
        """Get all competitors.
        
        Returns:
            List of competitors
        """
        return self.competitor_storage.list()
    
    def get_competitors_by_tag(self, tag: str) -> List[Competitor]:
        """Get competitors with a specific tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of competitors with the given tag
        """
        all_competitors = self.competitor_storage.list()
        
        return [
            comp for comp in all_competitors
            if any(t.name.lower() == tag.lower() for t in comp.tags)
        ]
    
    def create_feature_matrix(
        self, competitor_ids: Optional[List[UUID]] = None
    ) -> CompetitorFeatureMatrix:
        """Create a feature comparison matrix.
        
        Args:
            competitor_ids: Optional list of competitor IDs to include (all if None)
            
        Returns:
            CompetitorFeatureMatrix with feature comparisons
        """
        # Get competitors to include
        if competitor_ids:
            competitors = [self.competitor_storage.get(cid) for cid in competitor_ids]
        else:
            competitors = self.competitor_storage.list()
        
        # Initialize the matrix
        matrix = CompetitorFeatureMatrix()
        matrix.competitors = [comp.name for comp in competitors]
        
        # Collect all features across competitors
        all_features = set()
        for comp in competitors:
            all_features.update(comp.feature_comparison.keys())
        
        matrix.features = sorted(list(all_features))
        
        # Build the matrix
        for comp in competitors:
            matrix.matrix[comp.name] = {}
            for feature in matrix.features:
                matrix.matrix[comp.name][feature] = comp.feature_comparison.get(feature, False)
        
        return matrix
    
    def create_market_segment_distribution(
        self, competitor_ids: Optional[List[UUID]] = None
    ) -> MarketSegmentDistribution:
        """Create a market segment distribution.
        
        Args:
            competitor_ids: Optional list of competitor IDs to include (all if None)
            
        Returns:
            MarketSegmentDistribution with segment mappings
        """
        # Get competitors to include
        if competitor_ids:
            competitors = [self.competitor_storage.get(cid) for cid in competitor_ids]
        else:
            competitors = self.competitor_storage.list()
        
        # Initialize the distribution
        distribution = MarketSegmentDistribution()
        
        # Add competitors to segments
        for comp in competitors:
            for segment in comp.target_segments:
                distribution.add_competitor(comp.name, segment)
        
        return distribution
    
    def create_pricing_comparison(
        self, competitor_ids: Optional[List[UUID]] = None
    ) -> PricingComparison:
        """Create a pricing comparison.
        
        Args:
            competitor_ids: Optional list of competitor IDs to include (all if None)
            
        Returns:
            PricingComparison with pricing models and details
        """
        # Get competitors to include
        if competitor_ids:
            competitors = [self.competitor_storage.get(cid) for cid in competitor_ids]
        else:
            competitors = self.competitor_storage.list()
        
        # Initialize the comparison
        comparison = PricingComparison()
        comparison.competitors = [comp.name for comp in competitors]
        
        # Add pricing models and details
        for comp in competitors:
            comparison.pricing_models[comp.name] = comp.pricing_model or "Unknown"
            
            # Add details if available
            if comp.pricing_details:
                pricing_parts = comp.pricing_details.split(";")
                details = {}
                for part in pricing_parts:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        details[key.strip()] = value.strip()
                
                comparison.pricing_details[comp.name] = details
        
        return comparison
    
    def find_feature_gaps(
        self, your_features: List[str], competitor_ids: Optional[List[UUID]] = None
    ) -> Dict[str, List[str]]:
        """Find feature gaps between your product and competitors.
        
        Args:
            your_features: List of your product's features
            competitor_ids: Optional list of competitor IDs to include (all if None)
            
        Returns:
            Dictionary mapping competitors to lists of features they have that you don't
        """
        # Get competitors to include
        if competitor_ids:
            competitors = [self.competitor_storage.get(cid) for cid in competitor_ids]
        else:
            competitors = self.competitor_storage.list()
        
        # Convert your features to a set for faster lookups
        your_feature_set = set(your_features)
        
        # Find gaps
        gaps = {}
        
        for comp in competitors:
            comp_features = set(
                feature for feature, has_feature in comp.feature_comparison.items()
                if has_feature
            )
            
            # Features competitor has that you don't
            missing_features = comp_features - your_feature_set
            
            if missing_features:
                gaps[comp.name] = sorted(list(missing_features))
        
        return gaps
    
    def find_competitive_advantages(
        self, your_features: List[str], competitor_ids: Optional[List[UUID]] = None
    ) -> Dict[str, List[str]]:
        """Find features that give you a competitive advantage.
        
        Args:
            your_features: List of your product's features
            competitor_ids: Optional list of competitor IDs to include (all if None)
            
        Returns:
            Dictionary mapping competitors to lists of features you have that they don't
        """
        # Get competitors to include
        if competitor_ids:
            competitors = [self.competitor_storage.get(cid) for cid in competitor_ids]
        else:
            competitors = self.competitor_storage.list()
        
        # Convert your features to a set for faster lookups
        your_feature_set = set(your_features)
        
        # Find advantages
        advantages = {}
        
        for comp in competitors:
            comp_features = set(
                feature for feature, has_feature in comp.feature_comparison.items()
                if has_feature
            )
            
            # Features you have that competitor doesn't
            advantage_features = your_feature_set - comp_features
            
            if advantage_features:
                advantages[comp.name] = sorted(list(advantage_features))
        
        return advantages
    
    def calculate_feature_uniqueness(
        self, feature: str, competitor_ids: Optional[List[UUID]] = None
    ) -> float:
        """Calculate how unique a feature is among competitors.
        
        Args:
            feature: Feature to check
            competitor_ids: Optional list of competitor IDs to include (all if None)
            
        Returns:
            Uniqueness score between 0 (everyone has it) and 1 (nobody has it)
        """
        # Get competitors to include
        if competitor_ids:
            competitors = [self.competitor_storage.get(cid) for cid in competitor_ids]
        else:
            competitors = self.competitor_storage.list()
        
        if not competitors:
            return 1.0  # No competitors means it's unique
        
        # Count how many competitors have the feature
        has_feature_count = sum(
            1 for comp in competitors
            if comp.feature_comparison.get(feature, False)
        )
        
        # Calculate uniqueness
        return 1.0 - (has_feature_count / len(competitors))
    
    def find_whitespace_opportunities(
        self, competitor_ids: Optional[List[UUID]] = None
    ) -> List[Tuple[str, List[str]]]:
        """Find whitespace opportunities in the market.
        
        This function identifies segments with few competitors or feature gaps.
        
        Args:
            competitor_ids: Optional list of competitor IDs to include (all if None)
            
        Returns:
            List of (segment, reasons) tuples
        """
        # Get competitors to include
        if competitor_ids:
            competitors = [self.competitor_storage.get(cid) for cid in competitor_ids]
        else:
            competitors = self.competitor_storage.list()
        
        # Get segment distribution
        segments = MarketSegmentDistribution()
        for comp in competitors:
            for segment in comp.target_segments:
                segments.add_competitor(comp.name, segment)
        
        # Find opportunities
        opportunities = []
        
        # 1. Segments with few competitors
        for segment, comps in segments.segments.items():
            if len(comps) < 3:  # Arbitrary threshold
                reasons = [f"Only {len(comps)} competitors in this segment"]
                opportunities.append((segment, reasons))
        
        # 2. Feature gaps across segments
        all_features = set()
        for comp in competitors:
            all_features.update(
                feature for feature, has_feature in comp.feature_comparison.items()
                if has_feature
            )
        
        for segment, comps in segments.segments.items():
            # Get features available in this segment
            segment_features = set()
            for comp_name in comps:
                comp = next((c for c in competitors if c.name == comp_name), None)
                if comp:
                    segment_features.update(
                        feature for feature, has_feature in comp.feature_comparison.items()
                        if has_feature
                    )
            
            # Check for missing features
            missing_features = all_features - segment_features
            if missing_features:
                # If this segment doesn't already have an opportunity
                if not any(segment == seg for seg, _ in opportunities):
                    reasons = [f"Missing features: {', '.join(sorted(list(missing_features))[:3])}"]
                    opportunities.append((segment, reasons))
                else:
                    # Add to existing opportunity
                    for i, (seg, reasons) in enumerate(opportunities):
                        if seg == segment:
                            reasons.append(f"Missing features: {', '.join(sorted(list(missing_features))[:3])}")
                            opportunities[i] = (seg, reasons)
        
        return opportunities
    
    def categorize_competitors_by_threat(
        self, competitor_ids: Optional[List[UUID]] = None
    ) -> Dict[str, List[Competitor]]:
        """Categorize competitors by threat level.
        
        Args:
            competitor_ids: Optional list of competitor IDs to include (all if None)
            
        Returns:
            Dictionary mapping threat levels to lists of competitors
        """
        # Get competitors to include
        if competitor_ids:
            competitors = [self.competitor_storage.get(cid) for cid in competitor_ids]
        else:
            competitors = self.competitor_storage.list()
        
        # Initialize categories
        categories = {
            "high": [],
            "medium": [],
            "low": [],
            "unknown": [],
        }
        
        for comp in competitors:
            if comp.threat_level is None:
                categories["unknown"].append(comp)
            elif comp.threat_level >= 0.7:
                categories["high"].append(comp)
            elif comp.threat_level >= 0.4:
                categories["medium"].append(comp)
            else:
                categories["low"].append(comp)
        
        return categories