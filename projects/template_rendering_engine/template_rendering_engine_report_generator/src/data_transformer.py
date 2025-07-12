"""Data transformation pipeline with aggregation, filtering, and pivot capabilities."""

from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
import pandas as pd
from pydantic import BaseModel, Field, field_validator, ValidationInfo


class AggregationType(str, Enum):
    """Types of aggregation operations."""

    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    STD = "std"
    VAR = "variance"
    FIRST = "first"
    LAST = "last"


class FilterOperator(str, Enum):
    """Filter operators for data filtering."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_EQUAL = "greater_equal"
    LESS_THAN = "less_than"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IS_NULL = "is_null"
    NOT_NULL = "not_null"


class FilterCondition(BaseModel):
    """A single filter condition."""

    column: str
    operator: FilterOperator
    value: Optional[Any] = None

    @field_validator("value")
    def validate_value(cls, v, info: ValidationInfo):
        operator = info.data.get("operator")
        if operator in [FilterOperator.IS_NULL, FilterOperator.NOT_NULL]:
            if v is not None:
                raise ValueError(f"Operator {operator} does not require a value")
        elif operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            if not isinstance(v, list):
                raise ValueError(f"Operator {operator} requires a list value")
        return v


class AggregationConfig(BaseModel):
    """Configuration for data aggregation."""

    group_by: List[str]
    aggregations: Dict[
        str, Union[AggregationType, List[Union[AggregationType, str]], str]
    ]

    @field_validator("group_by")
    def validate_group_by(cls, v):
        if not v:
            raise ValueError("group_by must contain at least one column")
        return v


class PivotConfig(BaseModel):
    """Configuration for pivot table generation."""

    index: Union[str, List[str]]
    columns: Union[str, List[str]]
    values: Union[str, List[str]]
    aggfunc: Union[str, Dict[str, str]] = "mean"
    fill_value: Optional[Any] = None

    @field_validator("index")
    def normalize_index(cls, v):
        return [v] if isinstance(v, str) else v

    @field_validator("columns")
    def normalize_columns(cls, v):
        return [v] if isinstance(v, str) else v

    @field_validator("values")
    def normalize_values(cls, v):
        return [v] if isinstance(v, str) else v


class DataTransformer:
    """Data transformation pipeline for report generation."""

    def __init__(self):
        """Initialize the data transformer."""
        self._custom_aggregations: Dict[str, Callable] = {}

    def register_custom_aggregation(self, name: str, func: Callable):
        """Register a custom aggregation function."""
        self._custom_aggregations[name] = func

    def filter_data(
        self,
        df: pd.DataFrame,
        conditions: List[FilterCondition],
        logic: str = "AND",
    ) -> pd.DataFrame:
        """Apply filter conditions to a DataFrame."""
        if not conditions:
            return df.copy()

        masks = []

        for condition in conditions:
            column = condition.column
            operator = condition.operator
            value = condition.value

            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found in DataFrame")

            if operator == FilterOperator.EQUALS:
                mask = df[column] == value
            elif operator == FilterOperator.NOT_EQUALS:
                mask = df[column] != value
            elif operator == FilterOperator.GREATER_THAN:
                mask = df[column] > value
            elif operator == FilterOperator.GREATER_EQUAL:
                mask = df[column] >= value
            elif operator == FilterOperator.LESS_THAN:
                mask = df[column] < value
            elif operator == FilterOperator.LESS_EQUAL:
                mask = df[column] <= value
            elif operator == FilterOperator.IN:
                mask = df[column].isin(value)
            elif operator == FilterOperator.NOT_IN:
                mask = ~df[column].isin(value)
            elif operator == FilterOperator.CONTAINS:
                mask = df[column].astype(str).str.contains(str(value), na=False)
            elif operator == FilterOperator.NOT_CONTAINS:
                mask = ~df[column].astype(str).str.contains(str(value), na=False)
            elif operator == FilterOperator.IS_NULL:
                mask = df[column].isna()
            elif operator == FilterOperator.NOT_NULL:
                mask = df[column].notna()
            else:
                raise ValueError(f"Unknown operator: {operator}")

            masks.append(mask)

        if logic.upper() == "AND":
            combined_mask = masks[0]
            for mask in masks[1:]:
                combined_mask = combined_mask & mask
        elif logic.upper() == "OR":
            combined_mask = masks[0]
            for mask in masks[1:]:
                combined_mask = combined_mask | mask
        else:
            raise ValueError(f"Logic must be 'AND' or 'OR', got '{logic}'")

        return df[combined_mask].copy()

    def aggregate_data(
        self,
        df: pd.DataFrame,
        config: AggregationConfig,
    ) -> pd.DataFrame:
        """Perform data aggregation based on configuration."""
        # Map aggregation types to pandas functions
        agg_map = {
            AggregationType.SUM: "sum",
            AggregationType.AVERAGE: "mean",
            AggregationType.COUNT: "count",
            AggregationType.MIN: "min",
            AggregationType.MAX: "max",
            AggregationType.MEDIAN: "median",
            AggregationType.STD: "std",
            AggregationType.VAR: "var",
            AggregationType.FIRST: "first",
            AggregationType.LAST: "last",
        }

        # Prepare aggregation dictionary
        agg_dict = {}
        for column, agg_type in config.aggregations.items():
            if isinstance(agg_type, list):
                agg_funcs = []
                for at in agg_type:
                    if isinstance(at, AggregationType):
                        agg_funcs.append(agg_map[at])
                    elif at in self._custom_aggregations:
                        agg_funcs.append(self._custom_aggregations[at])
                    else:
                        agg_funcs.append(at)
                agg_dict[column] = agg_funcs
            else:
                if isinstance(agg_type, AggregationType):
                    agg_dict[column] = agg_map[agg_type]
                elif agg_type in self._custom_aggregations:
                    agg_dict[column] = self._custom_aggregations[agg_type]
                else:
                    agg_dict[column] = agg_type

        # Perform groupby and aggregation
        grouped = df.groupby(config.group_by)
        result = grouped.agg(agg_dict)

        # Flatten column names if multi-level
        if isinstance(result.columns, pd.MultiIndex):
            result.columns = ["_".join(col).strip() for col in result.columns]

        return result.reset_index()

    def create_pivot_table(
        self,
        df: pd.DataFrame,
        config: PivotConfig,
    ) -> pd.DataFrame:
        """Create a pivot table from the DataFrame."""
        pivot = pd.pivot_table(
            df,
            index=config.index,
            columns=config.columns,
            values=config.values,
            aggfunc=config.aggfunc,
            fill_value=config.fill_value,
        )

        # Flatten column names if multi-level
        if isinstance(pivot.columns, pd.MultiIndex):
            pivot.columns = ["_".join(map(str, col)).strip() for col in pivot.columns]

        return pivot.reset_index()

    def transform_data_types(
        self,
        df: pd.DataFrame,
        type_map: Dict[str, str],
    ) -> pd.DataFrame:
        """Transform data types of DataFrame columns."""
        result = df.copy()

        for column, dtype in type_map.items():
            if column not in result.columns:
                raise ValueError(f"Column '{column}' not found in DataFrame")

            try:
                if dtype == "int":
                    result[column] = pd.to_numeric(
                        result[column], errors="coerce"
                    ).astype("Int64")
                elif dtype == "float":
                    result[column] = pd.to_numeric(result[column], errors="coerce")
                elif dtype == "string":
                    result[column] = result[column].astype(str)
                elif dtype == "datetime":
                    result[column] = pd.to_datetime(result[column], errors="coerce")
                elif dtype == "date":
                    result[column] = pd.to_datetime(
                        result[column], errors="coerce"
                    ).dt.date
                elif dtype == "bool":
                    result[column] = result[column].astype(bool)
                else:
                    result[column] = result[column].astype(dtype)
            except Exception as e:
                raise ValueError(
                    f"Failed to convert column '{column}' to {dtype}: {str(e)}"
                )

        return result

    def add_calculated_columns(
        self,
        df: pd.DataFrame,
        calculations: Dict[str, str],
    ) -> pd.DataFrame:
        """Add calculated columns to the DataFrame."""
        result = df.copy()

        for column_name, expression in calculations.items():
            try:
                # Use eval with the DataFrame context
                result[column_name] = result.eval(expression)
            except Exception as e:
                raise ValueError(
                    f"Failed to calculate column '{column_name}' with expression '{expression}': {str(e)}"
                )

        return result

    def sort_data(
        self,
        df: pd.DataFrame,
        sort_by: Union[str, List[str]],
        ascending: Union[bool, List[bool]] = True,
    ) -> pd.DataFrame:
        """Sort DataFrame by specified columns."""
        if isinstance(sort_by, str):
            sort_by = [sort_by]

        return df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)

    def limit_rows(
        self,
        df: pd.DataFrame,
        limit: int,
        offset: int = 0,
    ) -> pd.DataFrame:
        """Limit the number of rows returned."""
        return df.iloc[offset : offset + limit].copy()

    def format_numeric_columns(
        self,
        df: pd.DataFrame,
        format_map: Dict[str, str],
    ) -> pd.DataFrame:
        """Format numeric columns for display."""
        result = df.copy()

        for column, format_spec in format_map.items():
            if column not in result.columns:
                continue

            if "currency" in format_spec.lower():
                result[column] = result[column].apply(
                    lambda x: f"${x:,.2f}" if pd.notna(x) else ""
                )
            elif (
                "percentage" in format_spec.lower() or "percent" in format_spec.lower()
            ):
                result[column] = result[column].apply(
                    lambda x: f"{x:.1%}" if pd.notna(x) else ""
                )
            elif "," in format_spec:
                result[column] = result[column].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) else ""
                )
            else:
                result[column] = result[column].apply(
                    lambda x: format_spec.format(x) if pd.notna(x) else ""
                )

        return result
