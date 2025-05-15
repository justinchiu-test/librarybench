"""Tests for the checkpoint manager module."""

import os
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from concurrent_task_scheduler.failure_resilience.checkpoint_manager import (
    CheckpointManager,
    CheckpointCoordinator,
    ValidationResult,
    CheckpointCreationStrategy,
)

from concurrent_task_scheduler.models import (
    Checkpoint,
    CheckpointCompression,
    CheckpointMetadata,
    CheckpointPolicy,
    CheckpointStatus,
    CheckpointStorageType,
    CheckpointType,
    Simulation,
    SimulationStage,
    SimulationStageStatus,
    SimulationPriority,
    SimulationStatus,
    Result,
)


class TestCheckpointManager:
    """Tests for the CheckpointManager class."""

    @pytest.fixture
    def temp_checkpoint_dir(self):
        """Create a temporary directory for checkpoint files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def checkpoint_manager(self, temp_checkpoint_dir):
        """Create a checkpoint manager instance."""
        manager = CheckpointManager(temp_checkpoint_dir)
        yield manager
        manager.cleanup()

    @pytest.fixture
    def mock_simulation(self):
        """Create a mock simulation for testing."""
        sim = Simulation(
            id="sim-123",
            name="Test Simulation",
            description="A test simulation",
            status=SimulationStatus.RUNNING,
            priority=SimulationPriority.HIGH,
        )
        
        # Add a stage
        stage = SimulationStage(
            id="stage-1",
            name="Processing Stage",
            status=SimulationStageStatus.RUNNING,
            progress=0.5,
            estimated_duration=timedelta(hours=2),
        )
        sim.stages = {"stage-1": stage}
        
        # Mock the total_progress method
        sim.total_progress = lambda: 0.5
        
        return sim

    def test_register_policy(self, checkpoint_manager):
        """Test registering a checkpoint policy."""
        policy = CheckpointPolicy(
            name="Test Policy",
            description="A test policy",
            checkpoint_type=CheckpointType.FULL,
            storage_type=CheckpointStorageType.PARALLEL_FS,
            compression=CheckpointCompression.ZSTD,
            frequency_minutes=30,
        )
        
        policy_id = checkpoint_manager.register_policy(policy)
        assert policy_id == "test_policy"
        assert checkpoint_manager.policies[policy_id] == policy

    def test_get_default_policy(self, checkpoint_manager):
        """Test getting the default policy."""
        policy = checkpoint_manager.get_default_policy()
        
        assert policy.name == "Default"
        assert policy.description == "Default checkpoint policy"
        assert policy.checkpoint_type == CheckpointType.FULL
        assert policy.storage_type == CheckpointStorageType.PARALLEL_FS
        assert policy.compression == CheckpointCompression.ZSTD
        assert policy.frequency_minutes == 60
        assert policy.min_progress_delta == 0.05

    def test_create_manager_for_simulation(self, checkpoint_manager):
        """Test creating a checkpoint manager for a simulation."""
        result = checkpoint_manager.create_manager_for_simulation("sim-123")
        
        assert result.success is True
        manager = result.value
        
        assert manager.simulation_id == "sim-123"
        assert manager.checkpoint_policy.name == "Default"
        assert os.path.exists(os.path.join(checkpoint_manager.base_storage_path, "sim-123"))
        
        # Try to create another manager for the same simulation
        result2 = checkpoint_manager.create_manager_for_simulation("sim-123")
        assert result2.success is False
        assert "already exists" in result2.error

    def test_update_policy(self, checkpoint_manager):
        """Test updating a checkpoint policy for a simulation."""
        # First register a policy and create a manager
        policy = CheckpointPolicy(
            name="Updated Policy",
            description="An updated policy",
            checkpoint_type=CheckpointType.INCREMENTAL,
            storage_type=CheckpointStorageType.LOCAL,
            compression=CheckpointCompression.GZIP,
            frequency_minutes=15,
        )
        policy_id = checkpoint_manager.register_policy(policy)
        
        checkpoint_manager.create_manager_for_simulation("sim-123")
        
        # Now update the policy
        result = checkpoint_manager.update_policy("sim-123", policy_id)
        assert result.success is True
        
        # Check if policy was updated
        assert checkpoint_manager.simulation_managers["sim-123"].checkpoint_policy == policy
        
        # Test with non-existent simulation
        result = checkpoint_manager.update_policy("nonexistent", policy_id)
        assert result.success is False
        assert "No checkpoint manager found" in result.error
        
        # Test with non-existent policy
        result = checkpoint_manager.update_policy("sim-123", "nonexistent")
        assert result.success is False
        assert "Policy nonexistent not found" in result.error

    def test_should_create_checkpoint(self, checkpoint_manager, mock_simulation):
        """Test determining if a checkpoint should be created."""
        # Initially, should create (no previous checkpoints)
        assert checkpoint_manager.should_create_checkpoint(mock_simulation) is True
        
        # Create a manager with policy set to frequent checkpoints
        policy = CheckpointPolicy(
            name="Frequent",
            checkpoint_type=CheckpointType.FULL,
            frequency_minutes=1,  # Every minute
            min_progress_delta=0.01,  # Small progress change
        )
        policy_id = checkpoint_manager.register_policy(policy)
        checkpoint_manager.create_manager_for_simulation(mock_simulation.id)
        checkpoint_manager.update_policy(mock_simulation.id, policy_id)
        
        # Still should create since no checkpoints yet
        assert checkpoint_manager.should_create_checkpoint(mock_simulation) is True

    def test_create_checkpoint(self, checkpoint_manager, mock_simulation):
        """Test creating a checkpoint."""
        # Create a checkpoint
        result = checkpoint_manager.create_checkpoint(mock_simulation)
        
        assert result.success is True
        checkpoint = result.value
        
        # Verify checkpoint
        assert checkpoint.status == CheckpointStatus.COMPLETE
        assert checkpoint.metadata.simulation_id == mock_simulation.id
        assert checkpoint.metadata.simulation_name == mock_simulation.name
        assert checkpoint.metadata.progress_at_checkpoint == 0.5
        assert checkpoint.validation_hash is not None
        assert os.path.exists(checkpoint.path)
        
        # Verify files
        assert os.path.exists(os.path.join(checkpoint.path, "metadata.json"))
        assert os.path.exists(os.path.join(checkpoint.path, "simulation.json"))
        assert os.path.exists(os.path.join(checkpoint.path, "data.bin"))
        
        # Create a stage-specific checkpoint
        result = checkpoint_manager.create_checkpoint(mock_simulation, stage_id="stage-1")
        
        assert result.success is True
        checkpoint = result.value
        
        # Verify stage-specific data
        assert checkpoint.metadata.stage_id == "stage-1"
        assert checkpoint.metadata.stage_name == "Processing Stage"
        assert os.path.exists(os.path.join(checkpoint.path, "stage_stage-1.json"))

    def test_validate_checkpoint(self, checkpoint_manager, mock_simulation):
        """Test validating a checkpoint."""
        # Create a checkpoint
        result = checkpoint_manager.create_checkpoint(mock_simulation)
        assert result.success is True
        checkpoint = result.value
        
        # Validate checkpoint
        validation_result = checkpoint_manager.validate_checkpoint(checkpoint.id, mock_simulation.id)
        assert validation_result == ValidationResult.VALID
        
        # Test validation of non-existent checkpoint
        validation_result = checkpoint_manager.validate_checkpoint("nonexistent", mock_simulation.id)
        assert validation_result == ValidationResult.MISSING
        
        # Tamper with the checkpoint to make it incomplete
        incomplete_path = os.path.join(checkpoint.path, "metadata.json")
        os.remove(incomplete_path)
        
        # Now it should be incomplete
        validation_result = checkpoint_manager.validate_checkpoint(checkpoint.id, mock_simulation.id)
        assert validation_result == ValidationResult.INCOMPLETE
        
        # Restore for further tests
        with open(incomplete_path, "w") as f:
            f.write("{}")
            
        # Tamper with the validation hash to make it corrupted
        checkpoint.validation_hash = "invalid_hash"
        
        # Now it should be corrupted
        validation_result = checkpoint_manager.validate_checkpoint(checkpoint.id, mock_simulation.id)
        assert validation_result == ValidationResult.CORRUPTED

    def test_get_latest_checkpoint(self, checkpoint_manager, mock_simulation):
        """Test getting the latest checkpoint."""
        # Initially no checkpoints
        latest = checkpoint_manager.get_latest_checkpoint(mock_simulation.id)
        assert latest is None
        
        # Create a checkpoint
        result = checkpoint_manager.create_checkpoint(mock_simulation)
        assert result.success is True
        checkpoint1 = result.value
        
        # Verify latest checkpoint
        latest = checkpoint_manager.get_latest_checkpoint(mock_simulation.id)
        assert latest is not None
        assert latest.id == checkpoint1.id
        
        # Create another checkpoint
        result = checkpoint_manager.create_checkpoint(mock_simulation)
        assert result.success is True
        checkpoint2 = result.value
        
        # Verify new latest checkpoint
        latest = checkpoint_manager.get_latest_checkpoint(mock_simulation.id)
        assert latest is not None
        assert latest.id == checkpoint2.id
        
        # Test for specific stage
        result = checkpoint_manager.create_checkpoint(mock_simulation, stage_id="stage-1")
        assert result.success is True
        stage_checkpoint = result.value
        
        latest_stage = checkpoint_manager.get_latest_checkpoint(mock_simulation.id, stage_id="stage-1")
        assert latest_stage is not None
        assert latest_stage.id == stage_checkpoint.id

    def test_get_all_checkpoints(self, checkpoint_manager, mock_simulation):
        """Test getting all checkpoints."""
        # Initially no checkpoints
        checkpoints = checkpoint_manager.get_all_checkpoints(mock_simulation.id)
        assert len(checkpoints) == 0
        
        # Create checkpoints
        checkpoint_manager.create_checkpoint(mock_simulation)
        checkpoint_manager.create_checkpoint(mock_simulation)
        checkpoint_manager.create_checkpoint(mock_simulation, stage_id="stage-1")
        
        # Get all checkpoints
        all_checkpoints = checkpoint_manager.get_all_checkpoints(mock_simulation.id)
        assert len(all_checkpoints) == 3
        
        # Get stage-specific checkpoints
        stage_checkpoints = checkpoint_manager.get_all_checkpoints(mock_simulation.id, stage_id="stage-1")
        assert len(stage_checkpoints) == 1
        assert stage_checkpoints[0].metadata.stage_id == "stage-1"

    def test_restore_from_checkpoint(self, checkpoint_manager, mock_simulation):
        """Test restoring from a checkpoint."""
        # Create a checkpoint
        result = checkpoint_manager.create_checkpoint(mock_simulation)
        assert result.success is True
        checkpoint = result.value
        
        # Restore from the checkpoint
        result = checkpoint_manager.restore_from_checkpoint(checkpoint.id, mock_simulation.id)
        assert result.success is True
        
        # Verify restore count was updated
        assert checkpoint.restore_count == 1
        assert checkpoint.last_restore_time is not None
        
        # Attempt to restore from non-existent checkpoint
        result = checkpoint_manager.restore_from_checkpoint("nonexistent", mock_simulation.id)
        assert result.success is False
        assert "not found" in result.error
        
        # Tamper with the checkpoint to make it invalid
        checkpoint.status = CheckpointStatus.CORRUPTED
        
        # Attempt to restore from invalid checkpoint
        result = checkpoint_manager.restore_from_checkpoint(checkpoint.id, mock_simulation.id)
        assert result.success is False
        assert "invalid checkpoint" in result.error

    def test_archive_checkpoint(self, checkpoint_manager, mock_simulation):
        """Test archiving a checkpoint."""
        # Create a checkpoint
        result = checkpoint_manager.create_checkpoint(mock_simulation)
        assert result.success is True
        checkpoint = result.value
        
        # Archive the checkpoint
        result = checkpoint_manager.archive_checkpoint(checkpoint.id, mock_simulation.id)
        assert result.success is True
        archive_path = result.value
        
        # Verify status was updated
        assert checkpoint.status == CheckpointStatus.ARCHIVED
        
        # Archive path should point to archives directory
        assert "archives" in archive_path
        assert mock_simulation.id in archive_path
        assert checkpoint.id in archive_path


class TestCheckpointCoordinator:
    """Tests for the CheckpointCoordinator class."""

    @pytest.fixture
    def temp_checkpoint_dir(self):
        """Create a temporary directory for checkpoint files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def checkpoint_manager(self, temp_checkpoint_dir):
        """Create a checkpoint manager instance."""
        manager = CheckpointManager(temp_checkpoint_dir)
        yield manager
        manager.cleanup()

    @pytest.fixture
    def checkpoint_coordinator(self, checkpoint_manager):
        """Create a checkpoint coordinator instance."""
        coordinator = CheckpointCoordinator(checkpoint_manager)
        return coordinator

    @pytest.fixture
    def mock_simulations(self):
        """Create mock simulations for testing."""
        simulations = {}
        
        for i in range(3):
            sim = Simulation(
                id=f"sim-{i}",
                name=f"Test Simulation {i}",
                description=f"A test simulation {i}",
                status=SimulationStatus.RUNNING,
                priority=SimulationPriority.HIGH,
            )
            
            # Mock the total_progress method
            sim.total_progress = lambda: 0.5
            
            simulations[f"sim-{i}"] = sim
        
        return simulations

    def test_schedule_checkpoint(self, checkpoint_coordinator):
        """Test scheduling a checkpoint."""
        # Schedule a checkpoint
        checkpoint_coordinator.schedule_checkpoint("sim-123")
        
        # Verify it was scheduled
        assert "sim-123" in checkpoint_coordinator.scheduled_checkpoints
        
        # Schedule with specific time
        future_time = datetime.now() + timedelta(minutes=30)
        checkpoint_coordinator.schedule_checkpoint("sim-456", future_time)
        
        # Verify it was scheduled with correct time
        assert "sim-456" in checkpoint_coordinator.scheduled_checkpoints
        assert checkpoint_coordinator.scheduled_checkpoints["sim-456"] == future_time

    def test_process_scheduled_checkpoints(self, checkpoint_coordinator, checkpoint_manager, mock_simulations):
        """Test processing scheduled checkpoints."""
        # Create checkpoint manager for each simulation
        for sim_id in mock_simulations.keys():
            checkpoint_manager.create_manager_for_simulation(sim_id)
        
        # Schedule immediate checkpoints
        for sim_id in mock_simulations.keys():
            checkpoint_coordinator.schedule_checkpoint(sim_id)
        
        # Process scheduled checkpoints
        created = checkpoint_coordinator.process_scheduled_checkpoints(mock_simulations)
        
        # We should have created checkpoints for all simulations (up to max_concurrent)
        assert len(created) <= checkpoint_coordinator.max_concurrent_checkpoints
        assert all(sim_id in mock_simulations for sim_id in created)
        
        # These simulations should now have checkpoints
        for sim_id in created:
            assert sim_id in checkpoint_coordinator.last_checkpoint_time
        
        # Schedule should be cleared for these
        for sim_id in created:
            assert sim_id not in checkpoint_coordinator.scheduled_checkpoints

    def test_checkpoint_priority(self, checkpoint_coordinator, checkpoint_manager, mock_simulations):
        """Test checkpoint prioritization."""
        # Create manager for each simulation
        for sim_id in mock_simulations.keys():
            checkpoint_manager.create_manager_for_simulation(sim_id)
        
        # Set up different last checkpoint times
        now = datetime.now()
        checkpoint_coordinator.last_checkpoint_time = {
            "sim-0": now - timedelta(hours=1),  # 1 hour ago
            "sim-1": now - timedelta(hours=12),  # 12 hours ago
            "sim-2": None,  # Never checkpointed (highest priority)
        }
        
        # Schedule all checkpoints
        for sim_id in mock_simulations.keys():
            checkpoint_coordinator.schedule_checkpoint(sim_id)
        
        # Process scheduled checkpoints
        created = checkpoint_coordinator.process_scheduled_checkpoints(mock_simulations)
        
        # Verify order of priority
        if len(created) >= 3:
            assert "sim-2" in created  # Never checkpointed should be first
            
            # Of the remaining two, sim-1 should be before sim-0
            if "sim-0" in created and "sim-1" in created:
                sim1_idx = created.index("sim-1")
                sim0_idx = created.index("sim-0")
                assert sim1_idx < sim0_idx  # Lower index = higher priority
    
    def test_should_checkpoint_simulation(self, checkpoint_coordinator, checkpoint_manager, mock_simulations):
        """Test determining if a simulation should be checkpointed."""
        sim = mock_simulations["sim-0"]
        
        # First, it shouldn't be scheduled
        assert sim.id not in checkpoint_coordinator.scheduled_checkpoints
        
        # So check should return whether the manager says we should
        with patch.object(checkpoint_manager, 'should_create_checkpoint', return_value=True):
            assert checkpoint_coordinator.should_checkpoint_simulation(sim) is True
            
        with patch.object(checkpoint_manager, 'should_create_checkpoint', return_value=False):
            assert checkpoint_coordinator.should_checkpoint_simulation(sim) is False
        
        # If it's already scheduled, should always return False
        checkpoint_coordinator.scheduled_checkpoints[sim.id] = datetime.now()
        assert checkpoint_coordinator.should_checkpoint_simulation(sim) is False