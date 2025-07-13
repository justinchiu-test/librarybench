"""Conditional formatting engine for data values."""

from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
import pandas as pd
from pydantic import BaseModel, Field, field_validator, ValidationInfo, model_validator


class FormatCondition(str, Enum):
    """Types of formatting conditions."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_EQUAL = "greater_equal"
    LESS_THAN = "less_than"
    LESS_EQUAL = "less_equal"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_NULL = "is_null"
    NOT_NULL = "not_null"
    TOP_N = "top_n"
    BOTTOM_N = "bottom_n"
    ABOVE_AVERAGE = "above_average"
    BELOW_AVERAGE = "below_average"


class FormatStyle(BaseModel):
    """Styling attributes for formatted cells."""

    background_color: Optional[str] = None
    text_color: Optional[str] = None
    font_weight: Optional[str] = None
    font_style: Optional[str] = None
    border: Optional[str] = None
    text_decoration: Optional[str] = None
    font_size: Optional[str] = None

    @field_validator("background_color", "text_color")
    def validate_color(cls, v):
        if v and not (
            v.startswith("#")
            or v
            in [
                "red",
                "green",
                "blue",
                "yellow",
                "orange",
                "purple",
                "black",
                "white",
                "gray",
            ]
        ):
            raise ValueError("Color must be a hex code or valid color name")
        return v


class FormatRule(BaseModel):
    """A single formatting rule."""

    column: str
    condition: Union[FormatCondition, str]  # Allow custom conditions as strings
    value: Optional[Any] = None
    value2: Optional[Any] = None  # For BETWEEN conditions
    style: FormatStyle
    priority: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_value2(self):
        if self.condition in [FormatCondition.BETWEEN, FormatCondition.NOT_BETWEEN]:
            if self.value2 is None:
                raise ValueError(f"Condition {self.condition} requires value2")
        return self


class ConditionalFormatter:
    """Engine for applying conditional formatting to data."""

    def __init__(self):
        """Initialize the conditional formatter."""
        self._custom_conditions: Dict[str, Callable] = {}

    def register_custom_condition(self, name: str, func: Callable[[Any, Any], bool]):
        """Register a custom condition function."""
        self._custom_conditions[name] = func

    def apply_rules(
        self,
        df: pd.DataFrame,
        rules: List[FormatRule],
        output_format: str = "html",
    ) -> Union[str, pd.DataFrame]:
        """Apply formatting rules to a DataFrame."""
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)

        # Create a style DataFrame to track formatting
        style_df = pd.DataFrame("", index=df.index, columns=df.columns)

        for rule in sorted_rules:
            if rule.column not in df.columns:
                continue

            # Get mask for rows that meet the condition
            mask = self._evaluate_condition(df, rule)

            # Apply style to matching cells (only if not already styled)
            style_str = self._style_to_css(rule.style)
            # Only apply style where mask is True AND no style exists yet
            apply_mask = mask & (style_df[rule.column] == "")
            style_df.loc[apply_mask, rule.column] = style_str

        if output_format == "html":
            return self._apply_html_formatting(df, style_df)
        elif output_format == "styled_df":
            return self._apply_pandas_styling(df, style_df)
        else:
            return df

    def _evaluate_condition(self, df: pd.DataFrame, rule: FormatRule) -> pd.Series:
        """Evaluate a condition and return a boolean mask."""
        column = rule.column
        condition = rule.condition
        value = rule.value
        value2 = rule.value2

        series = df[column]

        if condition == FormatCondition.EQUALS:
            return series == value
        elif condition == FormatCondition.NOT_EQUALS:
            return series != value
        elif condition == FormatCondition.GREATER_THAN:
            return series > value
        elif condition == FormatCondition.GREATER_EQUAL:
            return series >= value
        elif condition == FormatCondition.LESS_THAN:
            return series < value
        elif condition == FormatCondition.LESS_EQUAL:
            return series <= value
        elif condition == FormatCondition.BETWEEN:
            return (series >= value) & (series <= value2)
        elif condition == FormatCondition.NOT_BETWEEN:
            return (series < value) | (series > value2)
        elif condition == FormatCondition.IN:
            return series.isin(value)
        elif condition == FormatCondition.NOT_IN:
            return ~series.isin(value)
        elif condition == FormatCondition.CONTAINS:
            return series.astype(str).str.contains(str(value), na=False)
        elif condition == FormatCondition.NOT_CONTAINS:
            return ~series.astype(str).str.contains(str(value), na=False)
        elif condition == FormatCondition.STARTS_WITH:
            return series.astype(str).str.startswith(str(value), na=False)
        elif condition == FormatCondition.ENDS_WITH:
            return series.astype(str).str.endswith(str(value), na=False)
        elif condition == FormatCondition.IS_NULL:
            return series.isna()
        elif condition == FormatCondition.NOT_NULL:
            return series.notna()
        elif condition == FormatCondition.TOP_N:
            if pd.api.types.is_numeric_dtype(series):
                threshold = series.nlargest(value).min()
                return series >= threshold
            return pd.Series(False, index=series.index)
        elif condition == FormatCondition.BOTTOM_N:
            if pd.api.types.is_numeric_dtype(series):
                threshold = series.nsmallest(value).max()
                return series <= threshold
            return pd.Series(False, index=series.index)
        elif condition == FormatCondition.ABOVE_AVERAGE:
            if pd.api.types.is_numeric_dtype(series):
                return series > series.mean()
            return pd.Series(False, index=series.index)
        elif condition == FormatCondition.BELOW_AVERAGE:
            if pd.api.types.is_numeric_dtype(series):
                return series < series.mean()
            return pd.Series(False, index=series.index)
        else:
            # Check for custom conditions
            if condition in self._custom_conditions:
                return series.apply(
                    lambda x: self._custom_conditions[condition](x, value)
                )
            raise ValueError(f"Unknown condition: {condition}")

    def _style_to_css(self, style: FormatStyle) -> str:
        """Convert FormatStyle to CSS string."""
        css_parts = []

        if style.background_color:
            css_parts.append(f"background-color: {style.background_color}")
        if style.text_color:
            css_parts.append(f"color: {style.text_color}")
        if style.font_weight:
            css_parts.append(f"font-weight: {style.font_weight}")
        if style.font_style:
            css_parts.append(f"font-style: {style.font_style}")
        if style.border:
            css_parts.append(f"border: {style.border}")
        if style.text_decoration:
            css_parts.append(f"text-decoration: {style.text_decoration}")
        if style.font_size:
            css_parts.append(f"font-size: {style.font_size}")

        return "; ".join(css_parts)

    def _apply_html_formatting(self, df: pd.DataFrame, style_df: pd.DataFrame) -> str:
        """Apply formatting and return as HTML."""
        html_parts = ['<table class="dataframe">']

        # Add header
        html_parts.append("<thead><tr>")
        for col in df.columns:
            html_parts.append(f"<th>{col}</th>")
        html_parts.append("</tr></thead>")

        # Add body
        html_parts.append("<tbody>")
        for idx, row in df.iterrows():
            html_parts.append("<tr>")
            for col in df.columns:
                style = style_df.loc[idx, col]
                cell_value = row[col]

                if pd.isna(cell_value):
                    cell_value = ""

                if style:
                    html_parts.append(f'<td style="{style}">{cell_value}</td>')
                else:
                    html_parts.append(f"<td>{cell_value}</td>")
            html_parts.append("</tr>")
        html_parts.append("</tbody>")
        html_parts.append("</table>")

        return "".join(html_parts)

    def _apply_pandas_styling(
        self, df: pd.DataFrame, style_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Apply formatting using pandas Styler."""

        def style_func(x):
            return style_df

        return df.style.apply(style_func, axis=None)

    def create_data_bars(
        self,
        df: pd.DataFrame,
        columns: List[str],
        color: str = "#4CAF50",
        min_width: int = 0,
        max_width: int = 100,
    ) -> pd.DataFrame:
        """Create data bars for numeric columns."""
        styled_df = df.copy()

        for col in columns:
            if col not in df.columns:
                continue

            if pd.api.types.is_numeric_dtype(df[col]):
                min_val = df[col].min()
                max_val = df[col].max()
                range_val = max_val - min_val

                if range_val > 0:
                    # Calculate bar width percentages
                    bar_widths = (df[col] - min_val) / range_val * (
                        max_width - min_width
                    ) + min_width

                    # Create bar HTML
                    styled_df[col] = df[col].apply(
                        lambda x: f'<div style="background: linear-gradient(90deg, {color} {bar_widths.loc[df[col] == x].iloc[0]:.1f}%, transparent {bar_widths.loc[df[col] == x].iloc[0]:.1f}%); padding: 2px 5px;">{x}</div>'
                    )

        return styled_df

    def create_color_scales(
        self,
        df: pd.DataFrame,
        columns: List[str],
        color_map: str = "RdYlGn",
        reverse: bool = False,
    ) -> pd.DataFrame:
        """Apply color scales to numeric columns."""
        import matplotlib.cm as cm
        import matplotlib.colors as colors

        styled_df = df.copy()
        cmap = cm.get_cmap(color_map)

        if reverse:
            cmap = cmap.reversed()

        for col in columns:
            if col not in df.columns:
                continue

            if pd.api.types.is_numeric_dtype(df[col]):
                min_val = df[col].min()
                max_val = df[col].max()

                if min_val != max_val:
                    norm = colors.Normalize(vmin=min_val, vmax=max_val)

                    def apply_color(x):
                        if pd.isna(x):
                            return ""
                        rgba = cmap(norm(x))
                        return f"background-color: rgba({int(rgba[0] * 255)}, {int(rgba[1] * 255)}, {int(rgba[2] * 255)}, {rgba[3]})"

                    # Apply color to column
                    styled_df[col] = df[col].apply(
                        lambda x: f'<span style="{apply_color(x)}; padding: 2px 5px;">{x}</span>'
                    )

        return styled_df

    def highlight_outliers(
        self,
        df: pd.DataFrame,
        columns: List[str],
        method: str = "iqr",
        multiplier: float = 1.5,
        style: Optional[FormatStyle] = None,
    ) -> List[FormatRule]:
        """Create rules to highlight statistical outliers."""
        if style is None:
            style = FormatStyle(background_color="#ffeb3b", font_weight="bold")

        rules = []

        for col in columns:
            if col not in df.columns:
                continue

            if pd.api.types.is_numeric_dtype(df[col]):
                if method == "iqr":
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - multiplier * IQR
                    upper_bound = Q3 + multiplier * IQR

                    # Rule for lower outliers
                    rules.append(
                        FormatRule(
                            column=col,
                            condition=FormatCondition.LESS_THAN,
                            value=lower_bound,
                            style=style,
                            priority=10,
                        )
                    )

                    # Rule for upper outliers
                    rules.append(
                        FormatRule(
                            column=col,
                            condition=FormatCondition.GREATER_THAN,
                            value=upper_bound,
                            style=style,
                            priority=10,
                        )
                    )
                elif method == "zscore":
                    mean = df[col].mean()
                    std = df[col].std()
                    threshold = multiplier * std

                    # Rule for outliers beyond z-score threshold
                    rules.append(
                        FormatRule(
                            column=col,
                            condition=FormatCondition.NOT_BETWEEN,
                            value=mean - threshold,
                            value2=mean + threshold,
                            style=style,
                            priority=10,
                        )
                    )

        return rules
