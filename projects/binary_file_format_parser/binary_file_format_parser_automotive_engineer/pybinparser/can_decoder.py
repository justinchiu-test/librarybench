"""CAN Bus data structure mapping and decoding module."""

from typing import Dict, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, model_validator
import struct


class ByteOrder(str, Enum):
    """Byte order for signal encoding."""

    MOTOROLA = "motorola"  # Big-endian
    INTEL = "intel"  # Little-endian


class CANSignal(BaseModel):
    """Represents a signal within a CAN message."""

    name: str
    start_bit: int = Field(ge=0, le=63)
    length: int = Field(ge=1, le=64)
    byte_order: ByteOrder = ByteOrder.INTEL
    scale: float = 1.0
    offset: float = 0.0
    unit: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    @model_validator(mode="after")
    def validate_signal_bounds(self):
        if self.start_bit + self.length > 64:
            raise ValueError("Signal exceeds CAN frame boundaries")
        return self

    def decode(self, data: bytes) -> float:
        """Decode signal value from CAN data bytes."""
        if len(data) > 8:
            raise ValueError("CAN data cannot exceed 8 bytes")

        # Pad data to 8 bytes
        padded_data = data + b"\x00" * (8 - len(data))

        # Extract signal bits based on byte order
        if self.byte_order == ByteOrder.INTEL:
            # Little-endian: convert bytes directly
            value = int.from_bytes(padded_data, byteorder="little")
            signal_value = (value >> self.start_bit) & ((1 << self.length) - 1)
        else:
            # Big-endian (Motorola): need to handle bit indexing differently
            # For Motorola, start_bit counts from MSB of first byte
            byte_idx = self.start_bit // 8
            bit_idx = self.start_bit % 8

            signal_value = 0
            bits_read = 0

            while bits_read < self.length and byte_idx < len(padded_data):
                # Read bits from current byte
                bits_in_byte = min(8 - bit_idx, self.length - bits_read)
                mask = ((1 << bits_in_byte) - 1) << (8 - bit_idx - bits_in_byte)
                byte_val = (padded_data[byte_idx] & mask) >> (
                    8 - bit_idx - bits_in_byte
                )

                # Add to signal value
                signal_value = (signal_value << bits_in_byte) | byte_val

                # Move to next byte
                bits_read += bits_in_byte
                byte_idx += 1
                bit_idx = 0

        # Apply scale and offset
        physical_value = (signal_value * self.scale) + self.offset

        # Apply min/max constraints
        if self.min_value is not None:
            physical_value = max(physical_value, self.min_value)
        if self.max_value is not None:
            physical_value = min(physical_value, self.max_value)

        return physical_value

    def encode(self, value: float) -> Tuple[int, int]:
        """Encode physical value to raw signal value and mask."""
        # Apply scale and offset
        raw_value = int((value - self.offset) / self.scale)

        # Create mask for signal position
        mask = ((1 << self.length) - 1) << self.start_bit

        # Position the value
        positioned_value = (raw_value & ((1 << self.length) - 1)) << self.start_bit

        return positioned_value, mask


class CANMessage(BaseModel):
    """Represents a CAN message with its signals."""

    id: int = Field(ge=0)
    name: str
    length: int = Field(ge=1, le=8)
    signals: Dict[str, CANSignal] = {}
    is_extended: bool = False

    @model_validator(mode="after")
    def validate_id(self):
        max_id = 0x1FFFFFFF if self.is_extended else 0x7FF
        if self.id > max_id:
            raise ValueError(
                f"CAN ID {self.id} exceeds maximum for {'extended' if self.is_extended else 'standard'} frame"
            )
        return self

    def decode(self, data: bytes) -> Dict[str, float]:
        """Decode all signals from CAN data."""
        if len(data) != self.length:
            raise ValueError(f"Expected {self.length} bytes, got {len(data)}")

        decoded_signals = {}
        for signal_name, signal in self.signals.items():
            decoded_signals[signal_name] = signal.decode(data)

        return decoded_signals

    def encode(self, signal_values: Dict[str, float]) -> bytes:
        """Encode signal values into CAN data bytes."""
        # Start with zeros
        data_int = 0

        for signal_name, value in signal_values.items():
            if signal_name not in self.signals:
                raise ValueError(f"Unknown signal: {signal_name}")

            signal = self.signals[signal_name]
            positioned_value, mask = signal.encode(value)

            # Clear the bits where the signal will be placed and set new value
            data_int = (data_int & ~mask) | positioned_value

        # Convert to bytes
        if any(s.byte_order == ByteOrder.MOTOROLA for s in self.signals.values()):
            data = data_int.to_bytes(8, byteorder="big")
        else:
            data = data_int.to_bytes(8, byteorder="little")

        return data[: self.length]


class CANDecoder:
    """CAN message decoder with DBC-style signal definitions."""

    def __init__(self):
        self.messages: Dict[int, CANMessage] = {}

    def add_message(self, message: CANMessage) -> None:
        """Add a CAN message definition."""
        self.messages[message.id] = message

    def add_signal(self, message_id: int, signal: CANSignal) -> None:
        """Add a signal to an existing message."""
        if message_id not in self.messages:
            raise ValueError(f"Message ID {message_id} not found")

        self.messages[message_id].signals[signal.name] = signal

    def decode_message(self, can_id: int, data: bytes) -> Optional[Dict[str, float]]:
        """Decode a CAN message by ID."""
        if can_id not in self.messages:
            return None

        return self.messages[can_id].decode(data)

    def encode_message(self, can_id: int, signal_values: Dict[str, float]) -> bytes:
        """Encode signal values into CAN data."""
        if can_id not in self.messages:
            raise ValueError(f"Unknown CAN ID: {can_id}")

        return self.messages[can_id].encode(signal_values)

    def get_message_by_name(self, name: str) -> Optional[CANMessage]:
        """Get message definition by name."""
        for message in self.messages.values():
            if message.name == name:
                return message
        return None

    def parse_can_frame(
        self, frame_data: bytes
    ) -> Optional[Tuple[int, bytes, Dict[str, float]]]:
        """Parse a complete CAN frame (ID + data)."""
        if len(frame_data) < 4:
            raise ValueError("Invalid CAN frame data")

        # Extract CAN ID (assumes standard format with ID in first 4 bytes)
        can_id = struct.unpack(">I", frame_data[:4])[0]

        # Check if extended ID
        is_extended = (can_id & 0x80000000) != 0
        if is_extended:
            can_id &= 0x1FFFFFFF
        else:
            can_id &= 0x7FF

        # Extract data
        data = frame_data[4:]

        # Try to decode
        decoded = self.decode_message(can_id, data)

        return can_id, data, decoded if decoded else {}
