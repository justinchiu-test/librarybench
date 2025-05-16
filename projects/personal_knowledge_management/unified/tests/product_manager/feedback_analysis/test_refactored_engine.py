"""Test the refactored FeedbackAnalysisEngine."""
import os
import tempfile
import pytest
from pathlib import Path
from uuid import uuid4

from common.core.storage import LocalStorage
from common.core.knowledge import KnowledgeGraph, StandardKnowledgeBase
from productmind.feedback_analysis.engine import FeedbackAnalysisEngine
from productmind.models import Feedback, SourceType, Sentiment, Theme


@pytest.fixture
def temp_storage():
    """Create a temporary directory for storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(Path(tmpdir))
        yield storage


def test_feedback_analysis_engine_refactored(temp_storage):
    """Test that the refactored engine initializes and works correctly."""
    # Initialize engine with the storage
    engine = FeedbackAnalysisEngine(storage=temp_storage)
    
    # Verify engine properties
    assert isinstance(engine.knowledge_base, StandardKnowledgeBase)
    assert isinstance(engine.knowledge_graph, KnowledgeGraph)
    
    # Create a test feedback item
    feedback = Feedback(
        title="Test Feedback",
        content="This is a test feedback. I really like the product but the UI could be improved.",
        source=SourceType.SURVEY,
        tags={"test", "feedback"}
    )
    
    # Add the feedback
    feedback_ids = engine.add_feedback(feedback)
    assert len(feedback_ids) == 1
    
    # Retrieve the feedback
    retrieved = engine.get_feedback(feedback_ids[0])
    assert retrieved is not None
    assert retrieved.id == feedback.id
    assert retrieved.title == "Test Feedback"
    assert retrieved.content == feedback.content
    
    # Test sentiment analysis
    sentiments = engine.analyze_sentiment(feedback)
    assert len(sentiments) == 1
    assert feedback_ids[0] in sentiments
    assert sentiments[feedback_ids[0]] == Sentiment.POSITIVE
    
    # Test that the feedback was updated with sentiment
    updated = engine.get_feedback(feedback_ids[0])
    assert updated.sentiment == Sentiment.POSITIVE
    
    # Test theme extraction (with simplified settings for testing)
    engine.min_cluster_size = 1
    engine.max_themes = 5
    themes = engine.extract_themes([feedback_ids[0]], min_frequency=1)
    assert len(themes) > 0
    
    # Verify theme was created correctly
    assert isinstance(themes[0], Theme)
    assert themes[0].feedback_ids[0] == feedback.id
    
    # Test the updated feedback has themes
    updated = engine.get_feedback(feedback_ids[0])
    assert len(updated.themes) > 0
    
    # Test search
    search_results = engine.search_feedback("test feedback")
    assert len(search_results) == 1
    assert search_results[0].id == feedback.id