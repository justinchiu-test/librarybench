"""Execution pipeline and context for query language interpreters."""

from typing import Any, Callable, Dict, List, Optional, Set, Union
from abc import ABC, abstractmethod

from common.core.query import BaseQuery, ExecutionContext


class ExecutionPipeline:
    """Pipeline for executing queries."""

    def __init__(self):
        """Initialize an execution pipeline."""
        self.steps: List[Callable[[BaseQuery, Dict[str, Any]], None]] = []
        self.pre_processors: List[Callable[[BaseQuery], None]] = []
        self.post_processors: List[Callable[[BaseQuery, Dict[str, Any]], None]] = []

    def add_pre_processor(self, processor: Callable[[BaseQuery], None]) -> None:
        """Add a pre-processor to the pipeline.

        Args:
            processor: Pre-processor function
        """
        self.pre_processors.append(processor)

    def add_step(self, step: Callable[[BaseQuery, Dict[str, Any]], None]) -> None:
        """Add an execution step to the pipeline.

        Args:
            step: Execution step function
        """
        self.steps.append(step)

    def add_post_processor(
        self, processor: Callable[[BaseQuery, Dict[str, Any]], None]
    ) -> None:
        """Add a post-processor to the pipeline.

        Args:
            processor: Post-processor function
        """
        self.post_processors.append(processor)

    def execute(self, query: BaseQuery) -> Dict[str, Any]:
        """Execute the pipeline on a query.

        Args:
            query: Query to execute

        Returns:
            Dict[str, Any]: Execution results
        """
        # Initialize execution context if not already set
        if not query.get_execution_context():
            query.set_execution_context(ExecutionContext())
            
        # Initialize results
        results: Dict[str, Any] = {}
        
        # Run pre-processors
        for processor in self.pre_processors:
            processor(query)
        
        # Run execution steps
        for step in self.steps:
            step(query, results)
        
        # Run post-processors
        for processor in self.post_processors:
            processor(query, results)
        
        return results


class ExecutionStep(ABC):
    """Base class for execution steps."""

    @abstractmethod
    def execute(self, query: BaseQuery, results: Dict[str, Any]) -> None:
        """Execute the step on a query.

        Args:
            query: Query to execute
            results: Current execution results
        """
        pass


class PreProcessor(ABC):
    """Base class for pre-processors."""

    @abstractmethod
    def process(self, query: BaseQuery) -> None:
        """Process a query before execution.

        Args:
            query: Query to process
        """
        pass


class PostProcessor(ABC):
    """Base class for post-processors."""

    @abstractmethod
    def process(self, query: BaseQuery, results: Dict[str, Any]) -> None:
        """Process a query after execution.

        Args:
            query: Executed query
            results: Execution results
        """
        pass