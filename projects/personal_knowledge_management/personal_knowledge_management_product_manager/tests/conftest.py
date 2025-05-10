"""
Pytest configuration for ProductInsight.

This module provides pytest fixtures that are available to all test modules.
"""

import pytest

# Import fixtures to make them available to all tests
from tests.fixtures.fixtures import (
    temp_dir,
    mock_data_generator,
    mock_feedback_items,
    mock_feedback_clusters,
    mock_strategic_objectives,
    mock_features,
    mock_decisions,
    mock_stakeholders,
    mock_stakeholder_perspectives,
    mock_competitors,
    populated_storage_dir,
    feedback_manager,
)