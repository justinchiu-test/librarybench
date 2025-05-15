import pytest
from unittest.mock import MagicMock, call
from datetime import datetime, timedelta

from render_farm_manager.core.models import (
    RenderClient,
    RenderNode,
    RenderJob,
    RenderJobStatus,
    ServiceTier,
    NodeType,
    EnergyMode,
    LogLevel,
)
from render_farm_manager.core.manager import RenderFarmManager


@pytest.fixture
def audit_logger():
    return MagicMock()


@pytest.fixture
def performance_metrics():
    return MagicMock()


@pytest.fixture
def farm_manager(audit_logger, performance_metrics):
    """Creates a render farm manager with mocked audit logger and performance metrics."""
    return RenderFarmManager(
        audit_logger=audit_logger,
        performance_metrics=performance_metrics
    )


@pytest.fixture
def client():
    """Creates a test client."""
    return RenderClient(
        client_id="client1",
        name="Test Client",
        service_tier=ServiceTier.PREMIUM,
    )


@pytest.fixture
def render_node():
    """Creates a test render node."""
    return RenderNode(
        node_id="node1",
        name="Test Node",
        node_type=NodeType.GPU,
        cpu_cores=16,
        memory_gb=64,
        gpu_count=2,
    )


@pytest.fixture
def render_job():
    """Creates a test render job."""
    now = datetime.now()
    return RenderJob(
        job_id="job1",
        client_id="client1",
        name="Test Job",
        priority=100,
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=2.0,
        deadline=now + timedelta(hours=4),
    )


def test_audit_logging_completeness(farm_manager, audit_logger, client, render_node, render_job):
    """Test that all important operations are properly logged to the audit logger."""
    # Client operations
    farm_manager.add_client(client)
    farm_manager.update_client_tier(client.client_id, ServiceTier.STANDARD)
    
    # Node operations
    farm_manager.add_node(render_node)
    farm_manager.set_node_online(render_node.node_id, False)
    farm_manager.set_node_online(render_node.node_id, True)
    
    # Set node back online to schedule jobs
    render_node.is_online = True
    
    # Job operations
    farm_manager.submit_job(render_job)
    farm_manager.run_scheduling_cycle()
    farm_manager.update_job_progress(render_job.job_id, 50.0)
    farm_manager.update_job_priority(render_job.job_id, 90)
    farm_manager.complete_job(render_job.job_id)
    
    # System operations
    farm_manager.set_energy_mode(EnergyMode.EFFICIENCY)
    
    # Verify all important operations were logged
    # We should have at least these log calls:
    
    # Client operations logged
    assert audit_logger.log_client_added.call_count == 1
    assert audit_logger.log_client_updated.call_count == 1
    
    # Node operations logged
    assert audit_logger.log_node_added.call_count == 1
    assert audit_logger.log_node_updated.call_count >= 1
    
    # Job operations logged
    assert audit_logger.log_job_submitted.call_count == 1
    assert audit_logger.log_job_scheduled.call_count >= 1
    assert audit_logger.log_job_updated.call_count >= 1
    assert audit_logger.log_job_completed.call_count == 1
    
    # System operations logged
    assert audit_logger.log_energy_mode_changed.call_count == 1
    
    # Scheduling cycle logged
    assert audit_logger.log_scheduling_cycle.call_count >= 1
    
    # Verify log format/content for a few key events
    audit_logger.log_client_added.assert_called_with(
        client_id=client.client_id,
        name=client.name,
        service_tier=ServiceTier.PREMIUM
    )
    
    audit_logger.log_job_submitted.assert_called_with(
        job_id=render_job.job_id,
        client_id=render_job.client_id,
        name=render_job.name,
        priority=render_job.priority
    )
    
    audit_logger.log_energy_mode_changed.assert_called_with(
        old_mode=EnergyMode.BALANCED,  # Default mode
        new_mode=EnergyMode.EFFICIENCY
    )


def test_audit_log_levels(farm_manager, audit_logger, client, render_node, render_job):
    """Test that audit logging respects log level settings."""
    # Setup: configure audit logger with log level filters
    # In a real implementation, we would set log level on the audit logger
    # For this test, we'll assume the behavior and verify the mock calls
    
    # Add client, node, and job
    farm_manager.add_client(client)
    farm_manager.add_node(render_node)
    farm_manager.submit_job(render_job)
    
    # Run operations at different severity levels
    
    # INFO level - normal operations
    farm_manager.run_scheduling_cycle()
    farm_manager.update_job_progress(render_job.job_id, 50.0)
    
    # WARNING level - anomalies
    farm_manager.handle_node_failure(render_node.node_id)
    
    # ERROR level - critical issues
    # Simulate an error condition by calling audit_logger directly 
    # (since RenderFarmManager might not have explicit error scenarios)
    farm_manager.audit_logger.log_error(
        message="Critical error detected in node communication",
        source="NodeCommunicationService",
        severity=LogLevel.ERROR
    )
    
    # Verify calls were made with appropriate log levels
    info_calls = [
        call for call in audit_logger.log_event.call_args_list 
        if call[1].get('log_level', LogLevel.INFO) == LogLevel.INFO
    ]
    
    warning_calls = [
        call for call in audit_logger.log_event.call_args_list 
        if call[1].get('log_level', LogLevel.INFO) == LogLevel.WARNING
    ]
    
    error_calls = [
        call for call in audit_logger.log_event.call_args_list 
        if call[1].get('log_level', LogLevel.INFO) == LogLevel.ERROR
    ]
    
    # There should be calls at all log levels
    assert len(info_calls) > 0, "Expected INFO level audit log entries"
    assert len(warning_calls) > 0, "Expected WARNING level audit log entries"
    assert len(error_calls) > 0, "Expected ERROR level audit log entries"
    
    # Verify node failure was logged as a warning
    audit_logger.log_node_failure.assert_called_with(
        node_id=render_node.node_id
    )


def test_performance_metrics_tracking(farm_manager, performance_metrics, client, render_node, render_job):
    """Test that performance metrics are properly tracked alongside audit logging."""
    # Setup
    farm_manager.add_client(client)
    farm_manager.add_node(render_node)
    farm_manager.submit_job(render_job)
    
    # Run scheduling operations
    farm_manager.run_scheduling_cycle()
    
    # Update job progress and complete it
    farm_manager.update_job_progress(render_job.job_id, 50.0)
    farm_manager.update_job_progress(render_job.job_id, 100.0)
    farm_manager.complete_job(render_job.job_id)
    
    # Verify performance metrics were updated
    assert performance_metrics.update_scheduling_cycle_time.call_count >= 1
    assert performance_metrics.update_job_turnaround_time.call_count >= 1
    assert performance_metrics.update_node_utilization.call_count >= 1
    
    # Verify client metrics
    assert performance_metrics.update_client_job_count.call_count >= 1
    assert performance_metrics.update_client_resource_metrics.call_count >= 1
    
    # Check that metrics are paired with appropriate audit logs
    job_completion_metrics = [
        call for call in performance_metrics.update_job_turnaround_time.call_args_list
        if call[1].get('job_id') == render_job.job_id
    ]
    
    assert len(job_completion_metrics) > 0, "Job completion metrics should be tracked"
    
    # Verify audit logs and metrics work together for a complete picture
    # For scheduling cycles, both should be updated
    assert performance_metrics.update_scheduling_cycle_time.call_count >= audit_logger.log_scheduling_cycle.call_count
    
    # For job completion, both should be updated
    assert performance_metrics.update_job_turnaround_time.call_count >= audit_logger.log_job_completed.call_count