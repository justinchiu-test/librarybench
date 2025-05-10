"""
Tests for the decisions module.

This module tests the decision management functionality of the ProductInsight system.
"""

import os
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from product_insight.decisions.manager import DecisionManager
from product_insight.models import (
    Decision,
    Feature,
    StrategicObjective,
    Tag
)
from product_insight.storage import FileStorage

from tests.fixtures.fixtures import (
    mock_data_generator,
    mock_decisions,
    populated_storage_dir,
    temp_dir,
)


class TestDecisionManager:
    """Tests for the DecisionManager class."""
    
    def test_add_decision(self, temp_dir):
        """Test adding a decision."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create a decision
        decision = Decision(
            title="Implement new authentication system",
            description="Decision regarding the authentication system approach",
            context="Current authentication is outdated and insecure",
            rationale="New system provides better security and user experience",
            alternatives=["Keep current system", "Use third-party solution"]
        )
        
        # Add the decision
        added_decision = manager.add_decision(decision)
        
        # Check the result
        assert added_decision.id == decision.id
        assert added_decision.title == "Implement new authentication system"
        
        # Verify storage
        stored_decision = manager.decision_storage.get(decision.id)
        assert stored_decision.id == decision.id
        assert stored_decision.title == "Implement new authentication system"
    
    def test_update_decision(self, temp_dir):
        """Test updating a decision."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create and add a decision
        decision = Decision(
            title="Original Decision",
            description="Original description",
            context="Original context",
            rationale="Original rationale"
        )
        added_decision = manager.add_decision(decision)
        
        # Update the decision
        added_decision.title = "Updated Decision"
        added_decision.description = "Updated description"
        added_decision.outcome_notes = "Implementation was successful"
        added_decision.outcome_date = datetime.now()
        
        updated_decision = manager.update_decision(added_decision)
        
        # Check the result
        assert updated_decision.id == decision.id
        assert updated_decision.title == "Updated Decision"
        assert updated_decision.description == "Updated description"
        assert updated_decision.outcome_notes == "Implementation was successful"
        assert updated_decision.outcome_date is not None
        
        # Verify storage
        stored_decision = manager.decision_storage.get(decision.id)
        assert stored_decision.title == "Updated Decision"
        assert stored_decision.outcome_notes == "Implementation was successful"
    
    def test_get_decision(self, temp_dir, mock_decisions):
        """Test retrieving a decision."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add a decision
        decision = mock_decisions[0]
        added_decision = manager.add_decision(decision)
        
        # Get the decision
        retrieved_decision = manager.get_decision(added_decision.id)
        
        # Check the result
        assert retrieved_decision.id == added_decision.id
        assert retrieved_decision.title == added_decision.title
    
    def test_list_decisions(self, temp_dir, mock_decisions):
        """Test listing decisions."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add multiple decisions
        for decision in mock_decisions[:3]:
            manager.add_decision(decision)
        
        # List decisions
        decisions = manager.list_decisions()
        
        # Check the result
        assert len(decisions) == 3
    
    def test_delete_decision(self, temp_dir, mock_decisions):
        """Test deleting a decision."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add a decision
        decision = mock_decisions[0]
        added_decision = manager.add_decision(decision)
        
        # Delete the decision
        result = manager.delete_decision(added_decision.id)
        
        # Check the result
        assert result is True
        
        # Verify storage
        with pytest.raises(Exception):
            manager.decision_storage.get(added_decision.id)
    
    def test_add_retrospective(self, temp_dir, mock_decisions):
        """Test adding a retrospective to a decision."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add a decision with an outcome
        decision = mock_decisions[0]
        decision.outcome_notes = "Implementation was completed"
        decision.outcome_date = datetime.now() - timedelta(days=30)
        added_decision = manager.add_decision(decision)
        
        # Add a retrospective
        retrospective = "In retrospect, we should have allocated more resources to testing."
        decision_with_retro = manager.add_retrospective(added_decision.id, retrospective)
        
        # Check result
        assert decision_with_retro.id == added_decision.id
        assert decision_with_retro.retrospective == retrospective
        
        # Verify storage
        stored_decision = manager.decision_storage.get(added_decision.id)
        assert stored_decision.retrospective == retrospective
    
    def test_get_decisions_by_date_range(self, temp_dir, mock_decisions):
        """Test getting decisions by date range."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add decisions with different dates
        now = datetime.now()
        
        # Recent decision
        recent_decision = mock_decisions[0]
        recent_decision.decision_date = now - timedelta(days=15)
        manager.add_decision(recent_decision)
        
        # Older decision
        older_decision = mock_decisions[1]
        older_decision.decision_date = now - timedelta(days=100)
        manager.add_decision(older_decision)
        
        # Future decision (e.g., planned)
        future_decision = mock_decisions[2]
        future_decision.decision_date = now + timedelta(days=15)
        manager.add_decision(future_decision)
        
        # Get decisions for last 30 days
        recent_decisions = manager.get_decisions_by_date_range(
            start_date=now - timedelta(days=30),
            end_date=now
        )
        
        # Check result
        assert len(recent_decisions) == 1
        assert recent_decisions[0].id == recent_decision.id
        
        # Get all decisions
        all_decisions = manager.get_decisions_by_date_range(
            start_date=now - timedelta(days=200),
            end_date=now + timedelta(days=30)
        )
        
        # Check result
        assert len(all_decisions) == 3
    
    def test_search_decisions(self, temp_dir, mock_decisions):
        """Test searching decisions."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add decisions with different content
        decision1 = Decision(
            title="Authentication System Redesign",
            description="Decision about authentication approach",
            context="Security concerns with current system",
            rationale="Better security and user experience"
        )
        
        decision2 = Decision(
            title="Data Storage Strategy",
            description="Decision about data storage approach",
            context="Performance issues with current storage",
            rationale="Better performance and scalability"
        )
        
        manager.add_decision(decision1)
        manager.add_decision(decision2)
        
        # Search for "authentication"
        auth_results = manager.search_decisions("authentication")
        
        # Check result
        assert len(auth_results) == 1
        assert auth_results[0].title == "Authentication System Redesign"
        
        # Search for "performance"
        perf_results = manager.search_decisions("performance")
        
        # Check result
        assert len(perf_results) == 1
        assert perf_results[0].title == "Data Storage Strategy"
    
    def test_get_decisions_by_status(self, temp_dir, mock_decisions):
        """Test getting decisions with or without outcomes."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add decisions with and without outcomes
        decision_with_outcome = mock_decisions[0]
        decision_with_outcome.outcome_notes = "Implementation successful"
        decision_with_outcome.outcome_date = datetime.now() - timedelta(days=10)
        manager.add_decision(decision_with_outcome)
        
        decision_without_outcome = mock_decisions[1]
        decision_without_outcome.outcome_notes = None
        decision_without_outcome.outcome_date = None
        manager.add_decision(decision_without_outcome)
        
        # Get decisions with outcomes
        completed_decisions = manager.get_decisions_by_status(has_outcome=True)
        
        # Check result
        assert len(completed_decisions) == 1
        assert completed_decisions[0].id == decision_with_outcome.id
        
        # Get decisions without outcomes
        pending_decisions = manager.get_decisions_by_status(has_outcome=False)
        
        # Check result
        assert len(pending_decisions) == 1
        assert pending_decisions[0].id == decision_without_outcome.id
    
    def test_get_decisions_by_feature(self, temp_dir, mock_decisions, mock_data_generator):
        """Test getting decisions related to a feature."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create a feature
        feature_id = uuid4()
        
        # Add decisions, some related to the feature
        decision_related = mock_decisions[0]
        decision_related.feature_ids = [feature_id]
        manager.add_decision(decision_related)
        
        decision_unrelated = mock_decisions[1]
        decision_unrelated.feature_ids = [uuid4()]  # Different feature
        manager.add_decision(decision_unrelated)
        
        # Get decisions for the feature
        feature_decisions = manager.get_decisions_by_feature(feature_id)
        
        # Check result
        assert len(feature_decisions) == 1
        assert feature_decisions[0].id == decision_related.id
    
    def test_get_decisions_by_objective(self, temp_dir, mock_decisions, mock_data_generator):
        """Test getting decisions related to a strategic objective."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create an objective
        objective_id = uuid4()
        
        # Add decisions, some related to the objective
        decision_related = mock_decisions[0]
        decision_related.objective_ids = [objective_id]
        manager.add_decision(decision_related)
        
        decision_unrelated = mock_decisions[1]
        decision_unrelated.objective_ids = [uuid4()]  # Different objective
        manager.add_decision(decision_unrelated)
        
        # Get decisions for the objective
        objective_decisions = manager.get_decisions_by_objective(objective_id)
        
        # Check result
        assert len(objective_decisions) == 1
        assert objective_decisions[0].id == decision_related.id
    
    def test_get_decision_history(self, temp_dir, mock_decisions):
        """Test getting the history of related decisions."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create a chain of related decisions
        decision1 = Decision(
            title="Initial Authentication Approach",
            description="First decision about authentication",
            context="Need secure authentication",
            rationale="Selected OAuth for simplicity",
            decision_date=datetime.now() - timedelta(days=100)
        )
        
        decision2 = Decision(
            title="Authentication Enhancement",
            description="Follow-up to initial authentication decision",
            context="OAuth implementation has limitations",
            rationale="Adding MFA for additional security",
            decision_date=datetime.now() - timedelta(days=50)
        )
        
        decision3 = Decision(
            title="Authentication Redesign",
            description="Complete redesign of authentication",
            context="Current approach not meeting needs",
            rationale="Moving to a custom solution",
            decision_date=datetime.now() - timedelta(days=10)
        )
        
        # Add decisions
        added1 = manager.add_decision(decision1)
        decision2.related_decisions = [added1.id]
        added2 = manager.add_decision(decision2)
        decision3.related_decisions = [added2.id]
        added3 = manager.add_decision(decision3)
        
        # Get decision history
        history = manager.get_decision_history(added3.id)
        
        # Check result
        assert len(history) == 3
        assert history[0].id == added1.id  # Oldest first
        assert history[1].id == added2.id
        assert history[2].id == added3.id  # Most recent last
    
    def test_generate_decision_report(self, temp_dir, mock_decisions):
        """Test generating a decision report."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add a decision with comprehensive data
        decision = Decision(
            title="Major Platform Migration",
            description="Decision to migrate from on-premise to cloud platform",
            context="Growing scalability and maintenance challenges with current platform",
            rationale="Cloud offers better scalability, reduced maintenance, and modern features",
            alternatives=["Stay on-premise with upgrades", "Hybrid approach", "Different cloud provider"],
            decided_by=[uuid4(), uuid4()],
            stakeholder_input={str(uuid4()): "Supportive of cloud migration"},
            decision_date=datetime.now() - timedelta(days=90),
            outcome_notes="Migration completed successfully with minor issues",
            outcome_date=datetime.now() - timedelta(days=30),
            retrospective="Should have allocated more time for data migration testing"
        )
        
        added_decision = manager.add_decision(decision)
        
        # Generate report
        report = manager.generate_decision_report(added_decision.id)

        # Check result
        assert "Major Platform Migration" in report
        assert "Growing scalability" in report
        assert "alternatives" in report.lower()
        assert "outcome" in report.lower()
        assert "retrospective" in report.lower()