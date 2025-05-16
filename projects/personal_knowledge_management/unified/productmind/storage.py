"""Storage system for the ProductMind knowledge management system.

This module is a thin wrapper around the common.core.storage.LocalStorage implementation.
It provides backward compatibility for ProductMind-specific storage operations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel

# Import from common library
from common.core.storage import LocalStorage as CommonLocalStorage, StorageError
from common.core.models import KnowledgeNode

T = TypeVar('T', bound=KnowledgeNode)


# Create a subclass of the common LocalStorage to maintain backward compatibility
class LocalStorage(CommonLocalStorage):
    """Storage system that persists data to the local filesystem in plain text formats.
    
    This class extends the CommonLocalStorage class from the common library
    and maintains backward compatibility with ProductMind-specific paths and behaviors.
    """

    def __init__(self, base_path: Union[str, Path]):
        """Initialize the storage system.
        
        Args:
            base_path: The base directory for storing all data.
        """
        # Initialize the parent class
        super().__init__(base_path)
        
        # Ensure ProductMind-specific directories exist
        self._ensure_productmind_directories()
        
    def _ensure_productmind_directories(self) -> None:
        """Create necessary ProductMind-specific directories if they don't exist."""
        pm_directories = [
            'feedback',
            'clusters',
            'themes',
            'features',
            'competitors',
            'stakeholders',
            'stakeholder_relationships',
            'perspectives',
            'nodes/stakeholders',
            'nodes/perspectives',
            'nodes/relationships'
        ]
        
        for directory in pm_directories:
            path = self.base_path / directory
            path.mkdir(parents=True, exist_ok=True)
            
    def _get_collection_path(self, model_type: Type[T]) -> Path:
        """Get the path for a specific collection based on model type.
        
        This method overrides the parent method to ensure backward compatibility
        with ProductMind-specific paths.
        
        Args:
            model_type: The type of model to determine the collection.
            
        Returns:
            Path to the collection directory.
        """
        # Handle ProductMind-specific model types
        type_name = model_type.__name__
        
        if type_name == 'Feedback':
            return self.base_path / 'feedback'
        elif type_name == 'FeedbackCluster':
            return self.base_path / 'clusters'
        elif type_name == 'Theme':
            return self.base_path / 'themes'
        elif type_name == 'Feature':
            return self.base_path / 'features'
        elif type_name == 'Competitor':
            return self.base_path / 'competitors'
        elif type_name == 'Stakeholder':
            return self.base_path / 'stakeholders'
        elif type_name == 'StakeholderRelationship':
            return self.base_path / 'stakeholder_relationships'
        elif type_name == 'Decision':
            return self.base_path / 'nodes' / 'decisions'
        elif type_name == 'Perspective':
            return self.base_path / 'perspectives'
            
        # Use the parent class method for other model types
        return super()._get_collection_path(model_type)