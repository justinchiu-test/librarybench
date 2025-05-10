"""
Tests for the stakeholders module.

This module tests the stakeholder management functionality of the ProductInsight system.
"""

import os
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from product_insight.models import (
    Stakeholder,
    StakeholderPerspective,
    StakeholderRoleEnum,
    InfluenceEnum,
    SentimentEnum,
    Tag
)
from product_insight.stakeholders.manager import StakeholderManager
from product_insight.stakeholders.visualization import (
    create_alignment_chart,
    create_stakeholder_map,
    create_perspective_heatmap
)
from product_insight.storage import FileStorage

from tests.fixtures.fixtures import (
    mock_data_generator,
    mock_stakeholders,
    mock_stakeholder_perspectives,
    populated_storage_dir,
    temp_dir,
)


class TestStakeholderManager:
    """Tests for the StakeholderManager class."""
    
    def test_add_stakeholder(self, temp_dir):
        """Test adding a stakeholder."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Create a stakeholder
        stakeholder = Stakeholder(
            name="John Smith",
            role=StakeholderRoleEnum.EXECUTIVE,
            organization="Acme Corp",
            email="john.smith@acme.com",
            influence=InfluenceEnum.HIGH,
            key_concerns=["Performance", "Security"]
        )
        
        # Add the stakeholder
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Check the result
        assert added_stakeholder.id == stakeholder.id
        assert added_stakeholder.name == "John Smith"
        assert added_stakeholder.role == StakeholderRoleEnum.EXECUTIVE
        
        # Verify storage
        stored_stakeholder = manager.stakeholder_storage.get(stakeholder.id)
        assert stored_stakeholder.id == stakeholder.id
        assert stored_stakeholder.name == "John Smith"
    
    def test_update_stakeholder(self, temp_dir):
        """Test updating a stakeholder."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Create and add a stakeholder
        stakeholder = Stakeholder(
            name="Original Name",
            role=StakeholderRoleEnum.PRODUCT,
            influence=InfluenceEnum.MEDIUM
        )
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Update the stakeholder
        added_stakeholder.name = "Updated Name"
        added_stakeholder.influence = InfluenceEnum.HIGH
        added_stakeholder.key_concerns = ["New Concern"]
        
        updated_stakeholder = manager.update_stakeholder(added_stakeholder)
        
        # Check the result
        assert updated_stakeholder.id == stakeholder.id
        assert updated_stakeholder.name == "Updated Name"
        assert updated_stakeholder.influence == InfluenceEnum.HIGH
        assert "New Concern" in updated_stakeholder.key_concerns
        
        # Verify storage
        stored_stakeholder = manager.stakeholder_storage.get(stakeholder.id)
        assert stored_stakeholder.name == "Updated Name"
        assert stored_stakeholder.influence == InfluenceEnum.HIGH
    
    def test_get_stakeholder(self, temp_dir, mock_stakeholders):
        """Test retrieving a stakeholder."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add a stakeholder
        stakeholder = mock_stakeholders[0]
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Get the stakeholder
        retrieved_stakeholder = manager.get_stakeholder(added_stakeholder.id)
        
        # Check the result
        assert retrieved_stakeholder.id == added_stakeholder.id
        assert retrieved_stakeholder.name == added_stakeholder.name
    
    def test_delete_stakeholder(self, temp_dir, mock_stakeholders):
        """Test deleting a stakeholder."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add a stakeholder
        stakeholder = mock_stakeholders[0]
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Delete the stakeholder
        result = manager.delete_stakeholder(added_stakeholder.id)
        
        # Check the result
        assert result is True
        
        # Verify storage
        with pytest.raises(Exception):
            manager.stakeholder_storage.get(added_stakeholder.id)
    
    def test_get_stakeholders_by_role(self, temp_dir, mock_stakeholders):
        """Test getting stakeholders by role."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Ensure we have stakeholders with different roles
        engineering_stakeholders = []
        for stakeholder in mock_stakeholders[:5]:
            # Make sure we have some engineering stakeholders
            if len(engineering_stakeholders) < 2 and stakeholder.role != StakeholderRoleEnum.ENGINEERING:
                stakeholder.role = StakeholderRoleEnum.ENGINEERING
                engineering_stakeholders.append(stakeholder)
            manager.add_stakeholder(stakeholder)
        
        # Add one more with a specific role
        stakeholder = Stakeholder(
            name="New Engineer",
            role=StakeholderRoleEnum.ENGINEERING,
            influence=InfluenceEnum.MEDIUM
        )
        manager.add_stakeholder(stakeholder)
        engineering_stakeholders.append(stakeholder)
        
        # Get stakeholders by role
        engineers = manager.get_stakeholders_by_role(StakeholderRoleEnum.ENGINEERING)
        
        # Check results
        assert len(engineers) == len(engineering_stakeholders)
        assert any(s.name == "New Engineer" for s in engineers)
    
    def test_search_stakeholders(self, temp_dir, mock_stakeholders):
        """Test searching stakeholders."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add stakeholders with different attributes
        for stakeholder in mock_stakeholders[:5]:
            manager.add_stakeholder(stakeholder)
        
        # Add a stakeholder with specific attributes
        stakeholder = Stakeholder(
            name="Project Manager",
            role=StakeholderRoleEnum.PRODUCT,
            organization="Tech Solutions",
            influence=InfluenceEnum.HIGH,
            key_concerns=["Usability", "Performance"]
        )
        manager.add_stakeholder(stakeholder)
        
        # Create a search query
        from product_insight.stakeholders.manager import StakeholderQuery
        query = StakeholderQuery(
            text="Tech",
            roles=[StakeholderRoleEnum.PRODUCT],
            influence_levels=[InfluenceEnum.HIGH]
        )
        
        # Search stakeholders
        results = manager.search_stakeholders(query)
        
        # Check results
        assert len(results) >= 1
        assert any(s.name == "Project Manager" for s in results)
    
    def test_add_engagement_history(self, temp_dir, mock_stakeholders):
        """Test adding engagement history to a stakeholder."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add a stakeholder
        stakeholder = mock_stakeholders[0]
        # Clear existing history
        stakeholder.engagement_history = []
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Add engagement history
        engagement = "Met to discuss product roadmap. Very interested in mobile features."
        updated_stakeholder = manager.add_engagement_history(added_stakeholder.id, engagement)
        
        # Check results
        assert len(updated_stakeholder.engagement_history) == 1
        assert "mobile features" in updated_stakeholder.engagement_history[0]
        
        # Verify timestamp format in the entry
        entry = updated_stakeholder.engagement_history[0]
        assert "[" in entry and "]" in entry
    
    def test_add_stakeholder_perspective(self, temp_dir, mock_stakeholders):
        """Test adding a stakeholder perspective."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add a stakeholder
        stakeholder = mock_stakeholders[0]
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Create a perspective
        perspective = StakeholderPerspective(
            stakeholder_id=added_stakeholder.id,
            topic="Feature Prioritization",
            perspective="We should focus on mobile experience before desktop redesign",
            sentiment=SentimentEnum.POSITIVE,
            related_feature_ids=[uuid4()]
        )
        
        # Add the perspective
        added_perspective = manager.add_stakeholder_perspective(perspective)
        
        # Check results
        assert added_perspective.id == perspective.id
        assert added_perspective.stakeholder_id == added_stakeholder.id
        assert added_perspective.topic == "Feature Prioritization"
        
        # Verify storage
        stored_perspective = manager.perspective_storage.get(perspective.id)
        assert stored_perspective.id == perspective.id
        assert stored_perspective.topic == "Feature Prioritization"
    
    def test_get_stakeholder_perspectives(self, temp_dir, mock_stakeholders):
        """Test getting perspectives for a stakeholder."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add a stakeholder
        stakeholder = mock_stakeholders[0]
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Add multiple perspectives
        perspective1 = StakeholderPerspective(
            stakeholder_id=added_stakeholder.id,
            topic="Topic 1",
            perspective="Perspective 1",
            date_recorded=datetime.now() - timedelta(days=10)
        )
        
        perspective2 = StakeholderPerspective(
            stakeholder_id=added_stakeholder.id,
            topic="Topic 2",
            perspective="Perspective 2",
            date_recorded=datetime.now() - timedelta(days=5)
        )
        
        manager.add_stakeholder_perspective(perspective1)
        manager.add_stakeholder_perspective(perspective2)
        
        # Get perspectives
        perspectives = manager.get_stakeholder_perspectives(added_stakeholder.id)
        
        # Check results
        assert len(perspectives) == 2
        # Should be sorted by date, newest first
        assert perspectives[0].topic == "Topic 2"
        assert perspectives[1].topic == "Topic 1"
    
    def test_get_perspectives_on_topic(self, temp_dir, mock_stakeholders):
        """Test getting perspectives on a specific topic."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add multiple stakeholders
        stakeholder1 = mock_stakeholders[0]
        stakeholder2 = mock_stakeholders[1]
        added1 = manager.add_stakeholder(stakeholder1)
        added2 = manager.add_stakeholder(stakeholder2)
        
        # Add perspectives on the same topic
        topic = "Product Roadmap"
        
        perspective1 = StakeholderPerspective(
            stakeholder_id=added1.id,
            topic=topic,
            perspective="We should focus on mobile features",
            sentiment=SentimentEnum.POSITIVE
        )
        
        perspective2 = StakeholderPerspective(
            stakeholder_id=added2.id,
            topic=topic,
            perspective="We should prioritize desktop experience",
            sentiment=SentimentEnum.NEGATIVE
        )
        
        # Add perspective on a different topic
        perspective3 = StakeholderPerspective(
            stakeholder_id=added1.id,
            topic="Pricing Strategy",
            perspective="We should increase enterprise pricing",
            sentiment=SentimentEnum.NEUTRAL
        )
        
        manager.add_stakeholder_perspective(perspective1)
        manager.add_stakeholder_perspective(perspective2)
        manager.add_stakeholder_perspective(perspective3)
        
        # Get perspectives on the topic
        perspectives = manager.get_perspectives_on_topic(topic)
        
        # Check results
        assert len(perspectives) == 2
        for stakeholder, perspective in perspectives:
            assert perspective.topic == topic
    
    def test_update_feature_preference(self, temp_dir, mock_stakeholders):
        """Test updating a stakeholder's feature preference."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add a stakeholder
        stakeholder = mock_stakeholders[0]
        # Clear existing preferences
        stakeholder.feature_preferences = {}
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Update feature preference
        feature_id = uuid4()
        preference = 0.8  # High preference
        updated_stakeholder = manager.update_feature_preference(
            added_stakeholder.id, feature_id, preference
        )
        
        # Check results
        assert feature_id in updated_stakeholder.feature_preferences
        assert updated_stakeholder.feature_preferences[feature_id] == preference
        
        # Verify storage
        stored_stakeholder = manager.stakeholder_storage.get(added_stakeholder.id)
        assert feature_id in stored_stakeholder.feature_preferences
        assert stored_stakeholder.feature_preferences[feature_id] == preference
    
    def test_update_objective_alignment(self, temp_dir, mock_stakeholders):
        """Test updating a stakeholder's objective alignment."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add a stakeholder
        stakeholder = mock_stakeholders[0]
        # Clear existing alignments
        stakeholder.objective_alignment = {}
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Update objective alignment
        objective_id = uuid4()
        alignment = 0.9  # High alignment
        updated_stakeholder = manager.update_objective_alignment(
            added_stakeholder.id, objective_id, alignment
        )
        
        # Check results
        assert objective_id in updated_stakeholder.objective_alignment
        assert updated_stakeholder.objective_alignment[objective_id] == alignment
        
        # Verify storage
        stored_stakeholder = manager.stakeholder_storage.get(added_stakeholder.id)
        assert objective_id in stored_stakeholder.objective_alignment
        assert stored_stakeholder.objective_alignment[objective_id] == alignment
    
    def test_calculate_stakeholder_alignment(self, temp_dir, mock_stakeholders):
        """Test calculating stakeholder alignment with objectives."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add stakeholders with objective alignments
        objective1_id = uuid4()
        objective2_id = uuid4()
        
        stakeholder1 = mock_stakeholders[0]
        stakeholder1.objective_alignment = {
            objective1_id: 0.8,
            objective2_id: 0.3
        }
        
        stakeholder2 = mock_stakeholders[1]
        stakeholder2.objective_alignment = {
            objective1_id: 0.4,
            objective2_id: 0.9
        }
        
        manager.add_stakeholder(stakeholder1)
        manager.add_stakeholder(stakeholder2)
        
        # Calculate alignment
        alignments = manager.calculate_stakeholder_alignment([objective1_id, objective2_id])
        
        # Check results
        assert len(alignments) == 2
        
        # Verify alignment scores
        for alignment in alignments:
            if alignment.stakeholder_name == stakeholder1.name:
                assert str(objective1_id) in alignment.alignment_scores
                assert str(objective2_id) in alignment.alignment_scores
                assert alignment.alignment_scores[str(objective1_id)] == 0.8
                assert alignment.alignment_scores[str(objective2_id)] == 0.3
                assert alignment.overall_alignment == 0.55  # Average
    
    def test_generate_stakeholder_report(self, temp_dir, mock_stakeholders, mock_stakeholder_perspectives):
        """Test generating a stakeholder report."""
        # Create a manager
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add a stakeholder with comprehensive data
        stakeholder = mock_stakeholders[0]
        feature_id = uuid4()
        objective_id = uuid4()
        
        stakeholder.feature_preferences = {feature_id: 0.9}
        stakeholder.objective_alignment = {objective_id: 0.8}
        stakeholder.key_concerns = ["Performance", "Usability"]
        stakeholder.engagement_history = ["[2023-01-01 10:00] Initial meeting", "[2023-02-01 15:00] Follow-up call"]
        
        added_stakeholder = manager.add_stakeholder(stakeholder)
        
        # Add a perspective
        perspective = StakeholderPerspective(
            stakeholder_id=added_stakeholder.id,
            topic="Product Direction",
            perspective="Very positive about the new mobile focus",
            sentiment=SentimentEnum.POSITIVE
        )
        manager.add_stakeholder_perspective(perspective)
        
        # Generate report (markdown format)
        report_md = manager.generate_stakeholder_report([added_stakeholder], "markdown")
        
        # Check markdown results
        assert "# Stakeholder Report" in report_md
        assert added_stakeholder.name in report_md
        assert "**Influence:**" in report_md
        assert "**Key Concerns:**" in report_md
        assert "Performance" in report_md
        assert "Product Direction" in report_md
        
        # Generate report (text format)
        report_text = manager.generate_stakeholder_report([added_stakeholder], "text")
        
        # Check text results
        assert "STAKEHOLDER REPORT" in report_text
        assert added_stakeholder.name in report_text
        assert "Influence:" in report_text
        assert "Key Concerns:" in report_text
        assert "Performance" in report_text


class TestStakeholderVisualization:
    """Tests for stakeholder visualization functions."""
    
    def test_create_stakeholder_map(self, temp_dir, mock_stakeholders):
        """Test creating a stakeholder influence/interest map."""
        # Create test data
        stakeholders = mock_stakeholders[:5]
        
        # Ensure we have stakeholders with different influences
        influence_levels = list(InfluenceEnum)
        for i, stakeholder in enumerate(stakeholders):
            stakeholder.influence = influence_levels[i % len(influence_levels)]
        
        # Add various feature preferences to create interest levels
        feature_id = uuid4()
        for i, stakeholder in enumerate(stakeholders):
            stakeholder.feature_preferences = {feature_id: min(1.0, 0.2 * (i + 1))}
        
        # Create stakeholder map
        stakeholder_map = create_stakeholder_map(stakeholders, feature_id)
        
        # Check results
        assert "title" in stakeholder_map
        assert "quadrants" in stakeholder_map
        assert len(stakeholder_map["stakeholders"]) == 5
        
        # Each stakeholder should have x, y coordinates and be in a quadrant
        for s in stakeholder_map["stakeholders"]:
            assert "x" in s
            assert "y" in s
            assert "quadrant" in s
            assert "name" in s
            assert "id" in s
            assert "role" in s
            
            # Coordinates should be between 0 and 1
            assert 0 <= s["x"] <= 1
            assert 0 <= s["y"] <= 1
    
    def test_create_alignment_chart(self, temp_dir, mock_stakeholders):
        """Test creating a stakeholder alignment chart."""
        # Create test data
        stakeholders = mock_stakeholders[:4]
        objectives = [
            ("Objective 1", uuid4()),
            ("Objective 2", uuid4()),
            ("Objective 3", uuid4())
        ]
        
        # Add alignment data
        for i, stakeholder in enumerate(stakeholders):
            stakeholder.objective_alignment = {
                objectives[0][1]: 0.2 + (i * 0.2),  # Different alignments
                objectives[1][1]: 0.5,               # Same alignment
                objectives[2][1]: max(0.1, 0.9 - (i * 0.2))  # Inverse pattern
            }
        
        # Create alignment chart
        alignment_chart = create_alignment_chart(stakeholders, objectives)
        
        # Check results
        assert "title" in alignment_chart
        assert "stakeholders" in alignment_chart
        assert "objectives" in alignment_chart
        assert "data" in alignment_chart
        
        assert len(alignment_chart["stakeholders"]) == 4
        assert len(alignment_chart["objectives"]) == 3
        assert len(alignment_chart["data"]) == 12  # 4 stakeholders * 3 objectives
        
        # Each data point should have stakeholder, objective, and value
        for point in alignment_chart["data"]:
            assert "stakeholder" in point
            assert "objective" in point
            assert "value" in point
            assert 0 <= point["value"] <= 1
    
    def test_create_perspective_heatmap(self, temp_dir, mock_stakeholders, mock_stakeholder_perspectives):
        """Test creating a perspective sentiment heatmap."""
        # Create a manager to access stakeholders and perspectives
        manager = StakeholderManager(storage_dir=temp_dir)
        
        # Add stakeholders
        added_stakeholders = []
        for stakeholder in mock_stakeholders[:3]:
            added = manager.add_stakeholder(stakeholder)
            added_stakeholders.append(added)
        
        # Define topics
        topics = ["UI Design", "Performance", "Mobile Strategy"]
        
        # Add perspectives with different sentiments for each stakeholder on each topic
        sentiments = list(SentimentEnum)
        for i, stakeholder in enumerate(added_stakeholders):
            for j, topic in enumerate(topics):
                sentiment = sentiments[(i + j) % len(sentiments)]
                perspective = StakeholderPerspective(
                    stakeholder_id=stakeholder.id,
                    topic=topic,
                    perspective=f"Perspective on {topic}",
                    sentiment=sentiment
                )
                manager.add_stakeholder_perspective(perspective)
        
        # Get all perspectives
        all_perspectives = []
        for s in added_stakeholders:
            perspectives = manager.get_stakeholder_perspectives(s.id)
            all_perspectives.extend(perspectives)
        
        # Create perspective heatmap
        heatmap = create_perspective_heatmap(added_stakeholders, all_perspectives, topics)
        
        # Check results
        assert "title" in heatmap
        assert "stakeholders" in heatmap
        assert "topics" in heatmap
        assert "data" in heatmap
        
        assert len(heatmap["stakeholders"]) == 3
        assert len(heatmap["topics"]) == 3
        assert len(heatmap["data"]) <= 9  # Max 3 stakeholders * 3 topics

        # Each data point should have stakeholder, topic, and sentiment value
        for point in heatmap["data"]:
            assert "stakeholder" in point
            assert "topic" in point
            assert "sentiment" in point
            assert -1 <= point["sentiment"] <= 1  # Sentiment should be normalized to [-1, 1]