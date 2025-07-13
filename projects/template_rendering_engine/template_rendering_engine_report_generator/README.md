# PyTemplate - Business Report Generation Engine

PyTemplate is a powerful template rendering engine designed for creating automated business reports from data warehouse sources. It features comprehensive data transformation capabilities, visualization support, and conditional formatting for business analysts.

## Overview

PyTemplate provides a complete solution for generating data-driven reports by:
- Executing SQL queries against multiple data sources with connection pooling
- Transforming data with aggregation, filtering, and pivot table generation
- Creating charts and visualizations using matplotlib/seaborn
- Applying conditional formatting based on data values
- Supporting parameterized reports with runtime parameter injection

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage Examples

### Basic Report Generation

```python
from src import (
    TemplateEngine,
    DatabaseConfig,
    ReportTemplate,
    QueryDefinition,
    ReportSection,
    ParameterDefinition,
    ParameterType,
)

# Initialize the template engine
engine = TemplateEngine()

# Add data sources
warehouse_config = DatabaseConfig(
    connection_string="postgresql://user:pass@localhost/warehouse",
    pool_size=10
)
engine.add_data_source("warehouse", warehouse_config)

# Define report parameters
parameters = [
    ParameterDefinition(
        name="start_date",
        type=ParameterType.DATE,
        description="Report start date",
        required=True
    ),
    ParameterDefinition(
        name="min_amount",
        type=ParameterType.FLOAT,
        description="Minimum transaction amount",
        default=100.0
    )
]

# Define queries
queries = [
    QueryDefinition(
        name="sales_summary",
        source="warehouse",
        query="""
            SELECT 
                category,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM sales
            WHERE date >= :start_date
                AND amount >= :min_amount
            GROUP BY category
        """
    )
]

# Define report sections
sections = [
    ReportSection(
        name="summary",
        template="""
            <h2>Sales Summary Report</h2>
            <p>Report Date: {{start_date}}</p>
            <p>Minimum Amount Filter: {{min_amount | currency}}</p>
            {{tables.summary_sales_summary | safe}}
        """,
        queries=["sales_summary"],
        order=1
    )
]

# Create report template
template = ReportTemplate(
    name="Monthly Sales Report",
    description="Monthly sales analysis by category",
    parameters=parameters,
    queries=queries,
    sections=sections
)

# Generate report
report_params = {
    "start_date": "2024-01-01",
    "min_amount": 500.0
}

html_report = engine.render_report(
    template,
    report_params,
    output_path="reports/sales_report.html"
)
```

### Data Transformation Example

```python
from src import (
    DataTransformer,
    FilterCondition,
    FilterOperator,
    AggregationConfig,
    AggregationType,
    PivotConfig,
)

# Create transformer
transformer = DataTransformer()

# Filter data
conditions = [
    FilterCondition(
        column="amount",
        operator=FilterOperator.GREATER_THAN,
        value=1000
    ),
    FilterCondition(
        column="status",
        operator=FilterOperator.IN,
        value=["completed", "pending"]
    )
]
filtered_df = transformer.filter_data(df, conditions, logic="AND")

# Aggregate data
agg_config = AggregationConfig(
    group_by=["category", "region"],
    aggregations={
        "amount": [AggregationType.SUM, AggregationType.AVERAGE],
        "quantity": AggregationType.COUNT
    }
)
aggregated_df = transformer.aggregate_data(df, agg_config)

# Create pivot table
pivot_config = PivotConfig(
    index="category",
    columns="month",
    values="amount",
    aggfunc="sum",
    fill_value=0
)
pivot_df = transformer.create_pivot_table(df, pivot_config)
```

### Chart Generation Example

```python
from src import ChartGenerator, ChartConfig, ChartType, ChartStyle

# Create chart generator
generator = ChartGenerator()

# Configure chart
chart_config = ChartConfig(
    chart_type=ChartType.BAR,
    x_column="category",
    y_column="total_amount",
    style=ChartStyle(
        title="Sales by Category",
        x_label="Product Category",
        y_label="Total Sales ($)",
        color_palette="Set2",
        width=12,
        height=6
    ),
    sort_by="total_amount",
    sort_ascending=False,
    top_n=10
)

# Generate chart (returns base64-encoded image)
chart_image = generator.generate_chart(df, chart_config)
```

### Conditional Formatting Example

```python
from src import (
    ConditionalFormatter,
    FormatRule,
    FormatCondition,
    FormatStyle,
)

# Create formatter
formatter = ConditionalFormatter()

# Define formatting rules
rules = [
    FormatRule(
        column="total_amount",
        condition=FormatCondition.GREATER_THAN,
        value=10000,
        style=FormatStyle(
            background_color="#4CAF50",
            text_color="white",
            font_weight="bold"
        ),
        priority=10
    ),
    FormatRule(
        column="growth_rate",
        condition=FormatCondition.LESS_THAN,
        value=0,
        style=FormatStyle(
            background_color="#f44336",
            text_color="white"
        ),
        priority=5
    )
]

# Apply formatting
formatted_html = formatter.apply_rules(df, rules, output_format="html")
```

### Parameter Injection Example

```python
from src import ParameterInjector, DateRange

# Create injector
injector = ParameterInjector()

# Register parameters
injector.register_parameter(ParameterDefinition(
    name="date_range",
    type=ParameterType.DATE_RANGE,
    description="Report date range"
))

# Inject parameters into template
template = "SELECT * FROM orders WHERE {{date_range}}"
params = {
    "date_range": DateRange(
        start=date(2024, 1, 1),
        end=date(2024, 1, 31)
    )
}

# Special parameters are automatically available
template = "Report generated on {{today}} for {{last_month}}"
result = injector.inject_parameters(template, {})
```

## Running Tests

To run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-json-report

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Generate JSON report (required for validation)
pytest --json-report --json-report-file=pytest_results.json
```

## Key Features

### SQL Query Integration
- Connection pooling for efficient database access
- Support for multiple data sources
- Parameterized queries with SQL injection protection
- Streaming support for large result sets

### Data Transformation
- Powerful filtering with multiple operators
- Aggregation functions (sum, average, count, etc.)
- Pivot table generation
- Data type conversion and calculated columns

### Visualization
- Multiple chart types (bar, line, pie, scatter, etc.)
- Customizable styling and color palettes
- Automatic data sorting and top-N filtering
- Support for multiple charts in a single report

### Conditional Formatting
- Rule-based formatting with priorities
- Statistical outlier detection
- Data bars and color scales
- Custom condition functions

### Parameter System
- Multiple parameter types with validation
- Special parameters (today, last_month, etc.)
- Runtime parameter injection
- Batch report generation support

## Architecture

PyTemplate follows a modular architecture:

- **SQLExecutor**: Handles database connections and query execution
- **DataTransformer**: Provides data manipulation capabilities
- **ChartGenerator**: Creates visualizations from data
- **ConditionalFormatter**: Applies formatting rules to data
- **ParameterInjector**: Manages report parameters
- **TemplateEngine**: Orchestrates all components for report generation

## Performance Considerations

- Connection pooling minimizes database connection overhead
- Streaming query execution handles large datasets efficiently
- Query result caching reduces redundant database calls
- Optimized data transformations using pandas

## Thread Safety

The template engine is designed to be thread-safe for concurrent report generation:
- Connection pools are thread-safe
- Each report generation creates independent contexts
- Shared resources use appropriate locking mechanisms

## License

This project is part of the LibraryBench testing framework.