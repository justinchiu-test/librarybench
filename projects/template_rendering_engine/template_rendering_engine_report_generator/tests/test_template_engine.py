"""Tests for template rendering engine."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import date

from src.template_engine import (
    TemplateEngine,
    QueryDefinition,
    ReportSection,
    ReportTemplate,
)
from src.sql_executor import DatabaseConfig, QueryResult
from src.chart_generator import ChartConfig, ChartType
from src.formatting_engine import FormatRule, FormatCondition, FormatStyle
from src.parameter_injector import ParameterDefinition, ParameterType


class TestQueryDefinition:
    """Test query definition configuration."""

    def test_basic_query(self):
        """Test basic query definition."""
        query = QueryDefinition(
            name="sales_data",
            source="warehouse",
            query="SELECT * FROM sales WHERE date = :report_date",
        )
        assert query.name == "sales_data"
        assert query.source == "warehouse"
        assert query.cache == False  # Default

    def test_query_with_transformations(self):
        """Test query with transformations."""
        query = QueryDefinition(
            name="filtered_sales",
            source="warehouse",
            query="SELECT * FROM sales",
            transformations=[
                {
                    "type": "filter",
                    "conditions": [
                        {"column": "amount", "operator": "greater_than", "value": 100}
                    ],
                },
                {"type": "sort", "by": "date", "ascending": False},
            ],
            cache=True,
        )
        assert len(query.transformations) == 2
        assert query.cache == True


class TestReportSection:
    """Test report section configuration."""

    def test_basic_section(self):
        """Test basic report section."""
        section = ReportSection(
            name="summary", template="<h2>Sales Summary</h2>", order=1
        )
        assert section.name == "summary"
        assert section.order == 1
        assert section.queries is None

    def test_section_with_components(self):
        """Test section with queries, charts, and formatting."""
        chart_config = ChartConfig(
            chart_type=ChartType.BAR, x_column="category", y_column="total"
        )
        format_rule = FormatRule(
            column="total",
            condition=FormatCondition.GREATER_THAN,
            value=1000,
            style=FormatStyle(background_color="green"),
        )

        section = ReportSection(
            name="analysis",
            template="<div>{{tables.analysis_sales_data}}</div>",
            queries=["sales_data"],
            charts=[chart_config],
            formatting=[format_rule],
            order=2,
        )
        assert len(section.queries) == 1
        assert len(section.charts) == 1
        assert len(section.formatting) == 1


class TestReportTemplate:
    """Test report template configuration."""

    def test_basic_template(self):
        """Test basic report template."""
        param = ParameterDefinition(
            name="report_date", type=ParameterType.DATE, required=True
        )
        query = QueryDefinition(name="data", source="db", query="SELECT * FROM table")
        section = ReportSection(name="main", template="<p>Report</p>", order=0)

        template = ReportTemplate(
            name="Monthly Report",
            description="Monthly sales report",
            parameters=[param],
            queries=[query],
            sections=[section],
        )

        assert template.name == "Monthly Report"
        assert len(template.parameters) == 1
        assert template.output_format == "html"  # Default

    def test_get_ordered_sections(self):
        """Test section ordering."""
        sections = [
            ReportSection(name="footer", template="", order=3),
            ReportSection(name="header", template="", order=1),
            ReportSection(name="body", template="", order=2),
        ]

        template = ReportTemplate(
            name="Test", parameters=[], queries=[], sections=sections
        )

        ordered = template.get_ordered_sections()
        assert ordered[0].name == "header"
        assert ordered[1].name == "body"
        assert ordered[2].name == "footer"


class TestTemplateEngine:
    """Test template engine functionality."""

    @pytest.fixture
    def engine(self):
        """Create a test template engine."""
        return TemplateEngine()

    @pytest.fixture
    def sample_config(self):
        """Create sample database config."""
        return DatabaseConfig(connection_string="sqlite:///:memory:")

    @pytest.fixture
    def sample_template(self):
        """Create a sample report template."""
        param = ParameterDefinition(
            name="min_amount", type=ParameterType.FLOAT, default=100.0
        )

        query = QueryDefinition(
            name="sales_data",
            source="main",
            query="SELECT category, SUM(amount) as total FROM sales GROUP BY category",
        )

        section = ReportSection(
            name="summary",
            template="""
            <h2>Sales Summary</h2>
            <p>Minimum amount filter: {{min_amount}}</p>
            {{tables.summary_sales_data|safe}}
            """,
            queries=["sales_data"],
            order=1,
        )

        return ReportTemplate(
            name="Sales Report", parameters=[param], queries=[query], sections=[section]
        )

    def test_initialization(self, engine):
        """Test engine initialization."""
        assert engine.sql_executor is not None
        assert engine.data_transformer is not None
        assert engine.chart_generator is not None
        assert engine.formatter is not None
        assert engine.parameter_injector is not None
        assert engine.jinja_env is not None

    def test_custom_filters(self, engine):
        """Test custom Jinja2 filters."""
        # Test currency filter
        assert engine.jinja_env.filters["currency"](1234.56) == "$1,234.56"
        assert engine.jinja_env.filters["currency"](None) == ""

        # Test percentage filter
        assert engine.jinja_env.filters["percentage"](0.123) == "12.3%"

        # Test number filter
        assert engine.jinja_env.filters["number"](1234567) == "1,234,567"

    def test_add_data_source(self, engine, sample_config):
        """Test adding data source."""
        engine.add_data_source("main", sample_config)

        assert "main" in engine.sql_executor._executors

    def test_register_template(self, engine, sample_template):
        """Test template registration."""
        engine.register_template(sample_template)

        # Parameters should be registered
        assert "min_amount" in engine.parameter_injector._definitions

    @patch.object(TemplateEngine, "_execute_queries")
    @patch.object(TemplateEngine, "_render_section")
    def test_render_report(
        self, mock_render_section, mock_execute_queries, engine, sample_template
    ):
        """Test report rendering."""
        # Mock query execution
        mock_execute_queries.return_value = {
            "sales_data": pd.DataFrame(
                {"category": ["A", "B", "C"], "total": [1000, 1500, 2000]}
            )
        }

        # Mock section rendering
        mock_render_section.return_value = "<div>Rendered section</div>"

        # Render report
        parameters = {"min_amount": 500.0}
        result = engine.render_report(sample_template, parameters)

        # Verify calls
        mock_execute_queries.assert_called_once()
        mock_render_section.assert_called_once()

        # Verify HTML structure
        assert "<!DOCTYPE html>" in result
        assert "<title>Sales Report</title>" in result
        assert "Rendered section" in result

    @patch("src.template_engine.MultiSourceExecutor.execute_query")
    def test_execute_queries(self, mock_execute, engine):
        """Test query execution."""
        # Setup mock
        mock_result = QueryResult(
            data=[{"id": 1, "value": 100}, {"id": 2, "value": 200}],
            columns=["id", "value"],
            row_count=2,
            execution_time=0.1,
            query="SELECT * FROM test",
            parameters=None,
        )
        mock_execute.return_value = mock_result

        # Add data source
        engine.add_data_source(
            "test_db", DatabaseConfig(connection_string="sqlite:///:memory:")
        )

        # Define queries
        queries = [
            QueryDefinition(
                name="test_query",
                source="test_db",
                query="SELECT * FROM test WHERE value > {{min_value}}",
            )
        ]

        # Execute queries
        parameters = {"min_value": 50}
        results = engine._execute_queries(queries, parameters)

        assert "test_query" in results
        assert len(results["test_query"]) == 2
        assert results["test_query"]["value"].sum() == 300

    def test_apply_transformations(self, engine):
        """Test data transformations."""
        df = pd.DataFrame(
            {"category": ["A", "B", "A", "B"], "value": [100, 200, 150, 250]}
        )

        transformations = [
            {
                "type": "filter",
                "conditions": [
                    {"column": "value", "operator": "greater_than", "value": 100}
                ],
                "logic": "AND",
            },
            {
                "type": "aggregate",
                "config": {"group_by": ["category"], "aggregations": {"value": "sum"}},
            },
            {"type": "sort", "by": "value", "ascending": False},
        ]

        result = engine._apply_transformations(df, transformations)

        # Should have filtered, aggregated, and sorted
        assert len(result) == 2
        assert result.iloc[0]["value"] == 450  # B group (200 + 250)
        assert result.iloc[1]["value"] == 150  # A group (only 150)

    @patch("src.template_engine.ChartGenerator.generate_chart")
    @patch("src.template_engine.ConditionalFormatter.apply_rules")
    def test_render_section(self, mock_format, mock_chart, engine):
        """Test section rendering."""
        # Setup mocks
        mock_chart.return_value = "base64_chart_data"
        mock_format.return_value = "<table>Formatted table</table>"

        # Create section
        section = ReportSection(
            name="test_section",
            template="""
            <h2>{{title}}</h2>
            <img src="data:image/png;base64,{{charts.test_section_chart_0}}">
            {{tables.test_section_data|safe}}
            """,
            queries=["data"],
            charts=[ChartConfig(chart_type=ChartType.BAR, x_column="x", y_column="y")],
            formatting=[
                FormatRule(
                    column="value",
                    condition=FormatCondition.GREATER_THAN,
                    value=100,
                    style=FormatStyle(background_color="green"),
                )
            ],
        )

        # Create context
        context = {
            "parameters": {"title": "Test Report"},
            "queries": {"data": pd.DataFrame({"x": ["A", "B"], "y": [100, 200]})},
            "data": {},
            "charts": {},
            "tables": {},
        }

        # Render section
        result = engine._render_section(section, context, {"title": "Test Report"})

        # Verify rendering
        assert "<h2>Test Report</h2>" in result
        # Chart should be in the img tag
        assert '<img src="data:image/png;base64,base64_chart_data">' in result
        assert "Formatted table" in result

        # Verify context updates
        assert "test_section_chart_0" in context["charts"]
        assert "test_section_data" in context["tables"]

    def test_create_html_report(self, engine):
        """Test HTML report creation."""
        sections = [
            "<h2>Section 1</h2><p>Content 1</p>",
            "<h2>Section 2</h2><p>Content 2</p>",
        ]

        result = engine._create_html_report("Test Report", sections)

        assert "<!DOCTYPE html>" in result
        assert "<title>Test Report</title>" in result
        assert "Section 1" in result
        assert "Section 2" in result
        assert "Generated:" in result  # Timestamp

    def test_validate_template(self, engine):
        """Test template validation."""
        # Create invalid template
        template = ReportTemplate(
            name="Invalid Report",
            parameters=[],
            queries=[
                QueryDefinition(
                    name="query1",
                    source="missing_source",  # Invalid source
                    query="SELECT * FROM table",
                )
            ],
            sections=[
                ReportSection(
                    name="section1",
                    template="Valid template",
                    queries=["missing_query"],  # Invalid query reference
                ),
                ReportSection(
                    name="section2",
                    template="{{invalid.syntax",  # Invalid Jinja2
                    queries=[],
                ),
            ],
        )

        errors = engine.validate_template(template)

        assert len(errors) >= 3
        assert any("missing_source" in error for error in errors)
        assert any("missing_query" in error for error in errors)
        assert any("invalid template" in error for error in errors)

    def test_cache_functionality(self, engine):
        """Test query result caching."""
        query = QueryDefinition(
            name="cached_query", source="test", query="SELECT * FROM data", cache=True
        )

        # First execution
        result1 = QueryResult(
            data=[{"id": 1}],
            columns=["id"],
            row_count=1,
            execution_time=0.1,
            query="SELECT * FROM data",
            parameters=None,
        )

        cache_key = f"cached_query_{{}}"  # Empty params
        engine._query_cache[cache_key] = result1

        # Verify cache is used
        assert cache_key in engine._query_cache
        assert engine._query_cache[cache_key] == result1

    def test_file_template_loading(self, engine):
        """Test loading template from file."""
        with patch.object(engine.jinja_env, "get_template") as mock_get:
            mock_template = Mock()
            mock_template.render.return_value = "<div>File template</div>"
            mock_get.return_value = mock_template

            section = ReportSection(
                name="file_section", template="file:reports/monthly.html", queries=[]
            )

            context = {"data": {}, "charts": {}, "tables": {}}
            result = engine._render_section(section, context, {})

            mock_get.assert_called_once_with("reports/monthly.html")
            assert result == "<div>File template</div>"

    @patch("pathlib.Path.write_text")
    def test_save_report_to_file(self, mock_write, engine, sample_template):
        """Test saving report to file."""
        with patch.object(engine, "_execute_queries") as mock_exec:
            mock_exec.return_value = {}

            with patch.object(engine, "_render_section") as mock_render:
                mock_render.return_value = "<div>Section</div>"

                # Render with output path
                engine.render_report(
                    sample_template, {"min_amount": 100}, output_path="/tmp/report.html"
                )

                # Verify file was written
                mock_write.assert_called_once()
