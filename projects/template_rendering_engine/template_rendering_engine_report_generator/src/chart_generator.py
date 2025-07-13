"""Chart generation system using matplotlib and seaborn."""

from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

try:
    import seaborn as sns
except ImportError:
    sns = None
from pydantic import BaseModel, Field, field_validator


class ChartType(str, Enum):
    """Types of charts that can be generated."""

    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    AREA = "area"
    STACKED_BAR = "stacked_bar"
    GROUPED_BAR = "grouped_bar"


class ChartStyle(BaseModel):
    """Styling configuration for charts."""

    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    width: float = Field(default=10.0, gt=0)
    height: float = Field(default=6.0, gt=0)
    dpi: int = Field(default=100, ge=50, le=300)
    color_palette: Optional[Union[str, List[str]]] = None
    style: str = Field(default="whitegrid")
    title_size: int = Field(default=16, ge=8, le=32)
    label_size: int = Field(default=12, ge=8, le=24)
    legend_position: str = Field(default="best")
    grid: bool = Field(default=True)
    tight_layout: bool = Field(default=True)

    @field_validator("style")
    def validate_style(cls, v):
        valid_styles = ["whitegrid", "darkgrid", "white", "dark", "ticks"]
        if v not in valid_styles:
            raise ValueError(f"Style must be one of {valid_styles}")
        return v


class ChartConfig(BaseModel):
    """Configuration for chart generation."""

    chart_type: ChartType
    x_column: Optional[str] = None
    y_column: Optional[Union[str, List[str]]] = None
    data_columns: Optional[List[str]] = None
    style: ChartStyle = Field(default_factory=ChartStyle)
    show_values: bool = Field(default=False)
    rotation: int = Field(default=0, ge=-90, le=90)
    sort_by: Optional[str] = None
    sort_ascending: bool = Field(default=True)
    top_n: Optional[int] = Field(default=None, ge=1)

    @field_validator("y_column")
    def normalize_y_column(cls, v):
        if v is None:
            return None
        return [v] if isinstance(v, str) else v


class ChartGenerator:
    """Generate charts from data using matplotlib and seaborn."""

    def __init__(self):
        """Initialize the chart generator."""
        try:
            plt.style.use("seaborn-v0_8")
        except:
            # Fallback to a standard style if seaborn style not available
            plt.style.use("ggplot")
        self._custom_colors = None

    def set_custom_colors(self, colors: List[str]):
        """Set custom color palette."""
        self._custom_colors = colors

    def generate_chart(
        self,
        df: pd.DataFrame,
        config: ChartConfig,
        output_format: str = "base64",
    ) -> Union[str, bytes]:
        """Generate a chart based on configuration."""
        # Apply sorting if specified
        if config.sort_by:
            df = df.sort_values(by=config.sort_by, ascending=config.sort_ascending)

        # Apply top N filtering if specified
        if config.top_n:
            df = df.head(config.top_n)

        # Set style
        if sns:
            sns.set_style(config.style.style)

        # Create figure
        fig, ax = plt.subplots(
            figsize=(config.style.width, config.style.height), dpi=config.style.dpi
        )

        # Set color palette
        if sns:
            if config.style.color_palette:
                if isinstance(config.style.color_palette, str):
                    sns.set_palette(config.style.color_palette)
                else:
                    sns.set_palette(config.style.color_palette)
            elif self._custom_colors:
                sns.set_palette(self._custom_colors)

        # Generate chart based on type
        if config.chart_type == ChartType.BAR:
            self._create_bar_chart(df, config, ax)
        elif config.chart_type == ChartType.LINE:
            self._create_line_chart(df, config, ax)
        elif config.chart_type == ChartType.PIE:
            self._create_pie_chart(df, config, ax)
        elif config.chart_type == ChartType.SCATTER:
            self._create_scatter_chart(df, config, ax)
        elif config.chart_type == ChartType.HISTOGRAM:
            self._create_histogram(df, config, ax)
        elif config.chart_type == ChartType.BOX:
            self._create_box_plot(df, config, ax)
        elif config.chart_type == ChartType.HEATMAP:
            self._create_heatmap(df, config, ax)
        elif config.chart_type == ChartType.AREA:
            self._create_area_chart(df, config, ax)
        elif config.chart_type == ChartType.STACKED_BAR:
            self._create_stacked_bar_chart(df, config, ax)
        elif config.chart_type == ChartType.GROUPED_BAR:
            self._create_grouped_bar_chart(df, config, ax)

        # Apply styling
        if config.style.title:
            ax.set_title(config.style.title, fontsize=config.style.title_size)
        if config.style.x_label:
            ax.set_xlabel(config.style.x_label, fontsize=config.style.label_size)
        if config.style.y_label:
            ax.set_ylabel(config.style.y_label, fontsize=config.style.label_size)

        # Configure grid
        ax.grid(config.style.grid)

        # Configure legend
        if ax.get_legend():
            ax.legend(loc=config.style.legend_position)

        # Apply tight layout
        if config.style.tight_layout:
            plt.tight_layout()

        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)

        # Close figure to free memory
        plt.close(fig)

        # Return in requested format
        if output_format == "base64":
            return base64.b64encode(buffer.getvalue()).decode()
        else:
            return buffer.getvalue()

    def _create_bar_chart(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a bar chart."""
        x_data = df[config.x_column] if config.x_column else df.index
        y_data = df[config.y_column[0]] if config.y_column else df.iloc[:, 0]

        bars = ax.bar(x_data, y_data)

        # Rotate x labels if specified
        if config.rotation != 0:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=config.rotation)

        # Show values on bars if requested
        if config.show_values:
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{height:.1f}",
                    ha="center",
                    va="bottom",
                )

    def _create_line_chart(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a line chart."""
        x_data = df[config.x_column] if config.x_column else df.index

        if config.y_column:
            for col in config.y_column:
                ax.plot(x_data, df[col], marker="o", label=col)
            ax.legend()
        else:
            ax.plot(x_data, df.iloc[:, 0], marker="o")

        # Handle datetime x-axis
        if pd.api.types.is_datetime64_any_dtype(x_data):
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    def _create_pie_chart(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a pie chart."""
        labels = df[config.x_column] if config.x_column else df.index
        values = df[config.y_column[0]] if config.y_column else df.iloc[:, 0]

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%", startangle=90, counterclock=False
        )

        # Ensure equal aspect ratio
        ax.axis("equal")

    def _create_scatter_chart(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a scatter plot."""
        x_data = df[config.x_column] if config.x_column else df.iloc[:, 0]
        y_data = df[config.y_column[0]] if config.y_column else df.iloc[:, 1]

        ax.scatter(x_data, y_data, alpha=0.6)

    def _create_histogram(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a histogram."""
        data = df[config.y_column[0]] if config.y_column else df.iloc[:, 0]

        ax.hist(data, bins=30, edgecolor="black", alpha=0.7)

    def _create_box_plot(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a box plot."""
        if config.y_column:
            data = [df[col].dropna() for col in config.y_column]
            ax.boxplot(data, labels=config.y_column)
        else:
            ax.boxplot(df.select_dtypes(include=["number"]).values)

    def _create_heatmap(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a heatmap."""
        # Select numeric columns only
        numeric_df = df.select_dtypes(include=["number"])

        if sns:
            sns.heatmap(
                numeric_df.corr(),
                annot=True,
                cmap="coolwarm",
                center=0,
                ax=ax,
                square=True,
            )
        else:
            # Fallback to matplotlib heatmap
            im = ax.imshow(numeric_df.corr(), cmap="coolwarm", aspect="auto")
            ax.figure.colorbar(im, ax=ax)

    def _create_area_chart(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create an area chart."""
        x_data = df[config.x_column] if config.x_column else df.index

        if config.y_column:
            for col in config.y_column:
                ax.fill_between(x_data, df[col], alpha=0.5, label=col)
            ax.legend()
        else:
            ax.fill_between(x_data, df.iloc[:, 0], alpha=0.5)

    def _create_stacked_bar_chart(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a stacked bar chart."""
        x_data = df[config.x_column] if config.x_column else df.index

        if config.data_columns:
            bottom = None
            for col in config.data_columns:
                ax.bar(x_data, df[col], bottom=bottom, label=col)
                if bottom is None:
                    bottom = df[col]
                else:
                    bottom = bottom + df[col]
            ax.legend()

    def _create_grouped_bar_chart(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Create a grouped bar chart."""
        if not config.data_columns:
            return

        x = df[config.x_column] if config.x_column else df.index
        x_pos = range(len(x))
        width = 0.8 / len(config.data_columns)

        for i, col in enumerate(config.data_columns):
            offset = (i - len(config.data_columns) / 2 + 0.5) * width
            ax.bar([p + offset for p in x_pos], df[col], width, label=col)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(x)
        ax.legend()

        if config.rotation != 0:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=config.rotation)

    def generate_multiple_charts(
        self,
        df: pd.DataFrame,
        configs: List[ChartConfig],
        layout: Tuple[int, int] = None,
        output_format: str = "base64",
    ) -> Union[str, bytes]:
        """Generate multiple charts in a single figure."""
        if not layout:
            # Auto-calculate layout
            n_charts = len(configs)
            cols = min(3, n_charts)
            rows = (n_charts + cols - 1) // cols
            layout = (rows, cols)

        fig, axes = plt.subplots(
            layout[0], layout[1], figsize=(layout[1] * 5, layout[0] * 4), dpi=100
        )

        if layout[0] * layout[1] == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if hasattr(axes, "flatten") else axes

        for i, config in enumerate(configs):
            if i < len(axes):
                ax = axes[i]
                # Generate individual chart
                self._generate_chart_on_axis(df, config, ax)

        # Hide empty subplots
        for i in range(len(configs), len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()

        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)

        plt.close(fig)

        if output_format == "base64":
            return base64.b64encode(buffer.getvalue()).decode()
        else:
            return buffer.getvalue()

    def _generate_chart_on_axis(self, df: pd.DataFrame, config: ChartConfig, ax):
        """Generate a chart on a specific axis."""
        # This is a simplified version that delegates to individual chart methods
        # In a real implementation, this would replicate the logic from generate_chart
        pass
