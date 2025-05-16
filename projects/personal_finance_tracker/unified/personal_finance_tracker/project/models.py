"""Project profitability analysis models."""

# Import models directly from common library
from common.core.models.project_metrics import (
    ProjectMetricType,
    ProfitabilityMetric,
    ProjectProfitability,
    ClientProfitability,
    TrendPoint,
    TrendAnalysis
)
from common.core.models.project import (
    Project,
    Client,
    TimeEntry,
    Invoice,
    ProjectStatus,
    BillingType
)
from common.core.models.transaction import BusinessTransaction, TransactionType
