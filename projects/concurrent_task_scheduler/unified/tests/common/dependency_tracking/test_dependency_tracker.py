"""Tests for the common dependency tracking system."""

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


class TestDependencyGraph:
    """Tests for the DependencyGraph class."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.graph = DependencyGraph("owner-test-1")
        
        # Add nodes
        self.graph.add_node("job-1", GraphNodeType.JOB)
        self.graph.add_node("job-2", GraphNodeType.JOB)
        self.graph.add_node("job-3", GraphNodeType.JOB)
        self.graph.add_node("job-4", GraphNodeType.JOB)
        
        # Add dependencies
        self.graph.add_dependency("job-1", "job-2")  # 1 -> 2
        self.graph.add_dependency("job-2", "job-3")  # 2 -> 3
        self.graph.add_dependency("job-2", "job-4")  # 2 -> 4
    
    def test_add_node(self):
        """Test adding a node to the graph."""
        self.graph.add_node("job-5", GraphNodeType.JOB)
        assert "job-5" in self.graph.nodes
    
    def test_add_dependency(self):
        """Test adding a dependency between nodes."""
        result = self.graph.add_dependency("job-3", "job-4")
        assert result.success
        
        # Get the dependency
        dependency = self.graph.get_dependency("job-3", "job-4")
        assert dependency is not None
        assert dependency.from_id == "job-3"
        assert dependency.to_id == "job-4"
        assert dependency.dependency_type == DependencyType.SEQUENTIAL
        assert dependency.state == DependencyState.PENDING
    
    def test_add_dependency_with_cycle(self):
        """Test that adding a dependency that creates a cycle fails."""
        result = self.graph.add_dependency("job-3", "job-1")
        assert not result.success
        assert "cycle" in result.error.lower()
    
    def test_remove_dependency(self):
        """Test removing a dependency."""
        result = self.graph.remove_dependency("job-2", "job-3")
        assert result.success
        assert not self.graph.has_edge("job-2", "job-3")
    
    def test_get_dependencies(self):
        """Test getting dependencies to and from a node."""
        deps_from = self.graph.get_dependencies_from("job-2")
        assert len(deps_from) == 2
        
        deps_to = self.graph.get_dependencies_to("job-2")
        assert len(deps_to) == 1
        assert deps_to[0].from_id == "job-1"
    
    def test_get_root_and_leaf_nodes(self):
        """Test getting root and leaf nodes."""
        roots = self.graph.get_root_nodes()
        assert "job-1" in roots
        
        leaves = self.graph.get_leaf_nodes()
        assert "job-3" in leaves
        assert "job-4" in leaves
    
    def test_get_ready_nodes(self):
        """Test getting nodes that are ready to execute."""
        # Initially, only the root node should be ready
        completed_nodes = set()
        ready = self.graph.get_ready_nodes(completed_nodes)
        assert "job-1" in ready
        assert len(ready) == 1
        
        # After completing job-1, job-2 should be ready
        completed_nodes.add("job-1")
        ready = self.graph.get_ready_nodes(completed_nodes)
        assert "job-2" in ready
        assert len(ready) == 1
        
        # After completing job-2, both job-3 and job-4 should be ready
        completed_nodes.add("job-2")
        ready = self.graph.get_ready_nodes(completed_nodes)
        assert "job-3" in ready
        assert "job-4" in ready
        assert len(ready) == 2
    
    def test_are_all_dependencies_satisfied(self):
        """Test checking if all dependencies to a node are satisfied."""
        # Initially, no dependencies are satisfied
        assert not self.graph.are_all_dependencies_satisfied("job-2")
        
        # Satisfy the dependency from job-1 to job-2
        dep = self.graph.get_dependency("job-1", "job-2")
        dep.satisfy()
        
        # Now all dependencies to job-2 should be satisfied
        assert self.graph.are_all_dependencies_satisfied("job-2")
    
    def test_update_node_status(self):
        """Test updating a node's status and propagating changes."""
        # Complete job-1
        affected = self.graph.update_node_status("job-1", "completed")
        assert "job-2" in affected
        
        # Check that the dependency from job-1 to job-2 is satisfied
        dep = self.graph.get_dependency("job-1", "job-2")
        assert dep.is_satisfied()
    
    def test_get_critical_path(self):
        """Test getting the critical path through the graph."""
        path = self.graph.get_critical_path()
        assert path
        assert path[0] == "job-1"  # Starting point
        
        # Check that the order is correct
        assert path.index("job-1") < path.index("job-2")
        
        # Either path through job-3 or job-4 could be the critical path
        assert path.index("job-2") < path.index("job-3") or path.index("job-2") < path.index("job-4")
    
    def test_is_node_blocked(self):
        """Test checking if a node is blocked."""
        # job-2 is blocked by job-1
        blocking = self.graph.is_node_blocked("job-2", set())
        assert "job-1" in blocking
        
        # After completing job-1, job-2 should not be blocked
        blocking = self.graph.is_node_blocked("job-2", {"job-1"})
        assert blocking is None
    
    def test_validate(self):
        """Test validating the graph."""
        # The test graph should be valid
        errors = self.graph.validate()
        assert not errors
        
        # Add a cycle to make it invalid
        # First remove a dependency to avoid error from add_dependency
        self.graph.remove_dependency("job-2", "job-3")
        
        # We manually create the cycle to bypass the add_dependency check
        self.graph.graph.add_edge("job-3", "job-1")
        
        # Now validation should fail
        errors = self.graph.validate()
        assert any("cycle" in error.lower() for error in errors)


class TestDependencyTracker:
    """Tests for the DependencyTracker class."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.tracker = DependencyTracker()
        self.jobs = self._create_test_jobs()
        self.owner_id = "test-owner-1"
    
    def _create_test_jobs(self) -> Dict[str, BaseJob]:
        """Create test jobs."""
        # Create jobs
        job1 = BaseJob(
            id="job-1",
            name="Job 1",
            status=JobStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        
        job2 = BaseJob(
            id="job-2",
            name="Job 2",
            status=JobStatus.PENDING,
            priority=Priority.MEDIUM,
            dependencies={"job-1"},  # Depends on job-1
        )
        
        job3 = BaseJob(
            id="job-3",
            name="Job 3",
            status=JobStatus.PENDING,
            priority=Priority.MEDIUM,
            dependencies={"job-2"},  # Depends on job-2
        )
        
        return {
            "job-1": job1,
            "job-2": job2,
            "job-3": job3,
        }
    
    def test_create_graph(self):
        """Test creating a dependency graph."""
        result = self.tracker.create_graph(self.owner_id)
        assert result.success
        
        # Check that the graph was created
        assert self.owner_id in self.tracker.graphs
    
    def test_register_dependency(self):
        """Test registering a dependency between jobs."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependency
        result = self.tracker.register_dependency(
            "job-1",
            "job-2",
            DependencyType.SEQUENTIAL,
        )
        
        assert result.success
        
        # Check that the dependency was added
        graph = self.tracker.graphs[self.owner_id]
        assert graph.has_edge("job-1", "job-2")
        
        # Check the dependency type
        dependency = graph.get_dependency("job-1", "job-2")
        assert dependency.dependency_type == DependencyType.SEQUENTIAL
    
    def test_check_dependency(self):
        """Test checking if a dependency is satisfied."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependency
        self.tracker.register_dependency(
            "job-1",
            "job-2",
            DependencyType.SEQUENTIAL,
        )
        
        # Initially, dependency is not satisfied
        result = self.tracker.check_dependency("job-1", "job-2")
        assert result.success
        assert not result.value
        
        # Update job-1 status to completed
        self.tracker.update_status(self.owner_id, "job-1", JobStatus.COMPLETED)
        
        # Now dependency should be satisfied
        result = self.tracker.check_dependency("job-1", "job-2")
        assert result.success
        assert result.value
    
    def test_update_status(self):
        """Test updating a job's status and propagating changes."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependency
        self.tracker.register_dependency(
            "job-1",
            "job-2",
            DependencyType.SEQUENTIAL,
        )
        
        # Update job-1 to completed
        result = self.tracker.update_status(
            self.owner_id,
            "job-1",
            JobStatus.COMPLETED,
        )
        
        assert result.success
        propagated = result.value
        
        # Check that dependencies are satisfied
        assert "job-2" in propagated
        
        # Check that the dependency from job-1 to job-2 is satisfied
        graph = self.tracker.graphs[self.owner_id]
        dependency = graph.get_dependency("job-1", "job-2")
        assert dependency.is_satisfied()
    
    def test_is_ready_to_run(self):
        """Test checking if a job is ready to run."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependencies
        self.tracker.register_dependency("job-1", "job-2")
        self.tracker.register_dependency("job-2", "job-3")
        
        # Initially, only job-1 is ready
        assert self.tracker.is_ready_to_run(self.owner_id, "job-1", set())
        assert not self.tracker.is_ready_to_run(self.owner_id, "job-2", set())
        assert not self.tracker.is_ready_to_run(self.owner_id, "job-3", set())
        
        # After job-1 is completed, job-2 should be ready
        completed_ids = {"job-1"}
        assert self.tracker.is_ready_to_run(self.owner_id, "job-2", completed_ids)
        assert not self.tracker.is_ready_to_run(self.owner_id, "job-3", completed_ids)
        
        # After job-2 is completed, job-3 should be ready
        completed_ids.add("job-2")
        assert self.tracker.is_ready_to_run(self.owner_id, "job-3", completed_ids)
    
    def test_get_ready_jobs(self):
        """Test getting jobs that are ready to execute."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependencies
        self.tracker.register_dependency("job-1", "job-2")
        self.tracker.register_dependency("job-2", "job-3")
        
        # Initially, only job-1 should be ready
        ready = self.tracker.get_ready_jobs(self.owner_id, set())
        assert "job-1" in ready
        assert len(ready) == 1
        
        # After job-1 is completed, job-2 should be ready
        ready = self.tracker.get_ready_jobs(self.owner_id, {"job-1"})
        assert "job-2" in ready
        assert len(ready) == 1
    
    def test_get_blocking_jobs(self):
        """Test getting jobs that are blocking a specific job."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependencies
        self.tracker.register_dependency("job-1", "job-2")
        self.tracker.register_dependency("job-2", "job-3")
        
        # job-2 is blocked by job-1
        blocking = self.tracker.get_blocking_jobs(self.owner_id, "job-2", set())
        assert "job-1" in blocking
        
        # job-3 is blocked by job-2
        blocking = self.tracker.get_blocking_jobs(self.owner_id, "job-3", set())
        assert "job-2" in blocking
        
        # After job-1 is completed, job-2 should not be blocked
        blocking = self.tracker.get_blocking_jobs(self.owner_id, "job-2", {"job-1"})
        assert not blocking
    
    def test_get_critical_path(self):
        """Test getting the critical path through the owner's workflow."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependencies
        self.tracker.register_dependency("job-1", "job-2")
        self.tracker.register_dependency("job-2", "job-3")
        
        # Get critical path
        path = self.tracker.get_critical_path(self.owner_id)
        
        # The path should include all jobs in correct order
        assert len(path) == 3
        assert path[0] == "job-1"
        assert path[1] == "job-2"
        assert path[2] == "job-3"
    
    def test_bypass_dependency(self):
        """Test manually bypassing a dependency."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependency
        self.tracker.register_dependency("job-1", "job-2")
        
        # Bypass the dependency
        result = self.tracker.bypass_dependency(
            self.owner_id,
            "job-1",
            "job-2",
        )
        
        assert result.success
        
        # Check that the dependency was bypassed (satisfied)
        graph = self.tracker.graphs[self.owner_id]
        dependency = graph.get_dependency("job-1", "job-2")
        assert dependency.is_satisfied()
        
        # Check that the manual override was recorded
        assert (
            "job-1",
            "job-2",
        ) in self.tracker.manual_overrides[self.owner_id]
    
    def test_add_dynamic_dependency(self):
        """Test adding a dynamically discovered dependency at runtime."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add a dynamic dependency from job-1 to job-3
        result = self.tracker.add_dynamic_dependency(
            self.owner_id,
            "job-1",
            "job-3",
            DependencyType.DATA,
        )
        
        assert result.success
        
        # Check that the dependency was added to the graph
        graph = self.tracker.graphs[self.owner_id]
        assert graph.has_edge("job-1", "job-3")
        
        # Check the dependency type
        dependency = graph.get_dependency("job-1", "job-3")
        assert dependency.dependency_type == DependencyType.DATA
    
    def test_get_execution_plan(self):
        """Test generating an execution plan."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependencies
        self.tracker.register_dependency("job-1", "job-2")
        self.tracker.register_dependency("job-2", "job-3")
        
        # Get execution plan
        result = self.tracker.get_execution_plan(self.owner_id)
        assert result.success
        plan = result.value
        
        # The plan should have 3 steps (one for each job)
        assert len(plan) == 3
        
        # Check that the jobs are in the correct order
        assert plan[0] == ["job-1"]
        assert plan[1] == ["job-2"]
        assert plan[2] == ["job-3"]
    
    def test_has_cycle(self):
        """Test checking for cycles in the dependency graph."""
        # Create graph
        self.tracker.create_graph(self.owner_id)
        
        # Add dependencies without cycle
        self.tracker.register_dependency("job-1", "job-2")
        self.tracker.register_dependency("job-2", "job-3")
        
        # Check for cycle - should be None
        result = self.tracker.has_cycle()
        assert result.success
        assert result.value is None
        
        # Manually create a cycle (bypassing checks)
        graph = self.tracker.graphs[self.owner_id]
        graph.graph.add_edge("job-3", "job-1")
        
        # Check for cycle - should detect it
        result = self.tracker.has_cycle()
        assert result.success
        assert result.value is not None
        assert "job-1" in result.value
        assert "job-3" in result.value