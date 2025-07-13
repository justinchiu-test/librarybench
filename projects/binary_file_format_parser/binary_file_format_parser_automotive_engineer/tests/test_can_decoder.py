"""Tests for CAN Bus data structure mapping and decoding."""

import pytest
from pybinparser.can_decoder import CANDecoder, CANSignal, CANMessage, ByteOrder


class TestCANSignal:
    """Test CANSignal functionality."""

    def test_signal_creation(self):
        """Test creating a CAN signal."""
        signal = CANSignal(
            name="EngineSpeed",
            start_bit=0,
            length=16,
            byte_order=ByteOrder.INTEL,
            scale=0.25,
            offset=0,
            unit="rpm",
        )
        assert signal.name == "EngineSpeed"
        assert signal.scale == 0.25
        assert signal.unit == "rpm"

    def test_signal_validation(self):
        """Test signal boundary validation."""
        with pytest.raises(ValueError):
            CANSignal(
                name="Invalid",
                start_bit=60,
                length=8,  # Would exceed 64-bit boundary
            )

    def test_signal_decode_intel(self):
        """Test decoding Intel (little-endian) signal."""
        signal = CANSignal(
            name="Speed",
            start_bit=0,
            length=16,
            byte_order=ByteOrder.INTEL,
            scale=0.01,
            offset=0,
        )
        # Data: 0x1234 in little-endian = [0x34, 0x12]
        data = bytes([0x34, 0x12, 0, 0, 0, 0, 0, 0])
        value = signal.decode(data)
        assert value == pytest.approx(46.60)  # 0x1234 * 0.01

    def test_signal_decode_motorola(self):
        """Test decoding Motorola (big-endian) signal."""
        signal = CANSignal(
            name="Temperature",
            start_bit=0,
            length=8,
            byte_order=ByteOrder.MOTOROLA,
            scale=1.0,
            offset=-40,
        )
        data = bytes([0x64, 0, 0, 0, 0, 0, 0, 0])  # 100 decimal
        value = signal.decode(data)
        assert value == 60.0  # 100 - 40

    def test_signal_decode_with_limits(self):
        """Test signal decoding with min/max limits."""
        signal = CANSignal(
            name="Throttle",
            start_bit=0,
            length=8,
            scale=0.5,
            offset=0,
            min_value=0,
            max_value=100,
        )
        # Test value that would exceed max
        data = bytes([0xFF, 0, 0, 0, 0, 0, 0, 0])
        value = signal.decode(data)
        assert value == 100.0  # Clamped to max

    def test_signal_encode(self):
        """Test encoding physical value to raw signal."""
        signal = CANSignal(name="RPM", start_bit=8, length=16, scale=0.25, offset=0)
        positioned_value, mask = signal.encode(1000.0)
        # 1000 / 0.25 = 4000 = 0x0FA0
        # Positioned at bit 8: 0x0FA000
        assert positioned_value == 0x0FA000
        assert mask == 0xFFFF00


class TestCANMessage:
    """Test CANMessage functionality."""

    def test_message_creation(self):
        """Test creating a CAN message."""
        msg = CANMessage(id=0x100, name="EngineData", length=8, is_extended=False)
        assert msg.id == 0x100
        assert msg.name == "EngineData"
        assert msg.length == 8

    def test_message_id_validation(self):
        """Test CAN ID validation."""
        # Standard ID should not exceed 0x7FF
        with pytest.raises(ValueError):
            CANMessage(id=0x800, name="Invalid", length=8, is_extended=False)

        # Extended ID should not exceed 0x1FFFFFFF
        with pytest.raises(ValueError):
            CANMessage(id=0x20000000, name="Invalid", length=8, is_extended=True)

    def test_message_decode_multiple_signals(self):
        """Test decoding message with multiple signals."""
        msg = CANMessage(id=0x100, name="EngineData", length=8)

        # Add signals
        msg.signals["RPM"] = CANSignal(
            name="RPM", start_bit=0, length=16, scale=0.25, offset=0
        )
        msg.signals["Temperature"] = CANSignal(
            name="Temperature", start_bit=16, length=8, scale=1.0, offset=-40
        )
        msg.signals["Throttle"] = CANSignal(
            name="Throttle", start_bit=24, length=8, scale=0.392157, offset=0
        )

        # Test data
        data = bytes([0x10, 0x27, 0x78, 0x64, 0, 0, 0, 0])
        decoded = msg.decode(data)

        assert decoded["RPM"] == pytest.approx(2500.0)  # 0x2710 * 0.25
        assert decoded["Temperature"] == pytest.approx(80.0)  # 120 - 40
        assert decoded["Throttle"] == pytest.approx(39.2157)  # 100 * 0.392157

    def test_message_encode_signals(self):
        """Test encoding signal values into CAN data."""
        msg = CANMessage(id=0x200, name="ControlData", length=4)

        msg.signals["SetSpeed"] = CANSignal(
            name="SetSpeed", start_bit=0, length=16, scale=0.1, offset=0
        )
        msg.signals["Enable"] = CANSignal(
            name="Enable", start_bit=16, length=1, scale=1.0, offset=0
        )

        data = msg.encode(
            {
                "SetSpeed": 55.5,  # 555 raw
                "Enable": 1.0,
            }
        )

        assert len(data) == 4
        assert data[0] == 0x2B  # 555 & 0xFF
        assert data[1] == 0x02  # 555 >> 8
        assert data[2] & 0x01 == 1  # Enable bit set


class TestCANDecoder:
    """Test CANDecoder functionality."""

    def test_decoder_add_message(self):
        """Test adding messages to decoder."""
        decoder = CANDecoder()
        msg = CANMessage(id=0x100, name="TestMessage", length=8)
        decoder.add_message(msg)
        assert 0x100 in decoder.messages
        assert decoder.messages[0x100].name == "TestMessage"

    def test_decoder_add_signal(self):
        """Test adding signals to existing message."""
        decoder = CANDecoder()
        msg = CANMessage(id=0x100, name="Test", length=8)
        decoder.add_message(msg)

        signal = CANSignal(name="TestSignal", start_bit=0, length=8)
        decoder.add_signal(0x100, signal)

        assert "TestSignal" in decoder.messages[0x100].signals

    def test_decoder_decode_message(self):
        """Test decoding message by ID."""
        decoder = CANDecoder()

        # Set up a message with signals
        msg = CANMessage(id=0x123, name="SensorData", length=8)
        msg.signals["Sensor1"] = CANSignal(
            name="Sensor1", start_bit=0, length=16, scale=0.1
        )
        decoder.add_message(msg)

        # Decode
        data = bytes([0x64, 0x00, 0, 0, 0, 0, 0, 0])
        decoded = decoder.decode_message(0x123, data)
        assert decoded["Sensor1"] == pytest.approx(10.0)  # 100 * 0.1

        # Unknown ID should return None
        assert decoder.decode_message(0x999, data) is None

    def test_decoder_get_message_by_name(self):
        """Test finding message by name."""
        decoder = CANDecoder()
        msg = CANMessage(id=0x100, name="EngineData", length=8)
        decoder.add_message(msg)

        found = decoder.get_message_by_name("EngineData")
        assert found is not None
        assert found.id == 0x100

        assert decoder.get_message_by_name("NonExistent") is None

    def test_decoder_parse_can_frame(self):
        """Test parsing complete CAN frame."""
        decoder = CANDecoder()

        # Add a message
        msg = CANMessage(id=0x123, name="Test", length=4)
        msg.signals["Value"] = CANSignal(
            name="Value", start_bit=0, length=32, scale=1.0
        )
        decoder.add_message(msg)

        # Create frame: ID (4 bytes) + data
        frame = b"\x00\x00\x01\x23" + b"\x78\x56\x34\x12"

        can_id, data, decoded = decoder.parse_can_frame(frame)
        assert can_id == 0x123
        assert data == b"\x78\x56\x34\x12"
        assert decoded["Value"] == 0x12345678

    def test_extended_can_id_parsing(self):
        """Test parsing extended CAN ID."""
        decoder = CANDecoder()

        # Extended ID with bit 31 set
        frame = b"\x80\x00\x12\x34" + b"\x00\x00\x00\x00"
        can_id, data, decoded = decoder.parse_can_frame(frame)

        # Should mask to 29-bit extended ID
        assert can_id == 0x1234
        assert len(data) == 4
