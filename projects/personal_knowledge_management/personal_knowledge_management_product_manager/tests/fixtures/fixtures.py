"""
Test fixtures for ProductInsight.

This module provides pytest fixtures for testing the ProductInsight system.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Iterator, List, Tuple

import pytest

from product_insight.feedback.manager import FeedbackManager
from product_insight.models import (
    Competitor,
    Decision,
    Feature,
    FeedbackCluster,
    FeedbackItem,
    Stakeholder,
    StakeholderPerspective,
    StrategicObjective,
)
from product_insight.storage import FileStorage
from tests.fixtures.generators import MockDataGenerator


@pytest.fixture
def temp_dir() -> Iterator[str]:
    """Provide a temporary directory for test data.
    
    Yields:
        Path to temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_data_generator() -> MockDataGenerator:
    """Provide a mock data generator.
    
    Returns:
        MockDataGenerator instance
    """
    return MockDataGenerator(seed=42)  # Use fixed seed for reproducibility


@pytest.fixture
def mock_feedback_items(mock_data_generator: MockDataGenerator) -> List[FeedbackItem]:
    """Provide mock feedback items.
    
    Args:
        mock_data_generator: Mock data generator
        
    Returns:
        List of mock feedback items
    """
    return mock_data_generator.generate_feedback_items(50)


@pytest.fixture
def mock_feedback_clusters(
    mock_data_generator: MockDataGenerator, mock_feedback_items: List[FeedbackItem]
) -> List[FeedbackCluster]:
    """Provide mock feedback clusters.
    
    Args:
        mock_data_generator: Mock data generator
        mock_feedback_items: Mock feedback items
        
    Returns:
        List of mock feedback clusters
    """
    return mock_data_generator.generate_feedback_clusters(mock_feedback_items, 5)


@pytest.fixture
def mock_strategic_objectives(mock_data_generator: MockDataGenerator) -> List[StrategicObjective]:
    """Provide mock strategic objectives.
    
    Args:
        mock_data_generator: Mock data generator
        
    Returns:
        List of mock strategic objectives
    """
    return mock_data_generator.generate_strategic_objectives(20)


@pytest.fixture
def mock_features(mock_data_generator: MockDataGenerator) -> List[Feature]:
    """Provide mock features.
    
    Args:
        mock_data_generator: Mock data generator
        
    Returns:
        List of mock features
    """
    return mock_data_generator.generate_features(30)


@pytest.fixture
def mock_decisions(mock_data_generator: MockDataGenerator) -> List[Decision]:
    """Provide mock decisions.
    
    Args:
        mock_data_generator: Mock data generator
        
    Returns:
        List of mock decisions
    """
    return mock_data_generator.generate_decisions(15)


@pytest.fixture
def mock_stakeholders(mock_data_generator: MockDataGenerator) -> List[Stakeholder]:
    """Provide mock stakeholders.
    
    Args:
        mock_data_generator: Mock data generator
        
    Returns:
        List of mock stakeholders
    """
    return mock_data_generator.generate_stakeholders(25)


@pytest.fixture
def mock_stakeholder_perspectives(
    mock_data_generator: MockDataGenerator, mock_stakeholders: List[Stakeholder]
) -> List[StakeholderPerspective]:
    """Provide mock stakeholder perspectives.
    
    Args:
        mock_data_generator: Mock data generator
        mock_stakeholders: Mock stakeholders
        
    Returns:
        List of mock stakeholder perspectives
    """
    return mock_data_generator.generate_stakeholder_perspectives(mock_stakeholders, 2.0)


@pytest.fixture
def mock_competitors(mock_data_generator: MockDataGenerator) -> List[Competitor]:
    """Provide mock competitors.
    
    Args:
        mock_data_generator: Mock data generator
        
    Returns:
        List of mock competitors
    """
    return mock_data_generator.generate_competitors(10)


@pytest.fixture
def populated_storage_dir(
    temp_dir: str,
    mock_feedback_items: List[FeedbackItem],
    mock_feedback_clusters: List[FeedbackCluster],
    mock_strategic_objectives: List[StrategicObjective],
    mock_features: List[Feature],
    mock_decisions: List[Decision],
    mock_stakeholders: List[Stakeholder],
    mock_stakeholder_perspectives: List[StakeholderPerspective],
    mock_competitors: List[Competitor],
) -> str:
    """Provide a temporary directory populated with mock data.
    
    Args:
        temp_dir: Temporary directory
        mock_feedback_items: Mock feedback items
        mock_feedback_clusters: Mock feedback clusters
        mock_strategic_objectives: Mock strategic objectives
        mock_features: Mock features
        mock_decisions: Mock decisions
        mock_stakeholders: Mock stakeholders
        mock_stakeholder_perspectives: Mock stakeholder perspectives
        mock_competitors: Mock competitors
        
    Returns:
        Path to populated storage directory
    """
    # Define storage path
    storage_dir = os.path.join(temp_dir, "product_insight_data")
    os.makedirs(storage_dir, exist_ok=True)
    
    # Initialize storage interfaces
    feedback_storage = FileStorage(
        entity_type=FeedbackItem,
        storage_dir=os.path.join(storage_dir, "feedback"),
        format="json"
    )
    
    cluster_storage = FileStorage(
        entity_type=FeedbackCluster,
        storage_dir=os.path.join(storage_dir, "feedback_clusters"),
        format="json"
    )
    
    objective_storage = FileStorage(
        entity_type=StrategicObjective,
        storage_dir=os.path.join(storage_dir, "objectives"),
        format="json"
    )
    
    feature_storage = FileStorage(
        entity_type=Feature,
        storage_dir=os.path.join(storage_dir, "features"),
        format="json"
    )
    
    decision_storage = FileStorage(
        entity_type=Decision,
        storage_dir=os.path.join(storage_dir, "decisions"),
        format="json"
    )
    
    stakeholder_storage = FileStorage(
        entity_type=Stakeholder,
        storage_dir=os.path.join(storage_dir, "stakeholders"),
        format="json"
    )
    
    perspective_storage = FileStorage(
        entity_type=StakeholderPerspective,
        storage_dir=os.path.join(storage_dir, "stakeholder_perspectives"),
        format="json"
    )
    
    competitor_storage = FileStorage(
        entity_type=Competitor,
        storage_dir=os.path.join(storage_dir, "competitors"),
        format="json"
    )
    
    # Populate storage with mock data
    for item in mock_feedback_items:
        feedback_storage.save(item)
    
    for cluster in mock_feedback_clusters:
        cluster_storage.save(cluster)
    
    for objective in mock_strategic_objectives:
        objective_storage.save(objective)
    
    for feature in mock_features:
        feature_storage.save(feature)
    
    for decision in mock_decisions:
        decision_storage.save(decision)
    
    for stakeholder in mock_stakeholders:
        stakeholder_storage.save(stakeholder)
    
    for perspective in mock_stakeholder_perspectives:
        perspective_storage.save(perspective)
    
    for competitor in mock_competitors:
        competitor_storage.save(competitor)
    
    return storage_dir


@pytest.fixture
def feedback_manager(populated_storage_dir: str) -> FeedbackManager:
    """Provide a feedback manager with populated storage.
    
    Args:
        populated_storage_dir: Directory with populated storage
        
    Returns:
        FeedbackManager instance
    """
    return FeedbackManager(storage_dir=populated_storage_dir)