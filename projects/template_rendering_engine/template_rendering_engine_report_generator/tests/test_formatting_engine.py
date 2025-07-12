"""Tests for conditional formatting engine."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from src.formatting_engine import (
    ConditionalFormatter,
    FormatCondition,
    FormatStyle,
    FormatRule,
)


class TestFormatStyle:
    """Test formatting style configuration."""

    def test_valid_style(self):
        """Test creating valid format style."""
        style = FormatStyle(
            background_color="#FF0000",
            text_color="blue",
            font_weight="bold",
            font_style="italic",
        )
        assert style.background_color == "#FF0000"
        assert style.text_color == "blue"
        assert style.font_weight == "bold"

    def test_invalid_color(self):
        """Test color validation."""
        with pytest.raises(ValueError):
            FormatStyle(background_color="invalid_color")

        with pytest.raises(ValueError):
            FormatStyle(text_color="123456")  # Missing #

    def test_default_style(self):
        """Test default style values."""
        style = FormatStyle()
        assert style.background_color is None
        assert style.text_color is None
        assert style.font_weight is None


class TestFormatRule:
    """Test formatting rule configuration."""

    def test_basic_rule(self):
        """Test creating basic format rule."""
        style = FormatStyle(background_color="yellow")
        rule = FormatRule(
            column="value",
            condition=FormatCondition.GREATER_THAN,
            value=100,
            style=style,
        )
        assert rule.column == "value"
        assert rule.condition == FormatCondition.GREATER_THAN
        assert rule.value == 100
        assert rule.priority == 0

    def test_between_rule(self):
        """Test rule with BETWEEN condition."""
        style = FormatStyle(text_color="green")
        rule = FormatRule(
            column="score",
            condition=FormatCondition.BETWEEN,
            value=0,
            value2=100,
            style=style,
            priority=5,
        )
        assert rule.value2 == 100
        assert rule.priority == 5

    def test_between_rule_missing_value2(self):
        """Test BETWEEN rule without value2 fails."""
        style = FormatStyle()
        with pytest.raises(ValueError):
            FormatRule(
                column="score", condition=FormatCondition.BETWEEN, value=0, style=style
            )


class TestConditionalFormatter:
    """Test conditional formatting functionality."""

    @pytest.fixture
    def formatter(self):
        """Create a test formatter."""
        return ConditionalFormatter()

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["A", "B", "C", "D", "E"],
                "value": [50, 100, 150, 200, 250],
                "score": [0.2, 0.4, 0.6, 0.8, 1.0],
                "status": ["active", "inactive", "active", "pending", "active"],
                "description": [
                    "Test item",
                    None,
                    "Another test",
                    "Pending item",
                    "Final test",
                ],
            }
        )

    def test_apply_single_rule(self, formatter, sample_df):
        """Test applying single formatting rule."""
        rule = FormatRule(
            column="value",
            condition=FormatCondition.GREATER_THAN,
            value=150,
            style=FormatStyle(background_color="green"),
        )

        result = formatter.apply_rules(sample_df, [rule], output_format="styled_df")

        # Check that style was applied (result is a Styler object)
        assert hasattr(result, "data")  # Styler has data attribute

    def test_apply_multiple_rules(self, formatter, sample_df):
        """Test applying multiple formatting rules."""
        rules = [
            FormatRule(
                column="value",
                condition=FormatCondition.GREATER_THAN,
                value=150,
                style=FormatStyle(background_color="green"),
                priority=1,
            ),
            FormatRule(
                column="status",
                condition=FormatCondition.EQUALS,
                value="active",
                style=FormatStyle(text_color="blue"),
                priority=2,
            ),
        ]

        result = formatter.apply_rules(sample_df, rules, output_format="html")

        assert isinstance(result, str)
        assert "<table" in result
        assert "style=" in result

    def test_condition_evaluation_numeric(self, formatter, sample_df):
        """Test numeric condition evaluation."""
        # Test various numeric conditions
        conditions = [
            (FormatCondition.EQUALS, 100, [False, True, False, False, False]),
            (FormatCondition.NOT_EQUALS, 100, [True, False, True, True, True]),
            (FormatCondition.GREATER_THAN, 100, [False, False, True, True, True]),
            (FormatCondition.LESS_EQUAL, 150, [True, True, True, False, False]),
        ]

        for condition, value, expected in conditions:
            rule = FormatRule(
                column="value", condition=condition, value=value, style=FormatStyle()
            )
            mask = formatter._evaluate_condition(sample_df, rule)
            assert list(mask) == expected

    def test_condition_evaluation_between(self, formatter, sample_df):
        """Test BETWEEN condition evaluation."""
        rule = FormatRule(
            column="value",
            condition=FormatCondition.BETWEEN,
            value=100,
            value2=200,
            style=FormatStyle(),
        )

        mask = formatter._evaluate_condition(sample_df, rule)
        expected = [False, True, True, True, False]
        assert list(mask) == expected

    def test_condition_evaluation_string(self, formatter, sample_df):
        """Test string condition evaluation."""
        # Test CONTAINS
        rule = FormatRule(
            column="description",
            condition=FormatCondition.CONTAINS,
            value="test",
            style=FormatStyle(),
        )
        mask = formatter._evaluate_condition(sample_df, rule)
        expected = [
            False,
            False,
            True,
            False,
            True,
        ]  # "Test item" doesn't match "test" (case sensitive)
        assert list(mask) == expected

        # Test STARTS_WITH
        rule = FormatRule(
            column="status",
            condition=FormatCondition.STARTS_WITH,
            value="act",
            style=FormatStyle(),
        )
        mask = formatter._evaluate_condition(sample_df, rule)
        expected = [True, False, True, False, True]
        assert list(mask) == expected

    def test_condition_evaluation_null(self, formatter, sample_df):
        """Test NULL condition evaluation."""
        # Test IS_NULL
        rule = FormatRule(
            column="description", condition=FormatCondition.IS_NULL, style=FormatStyle()
        )
        mask = formatter._evaluate_condition(sample_df, rule)
        expected = [False, True, False, False, False]
        assert list(mask) == expected

        # Test NOT_NULL
        rule = FormatRule(
            column="description",
            condition=FormatCondition.NOT_NULL,
            style=FormatStyle(),
        )
        mask = formatter._evaluate_condition(sample_df, rule)
        expected = [True, False, True, True, True]
        assert list(mask) == expected

    def test_condition_evaluation_list(self, formatter, sample_df):
        """Test IN/NOT_IN condition evaluation."""
        # Test IN
        rule = FormatRule(
            column="status",
            condition=FormatCondition.IN,
            value=["active", "pending"],
            style=FormatStyle(),
        )
        mask = formatter._evaluate_condition(sample_df, rule)
        expected = [True, False, True, True, True]
        assert list(mask) == expected

        # Test NOT_IN
        rule = FormatRule(
            column="status",
            condition=FormatCondition.NOT_IN,
            value=["inactive"],
            style=FormatStyle(),
        )
        mask = formatter._evaluate_condition(sample_df, rule)
        expected = [True, False, True, True, True]
        assert list(mask) == expected

    def test_condition_evaluation_statistical(self, formatter, sample_df):
        """Test statistical condition evaluation."""
        # Test TOP_N
        rule = FormatRule(
            column="value",
            condition=FormatCondition.TOP_N,
            value=2,
            style=FormatStyle(),
        )
        mask = formatter._evaluate_condition(sample_df, rule)
        # Top 2 values are 250 and 200
        expected = [False, False, False, True, True]
        assert list(mask) == expected

        # Test ABOVE_AVERAGE
        rule = FormatRule(
            column="value", condition=FormatCondition.ABOVE_AVERAGE, style=FormatStyle()
        )
        mask = formatter._evaluate_condition(sample_df, rule)
        # Average is 150
        expected = [False, False, False, True, True]
        assert list(mask) == expected

    def test_style_to_css(self, formatter):
        """Test style to CSS conversion."""
        style = FormatStyle(
            background_color="#FF0000",
            text_color="blue",
            font_weight="bold",
            font_style="italic",
            border="1px solid black",
            text_decoration="underline",
            font_size="14px",
        )

        css = formatter._style_to_css(style)

        assert "background-color: #FF0000" in css
        assert "color: blue" in css
        assert "font-weight: bold" in css
        assert "font-style: italic" in css
        assert "border: 1px solid black" in css
        assert "text-decoration: underline" in css
        assert "font-size: 14px" in css

    def test_html_output(self, formatter, sample_df):
        """Test HTML output generation."""
        rule = FormatRule(
            column="value",
            condition=FormatCondition.GREATER_THAN,
            value=150,
            style=FormatStyle(background_color="green", text_color="white"),
        )

        html = formatter.apply_rules(sample_df, [rule], output_format="html")

        assert isinstance(html, str)
        assert '<table class="dataframe">' in html
        assert "<thead>" in html
        assert "<tbody>" in html
        assert 'style="background-color: green; color: white"' in html

    def test_priority_ordering(self, formatter, sample_df):
        """Test rule priority ordering."""
        rules = [
            FormatRule(
                column="value",
                condition=FormatCondition.GREATER_THAN,
                value=0,
                style=FormatStyle(background_color="yellow"),
                priority=1,
            ),
            FormatRule(
                column="value",
                condition=FormatCondition.GREATER_THAN,
                value=150,
                style=FormatStyle(background_color="green"),
                priority=10,  # Higher priority
            ),
        ]

        # The higher priority rule should override
        result = formatter.apply_rules(sample_df, rules, output_format="html")

        # Values > 150 should have green background, not yellow
        assert 'style="background-color: green"' in result

    def test_custom_condition(self, formatter, sample_df):
        """Test registering and using custom condition."""
        # Register custom condition
        formatter.register_custom_condition("is_even", lambda x, _: x % 2 == 0)

        rule = FormatRule(
            column="id", condition="is_even", style=FormatStyle(font_style="italic")
        )

        mask = formatter._evaluate_condition(sample_df, rule)
        expected = [False, True, False, True, False]  # IDs 2 and 4 are even
        assert list(mask) == expected

    def test_create_data_bars(self, formatter, sample_df):
        """Test data bar creation."""
        result = formatter.create_data_bars(
            sample_df, ["value"], color="#4CAF50", min_width=0, max_width=100
        )

        # Check that HTML div elements were created
        assert all('<div style="background:' in str(val) for val in result["value"])

    @patch("matplotlib.cm.get_cmap")
    def test_create_color_scales(self, mock_get_cmap, formatter, sample_df):
        """Test color scale creation."""
        # Mock colormap
        mock_cmap = Mock()
        mock_cmap.return_value = (0.5, 0.5, 0.5, 1.0)  # RGBA
        mock_get_cmap.return_value = mock_cmap

        result = formatter.create_color_scales(sample_df, ["value"], color_map="RdYlGn")

        # Check that span elements with background colors were created
        assert all(
            '<span style="background-color:' in str(val) for val in result["value"]
        )

    def test_highlight_outliers_iqr(self, formatter, sample_df):
        """Test outlier highlighting using IQR method."""
        rules = formatter.highlight_outliers(
            sample_df, ["value"], method="iqr", multiplier=1.5
        )

        assert len(rules) == 2  # One for lower, one for upper outliers
        assert all(rule.priority == 10 for rule in rules)
        assert rules[0].condition == FormatCondition.LESS_THAN
        assert rules[1].condition == FormatCondition.GREATER_THAN

    def test_highlight_outliers_zscore(self, formatter, sample_df):
        """Test outlier highlighting using z-score method."""
        rules = formatter.highlight_outliers(
            sample_df, ["value"], method="zscore", multiplier=2.0
        )

        assert len(rules) == 1
        assert rules[0].condition == FormatCondition.NOT_BETWEEN

    def test_invalid_column(self, formatter, sample_df):
        """Test handling of invalid column."""
        rule = FormatRule(
            column="invalid_column",
            condition=FormatCondition.EQUALS,
            value=100,
            style=FormatStyle(),
        )

        # Should skip invalid column without error
        result = formatter.apply_rules(sample_df, [rule], output_format="html")
        assert isinstance(result, str)

    def test_empty_dataframe(self, formatter):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        rule = FormatRule(
            column="value",
            condition=FormatCondition.GREATER_THAN,
            value=100,
            style=FormatStyle(),
        )

        result = formatter.apply_rules(empty_df, [rule], output_format="html")
        assert isinstance(result, str)
        assert "<table" in result
