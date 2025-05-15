"""Utility functions for data conversion."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Convert a Pydantic model to a dictionary suitable for serialization.
    
    Args:
        model: The model to convert.
        
    Returns:
        Dictionary representation of the model.
    """
    data = model.model_dump()
    
    # Convert UUID objects to strings
    convert_uuids_to_strings(data)
    
    # Convert Enum objects to strings
    convert_enums_to_strings(data)
    
    # Convert datetime objects to ISO format
    convert_datetimes_to_strings(data)
    
    # Convert sets to lists
    convert_sets_to_lists(data)
    
    # Convert Path objects to strings
    convert_paths_to_strings(data)
    
    return data


def convert_uuids_to_strings(data: Any) -> None:
    """Convert UUID objects to strings in a data structure.
    
    Args:
        data: The data structure to convert, modified in place.
    """
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, list):
                convert_uuids_to_strings(value)
            elif isinstance(value, dict):
                convert_uuids_to_strings(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, UUID):
                data[i] = str(item)
            elif isinstance(item, dict):
                convert_uuids_to_strings(item)
            elif isinstance(item, list):
                convert_uuids_to_strings(item)


def convert_enums_to_strings(data: Any) -> None:
    """Convert Enum objects to strings in a data structure.
    
    Args:
        data: The data structure to convert, modified in place.
    """
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, list):
                convert_enums_to_strings(value)
            elif isinstance(value, dict):
                convert_enums_to_strings(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, Enum):
                data[i] = item.value
            elif isinstance(item, dict):
                convert_enums_to_strings(item)
            elif isinstance(item, list):
                convert_enums_to_strings(item)


def convert_datetimes_to_strings(data: Any) -> None:
    """Convert datetime objects to ISO format strings in a data structure.
    
    Args:
        data: The data structure to convert, modified in place.
    """
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, list):
                convert_datetimes_to_strings(value)
            elif isinstance(value, dict):
                convert_datetimes_to_strings(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, datetime):
                data[i] = item.isoformat()
            elif isinstance(item, dict):
                convert_datetimes_to_strings(item)
            elif isinstance(item, list):
                convert_datetimes_to_strings(item)


def convert_sets_to_lists(data: Any) -> None:
    """Convert set objects to lists in a data structure.
    
    Args:
        data: The data structure to convert, modified in place.
    """
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, set):
                data[key] = list(value)
            elif isinstance(value, list):
                convert_sets_to_lists(value)
            elif isinstance(value, dict):
                convert_sets_to_lists(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, set):
                data[i] = list(item)
            elif isinstance(item, dict):
                convert_sets_to_lists(item)
            elif isinstance(item, list):
                convert_sets_to_lists(item)


def convert_paths_to_strings(data: Any) -> None:
    """Convert Path objects to strings in a data structure.
    
    Args:
        data: The data structure to convert, modified in place.
    """
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
            elif isinstance(value, list):
                convert_paths_to_strings(value)
            elif isinstance(value, dict):
                convert_paths_to_strings(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, Path):
                data[i] = str(item)
            elif isinstance(item, dict):
                convert_paths_to_strings(item)
            elif isinstance(item, list):
                convert_paths_to_strings(item)


def dict_to_model(data: Dict[str, Any], model_class: Type[BaseModel]) -> BaseModel:
    """Convert a dictionary to a Pydantic model.
    
    Args:
        data: The dictionary to convert.
        model_class: The model class to convert to.
        
    Returns:
        Instance of the model class.
    """
    # Make a copy to avoid modifying the original
    data_copy = json.loads(json.dumps(data))
    
    # Convert string UUIDs back to UUID objects
    convert_strings_to_uuids(data_copy)
    
    # Convert string values back to Enum objects
    convert_strings_to_enums(data_copy, model_class)
    
    # Create the model instance
    return model_class(**data_copy)


def convert_strings_to_uuids(data: Dict[str, Any]) -> None:
    """Convert string UUIDs back to UUID objects.
    
    Args:
        data: The data structure to convert, modified in place.
    """
    if isinstance(data, dict):
        # Convert 'id' fields to UUID
        if 'id' in data and isinstance(data['id'], str):
            try:
                data['id'] = UUID(data['id'])
            except ValueError:
                pass

        # Common UUID fields
        uuid_fields = [
            'source_id', 'target_id', 'node_id', 'author_id', 'parent_id', 
            'resolved_by', 'project_id', 'question_id', 'experiment_id',
            'citation_id', 'document_id', 'creator_id', 'owner_id'
        ]
        
        for field in uuid_fields:
            if field in data and isinstance(data[field], str) and data[field] != 'null':
                try:
                    data[field] = UUID(data[field])
                except ValueError:
                    pass

        # Lists of UUIDs
        uuid_list_fields = [
            'references', 'citations', 'notes', 'attachments', 'relations',
            'tags', 'experiments', 'questions', 'documents', 'replies', 
            'related_ids', 'dependencies', 'children', 'parents'
        ]

        for key in uuid_list_fields:
            if key in data and isinstance(data[key], list):
                for i, item in enumerate(data[key]):
                    if isinstance(item, str):
                        try:
                            data[key][i] = UUID(item)
                        except ValueError:
                            pass

        # Process nested structures
        for key, value in data.items():
            if isinstance(value, dict):
                convert_strings_to_uuids(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_strings_to_uuids(item)


def convert_strings_to_enums(data: Dict[str, Any], model_class: Type[BaseModel]) -> None:
    """Convert string values back to Enum objects based on the model type.
    
    Args:
        data: The data structure to convert, modified in place.
        model_class: The model class to use for enum conversion.
    """
    # This function needs to be implemented with knowledge of the model's enum fields
    # For a general implementation, you would need reflection or type annotations
    pass


def convert_strings_to_datetimes(data: Dict[str, Any]) -> None:
    """Convert ISO format string to datetime objects in a data structure.
    
    Args:
        data: The data structure to convert, modified in place.
    """
    if isinstance(data, dict):
        # Common datetime fields
        datetime_fields = ['created_at', 'updated_at', 'deadline', 'start_date', 'end_date', 'due_date']
        
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except ValueError:
                    pass
                    
        # Process nested structures
        for key, value in data.items():
            if isinstance(value, dict):
                convert_strings_to_datetimes(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_strings_to_datetimes(item)