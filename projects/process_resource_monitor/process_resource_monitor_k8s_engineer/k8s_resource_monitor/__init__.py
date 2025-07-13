"""Kubernetes resource monitoring library for platform engineers."""

from k8s_resource_monitor.exceptions import (
    K8sConnectionError,
    MetricsNotAvailableError,
    ResourceLimitError,
)
from k8s_resource_monitor.models import (
    HPAMetric,
    NamespaceResources,
    NodePressure,
    PodResources,
    ResourceBreach,
    ResourceQuota,
    ResourceRecommendation,
)
from k8s_resource_monitor.monitor import K8sResourceMonitor

__version__ = "0.1.0"
__all__ = [
    "HPAMetric",
    "K8sConnectionError",
    "K8sResourceMonitor",
    "MetricsNotAvailableError",
    "NamespaceResources",
    "NodePressure",
    "PodResources",
    "ResourceBreach",
    "ResourceLimitError",
    "ResourceQuota",
    "ResourceRecommendation",
]
