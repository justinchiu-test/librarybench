"""
Tests for the competitive analysis module.

This module tests the competitive intelligence tracking functionality
of the ProductInsight system.
"""

import os
from datetime import datetime
from typing import Dict, List
from uuid import uuid4

import pytest

from product_insight.competitive import analysis
from product_insight.competitive.analysis import CompetitiveAnalyzer
from product_insight.models import (
    Competitor,
    Feature,
    StatusEnum,
    Tag
)
from product_insight.storage import FileStorage

from tests.fixtures.fixtures import (
    mock_data_generator,
    mock_competitors,
    mock_features,
    populated_storage_dir,
    temp_dir,
)


class TestCompetitiveAnalyzer:
    """Tests for the CompetitiveAnalyzer class."""
    
    def test_add_competitor(self, temp_dir):
        """Test adding a competitor."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Create a competitor
        competitor = Competitor(
            name="Test Competitor",
            description="A test competitor",
            website="https://testcompetitor.com",
            pricing_model="Subscription",
            target_segments=["Enterprise", "SMB"],
            strengths=["User-friendly UI", "Fast implementation"],
            weaknesses=["Limited customization", "Poor mobile experience"]
        )
        
        # Add the competitor
        added_competitor = analyzer.add_competitor(competitor)
        
        # Check the result
        assert added_competitor.id == competitor.id
        assert added_competitor.name == "Test Competitor"
        
        # Verify storage
        stored_competitor = analyzer.competitor_storage.get(competitor.id)
        assert stored_competitor.id == competitor.id
        assert stored_competitor.name == "Test Competitor"
    
    def test_update_competitor(self, temp_dir):
        """Test updating a competitor."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Create and add a competitor
        competitor = Competitor(
            name="Original Competitor",
            description="Original description",
            strengths=["Original strength"]
        )
        added_competitor = analyzer.add_competitor(competitor)
        
        # Update the competitor
        added_competitor.name = "Updated Competitor"
        added_competitor.description = "Updated description"
        added_competitor.strengths = ["Original strength", "New strength"]
        
        updated_competitor = analyzer.update_competitor(added_competitor)
        
        # Check the result
        assert updated_competitor.id == competitor.id
        assert updated_competitor.name == "Updated Competitor"
        assert updated_competitor.description == "Updated description"
        assert len(updated_competitor.strengths) == 2
        
        # Verify storage
        stored_competitor = analyzer.competitor_storage.get(competitor.id)
        assert stored_competitor.name == "Updated Competitor"
        assert len(stored_competitor.strengths) == 2
    
    def test_get_competitor(self, temp_dir, mock_competitors):
        """Test retrieving a competitor."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add a competitor
        competitor = mock_competitors[0]
        added_competitor = analyzer.add_competitor(competitor)
        
        # Get the competitor
        retrieved_competitor = analyzer.get_competitor(added_competitor.id)
        
        # Check the result
        assert retrieved_competitor.id == added_competitor.id
        assert retrieved_competitor.name == added_competitor.name
    
    def test_list_competitors(self, temp_dir, mock_competitors):
        """Test listing competitors."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add multiple competitors
        for competitor in mock_competitors[:3]:
            analyzer.add_competitor(competitor)
        
        # List competitors
        competitors = analyzer.list_competitors()
        
        # Check the result
        assert len(competitors) == 3
    
    def test_delete_competitor(self, temp_dir, mock_competitors):
        """Test deleting a competitor."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add a competitor
        competitor = mock_competitors[0]
        added_competitor = analyzer.add_competitor(competitor)
        
        # Delete the competitor
        result = analyzer.delete_competitor(added_competitor.id)
        
        # Check the result
        assert result is True
        
        # Verify storage
        with pytest.raises(Exception):
            analyzer.competitor_storage.get(added_competitor.id)
    
    def test_compare_competitors(self, temp_dir, mock_competitors):
        """Test comparing competitors."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add competitors with different strengths and weaknesses
        competitor1 = Competitor(
            name="Competitor A",
            strengths=["UX Design", "API Integration", "Performance"],
            weaknesses=["Mobile Support", "Pricing"]
        )
        
        competitor2 = Competitor(
            name="Competitor B",
            strengths=["Mobile Support", "Customization", "API Integration"],
            weaknesses=["Performance", "Scalability"]
        )
        
        added_comp1 = analyzer.add_competitor(competitor1)
        added_comp2 = analyzer.add_competitor(competitor2)
        
        # Compare competitors
        comparison = analyzer.compare_competitors([added_comp1.id, added_comp2.id])
        
        # Check the results
        assert len(comparison.competitors) == 2
        assert comparison.common_strengths == ["API Integration"]
        assert "UX Design" in comparison.unique_strengths["Competitor A"]
        assert "Mobile Support" in comparison.unique_strengths["Competitor B"]
        assert "Mobile Support" in comparison.strengths_weaknesses_matrix
    
    def test_create_feature_matrix(self, temp_dir, mock_competitors, mock_features):
        """Test creating a feature matrix."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add competitors with feature comparisons
        for i, competitor in enumerate(mock_competitors[:3]):
            # Add feature comparisons
            feature_comparison = {}
            for j, feature in enumerate(mock_features[:5]):
                # Assign different features to different competitors
                has_feature = (i + j) % 2 == 0
                feature_comparison[feature.name] = has_feature
            
            competitor.feature_comparison = feature_comparison
            analyzer.add_competitor(competitor)
        
        # Create feature matrix
        matrix = analyzer.create_feature_matrix()
        
        # Check the results
        assert len(matrix.competitors) == 3
        assert len(matrix.features) >= 5
        assert len(matrix.matrix) == 3
        
        # All competitors should have some features
        assert all(len(features) > 0 for features in matrix.matrix.values())
    
    def test_get_competitors_by_segment(self, temp_dir, mock_competitors):
        """Test getting competitors by market segment."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add competitors with different segments
        for competitor in mock_competitors[:5]:
            # Ensure each competitor has some target segments
            if not competitor.target_segments:
                competitor.target_segments = ["Enterprise"]
            analyzer.add_competitor(competitor)
        
        # Add one with specific segment
        competitor = Competitor(
            name="SMB Competitor",
            target_segments=["SMB", "Startups"]
        )
        analyzer.add_competitor(competitor)
        
        # Get competitors by segment
        enterprise_competitors = analyzer.get_competitors_by_segment("Enterprise")
        smb_competitors = analyzer.get_competitors_by_segment("SMB")
        
        # Check results
        assert len(enterprise_competitors) > 0
        assert len(smb_competitors) > 0
        assert any(c.name == "SMB Competitor" for c in smb_competitors)
    
    def test_identify_market_gaps(self, temp_dir, mock_competitors, mock_features):
        """Test identifying market gaps."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add competitors with feature comparisons
        for competitor in mock_competitors[:3]:
            # Add feature comparisons
            feature_comparison = {}
            for feature in mock_features[:10]:
                # Randomly assign features (but ensure some gaps)
                has_feature = feature.name != mock_features[0].name  # Ensure first feature is a gap
                feature_comparison[feature.name] = has_feature
            
            competitor.feature_comparison = feature_comparison
            analyzer.add_competitor(competitor)
        
        # Add our features to the analyzer
        feature_storage = FileStorage(
            entity_type=Feature,
            storage_dir=f"{temp_dir}/features",
            format="json"
        )
        for feature in mock_features[:10]:
            feature_storage.save(feature)
        
        # Identify market gaps
        gaps = analyzer.identify_market_gaps(feature_storage)
        
        # Check results
        assert len(gaps) > 0
        assert mock_features[0].name in [gap.name for gap in gaps]
    
    def test_calculate_threat_levels(self, temp_dir, mock_competitors):
        """Test calculating threat levels for competitors."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add competitors
        added_competitors = []
        for competitor in mock_competitors[:3]:
            # Clear any existing threat levels
            competitor.threat_level = None
            added = analyzer.add_competitor(competitor)
            added_competitors.append(added)
        
        # Calculate threat levels
        threat_levels = analyzer.calculate_threat_levels()
        
        # Check results
        assert len(threat_levels) == 3
        for competitor_id, threat_level in threat_levels.items():
            assert 0 <= threat_level <= 1
            
            # Verify the competitor was updated
            updated_competitor = analyzer.get_competitor(competitor_id)
            assert updated_competitor.threat_level == threat_level
    
    def test_track_competitor_changes(self, temp_dir, mock_competitors):
        """Test tracking competitor changes over time."""
        # Create an analyzer
        analyzer = CompetitiveAnalyzer(storage_dir=temp_dir)
        
        # Add a competitor
        competitor = mock_competitors[0]
        
        # Make a series of updates to simulate changes over time
        competitor1 = analyzer.add_competitor(competitor)
        
        # First update
        competitor1.strengths = ["Strength 1", "Strength 2"]
        competitor1.weaknesses = ["Weakness 1"]
        competitor1.pricing_model = "Freemium"
        competitor1 = analyzer.update_competitor(competitor1)
        
        # Second update
        competitor1.strengths = ["Strength 1", "Strength 2", "New Strength"]
        competitor1.weaknesses = ["Weakness 1", "New Weakness"]
        competitor1.market_share = 15.0
        competitor1 = analyzer.update_competitor(competitor1)
        
        # Track changes
        changes = analyzer.track_competitor_changes(competitor1.id)
        
        # Check results
        assert len(changes) > 0
        assert any("strengths" in change for change in changes)
        assert any("market_share" in change for change in changes)