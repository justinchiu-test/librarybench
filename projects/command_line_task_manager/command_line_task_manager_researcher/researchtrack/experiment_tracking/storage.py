from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Union, Any
from uuid import UUID

from .models import (
    Experiment,
    ExperimentRun,
    ExperimentStatus,
    ExperimentComparison,
    Parameter,
    Metric,
    MetricType
)


class ExperimentStorageInterface(ABC):
    """Abstract interface for experiment tracking storage implementations."""
    
    @abstractmethod
    def create_experiment(self, experiment: Experiment) -> UUID:
        """
        Create a new experiment.
        
        Args:
            experiment: The experiment to create
            
        Returns:
            UUID: The ID of the created experiment
        """
        pass
    
    @abstractmethod
    def get_experiment(self, experiment_id: UUID) -> Optional[Experiment]:
        """
        Retrieve an experiment by ID.
        
        Args:
            experiment_id: The ID of the experiment to retrieve
            
        Returns:
            Optional[Experiment]: The experiment if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update_experiment(self, experiment: Experiment) -> bool:
        """
        Update an existing experiment.
        
        Args:
            experiment: The experiment with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_experiment(self, experiment_id: UUID) -> bool:
        """
        Delete an experiment by ID.
        
        Args:
            experiment_id: The ID of the experiment to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_experiments(
        self, task_id: Optional[UUID] = None, tags: Optional[List[str]] = None
    ) -> List[Experiment]:
        """
        List experiments with optional filtering.
        
        Args:
            task_id: Filter by associated task ID
            tags: Filter by tags (experiments must have all specified tags)
            
        Returns:
            List[Experiment]: List of experiments matching the criteria
        """
        pass
    
    @abstractmethod
    def create_run(self, run: ExperimentRun) -> UUID:
        """
        Create a new experiment run.
        
        Args:
            run: The experiment run to create
            
        Returns:
            UUID: The ID of the created run
        """
        pass
    
    @abstractmethod
    def get_run(self, run_id: UUID) -> Optional[ExperimentRun]:
        """
        Retrieve an experiment run by ID.
        
        Args:
            run_id: The ID of the run to retrieve
            
        Returns:
            Optional[ExperimentRun]: The run if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update_run(self, run: ExperimentRun) -> bool:
        """
        Update an existing experiment run.
        
        Args:
            run: The run with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_run(self, run_id: UUID) -> bool:
        """
        Delete an experiment run by ID.
        
        Args:
            run_id: The ID of the run to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_runs(
        self, experiment_id: UUID, status: Optional[ExperimentStatus] = None
    ) -> List[ExperimentRun]:
        """
        List runs of an experiment.
        
        Args:
            experiment_id: The ID of the experiment
            status: Filter by run status
            
        Returns:
            List[ExperimentRun]: List of experiment runs
        """
        pass
    
    @abstractmethod
    def create_comparison(self, comparison: ExperimentComparison) -> UUID:
        """
        Create a new experiment comparison.
        
        Args:
            comparison: The experiment comparison to create
            
        Returns:
            UUID: The ID of the created comparison
        """
        pass
    
    @abstractmethod
    def get_comparison(self, comparison_id: UUID) -> Optional[ExperimentComparison]:
        """
        Retrieve an experiment comparison by ID.
        
        Args:
            comparison_id: The ID of the comparison to retrieve
            
        Returns:
            Optional[ExperimentComparison]: The comparison if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update_comparison(self, comparison: ExperimentComparison) -> bool:
        """
        Update an existing experiment comparison.
        
        Args:
            comparison: The comparison with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_comparison(self, comparison_id: UUID) -> bool:
        """
        Delete an experiment comparison by ID.
        
        Args:
            comparison_id: The ID of the comparison to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_comparisons(self) -> List[ExperimentComparison]:
        """
        List all experiment comparisons.
        
        Returns:
            List[ExperimentComparison]: List of all comparisons
        """
        pass


class InMemoryExperimentStorage(ExperimentStorageInterface):
    """In-memory implementation of experiment tracking storage."""
    
    def __init__(self):
        self._experiments: Dict[UUID, Experiment] = {}
        self._runs: Dict[UUID, ExperimentRun] = {}
        self._comparisons: Dict[UUID, ExperimentComparison] = {}
    
    def create_experiment(self, experiment: Experiment) -> UUID:
        self._experiments[experiment.id] = experiment
        return experiment.id
    
    def get_experiment(self, experiment_id: UUID) -> Optional[Experiment]:
        return self._experiments.get(experiment_id)
    
    def update_experiment(self, experiment: Experiment) -> bool:
        if experiment.id not in self._experiments:
            return False
        
        # Update experiment
        self._experiments[experiment.id] = experiment
        
        # Update runs
        for run in experiment.runs:
            self._runs[run.id] = run
        
        return True
    
    def delete_experiment(self, experiment_id: UUID) -> bool:
        if experiment_id not in self._experiments:
            return False
        
        # Delete all runs
        experiment = self._experiments[experiment_id]
        for run in experiment.runs:
            if run.id in self._runs:
                del self._runs[run.id]
        
        # Delete experiment
        del self._experiments[experiment_id]
        
        # Update comparisons
        for comparison in self._comparisons.values():
            if experiment_id in comparison.experiment_ids:
                comparison.experiment_ids.remove(experiment_id)
        
        return True
    
    def list_experiments(
        self, task_id: Optional[UUID] = None, tags: Optional[List[str]] = None
    ) -> List[Experiment]:
        experiments = list(self._experiments.values())
        
        if task_id is not None:
            experiments = [exp for exp in experiments if exp.task_id == task_id]
        
        if tags:
            experiments = [
                exp for exp in experiments
                if all(tag in exp.tags for tag in tags)
            ]
        
        return experiments
    
    def create_run(self, run: ExperimentRun) -> UUID:
        # Store run
        self._runs[run.id] = run
        
        # Add run to experiment
        experiment = self._experiments.get(run.experiment_id)
        if experiment:
            if run not in experiment.runs:
                experiment.runs.append(run)
        
        return run.id
    
    def get_run(self, run_id: UUID) -> Optional[ExperimentRun]:
        return self._runs.get(run_id)
    
    def update_run(self, run: ExperimentRun) -> bool:
        if run.id not in self._runs:
            return False
        
        # Update run
        self._runs[run.id] = run
        
        # Update run in experiment
        experiment = self._experiments.get(run.experiment_id)
        if experiment:
            # Find and replace run in experiment
            for i, existing_run in enumerate(experiment.runs):
                if existing_run.id == run.id:
                    experiment.runs[i] = run
                    break
        
        return True
    
    def delete_run(self, run_id: UUID) -> bool:
        if run_id not in self._runs:
            return False
        
        run = self._runs[run_id]
        
        # Remove run from experiment
        experiment = self._experiments.get(run.experiment_id)
        if experiment:
            experiment.runs = [r for r in experiment.runs if r.id != run_id]
        
        # Delete run
        del self._runs[run_id]
        
        # Update comparisons
        for comparison in self._comparisons.values():
            if run_id in comparison.run_ids:
                comparison.run_ids.remove(run_id)
        
        return True
    
    def list_runs(
        self, experiment_id: UUID, status: Optional[ExperimentStatus] = None
    ) -> List[ExperimentRun]:
        # Get runs for experiment
        runs = [
            run for run in self._runs.values()
            if run.experiment_id == experiment_id
        ]
        
        if status:
            runs = [run for run in runs if run.status == status]
        
        # Sort by run number
        runs.sort(key=lambda r: r.run_number)
        
        return runs
    
    def create_comparison(self, comparison: ExperimentComparison) -> UUID:
        self._comparisons[comparison.id] = comparison
        return comparison.id
    
    def get_comparison(self, comparison_id: UUID) -> Optional[ExperimentComparison]:
        return self._comparisons.get(comparison_id)
    
    def update_comparison(self, comparison: ExperimentComparison) -> bool:
        if comparison.id not in self._comparisons:
            return False
        self._comparisons[comparison.id] = comparison
        return True
    
    def delete_comparison(self, comparison_id: UUID) -> bool:
        if comparison_id not in self._comparisons:
            return False
        del self._comparisons[comparison_id]
        return True
    
    def list_comparisons(self) -> List[ExperimentComparison]:
        return list(self._comparisons.values())