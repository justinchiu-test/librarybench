from datetime import datetime
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from .models import ResearchQuestion, ResearchTask, TaskPriority, TaskStatus
from .storage import TaskStorageInterface


class TaskManagementService:
    """Service for managing research tasks and questions."""

    def __init__(self, storage: TaskStorageInterface):
        """
        Initialize the task management service.

        Args:
            storage: The storage implementation to use
        """
        self._storage = storage

        # Reference validation callback to be set by external services
        self._validate_reference_callback = None

        # Dataset validation callback to be set by external services
        self._validate_dataset_callback = None

        # Environment validation callback to be set by external services
        self._validate_environment_callback = None

        # Experiment validation callback to be set by external services
        self._validate_experiment_callback = None

    def set_reference_validator(self, validator_callback):
        """
        Set a callback function to validate reference IDs.

        Args:
            validator_callback: A function that takes a reference ID and returns True if valid
        """
        self._validate_reference_callback = validator_callback

    def set_dataset_validator(self, validator_callback):
        """
        Set a callback function to validate dataset IDs.

        Args:
            validator_callback: A function that takes a dataset ID and returns True if valid
        """
        self._validate_dataset_callback = validator_callback

    def set_environment_validator(self, validator_callback):
        """
        Set a callback function to validate environment IDs.

        Args:
            validator_callback: A function that takes an environment ID and returns True if valid
        """
        self._validate_environment_callback = validator_callback

    def set_experiment_validator(self, validator_callback):
        """
        Set a callback function to validate experiment IDs.

        Args:
            validator_callback: A function that takes an experiment ID and returns True if valid
        """
        self._validate_experiment_callback = validator_callback
    
    # Task operations
    
    def create_task(
        self,
        title: str,
        description: str,
        status: TaskStatus = TaskStatus.PLANNED,
        priority: TaskPriority = TaskPriority.MEDIUM,
        estimated_hours: Optional[float] = None,
        due_date: Optional[datetime] = None,
        parent_task_id: Optional[UUID] = None,
        research_question_ids: Optional[Set[UUID]] = None,
        tags: Optional[Set[str]] = None,
        custom_metadata: Optional[Dict[str, Union[str, int, float, bool, list, dict]]] = None,
    ) -> UUID:
        """
        Create a new research task.
        
        Args:
            title: Task title
            description: Task description
            status: Task status
            priority: Task priority
            estimated_hours: Estimated hours to complete the task
            due_date: Task due date
            parent_task_id: Parent task ID if this is a subtask
            research_question_ids: Associated research question IDs
            tags: Task tags
            custom_metadata: Custom metadata key-value pairs
            
        Returns:
            UUID: The ID of the created task
            
        Raises:
            ValueError: If parent task doesn't exist
        """
        # Validate parent task if provided
        if parent_task_id:
            parent_task = self._storage.get_task(parent_task_id)
            if not parent_task:
                raise ValueError(f"Parent task with ID {parent_task_id} does not exist")
        
        # Validate research questions if provided
        if research_question_ids:
            for q_id in research_question_ids:
                question = self._storage.get_research_question(q_id)
                if not question:
                    raise ValueError(f"Research question with ID {q_id} does not exist")
        
        # Create task
        task = ResearchTask(
            title=title,
            description=description,
            status=status,
            priority=priority,
            estimated_hours=estimated_hours,
            due_date=due_date,
            parent_task_id=parent_task_id,
            research_question_ids=research_question_ids or set(),
            tags=tags or set(),
            custom_metadata=custom_metadata or {},
        )
        
        # Save task
        task_id = self._storage.create_task(task)
        
        # Update parent task if needed
        if parent_task_id:
            parent_task = self._storage.get_task(parent_task_id)
            if parent_task:
                parent_task.add_subtask(task_id)
                self._storage.update_task(parent_task)
        
        return task_id
    
    def get_task(self, task_id: UUID) -> Optional[ResearchTask]:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Optional[ResearchTask]: The task if found, None otherwise
        """
        return self._storage.get_task(task_id)
    
    def update_task(
        self,
        task_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        estimated_hours: Optional[float] = None,
        actual_hours: Optional[float] = None,
        due_date: Optional[datetime] = None,
    ) -> bool:
        """
        Update an existing task.
        
        Args:
            task_id: The ID of the task to update
            title: New task title
            description: New task description
            status: New task status
            priority: New task priority
            estimated_hours: New estimated hours
            actual_hours: New actual hours
            due_date: New due date
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        if priority is not None:
            update_data["priority"] = priority
        if estimated_hours is not None:
            update_data["estimated_hours"] = estimated_hours
        if actual_hours is not None:
            update_data["actual_hours"] = actual_hours
        if due_date is not None:
            update_data["due_date"] = due_date
        
        task.update(**update_data)
        return self._storage.update_task(task)
    
    def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete_task(task_id)
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        tags: Optional[Set[str]] = None,
        research_question_id: Optional[UUID] = None,
    ) -> List[ResearchTask]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Filter by task status
            priority: Filter by task priority
            tags: Filter by tags (tasks must have all specified tags)
            research_question_id: Filter by associated research question ID
            
        Returns:
            List[ResearchTask]: List of tasks matching the criteria
        """
        return self._storage.list_tasks(
            status=status,
            priority=priority,
            tags=tags,
            research_question_id=research_question_id,
        )
    
    def add_task_note(self, task_id: UUID, note: str) -> bool:
        """
        Add a note to a task.
        
        Args:
            task_id: The ID of the task
            note: The note to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.add_note(note)
        return self._storage.update_task(task)
    
    def add_task_tag(self, task_id: UUID, tag: str) -> bool:
        """
        Add a tag to a task.
        
        Args:
            task_id: The ID of the task
            tag: The tag to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.add_tag(tag)
        return self._storage.update_task(task)
    
    def remove_task_tag(self, task_id: UUID, tag: str) -> bool:
        """
        Remove a tag from a task.
        
        Args:
            task_id: The ID of the task
            tag: The tag to remove
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.remove_tag(tag)
        return self._storage.update_task(task)
    
    def update_task_custom_metadata(
        self, task_id: UUID, key: str, value: Union[str, int, float, bool, list, dict]
    ) -> bool:
        """
        Update a custom metadata field on a task.
        
        Args:
            task_id: The ID of the task
            key: The metadata key
            value: The metadata value
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.update_custom_metadata(key, value)
        return self._storage.update_task(task)
    
    def get_subtasks(self, parent_task_id: UUID) -> List[ResearchTask]:
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_task_id: The ID of the parent task
            
        Returns:
            List[ResearchTask]: List of subtasks
        """
        return self._storage.get_subtasks(parent_task_id)
    
    # Research question operations
    
    def create_research_question(
        self, text: str, description: Optional[str] = None, parent_question_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None
    ) -> UUID:
        """
        Create a new research question and optionally associate it with a task.

        Args:
            text: The research question text
            description: Optional detailed description
            parent_question_id: Parent question ID if this is a sub-question
            task_id: The ID of the task to associate with this question

        Returns:
            UUID: The ID of the created question

        Raises:
            ValueError: If parent question or task doesn't exist
        """
        # Validate parent question if provided
        if parent_question_id:
            parent_question = self._storage.get_research_question(parent_question_id)
            if not parent_question:
                raise ValueError(f"Parent question with ID {parent_question_id} does not exist")

        # Create question
        question = ResearchQuestion(
            text=text,
            description=description,
            parent_question_id=parent_question_id,
        )

        # Save question
        question_id = self._storage.create_research_question(question)

        # Associate with task if provided
        if task_id:
            task = self._storage.get_task(task_id)
            if not task:
                raise ValueError(f"Task with ID {task_id} does not exist")

            task.add_research_question(question_id)
            self._storage.update_task(task)

        return question_id
    
    def get_research_question(self, question_id: UUID) -> Optional[ResearchQuestion]:
        """
        Retrieve a research question by ID.
        
        Args:
            question_id: The ID of the research question to retrieve
            
        Returns:
            Optional[ResearchQuestion]: The research question if found, None otherwise
        """
        return self._storage.get_research_question(question_id)
    
    def update_research_question(
        self, question_id: UUID, text: Optional[str] = None, description: Optional[str] = None
    ) -> bool:
        """
        Update an existing research question.
        
        Args:
            question_id: The ID of the question to update
            text: New question text
            description: New description
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            ValueError: If question doesn't exist
        """
        question = self._storage.get_research_question(question_id)
        if not question:
            raise ValueError(f"Research question with ID {question_id} does not exist")
        
        update_data = {}
        if text is not None:
            update_data["text"] = text
        if description is not None:
            update_data["description"] = description
        
        question.update(**update_data)
        return self._storage.update_research_question(question)
    
    def delete_research_question(self, question_id: UUID) -> bool:
        """
        Delete a research question by ID.
        
        Args:
            question_id: The ID of the research question to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete_research_question(question_id)
    
    def list_research_questions(
        self, parent_question_id: Optional[UUID] = None
    ) -> List[ResearchQuestion]:
        """
        List research questions with optional filtering.
        
        Args:
            parent_question_id: Filter by parent question ID
            
        Returns:
            List[ResearchQuestion]: List of research questions matching the criteria
        """
        return self._storage.list_research_questions(parent_question_id=parent_question_id)
    
    def get_tasks_by_research_question(
        self, question_id: UUID
    ) -> List[ResearchTask]:
        """
        Get all tasks associated with a research question.
        
        Args:
            question_id: The ID of the research question
            
        Returns:
            List[ResearchTask]: List of tasks associated with the research question
        """
        return self._storage.get_tasks_by_research_question(question_id)
    
    def associate_task_with_research_question(
        self, task_id: UUID, question_id: UUID
    ) -> bool:
        """
        Associate a task with a research question.
        
        Args:
            task_id: The ID of the task
            question_id: The ID of the research question
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task or question doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        question = self._storage.get_research_question(question_id)
        if not question:
            raise ValueError(f"Research question with ID {question_id} does not exist")
        
        task.add_research_question(question_id)
        return self._storage.update_task(task)
    
    def dissociate_task_from_research_question(
        self, task_id: UUID, question_id: UUID
    ) -> bool:
        """
        Remove association between a task and a research question.

        Args:
            task_id: The ID of the task
            question_id: The ID of the research question

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        task.remove_research_question(question_id)
        return self._storage.update_task(task)

    # Reference association methods

    def add_reference_to_task(self, task_id: UUID, reference_id: UUID) -> bool:
        """
        Associate a bibliographic reference with a task.

        Args:
            task_id: The ID of the task
            reference_id: The ID of the bibliographic reference

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist or reference ID is invalid
        """
        # Validate task
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Validate reference if validator is set
        if self._validate_reference_callback and not self._validate_reference_callback(reference_id):
            raise ValueError(f"Reference with ID {reference_id} does not exist")

        # Add reference to task
        task.add_reference(reference_id)
        return self._storage.update_task(task)

    def remove_reference_from_task(self, task_id: UUID, reference_id: UUID) -> bool:
        """
        Remove association between a bibliographic reference and a task.

        Args:
            task_id: The ID of the task
            reference_id: The ID of the bibliographic reference

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist
        """
        # Validate task
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Remove reference from task
        task.remove_reference(reference_id)
        return self._storage.update_task(task)

    def get_task_references(self, task_id: UUID) -> Set[UUID]:
        """
        Get all bibliographic references associated with a task.

        Args:
            task_id: The ID of the task

        Returns:
            Set[UUID]: Set of reference IDs

        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        return task.reference_ids

    # Dataset association methods

    def add_dataset_to_task(self, task_id: UUID, dataset_id: UUID) -> bool:
        """
        Associate a dataset with a task.

        Args:
            task_id: The ID of the task
            dataset_id: The ID of the dataset

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist or dataset ID is invalid
        """
        # Validate task
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Validate dataset if validator is set
        if self._validate_dataset_callback and not self._validate_dataset_callback(dataset_id):
            raise ValueError(f"Dataset with ID {dataset_id} does not exist")

        # Add dataset to task
        task.add_dataset(dataset_id)
        return self._storage.update_task(task)

    def remove_dataset_from_task(self, task_id: UUID, dataset_id: UUID) -> bool:
        """
        Remove association between a dataset and a task.

        Args:
            task_id: The ID of the task
            dataset_id: The ID of the dataset

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist
        """
        # Validate task
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Remove dataset from task
        task.remove_dataset(dataset_id)
        return self._storage.update_task(task)

    def get_task_datasets(self, task_id: UUID) -> Set[UUID]:
        """
        Get all datasets associated with a task.

        Args:
            task_id: The ID of the task

        Returns:
            Set[UUID]: Set of dataset IDs

        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        return task.dataset_ids

    # Environment association methods

    def add_environment_to_task(self, task_id: UUID, environment_id: UUID) -> bool:
        """
        Associate a computational environment with a task.

        Args:
            task_id: The ID of the task
            environment_id: The ID of the environment

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist or environment ID is invalid
        """
        # Validate task
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Validate environment if validator is set
        if self._validate_environment_callback and not self._validate_environment_callback(environment_id):
            raise ValueError(f"Environment with ID {environment_id} does not exist")

        # Add environment to task
        task.add_environment(environment_id)
        return self._storage.update_task(task)

    def remove_environment_from_task(self, task_id: UUID, environment_id: UUID) -> bool:
        """
        Remove association between a computational environment and a task.

        Args:
            task_id: The ID of the task
            environment_id: The ID of the environment

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist
        """
        # Validate task
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Remove environment from task
        task.remove_environment(environment_id)
        return self._storage.update_task(task)

    def get_task_environments(self, task_id: UUID) -> Set[UUID]:
        """
        Get all computational environments associated with a task.

        Args:
            task_id: The ID of the task

        Returns:
            Set[UUID]: Set of environment IDs

        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        return task.environment_ids

    # Experiment association methods

    def add_experiment_to_task(self, task_id: UUID, experiment_id: UUID) -> bool:
        """
        Associate an experiment with a task.

        Args:
            task_id: The ID of the task
            experiment_id: The ID of the experiment

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist or experiment ID is invalid
        """
        # Validate task
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Validate experiment if validator is set
        if self._validate_experiment_callback and not self._validate_experiment_callback(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")

        # Add experiment to task
        task.add_experiment(experiment_id)
        return self._storage.update_task(task)

    def remove_experiment_from_task(self, task_id: UUID, experiment_id: UUID) -> bool:
        """
        Remove association between an experiment and a task.

        Args:
            task_id: The ID of the task
            experiment_id: The ID of the experiment

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If task doesn't exist
        """
        # Validate task
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Remove experiment from task
        task.remove_experiment(experiment_id)
        return self._storage.update_task(task)

    def get_task_experiments(self, task_id: UUID) -> Set[UUID]:
        """
        Get all experiments associated with a task.

        Args:
            task_id: The ID of the task

        Returns:
            Set[UUID]: Set of experiment IDs

        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")

        return task.experiment_ids