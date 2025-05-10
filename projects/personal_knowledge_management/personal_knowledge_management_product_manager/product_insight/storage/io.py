"""
Import/export functionality for ProductInsight.

This module provides functionality for importing and exporting data in various formats.
"""

import csv
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

import pandas as pd
import yaml
from pydantic import BaseModel, ValidationError

# Add custom YAML serializer and deserializer for UUID and Enum
def uuid_representer(dumper, data):
    """Custom YAML representer for UUID objects."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data))

def uuid_constructor(loader, node):
    """Custom YAML constructor for UUID objects."""
    value = loader.construct_scalar(node)
    return UUID(value)

def enum_representer(dumper, data):
    """Custom YAML representer for Enum objects."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data.value))

# Register the UUID and Enum handlers with PyYAML
yaml.SafeDumper.add_representer(UUID, uuid_representer)
yaml.SafeDumper.add_multi_representer(Enum, enum_representer)
yaml.SafeLoader.add_constructor('tag:yaml.org,2002:str', yaml.constructor.SafeConstructor.construct_scalar)

from product_insight.models import BaseEntity
from product_insight.storage.base import StorageInterface

T = TypeVar("T", bound=BaseEntity)


class ImportExportError(Exception):
    """Base exception for import/export errors."""
    pass


class FormatNotSupportedError(ImportExportError):
    """Exception raised when a format is not supported."""
    pass


class DataError(ImportExportError):
    """Exception raised when there's an issue with the data."""
    pass


class DataImporter(Generic[T]):
    """Imports data from various formats."""
    
    def __init__(self, entity_type: Type[T], storage: Optional[StorageInterface[T]] = None):
        """Initialize the importer.
        
        Args:
            entity_type: The Pydantic model class for the entities
            storage: Optional storage interface to save imported entities
        """
        self.entity_type = entity_type
        self.storage = storage
    
    def import_from_file(self, file_path: Union[str, Path]) -> List[T]:
        """Import entities from a file.
        
        Args:
            file_path: Path to the file to import
            
        Returns:
            List of imported entities
            
        Raises:
            FormatNotSupportedError: If the file format is not supported
            DataError: If there's an issue with the data
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == ".json":
            return self.import_from_json(path)
        elif suffix in (".yaml", ".yml"):
            return self.import_from_yaml(path)
        elif suffix == ".csv":
            return self.import_from_csv(path)
        else:
            raise FormatNotSupportedError(f"Format {suffix} is not supported")
    
    def import_from_json(self, file_path: Union[str, Path]) -> List[T]:
        """Import entities from a JSON file."""
        path = Path(file_path)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise DataError(f"Failed to read JSON file: {str(e)}")
        
        if not isinstance(data, list):
            data = [data]
        
        entities = []
        
        for item in data:
            try:
                entity = self.entity_type.model_validate(item)
                entities.append(entity)
                
                # Save to storage if provided
                if self.storage:
                    self.storage.save(entity)
            except ValidationError as e:
                raise DataError(f"Invalid entity data: {str(e)}")
        
        return entities
    
    def import_from_yaml(self, file_path: Union[str, Path]) -> List[T]:
        """Import entities from a YAML file."""
        path = Path(file_path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.load(f, Loader=yaml.SafeLoader)
        except Exception as e:
            raise DataError(f"Failed to read YAML file: {str(e)}")
        
        if not isinstance(data, list):
            data = [data]
        
        entities = []
        
        for item in data:
            try:
                entity = self.entity_type.model_validate(item)
                entities.append(entity)
                
                # Save to storage if provided
                if self.storage:
                    self.storage.save(entity)
            except ValidationError as e:
                raise DataError(f"Invalid entity data: {str(e)}")
        
        return entities
    
    def import_from_csv(self, file_path: Union[str, Path]) -> List[T]:
        """Import entities from a CSV file."""
        path = Path(file_path)
        
        try:
            df = pd.read_csv(path)
            # Convert DataFrame to list of dicts
            data = df.to_dict(orient="records")
        except Exception as e:
            raise DataError(f"Failed to read CSV file: {str(e)}")
        
        entities = []
        
        for item in data:
            try:
                # Clean up NaN values
                cleaned_item = {k: (v if pd.notna(v) else None) for k, v in item.items()}
                entity = self.entity_type.model_validate(cleaned_item)
                entities.append(entity)
                
                # Save to storage if provided
                if self.storage:
                    self.storage.save(entity)
            except ValidationError as e:
                raise DataError(f"Invalid entity data: {str(e)}")
        
        return entities


class DataExporter(Generic[T]):
    """Exports data to various formats."""
    
    def __init__(self, entity_type: Type[T], storage: Optional[StorageInterface[T]] = None):
        """Initialize the exporter.
        
        Args:
            entity_type: The Pydantic model class for the entities
            storage: Optional storage interface to retrieve entities
        """
        self.entity_type = entity_type
        self.storage = storage
    
    def export_to_file(
        self, file_path: Union[str, Path], entities: Optional[List[T]] = None
    ) -> None:
        """Export entities to a file.
        
        Args:
            file_path: Path to the output file
            entities: List of entities to export (if None, all entities from storage are exported)
            
        Raises:
            FormatNotSupportedError: If the file format is not supported
            DataError: If there's an issue with the data
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        # If entities not provided, get them from storage
        if entities is None:
            if self.storage is None:
                raise ValueError("Either entities or storage must be provided")
            entities = self.storage.list()
        
        if suffix == ".json":
            self.export_to_json(path, entities)
        elif suffix in (".yaml", ".yml"):
            self.export_to_yaml(path, entities)
        elif suffix == ".csv":
            self.export_to_csv(path, entities)
        else:
            raise FormatNotSupportedError(f"Format {suffix} is not supported")
    
    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for handling UUID and datetime."""
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
    
    def export_to_json(self, file_path: Union[str, Path], entities: List[T]) -> None:
        """Export entities to a JSON file."""
        path = Path(file_path)
        
        try:
            # Convert entities to dictionaries
            data = [entity.model_dump() for entity in entities]
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, default=self._json_serializer, indent=2)
        except Exception as e:
            raise DataError(f"Failed to write JSON file: {str(e)}")
    
    def export_to_yaml(self, file_path: Union[str, Path], entities: List[T]) -> None:
        """Export entities to a YAML file."""
        path = Path(file_path)

        try:
            # Convert entities to dictionaries with custom serialization
            data = []
            for entity in entities:
                # Convert to dict and convert UUIDs to strings
                entity_dict = entity.model_dump()
                self._convert_uuids_to_str(entity_dict)
                data.append(entity_dict)

            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, Dumper=yaml.SafeDumper)
        except Exception as e:
            raise DataError(f"Failed to write YAML file: {str(e)}")

    def _convert_uuids_to_str(self, data: Any) -> None:
        """Recursively convert UUIDs to strings in a data structure."""
        if isinstance(data, dict):
            for key, value in list(data.items()):
                if isinstance(value, UUID):
                    data[key] = str(value)
                elif isinstance(value, (dict, list)):
                    self._convert_uuids_to_str(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, UUID):
                    data[i] = str(item)
                elif isinstance(item, (dict, list)):
                    self._convert_uuids_to_str(item)
    
    def export_to_csv(self, file_path: Union[str, Path], entities: List[T]) -> None:
        """Export entities to a CSV file."""
        path = Path(file_path)
        
        try:
            # Convert entities to dictionaries
            data = [entity.model_dump() for entity in entities]
            
            # Convert to DataFrame and export
            df = pd.DataFrame(data)
            df.to_csv(path, index=False)
        except Exception as e:
            raise DataError(f"Failed to write CSV file: {str(e)}")


class ReportGenerator:
    """Generates reports from ProductInsight data."""
    
    @staticmethod
    def generate_feature_prioritization_report(
        features: List[Any], 
        file_path: Union[str, Path],
        format: str = "markdown"
    ) -> None:
        """Generate a feature prioritization report.
        
        Args:
            features: List of Feature objects
            file_path: Path to the output file
            format: Output format (markdown, html, or csv)
        """
        path = Path(file_path)
        format = format.lower()
        
        if format == "markdown":
            ReportGenerator._generate_markdown_prioritization_report(features, path)
        elif format == "html":
            ReportGenerator._generate_html_prioritization_report(features, path)
        elif format == "csv":
            ReportGenerator._generate_csv_prioritization_report(features, path)
        else:
            raise FormatNotSupportedError(f"Format {format} is not supported")
    
    @staticmethod
    def _generate_markdown_prioritization_report(features: List[Any], file_path: Path) -> None:
        """Generate a Markdown feature prioritization report."""
        # Sort features by priority
        sorted_features = sorted(
            features, 
            key=lambda f: f.priority_score if f.priority_score is not None else 0,
            reverse=True
        )
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Feature Prioritization Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Features by Priority\n\n")
            f.write("| Priority | Feature | Status | Value | Effort | Description |\n")
            f.write("|----------|---------|--------|-------|--------|-------------|\n")
            
            for feature in sorted_features:
                priority = feature.priority_score if feature.priority_score is not None else "N/A"
                value = feature.value_estimate if feature.value_estimate is not None else "N/A"
                effort = feature.effort_estimate if feature.effort_estimate is not None else "N/A"
                
                f.write(f"| {priority:.2f} | {feature.name} | {feature.status.value} | {value} | {effort} | {feature.description} |\n")
    
    @staticmethod
    def _generate_html_prioritization_report(features: List[Any], file_path: Path) -> None:
        """Generate an HTML feature prioritization report."""
        # Sort features by priority
        sorted_features = sorted(
            features, 
            key=lambda f: f.priority_score if f.priority_score is not None else 0,
            reverse=True
        )
        
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Feature Prioritization Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; text-align: left; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>Feature Prioritization Report</h1>
            <p>Generated on: {current_date}</p>

            <h2>Features by Priority</h2>
            <table>
                <tr>
                    <th>Priority</th>
                    <th>Feature</th>
                    <th>Status</th>
                    <th>Value</th>
                    <th>Effort</th>
                    <th>Description</th>
                </tr>
        """
        
        for feature in sorted_features:
            priority = f"{feature.priority_score:.2f}" if feature.priority_score is not None else "N/A"
            value = feature.value_estimate if feature.value_estimate is not None else "N/A"
            effort = feature.effort_estimate if feature.effort_estimate is not None else "N/A"
            
            html += f"""
                <tr>
                    <td>{priority}</td>
                    <td>{feature.name}</td>
                    <td>{feature.status.value}</td>
                    <td>{value}</td>
                    <td>{effort}</td>
                    <td>{feature.description}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
    
    @staticmethod
    def _generate_csv_prioritization_report(features: List[Any], file_path: Path) -> None:
        """Generate a CSV feature prioritization report."""
        # Sort features by priority
        sorted_features = sorted(
            features, 
            key=lambda f: f.priority_score if f.priority_score is not None else 0,
            reverse=True
        )
        
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Priority", "Feature", "Status", "Value", "Effort", "Description"])
            
            for feature in sorted_features:
                priority = feature.priority_score if feature.priority_score is not None else "N/A"
                value = feature.value_estimate if feature.value_estimate is not None else "N/A"
                effort = feature.effort_estimate if feature.effort_estimate is not None else "N/A"
                
                writer.writerow([priority, feature.name, feature.status.value, value, effort, feature.description])