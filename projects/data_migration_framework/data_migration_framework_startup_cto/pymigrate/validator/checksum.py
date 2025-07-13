"""Checksum validation for data integrity."""

import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal


class ChecksumValidator:
    """Validates data integrity using checksums."""
    
    def __init__(self, algorithm: str = "sha256"):
        """Initialize checksum validator."""
        self.algorithm = algorithm
        self._hash_func = getattr(hashlib, algorithm)
        
    def calculate_checksum(
        self,
        data: Dict[str, Any],
        exclude_fields: Optional[List[str]] = None
    ) -> str:
        """Calculate checksum for a data record."""
        if exclude_fields is None:
            exclude_fields = ["created_at", "updated_at", "_version", "_timestamp"]
            
        # Create normalized copy
        normalized = self._normalize_record(data, exclude_fields)
        
        # Convert to canonical JSON string
        json_str = json.dumps(
            normalized,
            sort_keys=True,
            ensure_ascii=True,
            default=self._json_encoder
        )
        
        # Calculate hash
        return self._hash_func(json_str.encode("utf-8")).hexdigest()
        
    def _normalize_record(
        self,
        data: Dict[str, Any],
        exclude_fields: List[str]
    ) -> Dict[str, Any]:
        """Normalize record for consistent hashing."""
        normalized = {}
        
        for key, value in data.items():
            # Skip excluded fields
            if key in exclude_fields:
                continue
                
            # Normalize value
            normalized_value = self._normalize_value(value)
            
            # Only include non-null values
            if normalized_value is not None:
                normalized[key] = normalized_value
                
        return normalized
        
    def _normalize_value(self, value: Any) -> Any:
        """Normalize individual values for consistent comparison."""
        if value is None:
            return None
            
        # Handle datetime objects
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, date):
            return value.isoformat()
            
        # Handle Decimal
        if isinstance(value, Decimal):
            # Normalize decimal representation
            return float(value)
            
        # Handle bytes
        if isinstance(value, bytes):
            return value.hex()
            
        # Handle lists
        if isinstance(value, list):
            return [self._normalize_value(v) for v in value]
            
        # Handle dicts
        if isinstance(value, dict):
            return {k: self._normalize_value(v) for k, v in value.items()}
            
        # Handle sets
        if isinstance(value, set):
            return sorted(list(value))
            
        return value
        
    def _json_encoder(self, obj: Any) -> Any:
        """Custom JSON encoder for special types."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return obj.hex()
        elif isinstance(obj, set):
            return sorted(list(obj))
            
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
    def calculate_table_checksum(
        self,
        records: List[Dict[str, Any]],
        id_field: str = "id"
    ) -> str:
        """Calculate checksum for an entire table."""
        # Sort records by ID for consistent ordering
        sorted_records = sorted(records, key=lambda r: r.get(id_field, ""))
        
        # Calculate checksum for each record
        checksums = []
        for record in sorted_records:
            record_checksum = self.calculate_checksum(record)
            checksums.append(record_checksum)
            
        # Combine all checksums
        combined = "".join(checksums)
        
        # Return final checksum
        return self._hash_func(combined.encode("utf-8")).hexdigest()
        
    def verify_checksum(
        self,
        data: Dict[str, Any],
        expected_checksum: str,
        exclude_fields: Optional[List[str]] = None
    ) -> bool:
        """Verify if data matches expected checksum."""
        actual_checksum = self.calculate_checksum(data, exclude_fields)
        return actual_checksum == expected_checksum
        
    def calculate_incremental_checksum(
        self,
        base_checksum: str,
        added_records: List[Dict[str, Any]],
        removed_records: List[Dict[str, Any]],
        modified_records: List[Tuple[Dict[str, Any], Dict[str, Any]]]
    ) -> str:
        """Calculate new checksum incrementally."""
        # This is a simplified implementation
        # In production, use more sophisticated incremental hashing
        
        components = [base_checksum]
        
        # Add checksums for new records
        for record in added_records:
            components.append(f"+{self.calculate_checksum(record)}")
            
        # Add checksums for removed records
        for record in removed_records:
            components.append(f"-{self.calculate_checksum(record)}")
            
        # Add checksums for modified records
        for old_record, new_record in modified_records:
            components.append(f"-{self.calculate_checksum(old_record)}")
            components.append(f"+{self.calculate_checksum(new_record)}")
            
        # Combine all components
        combined = "|".join(components)
        
        return self._hash_func(combined.encode("utf-8")).hexdigest()
        
    def calculate_column_checksum(
        self,
        records: List[Dict[str, Any]],
        column: str
    ) -> str:
        """Calculate checksum for a specific column across all records."""
        values = []
        
        for record in records:
            if column in record:
                normalized_value = self._normalize_value(record[column])
                values.append(str(normalized_value))
                
        # Sort values for consistency
        values.sort()
        
        # Combine and hash
        combined = "|".join(values)
        return self._hash_func(combined.encode("utf-8")).hexdigest()