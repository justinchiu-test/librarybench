"""Tests for chart generation system."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import base64
import io

from src.chart_generator import (
    ChartGenerator,
    ChartType,
    ChartStyle,
    ChartConfig,
)


class TestChartStyle:
    """Test chart style configuration."""

    def test_default_style(self):
        """Test default chart style settings."""
        style = ChartStyle()
        assert style.width == 10.0
        assert style.height == 6.0
        assert style.dpi == 100
        assert style.style == "whitegrid"
        assert style.title_size == 16
        assert style.grid == True

    def test_custom_style(self):
        """Test custom chart style settings."""
        style = ChartStyle(
            title="Test Chart",
            x_label="X Axis",
            y_label="Y Axis",
            width=12.0,
            height=8.0,
            color_palette="Set2",
            style="darkgrid",
        )
        assert style.title == "Test Chart"
        assert style.x_label == "X Axis"
        assert style.color_palette == "Set2"
        assert style.style == "darkgrid"

    def test_invalid_style(self):
        """Test invalid style validation."""
        with pytest.raises(ValueError):
            ChartStyle(style="invalid_style")

    def test_size_validation(self):
        """Test size parameter validation."""
        with pytest.raises(ValueError):
            ChartStyle(width=-1)

        with pytest.raises(ValueError):
            ChartStyle(dpi=400)  # Max is 300


class TestChartConfig:
    """Test chart configuration."""

    def test_basic_config(self):
        """Test basic chart configuration."""
        config = ChartConfig(
            chart_type=ChartType.BAR, x_column="category", y_column="value"
        )
        assert config.chart_type == ChartType.BAR
        assert config.x_column == "category"
        assert config.y_column == ["value"]  # Normalized to list

    def test_multiple_y_columns(self):
        """Test configuration with multiple Y columns."""
        config = ChartConfig(
            chart_type=ChartType.LINE,
            x_column="date",
            y_column=["sales", "profit", "costs"],
        )
        assert len(config.y_column) == 3
        assert "profit" in config.y_column

    def test_sorting_config(self):
        """Test sorting configuration."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="name",
            y_column="value",
            sort_by="value",
            sort_ascending=False,
            top_n=10,
        )
        assert config.sort_by == "value"
        assert config.sort_ascending == False
        assert config.top_n == 10


class TestChartGenerator:
    """Test chart generation functionality."""

    @pytest.fixture
    def generator(self):
        """Create a test chart generator."""
        return ChartGenerator()

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "category": ["A", "B", "C", "D", "E"],
                "value": [100, 200, 150, 300, 250],
                "value2": [80, 180, 140, 280, 240],
                "date": pd.date_range("2024-01-01", periods=5),
                "group": ["X", "Y", "X", "Y", "X"],
            }
        )

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_bar_chart(self, mock_close, mock_savefig, generator, sample_df):
        """Test bar chart generation."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            style=ChartStyle(title="Test Bar Chart"),
        )

        # Mock the buffer writing
        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"fake_image_data")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        # Verify result is base64 encoded
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        assert decoded == b"fake_image_data"

        # Verify plot was closed
        mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_line_chart(self, mock_close, mock_savefig, generator, sample_df):
        """Test line chart generation."""
        config = ChartConfig(
            chart_type=ChartType.LINE,
            x_column="date",
            y_column=["value", "value2"],
            style=ChartStyle(title="Multi-line Chart"),
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"line_chart_data")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)
        assert base64.b64decode(result) == b"line_chart_data"

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_pie_chart(self, mock_close, mock_savefig, generator, sample_df):
        """Test pie chart generation."""
        config = ChartConfig(
            chart_type=ChartType.PIE, x_column="category", y_column="value"
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"pie_chart_data")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)
        assert base64.b64decode(result) == b"pie_chart_data"

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_scatter_chart(
        self, mock_close, mock_savefig, generator, sample_df
    ):
        """Test scatter plot generation."""
        config = ChartConfig(
            chart_type=ChartType.SCATTER, x_column="value", y_column="value2"
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"scatter_data")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_histogram(self, mock_close, mock_savefig, generator, sample_df):
        """Test histogram generation."""
        config = ChartConfig(chart_type=ChartType.HISTOGRAM, y_column="value")

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"histogram_data")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_box_plot(self, mock_close, mock_savefig, generator, sample_df):
        """Test box plot generation."""
        config = ChartConfig(chart_type=ChartType.BOX, y_column=["value", "value2"])

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"box_plot_data")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("src.chart_generator.sns")
    def test_generate_heatmap(
        self, mock_sns, mock_close, mock_savefig, generator, sample_df
    ):
        """Test heatmap generation."""
        config = ChartConfig(chart_type=ChartType.HEATMAP)

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"heatmap_data")

        mock_savefig.side_effect = save_to_buffer

        # Mock sns methods
        if mock_sns:
            mock_sns.heatmap = Mock()

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_chart_with_sorting(self, mock_close, mock_savefig, generator, sample_df):
        """Test chart generation with data sorting."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            sort_by="value",
            sort_ascending=False,
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"sorted_chart")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_chart_with_top_n(self, mock_close, mock_savefig, generator, sample_df):
        """Test chart generation with top N filtering."""
        config = ChartConfig(
            chart_type=ChartType.BAR, x_column="category", y_column="value", top_n=3
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"top_n_chart")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_output_format_bytes(self, mock_close, mock_savefig, generator, sample_df):
        """Test chart generation with bytes output format."""
        config = ChartConfig(
            chart_type=ChartType.BAR, x_column="category", y_column="value"
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"raw_bytes_data")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config, output_format="bytes")

        assert isinstance(result, bytes)
        assert result == b"raw_bytes_data"

    def test_set_custom_colors(self, generator):
        """Test setting custom color palette."""
        colors = ["#FF0000", "#00FF00", "#0000FF"]
        generator.set_custom_colors(colors)

        assert generator._custom_colors == colors

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_area_chart(self, mock_close, mock_savefig, generator, sample_df):
        """Test area chart generation."""
        config = ChartConfig(
            chart_type=ChartType.AREA, x_column="date", y_column="value"
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"area_chart")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_stacked_bar_chart(
        self, mock_close, mock_savefig, generator, sample_df
    ):
        """Test stacked bar chart generation."""
        config = ChartConfig(
            chart_type=ChartType.STACKED_BAR,
            x_column="category",
            data_columns=["value", "value2"],
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"stacked_bar")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_grouped_bar_chart(
        self, mock_close, mock_savefig, generator, sample_df
    ):
        """Test grouped bar chart generation."""
        config = ChartConfig(
            chart_type=ChartType.GROUPED_BAR,
            x_column="category",
            data_columns=["value", "value2"],
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"grouped_bar")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.subplots")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_multiple_charts(
        self, mock_close, mock_savefig, mock_subplots, generator, sample_df
    ):
        """Test generating multiple charts in one figure."""
        # Mock subplots
        fig_mock = Mock()
        ax_mock = Mock()
        mock_subplots.return_value = (
            fig_mock,
            [[ax_mock, ax_mock], [ax_mock, ax_mock]],
        )

        configs = [
            ChartConfig(
                chart_type=ChartType.BAR, x_column="category", y_column="value"
            ),
            ChartConfig(chart_type=ChartType.LINE, x_column="date", y_column="value"),
            ChartConfig(
                chart_type=ChartType.PIE, x_column="category", y_column="value"
            ),
        ]

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"multiple_charts")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_multiple_charts(sample_df, configs, layout=(2, 2))

        assert isinstance(result, str)
        mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_chart_with_show_values(
        self, mock_close, mock_savefig, generator, sample_df
    ):
        """Test bar chart with value labels."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            show_values=True,
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"chart_with_values")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_chart_with_rotation(self, mock_close, mock_savefig, generator, sample_df):
        """Test chart with rotated labels."""
        config = ChartConfig(
            chart_type=ChartType.BAR, x_column="category", y_column="value", rotation=45
        )

        def save_to_buffer(buffer, **kwargs):
            buffer.write(b"rotated_labels")

        mock_savefig.side_effect = save_to_buffer

        result = generator.generate_chart(sample_df, config)

        assert isinstance(result, str)
