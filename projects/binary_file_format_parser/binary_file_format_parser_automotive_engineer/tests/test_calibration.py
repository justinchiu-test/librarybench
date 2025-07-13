"""Tests for sensor calibration data interpretation."""

import pytest
from pybinparser.calibration import (
    CalibrationDataExtractor,
    CalibrationTable,
    InterpolationMethod,
)
import struct


class TestCalibrationTable:
    """Test CalibrationTable functionality."""

    def test_1d_table_creation(self):
        """Test creating a 1D calibration table."""
        table = CalibrationTable(
            name="ThrottleMap",
            dimensions=1,
            x_axis=[0, 25, 50, 75, 100],
            values=[0, 10, 45, 80, 100],
            unit="%",
            interpolation=InterpolationMethod.LINEAR,
        )
        assert table.name == "ThrottleMap"
        assert table.dimensions == 1
        assert len(table.x_axis) == 5
        assert len(table.values) == 5

    def test_2d_table_creation(self):
        """Test creating a 2D calibration table."""
        table = CalibrationTable(
            name="FuelMap",
            dimensions=2,
            x_axis=[1000, 2000, 3000, 4000],  # RPM
            y_axis=[0, 25, 50, 75, 100],  # Load %
            values=[
                [10, 12, 14, 16],  # 0% load
                [12, 14, 16, 18],  # 25% load
                [14, 16, 18, 20],  # 50% load
                [16, 18, 20, 22],  # 75% load
                [18, 20, 22, 24],  # 100% load
            ],
            unit="ms",
        )
        assert table.dimensions == 2
        assert len(table.y_axis) == 5
        assert len(table.values) == 5
        assert len(table.values[0]) == 4

    def test_table_validation(self):
        """Test table dimension validation."""
        # Invalid dimensions
        with pytest.raises(ValueError):
            CalibrationTable(
                name="Invalid",
                dimensions=4,  # Only 1-3 supported
                x_axis=[1, 2, 3],
                values=[1, 2, 3],
            )

    def test_1d_interpolation_linear(self):
        """Test 1D linear interpolation."""
        table = CalibrationTable(
            name="Test",
            dimensions=1,
            x_axis=[0, 10, 20, 30],
            values=[0, 100, 150, 200],
            interpolation=InterpolationMethod.LINEAR,
        )

        # Exact points
        assert table.lookup(0) == 0
        assert table.lookup(10) == 100

        # Interpolated points
        assert table.lookup(5) == 50
        assert table.lookup(15) == 125
        assert table.lookup(25) == 175

        # Out of bounds
        assert table.lookup(-5) == 0  # Clamps to min
        assert table.lookup(35) == 200  # Clamps to max

    def test_1d_interpolation_nearest(self):
        """Test 1D nearest neighbor interpolation."""
        table = CalibrationTable(
            name="Test",
            dimensions=1,
            x_axis=[0, 10, 20],
            values=[0, 100, 200],
            interpolation=InterpolationMethod.NEAREST,
        )

        assert table.lookup(4) == 0  # Closer to 0
        assert table.lookup(6) == 100  # Closer to 10
        assert table.lookup(14) == 100  # Closer to 10
        assert table.lookup(16) == 200  # Closer to 20

    def test_2d_interpolation(self):
        """Test 2D bilinear interpolation."""
        table = CalibrationTable(
            name="Test",
            dimensions=2,
            x_axis=[0, 10],  # X axis
            y_axis=[0, 10],  # Y axis
            values=[
                [0, 10],  # y=0: values at x=0,10
                [20, 30],  # y=10: values at x=0,10
            ],
            interpolation=InterpolationMethod.LINEAR,
        )

        # Corner points
        assert table.lookup(0, 0) == 0
        assert table.lookup(10, 0) == 10
        assert table.lookup(0, 10) == 20
        assert table.lookup(10, 10) == 30

        # Center point (bilinear interpolation)
        assert table.lookup(5, 5) == 15

        # Edge interpolation
        assert table.lookup(5, 0) == 5  # Along x at y=0
        assert table.lookup(0, 5) == 10  # Along y at x=0

    def test_2d_interpolation_nearest(self):
        """Test 2D nearest neighbor interpolation."""
        table = CalibrationTable(
            name="Test",
            dimensions=2,
            x_axis=[0, 10],
            y_axis=[0, 10],
            values=[[0, 10], [20, 30]],
            interpolation=InterpolationMethod.NEAREST,
        )

        assert table.lookup(4, 4) == 0  # Closest to (0,0)
        assert table.lookup(6, 4) == 10  # Closest to (10,0)
        assert table.lookup(4, 6) == 20  # Closest to (0,10)
        assert table.lookup(6, 6) == 30  # Closest to (10,10)


class TestCalibrationDataExtractor:
    """Test CalibrationDataExtractor functionality."""

    def test_extractor_creation(self):
        """Test creating calibration data extractor."""
        extractor = CalibrationDataExtractor()
        assert len(extractor.tables) == 0
        assert len(extractor.correction_factors) == 0

    def test_add_table(self):
        """Test adding calibration table."""
        extractor = CalibrationDataExtractor()
        table = CalibrationTable(
            name="Test", dimensions=1, x_axis=[0, 100], values=[0, 100]
        )
        extractor.add_table(table)
        assert "Test" in extractor.tables

    def test_add_correction_factor(self):
        """Test adding correction factor."""
        extractor = CalibrationDataExtractor()
        extractor.add_correction_factor("Temperature", 1.05)
        assert extractor.correction_factors["Temperature"] == 1.05

    def test_parse_calibration_block_float(self):
        """Test parsing float calibration data."""
        extractor = CalibrationDataExtractor()

        # Create test data: 3 float values (big-endian)
        data = struct.pack(">fff", 10.0, 20.0, 30.0)

        format_spec = {
            "name": "TestTable",
            "offset": 0,
            "data_type": "float",
            "endian": "big",
            "dimensions": 1,
            "x_count": 2,
            "value_scale": 0.1,
            "unit": "V",
        }

        table = extractor.parse_calibration_block(data, format_spec)
        assert table.name == "TestTable"
        assert table.x_axis == [10.0, 20.0]
        assert table.values == [3.0]  # 30.0 * 0.1

    def test_parse_calibration_block_int16(self):
        """Test parsing int16 calibration data."""
        extractor = CalibrationDataExtractor()

        # Create test data: 2x2 table with int16 values
        x_data = struct.pack("<HH", 0, 1000)  # X axis
        y_data = struct.pack("<HH", 0, 100)  # Y axis
        values = struct.pack("<HHHH", 100, 200, 300, 400)  # 2x2 values
        data = x_data + y_data + values

        format_spec = {
            "name": "MAP",
            "offset": 0,
            "data_type": "uint16",
            "endian": "little",
            "dimensions": 2,
            "x_count": 2,
            "y_count": 2,
            "x_scale": 0.1,  # Scale x values
            "y_scale": 1.0,
            "value_scale": 0.01,  # Scale output values
            "unit": "kPa",
        }

        table = extractor.parse_calibration_block(data, format_spec)
        assert table.dimensions == 2
        assert table.x_axis == [0.0, 100.0]  # Scaled by 0.1
        assert table.y_axis == [0.0, 100.0]
        assert table.values[0][0] == 1.0  # 100 * 0.01
        assert table.values[1][1] == 4.0  # 400 * 0.01

    def test_apply_sensor_calibration_1d(self):
        """Test applying 1D sensor calibration."""
        extractor = CalibrationDataExtractor()

        # Add a voltage-to-temperature calibration table
        table = CalibrationTable(
            name="TempSensor",
            dimensions=1,
            x_axis=[0, 1, 2, 3, 4, 5],  # Voltage
            values=[-40, -20, 0, 25, 60, 100],  # Temperature
            unit="°C",
        )
        extractor.add_table(table)

        # Apply calibration
        voltage = 2.5
        temp = extractor.apply_sensor_calibration(voltage, "TempSensor")
        assert temp == pytest.approx(12.5)  # Linear interpolation between 0 and 25

    def test_apply_sensor_calibration_2d(self):
        """Test applying 2D sensor calibration with conditions."""
        extractor = CalibrationDataExtractor()

        # Add a pressure calibration table that depends on temperature
        table = CalibrationTable(
            name="PressureSensor",
            dimensions=2,
            x_axis=[0, 5],  # Voltage
            y_axis=[0, 100],  # Temperature
            values=[
                [0, 100],  # Pressure at temp=0
                [10, 110],  # Pressure at temp=100
            ],
            unit="kPa",
        )
        extractor.add_table(table)

        # Apply calibration with temperature condition
        voltage = 2.5
        conditions = {"temperature": 50}
        pressure = extractor.apply_sensor_calibration(
            voltage, "PressureSensor", conditions
        )
        assert pressure == pytest.approx(55.0)

    def test_apply_sensor_calibration_with_correction(self):
        """Test applying calibration with correction factor."""
        extractor = CalibrationDataExtractor()

        # Simple 1:1 calibration table
        table = CalibrationTable(
            name="Sensor", dimensions=1, x_axis=[0, 100], values=[0, 100]
        )
        extractor.add_table(table)

        # Add 5% correction factor
        extractor.add_correction_factor("Sensor", 1.05)

        value = extractor.apply_sensor_calibration(50, "Sensor")
        assert value == pytest.approx(52.5)  # 50 * 1.05

    def test_extract_calibration_from_memory(self):
        """Test extracting multiple calibration tables from memory."""
        extractor = CalibrationDataExtractor()

        # Create memory dump with two tables
        # Table 1 at offset 0: 2 floats
        table1_data = struct.pack(">ff", 1.0, 2.0)
        # Table 2 at offset 8: 4 uint16
        table2_data = struct.pack(">HHHH", 100, 200, 300, 400)

        memory_data = table1_data + table2_data

        calibration_map = {
            "Table1": {
                "offset": 0,
                "data_type": "float",
                "endian": "big",
                "dimensions": 1,
                "x_count": 1,
                "unit": "V",
            },
            "Table2": {
                "offset": 8,
                "data_type": "uint16",
                "endian": "big",
                "dimensions": 1,
                "x_count": 2,
                "unit": "ms",
            },
        }

        extracted = extractor.extract_calibration_from_memory(
            memory_data, calibration_map
        )

        assert len(extracted) == 2
        assert "Table1" in extracted
        assert "Table2" in extracted
        assert extractor.tables["Table1"].x_axis == [1.0]
        assert len(extractor.tables["Table1"].values) == 1
        assert extractor.tables["Table1"].values[0] == 2.0
        assert extractor.tables["Table2"].x_axis == [100, 200]
        assert len(extractor.tables["Table2"].values) == 2

    def test_unsupported_data_type(self):
        """Test handling unsupported data type."""
        extractor = CalibrationDataExtractor()

        format_spec = {"data_type": "unsupported", "dimensions": 1, "x_count": 1}

        with pytest.raises(ValueError):
            extractor.parse_calibration_block(b"\x00\x00", format_spec)
