"""Template rendering engine with all features integrated."""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import pandas as pd
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pydantic import BaseModel, Field

from .sql_executor import SQLExecutor, MultiSourceExecutor, DatabaseConfig, QueryResult
from .data_transformer import (
    DataTransformer,
    AggregationConfig,
    PivotConfig,
    FilterCondition,
)
from .chart_generator import ChartGenerator, ChartConfig
from .formatting_engine import ConditionalFormatter, FormatRule
from .parameter_injector import ParameterInjector, ParameterDefinition


class QueryDefinition(BaseModel):
    """Definition of a query to execute."""

    name: str
    source: str
    query: str
    parameters: Optional[Dict[str, Any]] = None
    transformations: Optional[List[Dict[str, Any]]] = None
    cache: bool = Field(default=False)


class ReportSection(BaseModel):
    """Definition of a report section."""

    name: str
    template: str
    queries: Optional[List[str]] = None
    charts: Optional[List[ChartConfig]] = None
    formatting: Optional[List[FormatRule]] = None
    order: int = Field(default=0)


class ReportTemplate(BaseModel):
    """Complete report template definition."""

    name: str
    description: Optional[str] = None
    parameters: List[ParameterDefinition]
    queries: List[QueryDefinition]
    sections: List[ReportSection]
    output_format: str = Field(default="html")

    def get_ordered_sections(self) -> List[ReportSection]:
        """Get sections ordered by their order field."""
        return sorted(self.sections, key=lambda s: s.order)


class TemplateEngine:
    """Main template rendering engine integrating all components."""

    def __init__(self, template_dir: Optional[str] = None):
        """Initialize the template engine."""
        self.sql_executor = MultiSourceExecutor()
        self.data_transformer = DataTransformer()
        self.chart_generator = ChartGenerator()
        self.formatter = ConditionalFormatter()
        self.parameter_injector = ParameterInjector()

        # Set up Jinja2 environment
        if template_dir:
            self.jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(["html", "xml"]),
            )
        else:
            self.jinja_env = Environment(autoescape=select_autoescape(["html", "xml"]))

        # Register custom Jinja2 filters
        self._register_filters()

        # Cache for query results
        self._query_cache: Dict[str, QueryResult] = {}

    def _register_filters(self):
        """Register custom Jinja2 filters."""
        self.jinja_env.filters["currency"] = lambda x: f"${x:,.2f}" if x else ""
        self.jinja_env.filters["percentage"] = lambda x: f"{x:.1%}" if x else ""
        self.jinja_env.filters["number"] = lambda x: f"{x:,.0f}" if x else ""
        self.jinja_env.filters["date"] = lambda x: x.strftime("%Y-%m-%d") if x else ""
        self.jinja_env.filters["datetime"] = (
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if x else ""
        )

    def add_data_source(self, name: str, config: DatabaseConfig):
        """Add a data source to the engine."""
        self.sql_executor.add_source(name, config)

    def register_template(self, template: ReportTemplate):
        """Register a report template."""
        # Register parameters
        for param in template.parameters:
            self.parameter_injector.register_parameter(param)

    def render_report(
        self,
        template: ReportTemplate,
        parameters: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """Render a complete report from template."""
        # Clear query cache
        self._query_cache.clear()

        # Execute all queries
        query_results = self._execute_queries(template.queries, parameters)

        # Prepare context for template rendering
        context = {
            "parameters": parameters,
            "queries": query_results,
            "data": {},
            "charts": {},
            "tables": {},
        }

        # Render each section
        rendered_sections = []
        for section in template.get_ordered_sections():
            section_html = self._render_section(section, context, parameters)
            rendered_sections.append(section_html)

        # Combine sections into final report
        if template.output_format == "html":
            report = self._create_html_report(template.name, rendered_sections)
        else:
            report = "\n\n".join(rendered_sections)

        # Save to file if path provided
        if output_path:
            Path(output_path).write_text(report)

        return report

    def _execute_queries(
        self,
        queries: List[QueryDefinition],
        parameters: Dict[str, Any],
    ) -> Dict[str, pd.DataFrame]:
        """Execute all queries and return results as DataFrames."""
        results = {}

        for query_def in queries:
            # Check cache
            cache_key = f"{query_def.name}_{json.dumps(parameters, sort_keys=True)}"
            if query_def.cache and cache_key in self._query_cache:
                result = self._query_cache[cache_key]
            else:
                # Inject parameters into query
                injected_query = self.parameter_injector.inject_parameters(
                    query_def.query, parameters
                )

                # Execute query
                result = self.sql_executor.execute_query(
                    query_def.source, injected_query, query_def.parameters
                )

                # Cache if requested
                if query_def.cache:
                    self._query_cache[cache_key] = result

            # Convert to DataFrame
            df = pd.DataFrame(result.data)

            # Apply transformations
            if query_def.transformations:
                df = self._apply_transformations(df, query_def.transformations)

            results[query_def.name] = df

        return results

    def _apply_transformations(
        self,
        df: pd.DataFrame,
        transformations: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """Apply a series of transformations to a DataFrame."""
        result = df.copy()

        for transform in transformations:
            transform_type = transform.get("type")

            if transform_type == "filter":
                conditions = [
                    FilterCondition(**c) for c in transform.get("conditions", [])
                ]
                logic = transform.get("logic", "AND")
                result = self.data_transformer.filter_data(result, conditions, logic)

            elif transform_type == "aggregate":
                config = AggregationConfig(**transform.get("config", {}))
                result = self.data_transformer.aggregate_data(result, config)

            elif transform_type == "pivot":
                config = PivotConfig(**transform.get("config", {}))
                result = self.data_transformer.create_pivot_table(result, config)

            elif transform_type == "sort":
                sort_by = transform.get("by")
                ascending = transform.get("ascending", True)
                result = self.data_transformer.sort_data(result, sort_by, ascending)

            elif transform_type == "limit":
                limit = transform.get("limit", 100)
                offset = transform.get("offset", 0)
                result = self.data_transformer.limit_rows(result, limit, offset)

            elif transform_type == "calculate":
                calculations = transform.get("calculations", {})
                result = self.data_transformer.add_calculated_columns(
                    result, calculations
                )

            elif transform_type == "type_convert":
                type_map = transform.get("type_map", {})
                result = self.data_transformer.transform_data_types(result, type_map)

        return result

    def _render_section(
        self,
        section: ReportSection,
        context: Dict[str, Any],
        parameters: Dict[str, Any],
    ) -> str:
        """Render a single report section."""
        # Prepare section-specific data
        section_data = {}

        # Get query results for this section
        if section.queries:
            for query_name in section.queries:
                if query_name in context["queries"]:
                    section_data[query_name] = context["queries"][query_name]

        # Generate charts
        if section.charts:
            for i, chart_config in enumerate(section.charts):
                # Get data for chart
                # If no data_columns specified, use the first available data
                if hasattr(chart_config, "data_columns") and chart_config.data_columns:
                    data_query = chart_config.data_columns[0]
                else:
                    # Use first query data if available
                    data_query = list(section_data.keys())[0] if section_data else None

                if data_query and data_query in section_data:
                    chart_data = section_data[data_query]
                    chart_image = self.chart_generator.generate_chart(
                        chart_data, chart_config
                    )
                    context["charts"][f"{section.name}_chart_{i}"] = chart_image

        # Apply formatting to tables
        if section.formatting:
            for query_name, df in section_data.items():
                formatted_html = self.formatter.apply_rules(
                    df, section.formatting, output_format="html"
                )
                context["tables"][f"{section.name}_{query_name}"] = formatted_html
        else:
            # Convert DataFrames to HTML without special formatting
            for query_name, df in section_data.items():
                context["tables"][f"{section.name}_{query_name}"] = df.to_html(
                    index=False, classes="dataframe"
                )

        # Update context with section data
        context["data"].update(section_data)

        # Render template
        if section.template.startswith("file:"):
            # Load template from file
            template_name = section.template[5:]
            template = self.jinja_env.get_template(template_name)
        else:
            # Use inline template
            template = self.jinja_env.from_string(section.template)

        # Inject parameters into context
        context.update(parameters)

        return template.render(**context)

    def _create_html_report(self, title: str, sections: List[str]) -> str:
        """Create a complete HTML report."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
        }
        .dataframe {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        .dataframe th {
            background-color: #007bff;
            color: white;
            padding: 10px;
            text-align: left;
        }
        .dataframe td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        .dataframe tr:hover {
            background-color: #f5f5f5;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background-color: white;
        }
        .section {
            margin-bottom: 40px;
        }
        .parameters {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .parameters h3 {
            margin-top: 0;
        }
        .parameters ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .timestamp {
            text-align: right;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="report-container">
        <h1>{{ title }}</h1>
        <div class="timestamp">Generated: {{ timestamp }}</div>
        
        {% for section in sections %}
        <div class="section">
            {{ section | safe }}
        </div>
        {% endfor %}
    </div>
</body>
</html>
        """

        template = self.jinja_env.from_string(html_template)
        return template.render(
            title=title,
            sections=sections,
            timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def validate_template(self, template: ReportTemplate) -> List[str]:
        """Validate a report template and return any errors."""
        errors = []

        # Check that all query sources exist
        available_sources = set(self.sql_executor._executors.keys())
        for query in template.queries:
            if query.source not in available_sources:
                errors.append(
                    f"Query '{query.name}' references unknown source '{query.source}'"
                )

        # Check that sections reference valid queries
        query_names = {q.name for q in template.queries}
        for section in template.sections:
            if section.queries:
                for query_name in section.queries:
                    if query_name not in query_names:
                        errors.append(
                            f"Section '{section.name}' references unknown query '{query_name}'"
                        )

        # Validate Jinja2 templates
        for section in template.sections:
            try:
                if section.template.startswith("file:"):
                    template_name = section.template[5:]
                    self.jinja_env.get_template(template_name)
                else:
                    self.jinja_env.from_string(section.template)
            except Exception as e:
                errors.append(
                    f"Section '{section.name}' has invalid template: {str(e)}"
                )

        return errors

    def generate_sample_report(self) -> str:
        """Generate a sample report to demonstrate capabilities."""
        # This would create a sample report with mock data
        # For testing purposes
        pass
