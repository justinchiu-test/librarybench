"""
Experiment models for the Academic Knowledge Vault system.

This module defines the data models for experiments, protocols, and results.
"""

import datetime
import enum
from typing import Dict, List, Optional, Set, Union, Any

from pydantic import BaseModel, Field, validator

from academic_knowledge_vault.models.base import (
    BaseKnowledgeItem,
    KnowledgeItemType,
    LinkedItem,
    Person,
    Reference,
    StorageInfo,
)


class ExperimentStatus(str, enum.Enum):
    """Status categories for experiments."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ANALYSIS = "analysis"
    PUBLISHED = "published"
    FAILED = "failed"
    ABORTED = "aborted"


class ParameterType(str, enum.Enum):
    """Types of experimental parameters."""

    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    RANGE = "range"
    CATEGORY = "category"
    FILE = "file"


class ProtocolParameter(BaseModel):
    """A parameter in an experimental protocol."""

    name: str
    description: str
    parameter_type: ParameterType
    required: bool = True
    default_value: Optional[Any] = None
    units: Optional[str] = None
    options: Optional[List[str]] = None  # For category parameters
    min_value: Optional[float] = None  # For range parameters
    max_value: Optional[float] = None  # For range parameters
    
    # Validation rules
    validation_rules: Optional[Dict[str, Any]] = None
    
    def validate_value(self, value: Any) -> bool:
        """
        Validate that a value conforms to the parameter requirements.
        Returns True if valid, False otherwise.
        """
        # Check if required value is missing
        if self.required and value is None:
            return False
        
        # Skip validation for None values if not required
        if value is None and not self.required:
            return True
        
        # Type validation
        if self.parameter_type == ParameterType.TEXT and not isinstance(value, str):
            return False
        elif self.parameter_type == ParameterType.NUMBER and not isinstance(value, (int, float)):
            return False
        elif self.parameter_type == ParameterType.BOOLEAN and not isinstance(value, bool):
            return False
        elif self.parameter_type == ParameterType.DATE and not isinstance(value, datetime.datetime):
            return False
        
        # Range validation
        if self.parameter_type == ParameterType.RANGE:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
        
        # Category validation
        if self.parameter_type == ParameterType.CATEGORY:
            if self.options is not None and value not in self.options:
                return False
        
        # Additional custom validation
        if self.validation_rules:
            # Implement custom validation logic here
            # This would be expanded in a real implementation
            pass
        
        return True


class ExperimentProtocol(BaseModel):
    """A protocol template for conducting experiments."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: int = 1
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Protocol details
    parameters: List[ProtocolParameter] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    materials: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)
    
    # Metadata
    tags: Set[str] = Field(default_factory=set)
    author_id: Optional[str] = None
    
    # References
    citation_references: List[Reference] = Field(default_factory=list)
    note_references: List[Reference] = Field(default_factory=list)
    
    # Version tracking
    previous_versions: List[str] = Field(default_factory=list)  # IDs of previous versions
    
    def add_parameter(self, parameter: ProtocolParameter) -> None:
        """Add a parameter to the protocol."""
        self.parameters.append(parameter)
        self.updated_at = datetime.datetime.now()
    
    def add_step(self, step_description: str) -> None:
        """Add a step to the protocol."""
        self.steps.append(step_description)
        self.updated_at = datetime.datetime.now()
    
    def create_new_version(self) -> 'ExperimentProtocol':
        """Create a new version of this protocol."""
        new_protocol = self.copy(deep=True)
        new_protocol.id = str(uuid.uuid4())
        new_protocol.version = self.version + 1
        new_protocol.created_at = datetime.datetime.now()
        new_protocol.updated_at = datetime.datetime.now()
        new_protocol.previous_versions.append(self.id)
        return new_protocol


class ExperimentResult(BaseModel):
    """Results from an experiment execution."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Data and metadata
    data_values: Dict[str, Any] = Field(default_factory=dict)
    data_files: List[str] = Field(default_factory=list)
    success: bool = True
    notes: Optional[str] = None
    
    # Statistical summary
    summary_statistics: Optional[Dict[str, Any]] = None
    
    # References
    related_results: List[str] = Field(default_factory=list)  # IDs of related results
    
    def add_data_value(self, key: str, value: Any) -> None:
        """Add a data value to the results."""
        self.data_values[key] = value
    
    def add_data_file(self, file_path: str) -> None:
        """Add a data file to the results."""
        self.data_files.append(file_path)
    
    def generate_summary_statistics(self) -> None:
        """
        Generate summary statistics from the data values.
        This is a placeholder - actual implementation would be more sophisticated.
        """
        # This would contain logic to analyze numeric data and generate statistics
        self.summary_statistics = {}
        
        # Simple example for numeric values
        numeric_values = {}
        for key, value in self.data_values.items():
            if isinstance(value, (int, float)):
                numeric_values[key] = value
        
        if numeric_values:
            # Calculate mean for each numeric field as an example
            self.summary_statistics = {
                f"{key}_mean": value for key, value in numeric_values.items()
            }


class Experiment(BaseKnowledgeItem):
    """An experiment with protocol, parameters, and results."""

    # Basic experiment information
    status: ExperimentStatus = ExperimentStatus.PLANNED
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    
    # Protocol and parameters
    protocol_id: Optional[str] = None
    protocol_version: Optional[int] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # People involved
    researchers: List[Person] = Field(default_factory=list)
    
    # Results
    results: List[ExperimentResult] = Field(default_factory=list)
    
    # Research context
    research_question_id: Optional[str] = None
    hypothesis_ids: List[str] = Field(default_factory=list)
    
    # Related knowledge items
    related_notes: List[Reference] = Field(default_factory=list)
    related_citations: List[Reference] = Field(default_factory=list)
    related_experiments: List[Reference] = Field(default_factory=list)
    
    # Storage information
    storage: Optional[StorageInfo] = None
    
    def add_researcher(self, person: Person) -> None:
        """Add a researcher to the experiment."""
        for existing_person in self.researchers:
            if existing_person.id == person.id:
                return  # Person already exists
        self.researchers.append(person)
        self.update_timestamp()
    
    def set_parameter(self, name: str, value: Any) -> None:
        """Set a parameter value for the experiment."""
        self.parameters[name] = value
        self.update_timestamp()
    
    def add_result(self, result: ExperimentResult) -> None:
        """Add a result to the experiment."""
        self.results.append(result)
        self.update_timestamp()
    
    def update_status(self, status: ExperimentStatus) -> None:
        """Update the status of the experiment."""
        self.status = status
        self.update_timestamp()
    
    def start_experiment(self) -> None:
        """Mark the experiment as started."""
        self.status = ExperimentStatus.IN_PROGRESS
        self.start_date = datetime.datetime.now()
        self.update_timestamp()
    
    def complete_experiment(self) -> None:
        """Mark the experiment as completed."""
        self.status = ExperimentStatus.COMPLETED
        self.end_date = datetime.datetime.now()
        self.update_timestamp()
    
    def validate_parameters(self, protocol: ExperimentProtocol) -> List[str]:
        """
        Validate the experiment parameters against the protocol.
        Returns a list of validation errors, or an empty list if all valid.
        """
        errors = []
        
        for param in protocol.parameters:
            if param.name in self.parameters:
                value = self.parameters[param.name]
                if not param.validate_value(value):
                    errors.append(f"Invalid value for parameter {param.name}: {value}")
            elif param.required:
                errors.append(f"Missing required parameter: {param.name}")
        
        return errors


class ExperimentCollection(BaseModel):
    """A collection of related experiments."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    experiment_ids: Set[str] = Field(default_factory=set)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    tags: Set[str] = Field(default_factory=set)
    
    def add_experiment(self, experiment_id: str) -> None:
        """Add an experiment to the collection."""
        self.experiment_ids.add(experiment_id)
        self.updated_at = datetime.datetime.now()
    
    def remove_experiment(self, experiment_id: str) -> None:
        """Remove an experiment from the collection."""
        if experiment_id in self.experiment_ids:
            self.experiment_ids.remove(experiment_id)
            self.updated_at = datetime.datetime.now()


import uuid