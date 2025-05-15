"""Example script showing how to initialize the RenderFarmManager."""

from render_farm_manager.core.manager import RenderFarmManager
from render_farm_manager.scheduling.deadline_scheduler import DeadlineScheduler
from render_farm_manager.resource_management.resource_partitioner import ResourcePartitioner
from render_farm_manager.node_specialization.specialization_manager import NodeSpecializationManager
from render_farm_manager.progressive_result.progressive_renderer import ProgressiveRenderer
from render_farm_manager.energy_optimization.energy_optimizer import EnergyOptimizer
from render_farm_manager.utils.logging import AuditLogger, PerformanceMonitor

# Initialize components
audit_logger = AuditLogger()
performance_monitor = PerformanceMonitor(audit_logger)

# Optional: Initialize components with custom parameters
scheduler = DeadlineScheduler(
    audit_logger=audit_logger,
    performance_monitor=performance_monitor,
    deadline_safety_margin_hours=2.0,
    enable_preemption=True
)

resource_manager = ResourcePartitioner(
    audit_logger=audit_logger,
    performance_monitor=performance_monitor,
    allow_borrowing=True,
    borrowing_limit_percentage=50.0
)

# Initialize RenderFarmManager with default components
manager = RenderFarmManager()

# Or initialize with custom components
custom_manager = RenderFarmManager(
    scheduler=scheduler,
    resource_manager=resource_manager,
    node_specializer=NodeSpecializationManager(audit_logger, performance_monitor),
    progressive_renderer=ProgressiveRenderer(audit_logger, performance_monitor),
    energy_optimizer=EnergyOptimizer(audit_logger, performance_monitor),
    audit_logger=audit_logger,
    performance_monitor=performance_monitor
)

# All parameters are optional - the manager will create defaults for any missing components
partial_custom_manager = RenderFarmManager(
    scheduler=scheduler,
    resource_manager=resource_manager
)