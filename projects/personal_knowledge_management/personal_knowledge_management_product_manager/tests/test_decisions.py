"""
Tests for the decisions module.

This module tests the decision management functionality of the ProductInsight system,
including decision documentation, retrieval, and analysis.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List
from uuid import UUID, uuid4

import pytest

from product_insight.models import (
    Decision,
    Stakeholder,
    StakeholderRoleEnum,
    InfluenceEnum,
    StatusEnum,
    Tag
)
from product_insight.decisions.manager import (
    DecisionManager,
    DecisionQuery,
    DecisionOutcome
)
from product_insight.decisions.visualization import (
    DecisionVisualizer,
    create_decision_timeline,
    create_decision_tree,
    create_stakeholder_influence_chart
)
from product_insight.storage import FileStorage

from tests.fixtures.fixtures import (
    mock_data_generator,
    mock_decisions,
    mock_stakeholders,
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
    
    def test_search_decisions(self, temp_dir, mock_decisions):
        """Test searching decisions by text."""
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
        query = DecisionQuery(text="authentication")
        auth_results = manager.search_decisions(query)
        
        # Check result
        assert len(auth_results) == 1
        assert auth_results[0].title == "Authentication System Redesign"
        
        # Search for "performance"
        query = DecisionQuery(text="performance")
        perf_results = manager.search_decisions(query)
        
        # Check result
        assert len(perf_results) == 1
        assert perf_results[0].title == "Data Storage Strategy"
    
    def test_search_decisions_by_date(self, temp_dir):
        """Test searching decisions by date range."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create decisions with different dates
        now = datetime.now()
        
        # Decision from 10 days ago
        decision1 = Decision(
            title="Old Decision",
            description="An old decision",
            context="Context",
            rationale="Rationale",
            decision_date=now - timedelta(days=10)
        )
        
        # Decision from 5 days ago
        decision2 = Decision(
            title="Recent Decision",
            description="A recent decision",
            context="Context",
            rationale="Rationale",
            decision_date=now - timedelta(days=5)
        )
        
        # Decision from today
        decision3 = Decision(
            title="New Decision",
            description="A new decision",
            context="Context",
            rationale="Rationale",
            decision_date=now
        )
        
        # Add decisions
        manager.add_decision(decision1)
        manager.add_decision(decision2)
        manager.add_decision(decision3)
        
        # Search for decisions from the last 7 days
        query = DecisionQuery(start_date=now - timedelta(days=7))
        results = manager.search_decisions(query)
        
        # Check results
        assert len(results) == 2
        assert any(d.title == "Recent Decision" for d in results)
        assert any(d.title == "New Decision" for d in results)
        assert not any(d.title == "Old Decision" for d in results)
        
        # Search for decisions between 15 and 3 days ago
        query = DecisionQuery(
            start_date=now - timedelta(days=15),
            end_date=now - timedelta(days=3)
        )
        results = manager.search_decisions(query)
        
        # Check results
        assert len(results) == 2
        assert any(d.title == "Old Decision" for d in results)
        assert any(d.title == "Recent Decision" for d in results)
        assert not any(d.title == "New Decision" for d in results)
    
    def test_search_decisions_by_tags(self, temp_dir):
        """Test searching decisions by tags."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create decisions with different tags
        tag1 = Tag(name="Mobile")
        tag2 = Tag(name="Architecture")
        tag3 = Tag(name="UX")
        
        decision1 = Decision(
            title="Mobile Decision",
            description="Description",
            context="Context",
            rationale="Rationale",
            tags=[tag1, tag2]
        )
        
        decision2 = Decision(
            title="Architecture Decision",
            description="Description",
            context="Context",
            rationale="Rationale",
            tags=[tag2, tag3]
        )
        
        decision3 = Decision(
            title="UX Decision",
            description="Description",
            context="Context",
            rationale="Rationale",
            tags=[tag3]
        )
        
        # Add decisions
        manager.add_decision(decision1)
        manager.add_decision(decision2)
        manager.add_decision(decision3)
        
        # Search for decisions with Mobile tag
        query = DecisionQuery(tags=["Mobile"])
        results = manager.search_decisions(query)
        
        # Check results
        assert len(results) == 1
        assert results[0].title == "Mobile Decision"
        
        # Search for decisions with Architecture tag
        query = DecisionQuery(tags=["Architecture"])
        results = manager.search_decisions(query)
        
        # Check results
        assert len(results) == 2
        assert any(d.title == "Mobile Decision" for d in results)
        assert any(d.title == "Architecture Decision" for d in results)
    
    def test_get_decisions_by_feature(self, temp_dir):
        """Test getting decisions related to a specific feature."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create feature IDs
        feature1_id = uuid4()
        feature2_id = uuid4()
        
        # Create decisions related to different features
        decision1 = Decision(
            title="Feature 1 Decision",
            description="Decision about Feature 1",
            context="Context",
            rationale="Rationale",
            feature_ids=[feature1_id]
        )
        
        decision2 = Decision(
            title="Feature 2 Decision",
            description="Decision about Feature 2",
            context="Context",
            rationale="Rationale",
            feature_ids=[feature2_id]
        )
        
        decision3 = Decision(
            title="Both Features Decision",
            description="Decision about both features",
            context="Context",
            rationale="Rationale",
            feature_ids=[feature1_id, feature2_id]
        )
        
        # Add decisions
        manager.add_decision(decision1)
        manager.add_decision(decision2)
        manager.add_decision(decision3)
        
        # Get decisions for feature 1
        decisions = manager.find_decisions_by_feature(feature1_id)
        
        # Check results
        assert len(decisions) == 2
        assert any(d.title == "Feature 1 Decision" for d in decisions)
        assert any(d.title == "Both Features Decision" for d in decisions)
        assert not any(d.title == "Feature 2 Decision" for d in decisions)
    
    def test_get_decisions_by_objective(self, temp_dir):
        """Test getting decisions related to a specific strategic objective."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create objective IDs
        objective1_id = uuid4()
        objective2_id = uuid4()
        
        # Create decisions related to different objectives
        decision1 = Decision(
            title="Objective 1 Decision",
            description="Decision about Objective 1",
            context="Context",
            rationale="Rationale",
            objective_ids=[objective1_id]
        )
        
        decision2 = Decision(
            title="Objective 2 Decision",
            description="Decision about Objective 2",
            context="Context",
            rationale="Rationale",
            objective_ids=[objective2_id]
        )
        
        decision3 = Decision(
            title="Both Objectives Decision",
            description="Decision about both objectives",
            context="Context",
            rationale="Rationale",
            objective_ids=[objective1_id, objective2_id]
        )
        
        # Add decisions
        manager.add_decision(decision1)
        manager.add_decision(decision2)
        manager.add_decision(decision3)
        
        # Get decisions for objective 1
        decisions = manager.find_decisions_by_objective(objective1_id)
        
        # Check results
        assert len(decisions) == 2
        assert any(d.title == "Objective 1 Decision" for d in decisions)
        assert any(d.title == "Both Objectives Decision" for d in decisions)
        assert not any(d.title == "Objective 2 Decision" for d in decisions)
    
    def test_find_decisions_by_stakeholder(self, temp_dir):
        """Test finding decisions involving a specific stakeholder."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)

        # Create stakeholder IDs
        stakeholder1_id = uuid4()
        stakeholder2_id = uuid4()

        # Create decisions involving different stakeholders
        decision1 = Decision(
            title="Stakeholder 1 Decision",
            description="Decision involving Stakeholder 1",
            context="Context",
            rationale="Rationale",
            decided_by=[stakeholder1_id]
        )

        decision2 = Decision(
            title="Stakeholder 2 Decision",
            description="Decision involving Stakeholder 2",
            context="Context",
            rationale="Rationale",
            decided_by=[stakeholder2_id]
        )

        decision3 = Decision(
            title="Both Stakeholders Decision",
            description="Decision involving both stakeholders",
            context="Context",
            rationale="Rationale",
            decided_by=[stakeholder1_id, stakeholder2_id]
        )

        decision4 = Decision(
            title="Stakeholder 1 Input Decision",
            description="Decision with input from Stakeholder 1",
            context="Context",
            rationale="Rationale",
            stakeholder_input={str(stakeholder1_id): "Input from Stakeholder 1"}
        )
        
        # Add decisions
        manager.add_decision(decision1)
        manager.add_decision(decision2)
        manager.add_decision(decision3)
        manager.add_decision(decision4)
        
        # Find decisions involving stakeholder 1
        decisions = manager.find_decisions_by_stakeholder(stakeholder1_id)
        
        # Check results
        assert len(decisions) == 3
        assert any(d.title == "Stakeholder 1 Decision" for d in decisions)
        assert any(d.title == "Both Stakeholders Decision" for d in decisions)
        assert any(d.title == "Stakeholder 1 Input Decision" for d in decisions)
        assert not any(d.title == "Stakeholder 2 Decision" for d in decisions)
    
    def test_get_decision_timeline(self, temp_dir):
        """Test getting a timeline of decisions."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Create decisions with different dates
        now = datetime.now()
        
        decision1 = Decision(
            title="Decision 1",
            description="First decision",
            context="Context",
            rationale="Rationale",
            decision_date=now - timedelta(days=30)
        )
        
        decision2 = Decision(
            title="Decision 2",
            description="Second decision",
            context="Context",
            rationale="Rationale",
            decision_date=now - timedelta(days=20)
        )
        
        decision3 = Decision(
            title="Decision 3",
            description="Third decision",
            context="Context",
            rationale="Rationale",
            decision_date=now - timedelta(days=10)
        )
        
        # Add decisions
        manager.add_decision(decision1)
        manager.add_decision(decision2)
        manager.add_decision(decision3)
        
        # Get timeline for all decisions
        timeline = manager.get_decision_timeline()
        
        # Check results
        assert len(timeline.decisions) == 3
        
        # Check that decisions are in chronological order
        dates = [date for date, _ in timeline.decisions]
        assert dates == sorted(dates)
        
        # Get timeline with date filter
        timeline = manager.get_decision_timeline(
            start_date=now - timedelta(days=25),
            end_date=now - timedelta(days=5)
        )
        
        # Check filtered results
        assert len(timeline.decisions) == 2
        assert any(d.title == "Decision 2" for _, d in timeline.decisions)
        assert any(d.title == "Decision 3" for _, d in timeline.decisions)
        assert not any(d.title == "Decision 1" for _, d in timeline.decisions)
    
    def test_add_decision_outcome(self, temp_dir, mock_decisions):
        """Test adding an outcome to a decision."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)
        
        # Add a decision without outcome
        decision = mock_decisions[0]
        # Ensure no outcome is set
        decision.outcome_notes = None
        decision.outcome_date = None
        decision.retrospective = None
        
        added_decision = manager.add_decision(decision)
        
        # Create outcome data
        outcome = DecisionOutcome(
            decision_id=added_decision.id,
            outcome_notes="Implementation completed successfully.",
            outcome_date=datetime.now(),
            success_rating=0.9,
            retrospective="The decision process was effective, though we could have involved more stakeholders."
        )
        
        # Add outcome
        updated_decision = manager.add_decision_outcome(added_decision.id, outcome)
        
        # Check results
        assert updated_decision.outcome_notes == "Implementation completed successfully."
        assert updated_decision.outcome_date is not None
        assert updated_decision.retrospective == "The decision process was effective, though we could have involved more stakeholders."
        
        # Verify storage
        stored_decision = manager.decision_storage.get(added_decision.id)
        assert stored_decision.outcome_notes == "Implementation completed successfully."
        assert stored_decision.outcome_date is not None
        assert stored_decision.retrospective == "The decision process was effective, though we could have involved more stakeholders."
    
    def test_generate_decision_report(self, temp_dir):
        """Test generating a report for decisions."""
        # Create a manager
        manager = DecisionManager(storage_dir=temp_dir)

        # Create decisions for the report
        now = datetime.now()
        stakeholder_id = uuid4()
        feature_id = uuid4()

        decision1 = Decision(
            title="Architecture Decision",
            description="Decision about system architecture",
            context="We need to choose an architecture for the new system.",
            rationale="We chose microservices for scalability and flexibility.",
            alternatives=["Monolith", "Serverless"],
            decision_date=now - timedelta(days=30),
            decided_by=[stakeholder_id],
            stakeholder_input={str(stakeholder_id): "I support this decision."},
            feature_ids=[feature_id],
            outcome_notes="Implementation is on track.",
            outcome_date=now - timedelta(days=10),
            tags=[Tag(name="Architecture"), Tag(name="Technical")]
        )
        
        decision2 = Decision(
            title="UI Framework Decision",
            description="Decision about UI framework",
            context="We need to choose a UI framework for the frontend.",
            rationale="We chose React for its ecosystem and flexibility.",
            alternatives=["Angular", "Vue"],
            decision_date=now - timedelta(days=20),
            feature_ids=[feature_id]
        )
        
        # Add decisions
        manager.add_decision(decision1)
        manager.add_decision(decision2)
        
        # Generate markdown report
        report = manager.generate_decision_report([decision1, decision2], "markdown")
        
        # Check report content
        assert "# Decision Report" in report
        assert "Architecture Decision" in report
        assert "UI Framework Decision" in report
        assert "We chose microservices for scalability and flexibility." in report
        assert "We chose React for its ecosystem and flexibility." in report
        assert "Monolith" in report
        assert "Angular" in report
        assert "Implementation is on track." in report
        
        # Generate text report
        report = manager.generate_decision_report([decision1, decision2], "text")
        
        # Check report content
        assert "DECISION REPORT" in report
        assert "TITLE: Architecture Decision" in report
        assert "TITLE: UI Framework Decision" in report
        assert "RATIONALE:" in report
        assert "We chose microservices for scalability and flexibility." in report
        assert "We chose React for its ecosystem and flexibility." in report


class TestDecisionVisualizer:
    """Tests for the DecisionVisualizer class."""
    
    def test_decision_to_markdown(self, mock_decisions):
        """Test converting a decision to Markdown format."""
        # Get a test decision
        decision = mock_decisions[0]
        
        # Convert to Markdown
        markdown = DecisionVisualizer.decision_to_markdown(decision)
        
        # Check Markdown content
        assert f"# {decision.title}" in markdown
        assert "## Context" in markdown
        assert decision.context in markdown
        assert "## Rationale" in markdown
        assert decision.rationale in markdown
        
        # Check alternatives if present
        if decision.alternatives:
            assert "## Alternatives Considered" in markdown
            for alt in decision.alternatives:
                assert alt in markdown
        
        # Check outcome if present
        if decision.outcome_notes:
            assert "## Outcome" in markdown
            assert decision.outcome_notes in markdown
    
    def test_timeline_to_json(self, mock_decisions):
        """Test converting a timeline to JSON."""
        from product_insight.decisions.visualization import TimelineItem

        # Create timeline items
        timeline_items = [
            TimelineItem(
                id=str(mock_decisions[0].id),
                title=mock_decisions[0].title,
                date=datetime.now().isoformat(),
                type="decision",
                description=mock_decisions[0].description,
                tags=["tag1", "tag2"],
                related_ids=["id1", "id2"]
            ),
            TimelineItem(
                id=str(mock_decisions[1].id),
                title=mock_decisions[1].title,
                date=(datetime.now() - timedelta(days=10)).isoformat(),
                type="decision",
                description=mock_decisions[1].description
            )
        ]

        # Convert to JSON
        json_str = DecisionVisualizer.timeline_to_json(timeline_items)

        # Check JSON content
        assert json_str
        assert mock_decisions[0].title in json_str
        assert mock_decisions[1].title in json_str
        assert '"type": "decision"' in json_str
        # Check that tags and related_ids are in JSON, avoiding exact format checks
        assert "tag1" in json_str and "tag2" in json_str
        assert "id1" in json_str and "id2" in json_str
    
    def test_decision_tree_to_json(self, mock_decisions):
        """Test converting a decision tree to JSON."""
        from product_insight.decisions.visualization import TreeNode
        
        # Create a tree structure
        root = TreeNode(
            id=str(mock_decisions[0].id),
            name=mock_decisions[0].title,
            type="decision",
            description=mock_decisions[0].description,
            date=datetime.now().isoformat(),
            children=[
                TreeNode(
                    id="feature1",
                    name="Feature 1",
                    type="feature",
                    description="Feature description"
                ),
                TreeNode(
                    id="objective1",
                    name="Objective 1",
                    type="objective",
                    description="Objective description"
                )
            ]
        )
        
        # Convert to JSON
        json_str = DecisionVisualizer.decision_tree_to_json(root)
        
        # Check JSON content
        assert json_str
        assert f'"{mock_decisions[0].title}"' in json_str
        assert '"Feature 1"' in json_str
        assert '"Objective 1"' in json_str
        assert '"children":' in json_str
        assert '"type": "feature"' in json_str
        assert '"type": "objective"' in json_str


def test_create_decision_timeline(mock_decisions):
    """Test creating a decision timeline visualization."""
    # Create test data with various decision dates
    decisions = []
    now = datetime.now()
    
    # Add decisions with different dates spanning 6 months
    for i in range(6):
        decision = Decision(
            title=f"Decision {i+1}",
            description=f"Description {i+1}",
            context="Context",
            rationale="Rationale", 
            decision_date=now - timedelta(days=i*30)  # Every 30 days
        )
        decisions.append(decision)
        
        # Add outcome dates for some decisions
        if i % 2 == 0:
            decision.outcome_date = now - timedelta(days=i*30 - 15)  # 15 days after decision
    
    # Create timeline
    timeline = create_decision_timeline(decisions)
    
    # Check results
    assert timeline
    assert "title" in timeline
    assert "decisions" in timeline
    assert "timespan" in timeline
    
    # Check decision entries
    for decision in decisions:
        # Each decision should be in the timeline
        assert any(d["title"] == decision.title for d in timeline["decisions"])
        
    # Check timespan
    assert timeline["timespan"]["start_date"] <= timeline["timespan"]["end_date"]
    

def test_create_decision_tree(mock_decisions):
    """Test creating a decision tree visualization."""
    # Create a complex decision with alternatives
    decision = Decision(
        title="Main Decision",
        description="A decision with alternatives",
        context="The context for this decision...",
        rationale="We chose Option A because...",
        alternatives=[
            "Option B: Would cost more but deliver faster",
            "Option C: Lower cost but higher maintenance",
            "Option D: Third-party solution with less control"
        ]
    )
    
    # Create decision tree
    tree = create_decision_tree(decision)
    
    # Check results
    assert tree
    assert "title" in tree
    assert "main_decision" in tree
    assert "alternatives" in tree
    assert "rationale" in tree
    
    assert tree["title"] == "Decision Tree: Main Decision"
    assert tree["main_decision"] == "Main Decision"
    assert len(tree["alternatives"]) == 3
    assert "Option B" in str(tree["alternatives"])
    assert "Option C" in str(tree["alternatives"])
    assert "Option D" in str(tree["alternatives"])
    assert tree["rationale"] == "We chose Option A because..."
    

def test_create_stakeholder_influence_chart(mock_decisions, mock_stakeholders):
    """Test creating a stakeholder influence chart for a decision."""
    # Use existing stakeholders from fixtures
    stakeholders = mock_stakeholders[:4]

    # Ensure stakeholders have different influence levels
    influence_levels = list(InfluenceEnum)
    for i, stakeholder in enumerate(stakeholders):
        stakeholder.influence = influence_levels[i % len(influence_levels)]

    # Create a decision with stakeholder input
    decision = Decision(
        title="Stakeholder Decision",
        description="A decision with stakeholder input",
        context="Context...",
        rationale="Rationale...",
        decided_by=[stakeholder.id for stakeholder in stakeholders[:2]],  # First two stakeholders decided
        stakeholder_input={
            str(stakeholders[0].id): "Strongly support",
            str(stakeholders[1].id): "Support with reservations",
            str(stakeholders[2].id): "Oppose due to technical concerns",
            str(stakeholders[3].id): "Neutral, need more information"
        }
    )
    
    # Create chart
    chart = create_stakeholder_influence_chart(decision, stakeholders)
    
    # Check results
    assert chart
    assert "title" in chart
    assert "stakeholders" in chart
    assert "decision" in chart
    
    assert chart["title"] == "Stakeholder Influence: Stakeholder Decision"
    assert len(chart["stakeholders"]) == 4
    
    # Check stakeholder entries
    for entry in chart["stakeholders"]:
        assert "id" in entry
        assert "name" in entry
        assert "role" in entry
        assert "influence" in entry
        assert "input" in entry
        assert "decided" in entry  # Boolean indicating if they made the decision