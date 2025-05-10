"""
Unit tests for experimentation framework.
"""

import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pytest
from pytest import approx

from feature_store.experimentation.assignment import (
    AssignmentStrategy, AssignmentType, HashModAssignment,
    ListBasedAssignment, PercentageAssignment
)
from feature_store.experimentation.consistent_hash import ConsistentHash
from feature_store.experimentation.experiment import (
    Experiment, ExperimentGroup, ExperimentStatus
)


class TestConsistentHash:
    """Tests for ConsistentHash class."""

    def test_bucket_assignment(self):
        """Test consistent bucket assignment."""
        # Create hash with 100 buckets
        hash_obj = ConsistentHash(num_buckets=100, hash_seed=42)
        
        # Get bucket for a key
        bucket1 = hash_obj.get_bucket("user_1")
        
        # Should be deterministic
        bucket1_again = hash_obj.get_bucket("user_1")
        assert bucket1 == bucket1_again
        
        # Different keys should (usually) get different buckets
        bucket2 = hash_obj.get_bucket("user_2")
        # Note: There's a small chance these could be the same by random chance
        
        # Get normalized value
        norm_value = hash_obj.get_bucket_normalized("user_1")
        assert 0 <= norm_value < 1.0
        
        # Check range inclusion
        assert hash_obj.is_in_range("user_1", 0.0, 1.0)
        
        # More specific range check
        in_first_half = hash_obj.is_in_range("user_1", 0.0, 0.5)
        in_second_half = hash_obj.is_in_range("user_1", 0.5, 1.0)
        assert in_first_half != in_second_half  # Must be in exactly one half
    
    def test_bucket_distribution(self):
        """Test distribution of keys across buckets."""
        # Create hash with 10 buckets
        hash_obj = ConsistentHash(num_buckets=10, hash_seed=42)
        
        # Create 1000 test keys
        keys = [f"user_{i}" for i in range(1000)]
        
        # Get distribution
        distribution = hash_obj.get_bucket_distribution(keys)
        
        # Should have entries for all buckets
        assert len(distribution) == 10
        assert set(distribution.keys()) == set(range(10))
        
        # Sum should equal number of keys
        assert sum(distribution.values()) == 1000
        
        # Should be roughly even distribution (within reasonable bounds)
        expected_per_bucket = 1000 / 10
        for count in distribution.values():
            # Allow 30% deviation from expected value
            assert count >= expected_per_bucket * 0.7
            assert count <= expected_per_bucket * 1.3
    
    def test_adding_buckets(self):
        """Test adding buckets while maintaining consistency."""
        # Create hash with 10 buckets
        hash_obj = ConsistentHash(num_buckets=10, hash_seed=42)
        
        # Create test keys
        keys = [f"user_{i}" for i in range(100)]
        
        # Record initial assignments
        initial_assignments = {key: hash_obj.get_bucket(key) for key in keys}
        
        # Update to 15 buckets
        hash_obj.update_num_buckets(15)
        
        # Record new assignments
        new_assignments = {key: hash_obj.get_bucket(key) for key in keys}
        
        # Count how many keys kept the same bucket
        kept_same = sum(1 for key in keys 
                     if initial_assignments[key] == new_assignments[key])
        
        # With consistent hashing, many keys should keep their original bucket
        # The exact percentage depends on implementation, but should be substantial
        assert kept_same >= 50  # At least 50% kept same bucket
    
    def test_percentage_based_setup(self):
        """Test percentage-based assignment setup."""
        # Create hash
        hash_obj = ConsistentHash(num_buckets=100, hash_seed=42)
        
        # Set up percentage-based assignment
        percentages = [0.1, 0.2, 0.3, 0.4]
        ranges = hash_obj.setup_percentage_based(percentages)
        
        # Verify ranges
        assert len(ranges) == 4
        assert ranges[0] == (0.0, 0.1)
        assert ranges[1] == (0.1, 0.3)
        assert ranges[2] == (0.3, 0.6)
        assert ranges[3] == (0.6, 1.0)
        
        # Test group assignment
        # Create 1000 test keys
        keys = [f"user_{i}" for i in range(1000)]
        
        # Assign keys to groups
        assignments = [hash_obj.get_group_for_ranges(key, ranges) for key in keys]
        
        # Count assignments
        counts = [assignments.count(i) for i in range(4)]
        
        # Verify roughly correct proportions
        assert counts[0] / 1000 == approx(0.1, abs=0.02)
        assert counts[1] / 1000 == approx(0.2, abs=0.02)
        assert counts[2] / 1000 == approx(0.3, abs=0.02)
        assert counts[3] / 1000 == approx(0.4, abs=0.02)


class TestAssignmentStrategies:
    """Tests for assignment strategies."""

    def test_percentage_assignment(self):
        """Test percentage-based assignment strategy."""
        # Create assignment
        groups = ["control", "test_a", "test_b"]
        weights = [0.6, 0.3, 0.1]
        
        assignment = PercentageAssignment(
            groups=groups,
            weights=weights,
            hash_seed=42
        )
        
        # Verify assignment type
        assert assignment.assignment_type == AssignmentType.PERCENTAGE
        
        # Create 1000 test keys
        keys = [f"user_{i}" for i in range(1000)]
        
        # Assign keys to groups
        assignments = [assignment.assign(key) for key in keys]
        
        # Count assignments
        counts = {group: assignments.count(group) for group in groups}
        
        # Verify roughly correct proportions
        assert counts["control"] / 1000 == approx(0.6, abs=0.03)
        assert counts["test_a"] / 1000 == approx(0.3, abs=0.03)
        assert counts["test_b"] / 1000 == approx(0.1, abs=0.03)
        
        # Test group membership check
        for key in keys[:10]:
            group = assignment.assign(key)
            assert assignment.is_in_group(key, group)
            for other_group in groups:
                if other_group != group:
                    assert not assignment.is_in_group(key, other_group)
        
        # Test updating weights
        new_weights = [0.5, 0.25, 0.25]
        assignment.update_weights(new_weights)
        
        # Re-assign keys
        new_assignments = [assignment.assign(key) for key in keys]
        
        # Count new assignments
        new_counts = {group: new_assignments.count(group) for group in groups}
        
        # Verify new proportions
        assert new_counts["control"] / 1000 == approx(0.5, abs=0.03)
        assert new_counts["test_a"] / 1000 == approx(0.25, abs=0.03)
        assert new_counts["test_b"] / 1000 == approx(0.25, abs=0.03)
    
    def test_hash_mod_assignment(self):
        """Test hash modulo assignment strategy."""
        # Create assignment
        groups = ["group_a", "group_b", "group_c"]
        
        assignment = HashModAssignment(
            groups=groups,
            hash_seed=42
        )
        
        # Verify assignment type
        assert assignment.assignment_type == AssignmentType.HASH_MOD
        
        # Create 1000 test keys
        keys = [f"user_{i}" for i in range(1000)]
        
        # Assign keys to groups
        assignments = [assignment.assign(key) for key in keys]
        
        # Count assignments
        counts = {group: assignments.count(group) for group in groups}
        
        # Should be roughly even distribution
        for group in groups:
            assert counts[group] / 1000 == approx(1/3, abs=0.05)
        
        # Test group membership check
        for key in keys[:10]:
            group = assignment.assign(key)
            assert assignment.is_in_group(key, group)
            for other_group in groups:
                if other_group != group:
                    assert not assignment.is_in_group(key, other_group)
        
        # Adding salt should change assignments
        salted_assignment = HashModAssignment(
            groups=groups,
            salt="experiment_1",
            hash_seed=42
        )
        
        # Assign keys with salted assignment
        salted_assignments = [salted_assignment.assign(key) for key in keys[:10]]
        
        # At least some assignments should differ
        assert any(a != b for a, b in zip(assignments[:10], salted_assignments))
    
    def test_list_based_assignment(self):
        """Test list-based assignment strategy."""
        # Create key lists
        key_lists = {
            "group_a": set([f"user_{i}" for i in range(10)]),
            "group_b": set([f"user_{i}" for i in range(10, 20)]),
            "group_c": set([f"user_{i}" for i in range(20, 30)])
        }
        
        # Create assignment
        assignment = ListBasedAssignment(
            groups=["group_a", "group_b", "group_c"],
            key_lists=key_lists,
            default_group="group_a"
        )
        
        # Verify assignment type
        assert assignment.assignment_type == AssignmentType.LIST_BASED
        
        # Test assignments
        assert assignment.assign("user_5") == "group_a"
        assert assignment.assign("user_15") == "group_b"
        assert assignment.assign("user_25") == "group_c"
        
        # Test default group
        assert assignment.assign("user_100") == "group_a"
        
        # Test group membership
        assert assignment.is_in_group("user_5", "group_a")
        assert not assignment.is_in_group("user_5", "group_b")
        
        # Test modifying lists
        assignment.add_key_to_group("user_100", "group_b")
        assert assignment.assign("user_100") == "group_b"
        
        # Test removing
        assert assignment.remove_key_from_group("user_5", "group_a")
        with pytest.raises(ValueError):
            assignment.assign("user_5")  # No longer in any group, no default


class TestExperiment:
    """Tests for Experiment class."""

    def test_experiment_creation_and_assignment(self):
        """Test creating experiments and assigning keys to groups."""
        # Create percentage-based experiment
        groups = ["control", "treatment"]
        weights = [0.7, 0.3]
        
        experiment = Experiment.create_percentage_based(
            name="test_experiment",
            groups=groups,
            weights=weights,
            description="A test experiment",
            metadata={"owner": "test_user"}
        )
        
        # Verify experiment properties
        assert experiment.name == "test_experiment"
        assert experiment.description == "A test experiment"
        assert experiment.groups == groups
        assert experiment.metadata["owner"] == "test_user"
        assert experiment.status == ExperimentStatus.DRAFT
        
        # Activate experiment
        experiment.activate()
        assert experiment.status == ExperimentStatus.ACTIVE
        
        # Assign keys to groups
        keys = [f"user_{i}" for i in range(100)]
        assignments = {key: experiment.get_group(key) for key in keys}
        
        # Verify assignment distribution
        control_count = list(assignments.values()).count("control")
        treatment_count = list(assignments.values()).count("treatment")
        
        assert control_count / 100 == approx(0.7, abs=0.1)
        assert treatment_count / 100 == approx(0.3, abs=0.1)
        
        # Test is_in_group
        for key, group in assignments.items():
            assert experiment.is_in_group(key, group)
            assert not experiment.is_in_group(key, "control" if group == "treatment" else "treatment")
    
    def test_experiment_lifecycle(self):
        """Test experiment lifecycle (activate, pause, complete, archive)."""
        # Create experiment
        experiment = Experiment.create_hash_based(
            name="lifecycle_test",
            groups=["A", "B"]
        )
        
        # Verify initial status
        assert experiment.status == ExperimentStatus.DRAFT
        
        # Test lifecycle transitions
        experiment.activate()
        assert experiment.status == ExperimentStatus.ACTIVE
        
        experiment.pause()
        assert experiment.status == ExperimentStatus.PAUSED
        
        experiment.activate()  # Can reactivate
        assert experiment.status == ExperimentStatus.ACTIVE
        
        experiment.complete()
        assert experiment.status == ExperimentStatus.COMPLETED
        
        experiment.archive()
        assert experiment.status == ExperimentStatus.ARCHIVED
        
        # Cannot get group for non-active experiment
        with pytest.raises(RuntimeError):
            experiment.get_group("user_1")
    
    def test_experiment_state_serialization(self):
        """Test state serialization and deserialization."""
        # Create experiment
        original = Experiment.create_percentage_based(
            name="serialization_test",
            groups=["X", "Y", "Z"],
            weights=[0.5, 0.3, 0.2],
            description="Test serialization",
            metadata={"purpose": "testing"}
        )
        original.activate()
        
        # Get state dict
        state = original.get_state_dict()
        
        # Verify state contains expected keys
        assert "name" in state
        assert "groups" in state
        assert "status" in state
        assert "weights" in state
        
        # Create from state
        recreated = Experiment.from_state_dict(state)
        
        # Verify recreated experiment
        assert recreated.name == original.name
        assert recreated.groups == original.groups
        assert recreated.status == original.status
        assert recreated.description == original.description
        assert recreated.metadata == original.metadata
        
        # Verify same group assignments
        test_keys = [f"user_{i}" for i in range(10)]
        for key in test_keys:
            assert recreated.get_group(key) == original.get_group(key)
    
    def test_experiment_group(self):
        """Test experiment groups."""
        # Create experiment group
        group = ExperimentGroup(
            name="test_group",
            description="A group of experiments",
            metadata={"domain": "recommendations"}
        )
        
        # Add experiments
        group.add_experiment("exp1")
        group.add_experiment("exp2")
        
        # Verify experiments
        assert "exp1" in group.experiments
        assert "exp2" in group.experiments
        
        # Remove experiment
        assert group.remove_experiment("exp1")
        assert "exp1" not in group.experiments
        assert "exp2" in group.experiments
        
        # Update metadata
        group.update_metadata({"priority": "high"})
        assert group.metadata["domain"] == "recommendations"
        assert group.metadata["priority"] == "high"
        
        # Update description
        group.update_description("Updated description")
        assert group.description == "Updated description"