"""
Dependency tracking for the unified concurrent task scheduler.

This module provides functionality for tracking dependencies between jobs and stages
that can be used by both the render farm manager and scientific computing implementations.
"""

from common.dependency_tracking.graph import (
    DependencyGraph,
    DependencyNode,
    GraphNodeType,
)

from common.dependency_tracking.tracker import (
    DependencyTracker,
    TransitionRule,
    TransitionTrigger,
)

from common.dependency_tracking.workflow import (
    WorkflowManager,
    WorkflowTemplate,
    WorkflowTemplateType,
    WorkflowStage,
    WorkflowNodeType,
    WorkflowTransition,
    WorkflowTransitionType,
    WorkflowInstance,
)