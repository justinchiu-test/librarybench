"""PyTemplate - A template rendering engine for automated business report generation."""

from .sql_executor import (
    SQLExecutor,
    MultiSourceExecutor,
    DatabaseConfig,
    QueryResult,
)
from .data_transformer import (
    DataTransformer,
    AggregationType,
    FilterOperator,
    FilterCondition,
    AggregationConfig,
    PivotConfig,
)
from .chart_generator import (
    ChartGenerator,
    ChartType,
    ChartStyle,
    ChartConfig,
)
from .formatting_engine import (
    ConditionalFormatter,
    FormatCondition,
    FormatStyle,
    FormatRule,
)
from .parameter_injector import (
    ParameterInjector,
    ParameterType,
    ParameterDefinition,
    DateRange,
)
from .template_engine import (
    TemplateEngine,
    QueryDefinition,
    ReportSection,
    ReportTemplate,
)

__version__ = "0.1.0"

__all__ = [
    # SQL Executor
    "SQLExecutor",
    "MultiSourceExecutor",
    "DatabaseConfig",
    "QueryResult",
    # Data Transformer
    "DataTransformer",
    "AggregationType",
    "FilterOperator",
    "FilterCondition",
    "AggregationConfig",
    "PivotConfig",
    # Chart Generator
    "ChartGenerator",
    "ChartType",
    "ChartStyle",
    "ChartConfig",
    # Formatting Engine
    "ConditionalFormatter",
    "FormatCondition",
    "FormatStyle",
    "FormatRule",
    # Parameter Injector
    "ParameterInjector",
    "ParameterType",
    "ParameterDefinition",
    "DateRange",
    # Template Engine
    "TemplateEngine",
    "QueryDefinition",
    "ReportSection",
    "ReportTemplate",
]
