"""Kubernetes resource monitoring library for platform engineers."""

from k8s_resource_monitor.monitor import K8sResourceMonitor
from k8s_resource_monitor.models import (
    NamespaceResources,
    NodePressure,
    PodResources,
    ResourceBreach,
    ResourceQuota,
)

__version__ = "0.1.0"
__all__ = [
    "K8sResourceMonitor",
    "NamespaceResources",
    "NodePressure",
    "PodResources",
    "ResourceBreach",
    "ResourceQuota",
]
