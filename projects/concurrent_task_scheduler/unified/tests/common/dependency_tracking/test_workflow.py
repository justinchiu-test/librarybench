"""Tests for the common workflow management system."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from common.core.models import (
    BaseJob,
    JobStatus,
    DependencyState,
    DependencyType,
    Priority,
    Result,
)
from common.dependency_tracking.graph import DependencyGraph, GraphNodeType
from common.dependency_tracking.tracker import DependencyTracker, TransitionTrigger
from common.dependency_tracking.workflow import (
    WorkflowManager,
    WorkflowTemplate,
    WorkflowTemplateType,
    WorkflowStage,
    WorkflowNodeType,
    WorkflowTransition,
    WorkflowTransitionType,
)


class TestWorkflowTemplate:
    """Tests for WorkflowTemplate."""
    
    def test_create_sequential(self):
        """Test creating a sequential workflow template."""
        template = WorkflowTemplate.create_sequential(
            name="Test Sequential Workflow",
            stage_names=["Stage 1", "Stage 2", "Stage 3"],
        )
        
        # Check template properties
        assert template.name == "Test Sequential Workflow"
        assert template.template_type == WorkflowTemplateType.SEQUENTIAL
        assert len(template.stages) == 3
        assert len(template.transitions) == 2  # 3 stages = 2 transitions
        
        # Check stages are named correctly
        stage_names = [stage.name for stage in template.stages.values()]
        assert "Stage 1" in stage_names
        assert "Stage 2" in stage_names
        assert "Stage 3" in stage_names
        
        # Check transitions connect stages in sequence
        for transition in template.transitions:
            from_stage = template.stages[transition.from_stage_id]
            to_stage = template.stages[transition.to_stage_id]
            assert stage_names.index(from_stage.name) == stage_names.index(to_stage.name) - 1
    
    def test_create_parallel(self):
        """Test creating a parallel workflow template."""
        template = WorkflowTemplate.create_parallel(
            name="Test Parallel Workflow",
            stage_names=["Stage A", "Stage B", "Stage C"],
        )
        
        # Check template properties
        assert template.name == "Test Parallel Workflow"
        assert template.template_type == WorkflowTemplateType.PARALLEL
        assert len(template.stages) == 5  # 3 stages + start + end
        assert len(template.transitions) == 6  # 3 from start + 3 to end
        
        # Check that start and end stages exist
        has_start = False
        has_end = False
        for stage in template.stages.values():
            if stage.node_type == WorkflowNodeType.START:
                has_start = True
            elif stage.node_type == WorkflowNodeType.END:
                has_end = True
        
        assert has_start
        assert has_end
        
        # Check that all stages connect from start and to end
        start_stage_id = next(stage_id for stage_id, stage in template.stages.items() 
                         if stage.node_type == WorkflowNodeType.START)
        end_stage_id = next(stage_id for stage_id, stage in template.stages.items() 
                       if stage.node_type == WorkflowNodeType.END)
        
        # Count connections from start and to end
        from_start_count = 0
        to_end_count = 0
        for transition in template.transitions:
            if transition.from_stage_id == start_stage_id:
                from_start_count += 1
            if transition.to_stage_id == end_stage_id:
                to_end_count += 1
        
        assert from_start_count == 3  # Should connect to all 3 stages
        assert to_end_count == 3  # All 3 stages should connect to end
    
    def test_validate(self):
        """Test workflow template validation."""
        # Create valid template
        template = WorkflowTemplate.create_sequential(
            name="Test Sequential Workflow",
            stage_names=["Stage 1", "Stage 2", "Stage 3"],
        )
        
        errors = template.validate()
        assert not errors
        
        # Create invalid template with cycle
        invalid_template = WorkflowTemplate(
            template_id="invalid",
            name="Invalid Template",
            template_type=WorkflowTemplateType.DAG,
        )
        
        # Add stages
        invalid_template.add_stage(WorkflowStage(stage_id="stage_1", name="Stage 1"))
        invalid_template.add_stage(WorkflowStage(stage_id="stage_2", name="Stage 2"))
        invalid_template.add_stage(WorkflowStage(stage_id="stage_3", name="Stage 3"))
        
        # Add cyclic dependencies: 1 -> 2 -> 3 -> 1
        invalid_template.add_transition(WorkflowTransition(from_stage_id="stage_1", to_stage_id="stage_2"))
        invalid_template.add_transition(WorkflowTransition(from_stage_id="stage_2", to_stage_id="stage_3"))
        invalid_template.add_transition(WorkflowTransition(from_stage_id="stage_3", to_stage_id="stage_1"))
        
        errors = invalid_template.validate()
        assert errors
        assert any("cycle" in error.lower() for error in errors)


class TestWorkflowManager:
    """Tests for WorkflowManager."""
    
    def setup_method(self):
        """Set up tests."""
        self.tracker = DependencyTracker()
        self.manager = WorkflowManager(self.tracker)
        self.jobs = self._create_test_jobs()
        self.owner_id = "test-owner-1"
    
    def _create_test_jobs(self) -> Dict[str, BaseJob]:
        """Create test jobs."""
        return {
            "job-1": BaseJob(id="job-1", name="Stage 1", status=JobStatus.PENDING, priority=Priority.MEDIUM),
            "job-2": BaseJob(id="job-2", name="Stage 2", status=JobStatus.PENDING, priority=Priority.MEDIUM),
            "job-3": BaseJob(id="job-3", name="Stage 3", status=JobStatus.PENDING, priority=Priority.MEDIUM),
        }
    
    def test_register_template(self):
        """Test registering a workflow template."""
        template = WorkflowTemplate.create_sequential(
            name="Test Sequential Workflow",
            stage_names=["Stage 1", "Stage 2", "Stage 3"],
        )
        
        result = self.manager.register_template(template)
        assert result.success
        
        assert template.id in self.manager.templates
    
    def test_create_instance(self):
        """Test creating a workflow instance from a template."""
        template = WorkflowTemplate.create_sequential(
            name="Test Sequential Workflow",
            stage_names=["Stage 1", "Stage 2", "Stage 3"],
        )
        
        # Register template
        self.manager.register_template(template)
        
        # Create instance
        result = self.manager.create_instance(template.id, self.owner_id, self.jobs)
        assert result.success
        
        instance = result.value
        
        # Check instance properties
        assert instance.template_id == template.id
        assert instance.owner_id == self.owner_id
        assert instance.status == JobStatus.PENDING
        
        # Check stage mapping
        assert len(instance.stage_mapping) == 3
        
        # Check that jobs were mapped to the correct stages
        for template_stage_id, template_stage in template.stages.items():
            job_id = instance.get_job_id(template_stage_id)
            if job_id:
                job = self.jobs[job_id]
                assert job.name == template_stage.name
    
    def test_create_linear_workflow(self):
        """Test creating a linear workflow."""
        result = self.manager.create_linear_workflow(
            self.owner_id,
            ["Stage 1", "Stage 2", "Stage 3"],
            self.jobs,
        )
        
        assert result.success
        instance = result.value
        
        # Check instance properties
        assert instance.owner_id == self.owner_id
        
        # Check jobs
        job_ids = []
        for template_stage_id in sorted(instance.stage_mapping.keys()):
            job_id = instance.get_job_id(template_stage_id)
            if job_id:
                job_ids.append(job_id)
        
        # Get jobs in dependency order
        ordered_job_ids = []
        for job_id in job_ids:
            # Check dependencies
            job = self.jobs[job_id]
            if hasattr(job, 'dependencies') and job.dependencies:
                depends_on = list(job.dependencies)[0]
                if depends_on in job_ids:
                    # This is a dependent job
                    assert job_ids.index(depends_on) < job_ids.index(job_id)
    
    def test_create_parallel_workflow(self):
        """Test creating a parallel workflow."""
        result = self.manager.create_parallel_workflow(
            self.owner_id,
            ["Stage 1", "Stage 2", "Stage 3"],
            self.jobs,
        )
        
        assert result.success
        instance = result.value
        
        # Check instance properties
        assert instance.owner_id == self.owner_id
        
        # Check that all jobs are in the stage mapping
        job_ids = set()
        for template_stage_id, job_id in instance.stage_mapping.items():
            if "stage_" in template_stage_id:  # Skip start/end stages
                job_ids.add(job_id)
        
        assert len(job_ids) == 3
    
    def test_get_next_jobs(self):
        """Test getting the next jobs to execute."""
        # Create linear workflow
        result = self.manager.create_linear_workflow(
            self.owner_id,
            ["Stage 1", "Stage 2", "Stage 3"],
            self.jobs,
        )
        
        assert result.success
        instance = result.value
        
        # Initially, only the first job should be ready
        next_result = self.manager.get_next_jobs(instance.id, self.jobs)
        assert next_result.success
        next_jobs = next_result.value
        
        assert len(next_jobs) == 1
        
        # Get the job ID of the first stage
        for template_stage_id, job_id in instance.stage_mapping.items():
            if "stage_1" in template_stage_id:
                first_job_id = job_id
                break
        
        assert first_job_id in next_jobs
        
        # Complete the first job
        self.jobs[first_job_id].status = JobStatus.COMPLETED
        
        # Get next jobs
        next_result = self.manager.get_next_jobs(instance.id, self.jobs)
        assert next_result.success
        next_jobs = next_result.value
        
        assert len(next_jobs) == 1
        
        # Get the job ID of the second stage
        for template_stage_id, job_id in instance.stage_mapping.items():
            if "stage_2" in template_stage_id:
                second_job_id = job_id
                break
        
        assert second_job_id in next_jobs
    
    def test_update_job_status(self):
        """Test updating a job status in a workflow instance."""
        # Create linear workflow
        result = self.manager.create_linear_workflow(
            self.owner_id,
            ["Stage 1", "Stage 2", "Stage 3"],
            self.jobs,
        )
        
        assert result.success
        instance = result.value
        
        # Get the job ID of the first stage
        for template_stage_id, job_id in instance.stage_mapping.items():
            if "stage_1" in template_stage_id:
                first_job_id = job_id
                break
        
        # Update status
        update_result = self.manager.update_job_status(
            instance.id,
            first_job_id,
            JobStatus.RUNNING,
            self.jobs,
        )
        
        assert update_result.success
        
        # Check that the job status was updated
        assert self.jobs[first_job_id].status == JobStatus.RUNNING
        
        # Check that the instance status was updated
        assert instance.status == JobStatus.RUNNING
        
        # Complete the job
        update_result = self.manager.update_job_status(
            instance.id,
            first_job_id,
            JobStatus.COMPLETED,
            self.jobs,
        )
        
        assert update_result.success
        
        # Check that the job status was updated
        assert self.jobs[first_job_id].status == JobStatus.COMPLETED
    
    def test_get_workflow_status(self):
        """Test getting the current status of a workflow instance."""
        # Create linear workflow
        result = self.manager.create_linear_workflow(
            self.owner_id,
            ["Stage 1", "Stage 2", "Stage 3"],
            self.jobs,
        )
        
        assert result.success
        instance = result.value
        
        # Get status
        status_result = self.manager.get_workflow_status(instance.id)
        assert status_result.success
        status = status_result.value
        
        # Check initial status
        assert status["instance_id"] == instance.id
        assert status["owner_id"] == self.owner_id
        assert status["status"] == JobStatus.PENDING.value
        assert status["progress"] == 0.0
        
        # Update a job status
        for template_stage_id, job_id in instance.stage_mapping.items():
            if "stage_1" in template_stage_id:
                first_job_id = job_id
                break
        
        self.jobs[first_job_id].status = JobStatus.COMPLETED
        
        # Update instance
        instance.update_status({job_id: job.status for job_id, job in self.jobs.items()})
        
        # Get updated status
        status_result = self.manager.get_workflow_status(instance.id)
        assert status_result.success
        status = status_result.value
        
        # Check progress (1 out of 3 jobs completed)
        assert status["progress"] == 1/3