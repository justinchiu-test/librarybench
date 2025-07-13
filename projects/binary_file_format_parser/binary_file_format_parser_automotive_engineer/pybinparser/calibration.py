"""Sensor calibration data interpretation module."""

from typing import Dict, List, Union, Optional
from enum import Enum
import struct
from pydantic import BaseModel, Field, field_validator, model_validator


class InterpolationMethod(str, Enum):
    """Interpolation methods for calibration data."""

    LINEAR = "linear"
    CUBIC = "cubic"
    NEAREST = "nearest"


class CalibrationTable(BaseModel):
    """Represents a calibration table or curve."""

    name: str
    dimensions: int = Field(ge=1, le=3)
    x_axis: List[float] = []
    y_axis: Optional[List[float]] = None
    z_axis: Optional[List[float]] = None
    values: List[Union[float, List[float], List[List[float]]]] = []
    unit: str = ""
    interpolation: InterpolationMethod = InterpolationMethod.LINEAR

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("Calibration tables support 1D, 2D, or 3D only")
        return v

    @model_validator(mode="after")
    def validate_values_shape(self):
        if self.x_axis and self.values:
            x_len = len(self.x_axis)

            if self.dimensions == 1:
                # For 1D tables, we don't enforce strict length matching
                # as values can be independent of x_axis length
                pass
            elif self.dimensions == 2 and self.y_axis:
                y_len = len(self.y_axis)
                if len(self.values) != y_len:
                    raise ValueError(
                        f"2D table rows {len(self.values)} doesn't match y_axis length {y_len}"
                    )
                for row in self.values:
                    if len(row) != x_len:
                        raise ValueError(
                            f"2D table column count doesn't match x_axis length {x_len}"
                        )
        return self

    def interpolate_1d(self, x: float) -> float:
        """Interpolate value from 1D table."""
        if not self.x_axis or not self.values:
            raise ValueError("Empty calibration table")

        # Handle out of bounds
        if x <= self.x_axis[0]:
            return self.values[0]
        if x >= self.x_axis[-1]:
            return self.values[-1]

        # Find surrounding points
        for i in range(len(self.x_axis) - 1):
            if self.x_axis[i] <= x <= self.x_axis[i + 1]:
                if self.interpolation == InterpolationMethod.NEAREST:
                    # Return nearest point
                    if abs(x - self.x_axis[i]) < abs(x - self.x_axis[i + 1]):
                        return self.values[i]
                    else:
                        return self.values[i + 1]
                else:  # LINEAR
                    # Linear interpolation
                    x1, x2 = self.x_axis[i], self.x_axis[i + 1]
                    y1, y2 = self.values[i], self.values[i + 1]
                    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

        return self.values[-1]

    def interpolate_2d(self, x: float, y: float) -> float:
        """Interpolate value from 2D table."""
        if not self.x_axis or not self.y_axis or not self.values:
            raise ValueError("Empty calibration table")

        # Find x indices
        x_idx1, x_idx2 = 0, 0
        for i in range(len(self.x_axis) - 1):
            if self.x_axis[i] <= x <= self.x_axis[i + 1]:
                x_idx1, x_idx2 = i, i + 1
                break
        else:
            if x < self.x_axis[0]:
                x_idx1 = x_idx2 = 0
            else:
                x_idx1 = x_idx2 = len(self.x_axis) - 1

        # Find y indices
        y_idx1, y_idx2 = 0, 0
        for i in range(len(self.y_axis) - 1):
            if self.y_axis[i] <= y <= self.y_axis[i + 1]:
                y_idx1, y_idx2 = i, i + 1
                break
        else:
            if y < self.y_axis[0]:
                y_idx1 = y_idx2 = 0
            else:
                y_idx1 = y_idx2 = len(self.y_axis) - 1

        if self.interpolation == InterpolationMethod.NEAREST:
            # Return nearest point
            x_nearest = (
                x_idx1
                if abs(x - self.x_axis[x_idx1]) < abs(x - self.x_axis[x_idx2])
                else x_idx2
            )
            y_nearest = (
                y_idx1
                if abs(y - self.y_axis[y_idx1]) < abs(y - self.y_axis[y_idx2])
                else y_idx2
            )
            return self.values[y_nearest][x_nearest]

        # Bilinear interpolation
        if x_idx1 == x_idx2 and y_idx1 == y_idx2:
            return self.values[y_idx1][x_idx1]
        elif x_idx1 == x_idx2:
            # Interpolate in y direction only
            y1, y2 = self.y_axis[y_idx1], self.y_axis[y_idx2]
            v1, v2 = self.values[y_idx1][x_idx1], self.values[y_idx2][x_idx1]
            return v1 + (v2 - v1) * (y - y1) / (y2 - y1)
        elif y_idx1 == y_idx2:
            # Interpolate in x direction only
            x1, x2 = self.x_axis[x_idx1], self.x_axis[x_idx2]
            v1, v2 = self.values[y_idx1][x_idx1], self.values[y_idx1][x_idx2]
            return v1 + (v2 - v1) * (x - x1) / (x2 - x1)
        else:
            # Full bilinear interpolation
            x1, x2 = self.x_axis[x_idx1], self.x_axis[x_idx2]
            y1, y2 = self.y_axis[y_idx1], self.y_axis[y_idx2]

            # Get corner values
            v11 = self.values[y_idx1][x_idx1]
            v12 = self.values[y_idx1][x_idx2]
            v21 = self.values[y_idx2][x_idx1]
            v22 = self.values[y_idx2][x_idx2]

            # Interpolate in x direction for both y values
            vx1 = v11 + (v12 - v11) * (x - x1) / (x2 - x1)
            vx2 = v21 + (v22 - v21) * (x - x1) / (x2 - x1)

            # Interpolate in y direction
            return vx1 + (vx2 - vx1) * (y - y1) / (y2 - y1)

    def lookup(self, *args) -> float:
        """Look up value in calibration table."""
        if self.dimensions == 1:
            if len(args) != 1:
                raise ValueError("1D table requires exactly one input")
            return self.interpolate_1d(args[0])
        elif self.dimensions == 2:
            if len(args) != 2:
                raise ValueError("2D table requires exactly two inputs")
            return self.interpolate_2d(args[0], args[1])
        else:
            raise NotImplementedError("3D interpolation not yet implemented")


class CalibrationDataExtractor:
    """Extracts and interprets sensor calibration data from ECU memory."""

    def __init__(self):
        self.tables: Dict[str, CalibrationTable] = {}
        self.correction_factors: Dict[str, float] = {}

    def add_table(self, table: CalibrationTable) -> None:
        """Add a calibration table."""
        self.tables[table.name] = table

    def add_correction_factor(self, name: str, factor: float) -> None:
        """Add a correction factor."""
        self.correction_factors[name] = factor

    def parse_calibration_block(
        self, data: bytes, format_spec: Dict
    ) -> CalibrationTable:
        """Parse a calibration data block based on format specification."""
        offset = format_spec.get("offset", 0)
        data_type = format_spec.get("data_type", "float")
        endian = format_spec.get("endian", "big")

        # Determine struct format
        endian_char = ">" if endian == "big" else "<"
        if data_type == "float":
            fmt = f"{endian_char}f"
            size = 4
        elif data_type == "double":
            fmt = f"{endian_char}d"
            size = 8
        elif data_type == "int16":
            fmt = f"{endian_char}h"
            size = 2
        elif data_type == "uint16":
            fmt = f"{endian_char}H"
            size = 2
        elif data_type == "int32":
            fmt = f"{endian_char}i"
            size = 4
        elif data_type == "uint32":
            fmt = f"{endian_char}I"
            size = 4
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

        # Extract dimensions
        dims = format_spec.get("dimensions", 1)
        x_count = format_spec.get("x_count", 0)
        y_count = format_spec.get("y_count", 0)

        # Parse axis values
        x_axis = []
        current_offset = offset
        for _ in range(x_count):
            if current_offset + size <= len(data):
                value = struct.unpack(
                    fmt, data[current_offset : current_offset + size]
                )[0]
                if "x_scale" in format_spec:
                    value *= format_spec["x_scale"]
                if "x_offset" in format_spec:
                    value += format_spec["x_offset"]
                x_axis.append(value)
                current_offset += size

        y_axis = None
        if dims >= 2:
            y_axis = []
            for _ in range(y_count):
                if current_offset + size <= len(data):
                    value = struct.unpack(
                        fmt, data[current_offset : current_offset + size]
                    )[0]
                    if "y_scale" in format_spec:
                        value *= format_spec["y_scale"]
                    if "y_offset" in format_spec:
                        value += format_spec["y_offset"]
                    y_axis.append(value)
                    current_offset += size

        # Parse values
        values = []
        if dims == 1:
            # For 1D tables, read values corresponding to x_count
            value_count = format_spec.get("value_count", x_count)
            for _ in range(value_count):
                if current_offset + size <= len(data):
                    value = struct.unpack(
                        fmt, data[current_offset : current_offset + size]
                    )[0]
                    if "value_scale" in format_spec:
                        value *= format_spec["value_scale"]
                    if "value_offset" in format_spec:
                        value += format_spec["value_offset"]
                    values.append(value)
                    current_offset += size
        elif dims == 2:
            for _ in range(y_count):
                row = []
                for _ in range(x_count):
                    if current_offset + size <= len(data):
                        value = struct.unpack(
                            fmt, data[current_offset : current_offset + size]
                        )[0]
                        if "value_scale" in format_spec:
                            value *= format_spec["value_scale"]
                        if "value_offset" in format_spec:
                            value += format_spec["value_offset"]
                        row.append(value)
                        current_offset += size
                values.append(row)

        return CalibrationTable(
            name=format_spec.get("name", "Unknown"),
            dimensions=dims,
            x_axis=x_axis,
            y_axis=y_axis,
            values=values,
            unit=format_spec.get("unit", ""),
            interpolation=InterpolationMethod(
                format_spec.get("interpolation", "linear")
            ),
        )

    def apply_sensor_calibration(
        self,
        raw_value: float,
        sensor_name: str,
        conditions: Optional[Dict[str, float]] = None,
    ) -> float:
        """Apply calibration to raw sensor value."""
        if sensor_name not in self.tables:
            # No calibration available, return raw value
            return raw_value

        table = self.tables[sensor_name]

        # Apply calibration based on table dimensions
        if table.dimensions == 1:
            calibrated_value = table.lookup(raw_value)
        elif table.dimensions == 2 and conditions:
            # Use condition (e.g., temperature) as second dimension
            condition_key = list(conditions.keys())[0] if conditions else None
            if condition_key and condition_key in conditions:
                calibrated_value = table.lookup(raw_value, conditions[condition_key])
            else:
                calibrated_value = raw_value
        else:
            calibrated_value = raw_value

        # Apply correction factor if available
        if sensor_name in self.correction_factors:
            calibrated_value *= self.correction_factors[sensor_name]

        return calibrated_value

    def extract_calibration_from_memory(
        self, memory_data: bytes, calibration_map: Dict[str, Dict]
    ) -> Dict[str, CalibrationTable]:
        """Extract multiple calibration tables from memory dump."""
        extracted_tables = {}

        for table_name, table_spec in calibration_map.items():
            try:
                # Add the table name to the spec
                table_spec["name"] = table_name
                table = self.parse_calibration_block(memory_data, table_spec)
                self.add_table(table)
                extracted_tables[table_name] = table
            except Exception as e:
                # Log error but continue with other tables
                print(f"Failed to extract calibration table {table_name}: {e}")

        return extracted_tables
