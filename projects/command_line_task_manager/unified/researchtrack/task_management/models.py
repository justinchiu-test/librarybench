from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from common.core.models import BaseEntity, BaseTask


# Define as regular Enum to match original code
class TaskStatus(str, Enum):
    """Status of a research task."""
    
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskPriority(str, Enum):
    """Priority level of a research task."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResearchQuestion(BaseEntity):
    """Model representing a research question."""
    
    text: str
    description: Optional[str] = None
    parent_question_id: Optional[str] = None
    
    def __init__(self, **data):
        # Convert parent_question_id to string if it's a UUID
        if 'parent_question_id' in data and isinstance(data['parent_question_id'], UUID):
            data['parent_question_id'] = str(data['parent_question_id'])
        super().__init__(**data)


class ResearchTask(BaseTask):
    """Model representing a research task with comprehensive metadata."""

    # Default values for required fields
    status: str = TaskStatus.PLANNED
    priority: str = TaskPriority.MEDIUM

    # Researcher-specific fields
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

    # Associations with research questions and subtasks
    research_question_ids: Set[Union[str, UUID]] = Field(default_factory=set)

    # Associations with other research artifacts
    reference_ids: Set[Union[str, UUID]] = Field(default_factory=set)  # Bibliographic references
    dataset_ids: Set[Union[str, UUID]] = Field(default_factory=set)    # Dataset versions
    environment_ids: Set[Union[str, UUID]] = Field(default_factory=set)  # Computational environments
    experiment_ids: Set[Union[str, UUID]] = Field(default_factory=set)  # Experiments

    # Additional properties for integration tests
    # These aren't persisted, but used for convenience in tests
    research_questions: List[Any] = Field(default_factory=list, exclude=True)
    references: List[Any] = Field(default_factory=list, exclude=True)
    datasets: List[Any] = Field(default_factory=list, exclude=True)
    environments: List[Any] = Field(default_factory=list, exclude=True)
    experiments: List[Any] = Field(default_factory=list, exclude=True)
    
    # For backward compatibility with tests - test code refers to parent_task_id 
    # but BaseTask uses parent_id
    @property
    def parent_task_id(self) -> Optional[UUID]:
        return self.parent_id
    
    # Handle parent_task_id in initialization
    def __init__(self, **data):
        if 'parent_task_id' in data and 'parent_id' not in data:
            # Convert to string if it's a UUID
            parent_id = data.pop('parent_task_id')
            if isinstance(parent_id, UUID):
                parent_id = str(parent_id)
            data['parent_id'] = parent_id
        elif 'parent_id' in data and isinstance(data['parent_id'], UUID):
            # Convert existing parent_id to string if it's a UUID
            data['parent_id'] = str(data['parent_id'])
        super().__init__(**data)
    
    @model_validator(mode='after')
    def ensure_status_is_enum_value(self) -> 'ResearchTask':
        """Ensure status is a valid TaskStatus value."""
        if isinstance(self.status, str) and self.status not in [s.value for s in TaskStatus]:
            self.status = TaskStatus.PLANNED.value
        elif isinstance(self.status, TaskStatus):
            self.status = self.status.value
        return self
    
    @model_validator(mode='after')
    def ensure_priority_is_enum_value(self) -> 'ResearchTask':
        """Ensure priority is a valid TaskPriority value."""
        if isinstance(self.priority, str) and self.priority not in [p.value for p in TaskPriority]:
            self.priority = TaskPriority.MEDIUM.value
        elif isinstance(self.priority, TaskPriority):
            self.priority = self.priority.value
        return self
    
    def add_research_question(self, question_id: Union[UUID, str]) -> None:
        """Associate a research question with this task."""
        # Convert UUID to string if needed
        if isinstance(question_id, UUID):
            question_id = str(question_id)
        self.research_question_ids.add(question_id)
        self.updated_at = datetime.now()
    
    def remove_research_question(self, question_id: Union[UUID, str]) -> None:
        """Remove association with a research question."""
        # Convert UUID to string if needed
        if isinstance(question_id, UUID):
            question_id = str(question_id)
        if question_id in self.research_question_ids:
            self.research_question_ids.remove(question_id)
            self.updated_at = datetime.now()

    # Bibliographic reference association methods
    def add_reference(self, reference_id: Union[UUID, str]) -> None:
        """Associate a bibliographic reference with this task."""
        # Convert UUID to string if needed
        if isinstance(reference_id, UUID):
            reference_id = str(reference_id)
        self.reference_ids.add(reference_id)
        self.updated_at = datetime.now()

    def remove_reference(self, reference_id: Union[UUID, str]) -> None:
        """Remove association with a bibliographic reference."""
        # Convert UUID to string if needed
        if isinstance(reference_id, UUID):
            reference_id = str(reference_id)
        if reference_id in self.reference_ids:
            self.reference_ids.remove(reference_id)
            self.updated_at = datetime.now()

    # Dataset association methods
    def add_dataset(self, dataset_id: Union[UUID, str]) -> None:
        """Associate a dataset with this task."""
        # Convert UUID to string if needed
        if isinstance(dataset_id, UUID):
            dataset_id = str(dataset_id)
        self.dataset_ids.add(dataset_id)
        self.updated_at = datetime.now()

    def remove_dataset(self, dataset_id: Union[UUID, str]) -> None:
        """Remove association with a dataset."""
        # Convert UUID to string if needed
        if isinstance(dataset_id, UUID):
            dataset_id = str(dataset_id)
        if dataset_id in self.dataset_ids:
            self.dataset_ids.remove(dataset_id)
            self.updated_at = datetime.now()

    # Environment association methods
    def add_environment(self, environment_id: Union[UUID, str]) -> None:
        """Associate a computational environment with this task."""
        # Convert UUID to string if needed
        if isinstance(environment_id, UUID):
            environment_id = str(environment_id)
        self.environment_ids.add(environment_id)
        self.updated_at = datetime.now()

    def remove_environment(self, environment_id: Union[UUID, str]) -> None:
        """Remove association with a computational environment."""
        # Convert UUID to string if needed
        if isinstance(environment_id, UUID):
            environment_id = str(environment_id)
        if environment_id in self.environment_ids:
            self.environment_ids.remove(environment_id)
            self.updated_at = datetime.now()

    # Experiment association methods
    def add_experiment(self, experiment_id: Union[UUID, str]) -> None:
        """Associate an experiment with this task."""
        # Convert UUID to string if needed
        if isinstance(experiment_id, UUID):
            experiment_id = str(experiment_id)
        self.experiment_ids.add(experiment_id)
        self.updated_at = datetime.now()

    def remove_experiment(self, experiment_id: Union[UUID, str]) -> None:
        """Remove association with an experiment."""
        # Convert UUID to string if needed
        if isinstance(experiment_id, UUID):
            experiment_id = str(experiment_id)
        if experiment_id in self.experiment_ids:
            self.experiment_ids.remove(experiment_id)
            self.updated_at = datetime.now()