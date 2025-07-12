"""Tests for data transformation pipeline."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date

from src.data_transformer import (
    DataTransformer,
    AggregationType,
    FilterOperator,
    FilterCondition,
    AggregationConfig,
    PivotConfig,
)


class TestFilterCondition:
    """Test filter condition validation."""

    def test_valid_condition(self):
        """Test creating valid filter conditions."""
        condition = FilterCondition(
            column="price", operator=FilterOperator.GREATER_THAN, value=100
        )
        assert condition.column == "price"
        assert condition.operator == FilterOperator.GREATER_THAN
        assert condition.value == 100

    def test_null_operators_no_value(self):
        """Test null operators don't require value."""
        condition = FilterCondition(
            column="description", operator=FilterOperator.IS_NULL
        )
        assert condition.value is None

    def test_null_operators_with_value_fails(self):
        """Test null operators fail with value."""
        with pytest.raises(ValueError):
            FilterCondition(
                column="description", operator=FilterOperator.IS_NULL, value="something"
            )

    def test_in_operator_requires_list(self):
        """Test IN operator requires list value."""
        with pytest.raises(ValueError):
            FilterCondition(column="status", operator=FilterOperator.IN, value="active")

        # Should work with list
        condition = FilterCondition(
            column="status", operator=FilterOperator.IN, value=["active", "pending"]
        )
        assert isinstance(condition.value, list)


class TestDataTransformer:
    """Test data transformation functionality."""

    @pytest.fixture
    def transformer(self):
        """Create a test data transformer."""
        return DataTransformer()

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["A", "B", "C", "D", "E"],
                "category": ["X", "Y", "X", "Y", "Z"],
                "value": [100, 200, 150, 300, 250],
                "price": [10.5, 20.0, 15.5, 30.0, 25.0],
                "status": ["active", "active", "inactive", "active", "pending"],
                "date": pd.date_range("2024-01-01", periods=5),
            }
        )

    def test_filter_data_single_condition(self, transformer, sample_df):
        """Test filtering with single condition."""
        condition = FilterCondition(
            column="value", operator=FilterOperator.GREATER_THAN, value=150
        )

        result = transformer.filter_data(sample_df, [condition])

        assert len(result) == 3
        assert all(result["value"] > 150)

    def test_filter_data_multiple_conditions_and(self, transformer, sample_df):
        """Test filtering with multiple AND conditions."""
        conditions = [
            FilterCondition(
                column="value", operator=FilterOperator.GREATER_EQUAL, value=150
            ),
            FilterCondition(
                column="category", operator=FilterOperator.EQUALS, value="X"
            ),
        ]

        result = transformer.filter_data(sample_df, conditions, logic="AND")

        assert len(result) == 1
        assert result.iloc[0]["value"] == 150
        assert result.iloc[0]["category"] == "X"

    def test_filter_data_multiple_conditions_or(self, transformer, sample_df):
        """Test filtering with multiple OR conditions."""
        conditions = [
            FilterCondition(
                column="value", operator=FilterOperator.LESS_THAN, value=150
            ),
            FilterCondition(
                column="status", operator=FilterOperator.EQUALS, value="pending"
            ),
        ]

        result = transformer.filter_data(sample_df, conditions, logic="OR")

        assert len(result) == 2

    def test_filter_data_in_operator(self, transformer, sample_df):
        """Test filtering with IN operator."""
        condition = FilterCondition(
            column="category", operator=FilterOperator.IN, value=["X", "Z"]
        )

        result = transformer.filter_data(sample_df, [condition])

        assert len(result) == 3
        assert set(result["category"]) == {"X", "Z"}

    def test_filter_data_contains_operator(self, transformer, sample_df):
        """Test filtering with CONTAINS operator."""
        condition = FilterCondition(
            column="status", operator=FilterOperator.CONTAINS, value="act"
        )

        result = transformer.filter_data(sample_df, [condition])

        assert len(result) == 4  # active and inactive

    def test_filter_data_null_operators(self, transformer):
        """Test filtering with NULL operators."""
        df = pd.DataFrame({"id": [1, 2, 3, 4], "value": [10, None, 20, None]})

        # Test IS_NULL
        condition = FilterCondition(column="value", operator=FilterOperator.IS_NULL)
        result = transformer.filter_data(df, [condition])
        assert len(result) == 2
        assert all(pd.isna(result["value"]))

        # Test NOT_NULL
        condition = FilterCondition(column="value", operator=FilterOperator.NOT_NULL)
        result = transformer.filter_data(df, [condition])
        assert len(result) == 2
        assert all(pd.notna(result["value"]))

    def test_filter_data_invalid_column(self, transformer, sample_df):
        """Test filtering with invalid column raises error."""
        condition = FilterCondition(
            column="invalid_column", operator=FilterOperator.EQUALS, value=100
        )

        with pytest.raises(ValueError, match="not found"):
            transformer.filter_data(sample_df, [condition])

    def test_aggregate_data_single_aggregation(self, transformer, sample_df):
        """Test data aggregation with single aggregation."""
        config = AggregationConfig(
            group_by=["category"], aggregations={"value": AggregationType.SUM}
        )

        result = transformer.aggregate_data(sample_df, config)

        assert len(result) == 3  # X, Y, Z categories
        assert set(result.columns) == {"category", "value"}
        assert result[result["category"] == "X"]["value"].iloc[0] == 250  # 100 + 150

    def test_aggregate_data_multiple_aggregations(self, transformer, sample_df):
        """Test data aggregation with multiple aggregations."""
        config = AggregationConfig(
            group_by=["category"],
            aggregations={
                "value": [AggregationType.SUM, AggregationType.AVERAGE],
                "price": AggregationType.MAX,
            },
        )

        result = transformer.aggregate_data(sample_df, config)

        assert "value_sum" in result.columns
        assert "value_mean" in result.columns
        assert "price_max" in result.columns

    def test_aggregate_data_custom_function(self, transformer, sample_df):
        """Test aggregation with custom function."""
        # Register custom aggregation
        transformer.register_custom_aggregation("range", lambda x: x.max() - x.min())

        config = AggregationConfig(
            group_by=["category"], aggregations={"value": "range"}
        )

        result = transformer.aggregate_data(sample_df, config)

        # X category has values 100 and 150, range = 50
        x_row = result[result["category"] == "X"]
        assert x_row["value"].iloc[0] == 50

    def test_create_pivot_table(self, transformer, sample_df):
        """Test pivot table creation."""
        config = PivotConfig(
            index="category",
            columns="status",
            values="value",
            aggfunc="sum",
            fill_value=0,
        )

        result = transformer.create_pivot_table(sample_df, config)

        assert "category" in result.columns
        # Check for flattened column names
        assert any("active" in col for col in result.columns)
        assert any("inactive" in col for col in result.columns)
        assert any("pending" in col for col in result.columns)

    def test_create_pivot_table_multiple_values(self, transformer, sample_df):
        """Test pivot table with multiple value columns."""
        config = PivotConfig(
            index="category",
            columns="status",
            values=["value", "price"],
            aggfunc="mean",
        )

        result = transformer.create_pivot_table(sample_df, config)

        # Should have flattened column names
        assert any("value" in col for col in result.columns)
        assert any("price" in col for col in result.columns)

    def test_transform_data_types(self, transformer):
        """Test data type transformation."""
        df = pd.DataFrame(
            {
                "int_str": ["1", "2", "3"],
                "float_str": ["1.5", "2.5", "3.5"],
                "date_str": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "bool_int": [1, 0, 1],
            }
        )

        type_map = {
            "int_str": "int",
            "float_str": "float",
            "date_str": "datetime",
            "bool_int": "bool",
        }

        result = transformer.transform_data_types(df, type_map)

        assert pd.api.types.is_integer_dtype(result["int_str"])
        assert pd.api.types.is_float_dtype(result["float_str"])
        assert pd.api.types.is_datetime64_any_dtype(result["date_str"])
        assert pd.api.types.is_bool_dtype(result["bool_int"])

    def test_add_calculated_columns(self, transformer, sample_df):
        """Test adding calculated columns."""
        calculations = {
            "total": "value * price",
            "value_pct": "value / value.sum()",
            "is_high_value": "value > 200",
        }

        result = transformer.add_calculated_columns(sample_df, calculations)

        assert "total" in result.columns
        assert "value_pct" in result.columns
        assert "is_high_value" in result.columns

        # Verify calculations
        assert result["total"].iloc[0] == 100 * 10.5
        assert abs(result["value_pct"].sum() - 1.0) < 0.001
        assert result["is_high_value"].iloc[1] == False  # value=200
        assert result["is_high_value"].iloc[3] == True  # value=300

    def test_sort_data(self, transformer, sample_df):
        """Test data sorting."""
        # Sort by single column
        result = transformer.sort_data(sample_df, "value", ascending=False)
        assert result["value"].iloc[0] == 300
        assert result["value"].iloc[-1] == 100

        # Sort by multiple columns
        result = transformer.sort_data(
            sample_df, ["category", "value"], ascending=[True, False]
        )
        first_x = result[result["category"] == "X"].iloc[0]
        assert first_x["value"] == 150  # Higher value in X category

    def test_limit_rows(self, transformer, sample_df):
        """Test row limiting."""
        # Test limit only
        result = transformer.limit_rows(sample_df, limit=3)
        assert len(result) == 3
        assert list(result["id"]) == [1, 2, 3]

        # Test limit with offset
        result = transformer.limit_rows(sample_df, limit=2, offset=2)
        assert len(result) == 2
        assert list(result["id"]) == [3, 4]

    def test_format_numeric_columns(self, transformer, sample_df):
        """Test numeric column formatting."""
        format_map = {"value": "{:,}", "price": "currency", "id": "percentage"}

        result = transformer.format_numeric_columns(sample_df, format_map)

        # Check formatting applied
        assert result["price"].iloc[0] == "$10.50"
        assert result["id"].iloc[0] == "100.0%"  # id=1 -> 100%

    def test_empty_dataframe_handling(self, transformer):
        """Test handling of empty DataFrames."""
        empty_df = pd.DataFrame()

        # Filter should return empty
        result = transformer.filter_data(empty_df, [])
        assert len(result) == 0

        # Sort should return empty
        result = transformer.sort_data(empty_df, [])
        assert len(result) == 0
