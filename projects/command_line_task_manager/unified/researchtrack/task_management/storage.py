from typing import Dict, List, Optional, Set, Union
from uuid import UUID

from common.core.storage import BaseStorageInterface, InMemoryStorage
from .models import ResearchQuestion, ResearchTask, TaskPriority, TaskStatus


class TaskStorageInterface(BaseStorageInterface[ResearchTask]):
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
        return self.delete(task_id)
    
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
        filters = {}
        if status:
            filters["status"] = status.value if isinstance(status, TaskStatus) else status
        if priority:
            filters["priority"] = priority.value if isinstance(priority, TaskPriority) else priority
        
        tasks = list(self._entities.values())
        
        # Apply status and priority filtering
        if status or priority:
            filtered_tasks = []
            for task in tasks:
                if status and task.status != filters["status"]:
                    continue
                if priority and task.priority != filters["priority"]:
                    continue
                filtered_tasks.append(task)
            tasks = filtered_tasks
        
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
                if research_question_id in task.research_question_ids
            ]
        
        return tasks
    
    def create_research_question(self, question: ResearchQuestion) -> str:
        """
        Create a new research question.
        
        Args:
            question: The research question to create
            
        Returns:
            UUID: The ID of the created research question
        """
        return self.create(question)
    
    def get_research_question(self, question_id: Union[str, UUID]) -> Optional[ResearchQuestion]:
        """
        Retrieve a research question by ID.
        
        Args:
            question_id: The ID of the research question to retrieve
            
        Returns:
            Optional[ResearchQuestion]: The research question if found, None otherwise
        """
        return self.get(question_id)
    
    def update_research_question(self, question: ResearchQuestion) -> bool:
        """
        Update an existing research question.
        
        Args:
            question: The research question with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        return self.update(question)
    
    def delete_research_question(self, question_id: Union[str, UUID]) -> bool:
        """
        Delete a research question by ID.
        
        Args:
            question_id: The ID of the research question to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self.delete(question_id)
    
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
        questions = self.list({})
        
        # If parent_question_id is not specified (default value), return all questions
        if parent_question_id is ...:
            return questions
        
        # If parent_question_id is set to None, return top-level questions (those with no parent)
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
        return [
            task
            for task in self.list_tasks()
            if question_id in task.research_question_ids
        ]
    
    def get_subtasks(self, parent_task_id: Union[str, UUID]) -> List[ResearchTask]:
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_task_id: The ID of the parent task
            
        Returns:
            List[ResearchTask]: List of subtasks
        """
        return [
            task
            for task in self.list_tasks()
            if task.parent_id == parent_task_id
        ]


class InMemoryTaskStorage(InMemoryStorage[ResearchTask], TaskStorageInterface):
    """In-memory implementation of task storage."""
    
    def __init__(self):
        super().__init__()
        self._questions: Dict[str, ResearchQuestion] = {}
    
    def create(self, entity) -> str:
        """Create an entity, handling both tasks and questions."""
        if isinstance(entity, ResearchTask):
            entity_id = str(entity.id)
            self._entities[entity_id] = entity
            return entity_id
        elif isinstance(entity, ResearchQuestion):
            entity_id = str(entity.id)
            self._questions[entity_id] = entity
            return entity_id
        else:
            raise TypeError(f"Unsupported entity type: {type(entity)}")
    
    def get(self, entity_id: Union[str, UUID]):
        """Get an entity, checking both tasks and questions."""
        # Convert UUID to string if needed
        if isinstance(entity_id, UUID):
            entity_id = str(entity_id)
            
        # Try to get from tasks
        entity = self._entities.get(entity_id)
        if entity:
            return entity
        
        # Try to get from questions
        return self._questions.get(entity_id)
    
    def update(self, entity) -> bool:
        """Update an entity, handling both tasks and questions."""
        entity_id = str(entity.id)
        
        if isinstance(entity, ResearchTask):
            if entity_id not in self._entities:
                return False
            self._entities[entity_id] = entity
            return True
        elif isinstance(entity, ResearchQuestion):
            if entity_id not in self._questions:
                return False
            self._questions[entity_id] = entity
            return True
        else:
            raise TypeError(f"Unsupported entity type: {type(entity)}")
    
    def delete(self, entity_id: Union[str, UUID]) -> bool:
        """Delete an entity, checking both tasks and questions."""
        # Convert UUID to string if needed
        if isinstance(entity_id, UUID):
            entity_id = str(entity_id)
            
        # Try to delete from tasks
        if entity_id in self._entities:
            del self._entities[entity_id]
            # Remove this task as a subtask from any parent tasks
            for task in self._entities.values():
                if entity_id in task.subtask_ids:
                    task.subtask_ids.remove(entity_id)
            return True
        
        # Try to delete from questions
        if entity_id in self._questions:
            # Check if this question is a parent to any other questions
            child_questions = [q for q in self._questions.values() if q.parent_question_id == entity_id]
            if child_questions:
                # Update child questions to remove parent reference
                for child in child_questions:
                    child.parent_question_id = None
            
            # Remove association from any tasks
            for task in self._entities.values():
                if entity_id in task.research_question_ids:
                    task.research_question_ids.remove(entity_id)
                    
            del self._questions[entity_id]
            return True
        
        return False
    
    def list(self, filters=None):
        """List entities of a specific type."""
        # Return tasks by default
        return list(self._entities.values())
        
    def list_research_questions(self, parent_question_id=...):
        """
        List research questions with optional filtering.
        
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