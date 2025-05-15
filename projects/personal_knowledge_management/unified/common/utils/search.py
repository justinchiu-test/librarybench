"""Utility functions for search operations."""

from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel

from common.core.models import KnowledgeNode

T = TypeVar('T', bound=KnowledgeNode)


def tokenize_text(text: str) -> List[str]:
    """Tokenize text into individual words for search indexing.
    
    Args:
        text: The text to tokenize.
        
    Returns:
        List of tokens.
    """
    # Simple tokenization by splitting on whitespace and converting to lowercase
    return [word.lower() for word in text.split() if word]


def build_index(items: List[T], fields: List[str]) -> Dict[str, Dict[str, Set[str]]]:
    """Build a search index for a list of items.
    
    Args:
        items: List of items to index.
        fields: List of fields to include in the index.
        
    Returns:
        Dictionary mapping fields to tokens to item IDs.
    """
    index = {}
    
    for field in fields:
        index[field] = {}
    
    for item in items:
        item_dict = item.model_dump()
        item_id = str(item.id)
        
        for field in fields:
            if field in item_dict and isinstance(item_dict[field], str):
                # Tokenize the field content
                tokens = tokenize_text(item_dict[field])
                
                # Add item ID to the index for each token
                for token in tokens:
                    if token not in index[field]:
                        index[field][token] = set()
                    index[field][token].add(item_id)
    
    return index


def search_index(index: Dict[str, Dict[str, Set[str]]], query: str, fields: List[str]) -> Set[str]:
    """Search an index for items matching a query.
    
    Args:
        index: The search index.
        query: The search query.
        fields: The fields to search in.
        
    Returns:
        Set of matching item IDs.
    """
    # Tokenize the query
    tokens = tokenize_text(query)
    
    # Find matching items
    matching_ids = set()
    first_match = True
    
    for token in tokens:
        token_matches = set()
        
        for field in fields:
            if field in index:
                for indexed_token, item_ids in index[field].items():
                    if token in indexed_token:
                        token_matches.update(item_ids)
        
        # Intersect with previous matches
        if first_match:
            matching_ids = token_matches
            first_match = False
        else:
            matching_ids &= token_matches
    
    return matching_ids


def simple_text_search(items: List[T], query: str, fields: List[str]) -> List[T]:
    """Simple in-memory text search.
    
    Args:
        items: List of items to search.
        query: The search query.
        fields: The fields to search in.
        
    Returns:
        List of matching items.
    """
    query_lower = query.lower()
    results = []
    
    for item in items:
        item_dict = item.model_dump()
        
        for field in fields:
            if field in item_dict and isinstance(item_dict[field], str):
                field_value = item_dict[field].lower()
                
                if query_lower in field_value:
                    if item not in results:
                        results.append(item)
                    break
    
    return results