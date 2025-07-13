"""Custom exceptions for K8s resource monitor."""


class K8sResourceMonitorError(Exception):
    """Base exception for K8s resource monitor."""

    pass


class K8sConnectionError(K8sResourceMonitorError):
    """Raised when connection to Kubernetes cluster fails."""

    pass


class MetricsNotAvailableError(K8sResourceMonitorError):
    """Raised when metrics server is not available or metrics cannot be retrieved."""

    pass


class ResourceLimitError(K8sResourceMonitorError):
    """Raised when resource limits are exceeded or invalid."""

    pass


class InvalidConfigurationError(K8sResourceMonitorError):
    """Raised when configuration is invalid."""

    pass


class QuotaExceededError(K8sResourceMonitorError):
    """Raised when namespace quota is exceeded."""

    pass
