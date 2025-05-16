"""Storage system for the ResearchBrain knowledge management system.

This module is now a thin wrapper around the common.core.storage.LocalStorage implementation.
It provides backward compatibility for ResearchBrain-specific storage operations.
"""

import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel

# Import from common library
from common.core.storage import LocalStorage as CommonLocalStorage, StorageError
from common.core.models import KnowledgeNode

T = TypeVar('T', bound=KnowledgeNode)
MAX_WORKERS = 8  # Maximum number of worker threads for parallel operations


# Create a subclass of the common LocalStorage to maintain backward compatibility
class LocalStorage(CommonLocalStorage):
    """Storage system that persists data to the local filesystem in plain text formats.
    
    This class extends the CommonLocalStorage class from the common library
    and maintains backward compatibility with ResearchBrain-specific paths and behaviors.
    """

    def __init__(self, base_path: Union[str, Path]):
        """Initialize the storage system.
        
        Args:
            base_path: The base directory for storing all data.
        """
        # Initialize the parent class
        super().__init__(base_path)
        
        # Ensure ResearchBrain-specific directories exist
        self._ensure_researchbrain_directories()
        
    def _ensure_researchbrain_directories(self) -> None:
        """Create necessary ResearchBrain-specific directories if they don't exist."""
        rb_directories = [
            'research_questions',
            'experiments',
            'grants',
            'collaborators',
            'templates'
        ]
        
        for directory in rb_directories:
            path = self.base_path / directory
            path.mkdir(parents=True, exist_ok=True)
            
    def _get_collection_path(self, model_type: Type[T]) -> Path:
        """Get the path for a specific collection based on model type.
        
        This method overrides the parent method to ensure backward compatibility
        with ResearchBrain-specific paths.
        
        Args:
            model_type: The type of model to determine the collection.
            
        Returns:
            Path to the collection directory.
        """
        # Handle ResearchBrain-specific model types
        type_name = model_type.__name__
        
        if type_name == 'ResearchQuestion':
            return self.base_path / 'research_questions'
        elif type_name == 'Experiment':
            return self.base_path / 'experiments'
        elif type_name == 'GrantProposal':
            return self.base_path / 'grants'
        elif type_name == 'Collaborator':
            return self.base_path / 'collaborators'
        elif type_name == 'Note':
            return self.base_path / 'nodes' / 'notes'
        elif type_name == 'Citation':
            return self.base_path / 'nodes' / 'citations'
        elif type_name == 'Annotation':
            return self.base_path / 'nodes' / 'annotations'
            
        # Use the parent class method for other model types
        return super()._get_collection_path(model_type)
        
    def export_to_dataframe(self, model_type: Type[T]) -> pd.DataFrame:
        """Export all items of a specific type to a pandas DataFrame.
        
        Args:
            model_type: The type of items to export.
            
        Returns:
            A DataFrame containing all items of the specified type.
        """
        items = self.list_all(model_type)
        if not items:
            return pd.DataFrame()
            
        # Convert to dict and normalize
        data = [item.model_dump() for item in items]
        
        # Convert UUIDs to strings for pandas compatibility
        for item_data in data:
            self._convert_uuids_to_strings(item_data)
            
        return pd.json_normalize(data)