"""
Tests for the storage module.

This module tests the storage functionality of the ProductInsight system.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
import yaml

from product_insight.models import (
    Feature,
    FeedbackItem,
    SourceEnum,
    Tag,
)
from product_insight.storage import (
    DataExporter,
    DataImporter,
    EntityNotFoundError,
    FileStorage,
    ReportGenerator,
)
from product_insight.storage.base import StorageInterface


class TestFileStorage:
    """Tests for the FileStorage class."""
    
    def test_initialization(self, temp_dir):
        """Test initializing a FileStorage instance."""
        # Create a storage instance
        storage_dir = os.path.join(temp_dir, "feedback")
        storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=storage_dir,
            format="json"
        )
        
        # Check properties
        assert storage.entity_type == FeedbackItem
        assert storage.storage_dir == Path(storage_dir)
        assert storage.format == "json"
        
        # Check directory creation
        assert os.path.exists(storage_dir)
    
    def test_save_and_get(self, temp_dir):
        """Test saving and retrieving an entity."""
        # Create a storage instance
        storage_dir = os.path.join(temp_dir, "feedback")
        storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=storage_dir,
            format="json"
        )
        
        # Create a feedback item
        feedback = FeedbackItem(
            content="Test feedback",
            source=SourceEnum.CUSTOMER_INTERVIEW
        )
        
        # Save the feedback item
        saved_feedback = storage.save(feedback)
        
        # Check the saved feedback
        assert saved_feedback.id == feedback.id
        assert saved_feedback.content == "Test feedback"
        assert saved_feedback.source == SourceEnum.CUSTOMER_INTERVIEW
        
        # Check file creation
        file_path = os.path.join(storage_dir, f"{feedback.id}.json")
        assert os.path.exists(file_path)
        
        # Retrieve the feedback item
        retrieved_feedback = storage.get(feedback.id)
        
        # Check the retrieved feedback
        assert retrieved_feedback.id == feedback.id
        assert retrieved_feedback.content == "Test feedback"
        assert retrieved_feedback.source == SourceEnum.CUSTOMER_INTERVIEW
    
    def test_list_entities(self, temp_dir):
        """Test listing entities."""
        # Create a storage instance
        storage_dir = os.path.join(temp_dir, "feedback")
        storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=storage_dir,
            format="json"
        )
        
        # Create and save multiple feedback items
        feedback1 = FeedbackItem(
            content="Test feedback 1",
            source=SourceEnum.CUSTOMER_INTERVIEW
        )
        feedback2 = FeedbackItem(
            content="Test feedback 2",
            source=SourceEnum.SURVEY
        )
        
        storage.save(feedback1)
        storage.save(feedback2)
        
        # List all feedback items
        all_feedback = storage.list()
        
        # Check results
        assert len(all_feedback) == 2
        
        # Check if original items are in the list
        feedback_ids = [feedback.id for feedback in all_feedback]
        assert feedback1.id in feedback_ids
        assert feedback2.id in feedback_ids
    
    def test_delete_entity(self, temp_dir):
        """Test deleting an entity."""
        # Create a storage instance
        storage_dir = os.path.join(temp_dir, "feedback")
        storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=storage_dir,
            format="json"
        )
        
        # Create and save a feedback item
        feedback = FeedbackItem(
            content="Test feedback",
            source=SourceEnum.CUSTOMER_INTERVIEW
        )
        
        storage.save(feedback)
        
        # Check file creation
        file_path = os.path.join(storage_dir, f"{feedback.id}.json")
        assert os.path.exists(file_path)
        
        # Delete the feedback item
        result = storage.delete(feedback.id)
        
        # Check deletion result
        assert result is True
        
        # Check file deletion
        assert not os.path.exists(file_path)
        
        # Try to get the deleted entity
        with pytest.raises(EntityNotFoundError):
            storage.get(feedback.id)
    
    def test_update_entity(self, temp_dir):
        """Test updating an entity."""
        # Create a storage instance
        storage_dir = os.path.join(temp_dir, "feedback")
        storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=storage_dir,
            format="json"
        )
        
        # Create and save a feedback item
        feedback = FeedbackItem(
            content="Test feedback",
            source=SourceEnum.CUSTOMER_INTERVIEW
        )
        
        storage.save(feedback)
        
        # Update the feedback content
        feedback.content = "Updated feedback"
        updated_feedback = storage.update(feedback)
        
        # Check the updated feedback
        assert updated_feedback.id == feedback.id
        assert updated_feedback.content == "Updated feedback"
        
        # Retrieve the feedback and check again
        retrieved_feedback = storage.get(feedback.id)
        assert retrieved_feedback.content == "Updated feedback"
    
    def test_different_formats(self, temp_dir):
        """Test storing entities in different formats."""
        # Create a feedback item
        feedback = FeedbackItem(
            content="Test feedback",
            source=SourceEnum.CUSTOMER_INTERVIEW
        )
        
        # Test JSON format
        json_storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=os.path.join(temp_dir, "json_feedback"),
            format="json"
        )
        
        json_storage.save(feedback)
        file_path = os.path.join(temp_dir, "json_feedback", f"{feedback.id}.json")
        assert os.path.exists(file_path)
        
        # Check file content
        with open(file_path, 'r') as f:
            content = f.read()
            data = json.loads(content)
            assert data["content"] == "Test feedback"
        
        # Test YAML format
        yaml_storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=os.path.join(temp_dir, "yaml_feedback"),
            format="yaml"
        )
        
        yaml_storage.save(feedback)
        file_path = os.path.join(temp_dir, "yaml_feedback", f"{feedback.id}.yaml")
        assert os.path.exists(file_path)
        
        # Check file content
        with open(file_path, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)
            assert data["content"] == "Test feedback"
        
        # Test Markdown format
        md_storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=os.path.join(temp_dir, "md_feedback"),
            format="markdown"
        )
        
        md_storage.save(feedback)
        file_path = os.path.join(temp_dir, "md_feedback", f"{feedback.id}.md")
        assert os.path.exists(file_path)
        
        # Check file content
        with open(file_path, 'r') as f:
            content = f.read()
            assert "Test feedback" in content


class TestDataImporter:
    """Tests for the DataImporter class."""
    
    def test_import_from_json(self, temp_dir):
        """Test importing data from a JSON file."""
        # Create a sample JSON file
        json_file = os.path.join(temp_dir, "features.json")
        features_data = [
            {
                "name": "Feature 1",
                "description": "Description 1",
                "status": "planned"
            },
            {
                "name": "Feature 2",
                "description": "Description 2",
                "status": "in_progress"
            }
        ]
        
        with open(json_file, 'w') as f:
            json.dump(features_data, f)
        
        # Initialize storage
        storage_dir = os.path.join(temp_dir, "features")
        storage = FileStorage(
            entity_type=Feature,
            storage_dir=storage_dir,
            format="json"
        )
        
        # Create importer
        importer = DataImporter(entity_type=Feature, storage=storage)
        
        # Import data
        imported_features = importer.import_from_file(json_file)
        
        # Check results
        assert len(imported_features) == 2
        assert imported_features[0].name == "Feature 1"
        assert imported_features[0].description == "Description 1"
        assert imported_features[1].name == "Feature 2"
        assert imported_features[1].description == "Description 2"
        
        # Check storage
        stored_features = storage.list()
        assert len(stored_features) == 2
    
    def test_import_from_yaml(self, temp_dir):
        """Test importing data from a YAML file."""
        # Create a sample YAML file
        yaml_file = os.path.join(temp_dir, "features.yaml")
        yaml_content = """
        - name: Feature 1
          description: Description 1
          status: planned
        - name: Feature 2
          description: Description 2
          status: in_progress
        """
        
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        
        # Initialize storage
        storage_dir = os.path.join(temp_dir, "features")
        storage = FileStorage(
            entity_type=Feature,
            storage_dir=storage_dir,
            format="json"
        )
        
        # Create importer
        importer = DataImporter(entity_type=Feature, storage=storage)
        
        # Import data
        imported_features = importer.import_from_file(yaml_file)
        
        # Check results
        assert len(imported_features) == 2
        assert imported_features[0].name == "Feature 1"
        assert imported_features[0].description == "Description 1"
        assert imported_features[1].name == "Feature 2"
        assert imported_features[1].description == "Description 2"


class TestDataExporter:
    """Tests for the DataExporter class."""
    
    def test_export_to_json(self, temp_dir):
        """Test exporting data to a JSON file."""
        # Create features
        features = [
            Feature(name="Feature 1", description="Description 1"),
            Feature(name="Feature 2", description="Description 2")
        ]
        
        # Initialize storage
        storage_dir = os.path.join(temp_dir, "features")
        storage = FileStorage(
            entity_type=Feature,
            storage_dir=storage_dir,
            format="json"
        )
        
        # Save features
        for feature in features:
            storage.save(feature)
        
        # Create exporter
        exporter = DataExporter(entity_type=Feature, storage=storage)
        
        # Export to JSON
        json_file = os.path.join(temp_dir, "exported_features.json")
        exporter.export_to_file(json_file)
        
        # Check file exists
        assert os.path.exists(json_file)
        
        # Check content
        with open(json_file, 'r') as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]["name"] == "Feature 1"
            assert data[0]["description"] == "Description 1"
            assert data[1]["name"] == "Feature 2"
            assert data[1]["description"] == "Description 2"
    
    def test_export_to_yaml(self, temp_dir):
        """Test exporting data to a YAML file."""
        # Create features
        features = [
            Feature(name="Feature 1", description="Description 1"),
            Feature(name="Feature 2", description="Description 2")
        ]
        
        # Create exporter
        exporter = DataExporter(entity_type=Feature, storage=None)
        
        # Export to YAML
        yaml_file = os.path.join(temp_dir, "exported_features.yaml")
        exporter.export_to_file(yaml_file, features)
        
        # Check file exists
        assert os.path.exists(yaml_file)
        
        # Check content
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            assert len(data) == 2
            assert data[0]["name"] == "Feature 1"
            assert data[0]["description"] == "Description 1"
            assert data[1]["name"] == "Feature 2"
            assert data[1]["description"] == "Description 2"


class TestReportGenerator:
    """Tests for the ReportGenerator class."""
    
    def test_feature_prioritization_report(self, temp_dir):
        """Test generating a feature prioritization report."""
        # Create features
        features = [
            Feature(
                name="Feature 1",
                description="Description 1",
                status="planned",
                effort_estimate=3.0,
                value_estimate=8.0,
                priority_score=0.8
            ),
            Feature(
                name="Feature 2",
                description="Description 2",
                status="in_progress",
                effort_estimate=5.0,
                value_estimate=6.0,
                priority_score=0.6
            )
        ]
        
        # Generate markdown report
        md_file = os.path.join(temp_dir, "feature_report.md")
        ReportGenerator.generate_feature_prioritization_report(features, md_file, "markdown")
        
        # Check file exists
        assert os.path.exists(md_file)
        
        # Check content
        with open(md_file, 'r') as f:
            content = f.read()
            assert "Feature Prioritization Report" in content
            assert "Feature 1" in content
            assert "Feature 2" in content
            assert "0.80" in content  # Priority score
            assert "0.60" in content  # Priority score
        
        # Generate HTML report
        html_file = os.path.join(temp_dir, "feature_report.html")
        ReportGenerator.generate_feature_prioritization_report(features, html_file, "html")
        
        # Check file exists
        assert os.path.exists(html_file)
        
        # Check content
        with open(html_file, 'r') as f:
            content = f.read()
            assert "<html>" in content
            assert "Feature Prioritization Report" in content
            assert "Feature 1" in content
            assert "Feature 2" in content
        
        # Generate CSV report
        csv_file = os.path.join(temp_dir, "feature_report.csv")
        ReportGenerator.generate_feature_prioritization_report(features, csv_file, "csv")
        
        # Check file exists
        assert os.path.exists(csv_file)
        
        # Check content
        with open(csv_file, 'r') as f:
            content = f.read()
            assert "Priority,Feature,Status,Value,Effort,Description" in content
            assert "Feature 1" in content
            assert "Feature 2" in content