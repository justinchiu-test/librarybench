from typing import Dict, List, Optional, Set, Union, TypeVar, Type, Any
from uuid import UUID
from abc import abstractmethod
import os

from common.core.storage import BaseStorageInterface, BaseTaskStorageInterface, InMemoryStorage, FilePersistentStorage
from common.core.security import CryptoManager
from .models import ResearchQuestion, ResearchTask, TaskPriority, TaskStatus


# Define a type variable for ResearchQuestion
RQ = TypeVar('RQ', bound=ResearchQuestion)


class TaskStorageInterface(BaseTaskStorageInterface):
    """Interface for research task storage implementations."""
    
    def create_task(self, task: ResearchTask) -> str:
        """
        Create a new research task.
        
        Args:
            task: The task to create
            
        Returns:
            str: The ID of the created task
        """
        return self.create(task)
    
    def get_task(self, task_id: Union[str, UUID]) -> Optional[ResearchTask]:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Optional[ResearchTask]: The task if found, None otherwise
        """
        return self.get(task_id)
    
    def update_task(self, task: ResearchTask) -> bool:
        """
        Update an existing task.
        
        Args:
            task: The task with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        return self.update(task)
    
    def delete_task(self, task_id: Union[str, UUID]) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        # Convert UUID to string if needed
        task_id_str = str(task_id) if isinstance(task_id, UUID) else task_id
        
        # Get the task before deleting it
        task = self.get(task_id_str)
        if not task:
            return False
            
        # If it has a parent, update the parent to remove this subtask
        if task.parent_id:
            parent_task = self.get(task.parent_id)
            if parent_task and task_id_str in parent_task.subtask_ids:
                parent_task.subtask_ids.remove(task_id_str)
                self.update(parent_task)
        
        # Also clean up references from any parent tasks that might have this as a subtask
        for parent_task in self._entities.values():
            if task_id_str in parent_task.subtask_ids:
                parent_task.subtask_ids.remove(task_id_str)
                self.update(parent_task)
                
        # Delete the task itself
        return self.delete(task_id_str)
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        tags: Optional[Set[str]] = None,
        research_question_id: Optional[Union[str, UUID]] = None,
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
        # Build filters dictionary
        filters = {}
        if status:
            filters["status"] = status.value if isinstance(status, TaskStatus) else status
        if priority:
            filters["priority"] = priority.value if isinstance(priority, TaskPriority) else priority
        
        # Get filtered tasks from the base list method
        tasks = self.list(filters)
        
        # Apply tag filtering
        if tags:
            tasks = [
                task for task in tasks if all(tag in task.tags for tag in tags)
            ]
        
        # Apply research question filtering
        if research_question_id:
            # Convert UUID to string if needed
            if isinstance(research_question_id, UUID):
                research_question_id = str(research_question_id)
                
            tasks = [
                task
                for task in tasks
                if hasattr(task, 'research_question_ids') and 
                research_question_id in task.research_question_ids
            ]
        
        return tasks
        
    def get_tasks_by_research_question(
        self, question_id: Union[str, UUID]
    ) -> List[ResearchTask]:
        """
        Get all tasks associated with a research question.
        
        Args:
            question_id: The ID of the research question
            
        Returns:
            List[ResearchTask]: List of tasks associated with the research question
        """
        question_id_str = str(question_id) if isinstance(question_id, UUID) else question_id
        
        return [
            task
            for task in self.list()
            if hasattr(task, 'research_question_ids') and 
            question_id_str in task.research_question_ids
        ]
        
    # Research question-related methods to be implemented by concrete classes
    
    @abstractmethod
    def create_research_question(self, question: ResearchQuestion) -> str:
        """
        Create a new research question.
        
        Args:
            question: The research question to create
            
        Returns:
            str: The ID of the created research question
        """
        pass
        
    @abstractmethod
    def get_research_question(self, question_id: Union[str, UUID]) -> Optional[ResearchQuestion]:
        """
        Retrieve a research question by ID.
        
        Args:
            question_id: The ID of the research question to retrieve
            
        Returns:
            Optional[ResearchQuestion]: The research question if found, None otherwise
        """
        pass
        
    @abstractmethod
    def update_research_question(self, question: ResearchQuestion) -> bool:
        """
        Update an existing research question.
        
        Args:
            question: The research question with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        pass
        
    @abstractmethod
    def delete_research_question(self, question_id: Union[str, UUID]) -> bool:
        """
        Delete a research question by ID.
        
        Args:
            question_id: The ID of the research question to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
        
    @abstractmethod
    def list_research_questions(
        self, parent_question_id: Optional[Union[str, UUID]] = ...
    ) -> List[ResearchQuestion]:
        """
        List research questions with optional filtering.
        
        Args:
            parent_question_id: Filter by parent question ID. If not provided, returns all questions.
                                If set to None, returns only top-level questions (with no parent).
                                
        Returns:
            List[ResearchQuestion]: List of research questions matching the criteria
        """
        pass


class ResearchQuestionStorage(BaseStorageInterface[ResearchQuestion]):
    """Storage interface specifically for research questions."""

    def __init__(self):
        """Initialize the research question storage."""
        self._questions: Dict[str, ResearchQuestion] = {}
    
    def create(self, entity: ResearchQuestion) -> str:
        """
        Create a new research question.
        
        Args:
            entity: The research question to create
            
        Returns:
            str: The ID of the created research question
        """
        entity_id = str(entity.id)
        self._questions[entity_id] = entity
        return entity_id
    
    def get(self, entity_id: Union[str, UUID]) -> Optional[ResearchQuestion]:
        """
        Retrieve a research question by ID.
        
        Args:
            entity_id: The ID of the research question to retrieve
            
        Returns:
            Optional[ResearchQuestion]: The research question if found, None otherwise
        """
        # Convert UUID to string if needed
        if isinstance(entity_id, UUID):
            entity_id = str(entity_id)
            
        return self._questions.get(entity_id)
    
    def update(self, entity: ResearchQuestion) -> bool:
        """
        Update an existing research question.
        
        Args:
            entity: The research question with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        entity_id = str(entity.id)
        
        if entity_id not in self._questions:
            return False
            
        self._questions[entity_id] = entity
        return True
    
    def delete(self, entity_id: Union[str, UUID]) -> bool:
        """
        Delete a research question by ID.
        
        Args:
            entity_id: The ID of the research question to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        # Convert UUID to string if needed
        if isinstance(entity_id, UUID):
            entity_id = str(entity_id)
            
        if entity_id not in self._questions:
            return False
            
        # Check if this question is a parent to any other questions
        child_questions = [q for q in self._questions.values() if q.parent_question_id == entity_id]
        if child_questions:
            # Update child questions to remove parent reference
            for child in child_questions:
                child.parent_question_id = None
                
        del self._questions[entity_id]
        return True
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[ResearchQuestion]:
        """
        List research questions with optional filtering.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            List[ResearchQuestion]: List of research questions matching the criteria
        """
        questions = list(self._questions.values())
        
        if not filters:
            return questions
            
        # Apply filters
        filtered_questions = []
        for question in questions:
            if all(hasattr(question, field) and getattr(question, field) == value 
                  for field, value in filters.items()):
                filtered_questions.append(question)
                
        return filtered_questions
    
    def list_by_parent(self, parent_question_id: Optional[Union[str, UUID]] = ...) -> List[ResearchQuestion]:
        """
        List research questions with optional parent filtering.
        
        Args:
            parent_question_id: Filter by parent question ID. If not provided, returns all questions.
                                If set to None, returns only top-level questions (with no parent).
                                
        Returns:
            List[ResearchQuestion]: List of research questions matching the criteria
        """
        questions = list(self._questions.values())
        
        # If parent_question_id is not specified (default value), return all questions
        if parent_question_id is ...:
            return questions
            
        # Convert UUID to string if needed
        if isinstance(parent_question_id, UUID):
            parent_question_id = str(parent_question_id)
            
        # If parent_question_id is set to None, return top-level questions
        # Otherwise, return questions with the specified parent
        filtered_questions = []
        for q in questions:
            # For parent_question_id=None, include questions with no parent
            if parent_question_id is None and q.parent_question_id is None:
                filtered_questions.append(q)
            # For specific parent_id, include questions with that parent
            elif q.parent_question_id == parent_question_id:
                filtered_questions.append(q)
                
        return filtered_questions


class InMemoryTaskStorage(InMemoryStorage[ResearchTask], TaskStorageInterface):
    """In-memory implementation of task storage."""
    
    def __init__(self):
        """Initialize the task storage."""
        super().__init__()
        self._question_storage = ResearchQuestionStorage()
        
    def get_subtasks(self, parent_id: Union[str, UUID]) -> List[ResearchTask]:
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_id: The ID of the parent task
            
        Returns:
            List[ResearchTask]: List of subtasks
        """
        # Convert UUID to string if needed
        if isinstance(parent_id, UUID):
            parent_id = str(parent_id)
            
        return [
            task for task in self._entities.values()
            if task.parent_id == parent_id
        ]
    
    def get_tasks_by_tag(self, tag: str) -> List[ResearchTask]:
        """
        Get all tasks with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List[ResearchTask]: List of tasks with the tag
        """
        return [
            task for task in self._entities.values()
            if tag in task.tags
        ]
    
    def get_tasks_by_status(self, status: str) -> List[ResearchTask]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: The status to search for
            
        Returns:
            List[ResearchTask]: List of tasks with the status
        """
        return [
            task for task in self._entities.values()
            if task.status == status
        ]
    
    # Delegate methods for question management
    def create_research_question(self, question: ResearchQuestion) -> str:
        """
        Create a new research question.
        
        Args:
            question: The research question to create
            
        Returns:
            str: The ID of the created research question
        """
        return self._question_storage.create(question)
    
    def get_research_question(self, question_id: Union[str, UUID]) -> Optional[ResearchQuestion]:
        """
        Retrieve a research question by ID.
        
        Args:
            question_id: The ID of the research question to retrieve
            
        Returns:
            Optional[ResearchQuestion]: The research question if found, None otherwise
        """
        return self._question_storage.get(question_id)
    
    def update_research_question(self, question: ResearchQuestion) -> bool:
        """
        Update an existing research question.
        
        Args:
            question: The research question with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        return self._question_storage.update(question)
    
    def delete_research_question(self, question_id: Union[str, UUID]) -> bool:
        """
        Delete a research question by ID.
        
        Args:
            question_id: The ID of the research question to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        question_id_str = str(question_id) if isinstance(question_id, UUID) else question_id
        
        # Check if successful
        if not self._question_storage.delete(question_id):
            return False
            
        # Remove association from any tasks
        for task in self._entities.values():
            if question_id_str in task.research_question_ids:
                task.research_question_ids.remove(question_id_str)
                
        return True
    
    def list_research_questions(self, parent_question_id: Optional[Union[str, UUID]] = ...) -> List[ResearchQuestion]:
        """
        List research questions with optional filtering.
        
        Args:
            parent_question_id: Filter by parent question ID. If not provided, returns all questions.
                               If set to None, returns only top-level questions (with no parent).
                               
        Returns:
            List[ResearchQuestion]: List of research questions matching the criteria
        """
        return self._question_storage.list_by_parent(parent_question_id)


class FileResearchQuestionStorage(FilePersistentStorage[ResearchQuestion]):
    """File-based storage for research questions."""
    
    def list_by_parent(self, parent_question_id: Optional[Union[str, UUID]] = ...) -> List[ResearchQuestion]:
        """
        List research questions with optional parent filtering.
        
        Args:
            parent_question_id: Filter by parent question ID. If not provided, returns all questions.
                                If set to None, returns only top-level questions (with no parent).
                                
        Returns:
            List[ResearchQuestion]: List of research questions matching the criteria
        """
        questions = self.list()
        
        # If parent_question_id is not specified (default value), return all questions
        if parent_question_id is ...:
            return questions
            
        # Convert UUID to string if needed
        if isinstance(parent_question_id, UUID):
            parent_question_id = str(parent_question_id)
            
        # If parent_question_id is set to None, return top-level questions
        # Otherwise, return questions with the specified parent
        filtered_questions = []
        for q in questions:
            # For parent_question_id=None, include questions with no parent
            if parent_question_id is None and q.parent_question_id is None:
                filtered_questions.append(q)
            # For specific parent_id, include questions with that parent
            elif q.parent_question_id == parent_question_id:
                filtered_questions.append(q)
                
        return filtered_questions


class FileTaskStorage(FilePersistentStorage[ResearchTask], TaskStorageInterface):
    """File-based implementation of task storage."""
    
    def __init__(
        self, 
        storage_dir: str, 
        entity_type: Type[ResearchTask] = ResearchTask,
        crypto_manager: Optional[CryptoManager] = None,
        use_encryption: bool = False
    ):
        """
        Initialize the file task storage.
        
        Args:
            storage_dir: Directory to store task files
            entity_type: The task type class (default is ResearchTask)
            crypto_manager: Optional crypto manager for encryption
            use_encryption: Whether to encrypt stored files
        """
        # Create main directory
        os.makedirs(storage_dir, exist_ok=True)
        
        # Create tasks subdirectory
        tasks_dir = os.path.join(storage_dir, "tasks")
        os.makedirs(tasks_dir, exist_ok=True)
        
        # Create questions subdirectory
        questions_dir = os.path.join(storage_dir, "questions")
        os.makedirs(questions_dir, exist_ok=True)
        
        # Initialize the task storage
        super().__init__(tasks_dir, entity_type, crypto_manager, use_encryption)
        
        # Initialize the question storage
        self._question_storage = FileResearchQuestionStorage(
            storage_dir=questions_dir,
            entity_type=ResearchQuestion,
            crypto_manager=crypto_manager,
            use_encryption=use_encryption
        )
    
    def get_subtasks(self, parent_id: Union[str, UUID]) -> List[ResearchTask]:
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_id: The ID of the parent task
            
        Returns:
            List[ResearchTask]: List of subtasks
        """
        # Convert UUID to string if needed
        if isinstance(parent_id, UUID):
            parent_id = str(parent_id)
            
        return [
            task for task in self.list()
            if task.parent_id == parent_id
        ]
    
    def get_tasks_by_tag(self, tag: str) -> List[ResearchTask]:
        """
        Get all tasks with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List[ResearchTask]: List of tasks with the tag
        """
        return [
            task for task in self.list()
            if tag in task.tags
        ]
    
    def get_tasks_by_status(self, status: str) -> List[ResearchTask]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: The status to search for
            
        Returns:
            List[ResearchTask]: List of tasks with the status
        """
        return [
            task for task in self.list()
            if task.status == status
        ]
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        tags: Optional[Set[str]] = None,
        research_question_id: Optional[Union[str, UUID]] = None,
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
        # Build filters dictionary
        filters = {}
        if status:
            filters["status"] = status.value if isinstance(status, TaskStatus) else status
        if priority:
            filters["priority"] = priority.value if isinstance(priority, TaskPriority) else priority
        
        # Get filtered tasks from the base list method
        tasks = self.list(filters)
        
        # Apply tag filtering
        if tags:
            tasks = [
                task for task in tasks if all(tag in task.tags for tag in tags)
            ]
        
        # Apply research question filtering
        if research_question_id:
            # Convert UUID to string if needed
            if isinstance(research_question_id, UUID):
                research_question_id = str(research_question_id)
                
            tasks = [
                task
                for task in tasks
                if hasattr(task, 'research_question_ids') and 
                research_question_id in task.research_question_ids
            ]
        
        return tasks
        
    def get_tasks_by_research_question(
        self, question_id: Union[str, UUID]
    ) -> List[ResearchTask]:
        """
        Get all tasks associated with a research question.
        
        Args:
            question_id: The ID of the research question
            
        Returns:
            List[ResearchTask]: List of tasks associated with the research question
        """
        question_id_str = str(question_id) if isinstance(question_id, UUID) else question_id
        
        return [
            task
            for task in self.list()
            if hasattr(task, 'research_question_ids') and 
            question_id_str in task.research_question_ids
        ]
    
    # Research question delegation methods
    
    def create_research_question(self, question: ResearchQuestion) -> str:
        """
        Create a new research question.
        
        Args:
            question: The research question to create
            
        Returns:
            str: The ID of the created research question
        """
        return self._question_storage.create(question)
    
    def get_research_question(self, question_id: Union[str, UUID]) -> Optional[ResearchQuestion]:
        """
        Retrieve a research question by ID.
        
        Args:
            question_id: The ID of the research question to retrieve
            
        Returns:
            Optional[ResearchQuestion]: The research question if found, None otherwise
        """
        return self._question_storage.get(question_id)
    
    def update_research_question(self, question: ResearchQuestion) -> bool:
        """
        Update an existing research question.
        
        Args:
            question: The research question with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        return self._question_storage.update(question)
    
    def delete_research_question(self, question_id: Union[str, UUID]) -> bool:
        """
        Delete a research question by ID.
        
        Args:
            question_id: The ID of the research question to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        question_id_str = str(question_id) if isinstance(question_id, UUID) else question_id
        
        # Check if successful
        if not self._question_storage.delete(question_id):
            return False
            
        # Remove association from any tasks
        tasks_to_update = []
        for task in self.list():
            if question_id_str in task.research_question_ids:
                task.research_question_ids.remove(question_id_str)
                tasks_to_update.append(task)
                
        # Update tasks that had the question associated
        for task in tasks_to_update:
            self.update(task)
                
        return True
    
    def list_research_questions(self, parent_question_id: Optional[Union[str, UUID]] = ...) -> List[ResearchQuestion]:
        """
        List research questions with optional filtering.
        
        Args:
            parent_question_id: Filter by parent question ID. If not provided, returns all questions.
                               If set to None, returns only top-level questions (with no parent).
                               
        Returns:
            List[ResearchQuestion]: List of research questions matching the criteria
        """
        return self._question_storage.list_by_parent(parent_question_id)