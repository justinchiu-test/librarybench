"""
Common utility functions for the unified concurrent task scheduler.

This module provides utility functions that are shared between
the render farm manager and scientific computing implementations.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pydantic import BaseModel


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and timedelta objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return {
                "__type__": "timedelta",
                "days": obj.days,
                "seconds": obj.seconds,
                "microseconds": obj.microseconds,
            }
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)


def datetime_decoder(obj):
    """JSON decoder that handles datetime and timedelta objects."""
    if "__type__" in obj and obj["__type__"] == "timedelta":
        return timedelta(
            days=obj["days"],
            seconds=obj["seconds"],
            microseconds=obj["microseconds"],
        )
    
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                obj[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    
    return obj


def serialize_model(model: BaseModel) -> Dict[str, Any]:
    """Serialize a BaseModel to a dictionary."""
    return json.loads(json.dumps(model.model_dump(), cls=DateTimeEncoder))


def deserialize_model(data: Dict[str, Any], model_class):
    """Deserialize a dictionary to a BaseModel."""
    return model_class(**json.loads(json.dumps(data), object_hook=datetime_decoder))


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with an optional prefix."""
    return f"{prefix}_{uuid4().hex}" if prefix else uuid4().hex


def calculate_hash(data: Union[str, bytes, Dict, List, BaseModel]) -> str:
    """Calculate SHA-256 hash of the given data."""
    hasher = hashlib.sha256()
    
    if isinstance(data, str):
        hasher.update(data.encode('utf-8'))
    elif isinstance(data, bytes):
        hasher.update(data)
    elif isinstance(data, (dict, list)):
        hasher.update(json.dumps(data, sort_keys=True, cls=DateTimeEncoder).encode('utf-8'))
    elif isinstance(data, BaseModel):
        hasher.update(json.dumps(data.model_dump(), sort_keys=True, cls=DateTimeEncoder).encode('utf-8'))
    else:
        hasher.update(str(data).encode('utf-8'))
    
    return hasher.hexdigest()


def create_directory_if_not_exists(path: str) -> bool:
    """Create a directory if it doesn't exist."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")
        return False


class PerformanceTimer:
    """Timer for measuring operation performance."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logging.debug(f"Operation '{self.operation_name}' took {duration:.3f} seconds")
    
    def get_duration(self) -> float:
        """Get the duration of the operation in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time


class ExponentialBackoff:
    """Utility for implementing exponential backoff."""
    
    def __init__(
        self, 
        initial_delay_seconds: float = 1.0,
        max_delay_seconds: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: float = 0.1,
    ):
        self.initial_delay = initial_delay_seconds
        self.max_delay = max_delay_seconds
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.attempt = 0
    
    def get_next_delay(self) -> float:
        """Get the next delay duration in seconds."""
        import random
        
        self.attempt += 1
        delay = min(
            self.max_delay,
            self.initial_delay * (self.backoff_factor ** (self.attempt - 1))
        )
        
        # Add jitter
        jitter_amount = delay * self.jitter
        delay = random.uniform(delay - jitter_amount, delay + jitter_amount)
        
        return max(0, delay)
    
    def reset(self):
        """Reset the backoff state."""
        self.attempt = 0


def weighted_average(values: List[float], weights: Optional[List[float]] = None) -> float:
    """Calculate weighted average of values."""
    if not values:
        return 0.0
    
    if weights is None:
        # Simple average if no weights provided
        return sum(values) / len(values)
    
    if len(weights) != len(values):
        raise ValueError("Length of weights must match length of values")
    
    weighted_sum = sum(v * w for v, w in zip(values, weights))
    weight_sum = sum(weights)
    
    if weight_sum == 0:
        return 0.0
        
    return weighted_sum / weight_sum