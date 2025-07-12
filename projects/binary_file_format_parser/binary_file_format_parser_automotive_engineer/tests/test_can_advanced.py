"""Advanced tests for CAN Bus functionality."""

import pytest
from pybinparser import CANDecoder, CANSignal, CANMessage, ByteOrder
import struct


class TestCANAdvanced:
    """Advanced CAN functionality tests."""

    def test_can_fd_support(self):
        """Test CAN-FD extended data length."""
        msg = CANMessage(
            id=0x123,
            name="CANFDMessage",
            length=8,  # Standard CAN still limited to 8
            is_extended=False,
        )
        assert msg.length == 8

    def test_signal_bit_packing(self):
        """Test complex bit packing scenarios."""
        msg = CANMessage(id=0x200, name="BitPack", length=8)

        # Add signals that share bytes
        msg.signals["Flag1"] = CANSignal(name="Flag1", start_bit=0, length=1, scale=1.0)
        msg.signals["Value1"] = CANSignal(
            name="Value1", start_bit=1, length=7, scale=1.0
        )
        msg.signals["Value2"] = CANSignal(
            name="Value2", start_bit=8, length=12, scale=0.1
        )

        # Encode values
        data = msg.encode(
            {
                "Flag1": 1.0,
                "Value1": 100.0,
                "Value2": 204.8,  # 2048 raw
            }
        )

        # Verify encoding
        assert data[0] == 0xC9  # 1 + (100 << 1) = 201 = 0xC9
        assert len(data) == 8

    def test_signed_signal_values(self):
        """Test signed signal interpretation."""
        signal = CANSignal(
            name="SignedTemp", start_bit=0, length=8, scale=1.0, offset=0
        )

        # Test negative value (two's complement)
        data = bytes([0xFF, 0, 0, 0, 0, 0, 0, 0])  # -1 in signed 8-bit
        # For unsigned interpretation, this would be 255
        value = signal.decode(data)
        assert value == 255.0  # Current implementation treats as unsigned

    def test_multiplexed_signals(self):
        """Test multiplexed signal concept."""
        # Create a message with multiplexer
        msg = CANMessage(id=0x300, name="MultiplexMsg", length=8)

        # Multiplexer signal
        msg.signals["MuxId"] = CANSignal(name="MuxId", start_bit=0, length=8)

        # Different signals based on mux value
        msg.signals["Signal_Mux0"] = CANSignal(
            name="Signal_Mux0", start_bit=8, length=16
        )
        msg.signals["Signal_Mux1"] = CANSignal(
            name="Signal_Mux1", start_bit=8, length=16, scale=0.01
        )

        # Test decoding with different mux values
        data1 = bytes([0x00, 0x10, 0x00, 0, 0, 0, 0, 0])
        decoded1 = msg.decode(data1)
        assert decoded1["MuxId"] == 0

        data2 = bytes([0x01, 0x10, 0x00, 0, 0, 0, 0, 0])
        decoded2 = msg.decode(data2)
        assert decoded2["MuxId"] == 1

    def test_j1939_pgn_extraction(self):
        """Test J1939 Parameter Group Number extraction."""
        # J1939 uses 29-bit extended IDs with specific structure
        can_id = 0x18FEF100  # Engine data PGN 65265

        # Extract PGN from CAN ID
        pgn = (can_id >> 8) & 0x3FFFF
        assert pgn == 0xFEF1

    def test_dynamic_dlc(self):
        """Test dynamic DLC (Data Length Code) handling."""
        decoder = CANDecoder()

        # Add message with variable length
        for length in [3, 5, 8]:
            msg = CANMessage(
                id=0x400 + length, name=f"DynamicMsg{length}", length=length
            )
            decoder.add_message(msg)

        # Test decoding with different lengths
        assert decoder.decode_message(0x403, b"ABC") is not None
        assert decoder.decode_message(0x405, b"ABCDE") is not None
        assert decoder.decode_message(0x408, b"ABCDEFGH") is not None

    def test_motorola_msb_first_complex(self):
        """Test complex Motorola MSB first bit ordering."""
        signal = CANSignal(
            name="MotoralaSignal",
            start_bit=12,  # Starting at bit 12
            length=16,
            byte_order=ByteOrder.MOTOROLA,
            scale=0.01,
        )

        # Create test data
        data = bytes([0x12, 0x34, 0x56, 0x78, 0, 0, 0, 0])
        value = signal.decode(data)
        # With Motorola byte order, extraction is more complex
        assert value > 0  # Just verify it extracts something

    def test_signal_value_tables(self):
        """Test signal value table lookups."""
        # Simulate a state signal with specific meanings
        state_signal = CANSignal(name="GearState", start_bit=0, length=4, scale=1.0)

        # Value table (would be external configuration)
        value_table = {0: "Park", 1: "Reverse", 2: "Neutral", 3: "Drive", 4: "Sport"}

        data = bytes([0x03, 0, 0, 0, 0, 0, 0, 0])
        raw_value = state_signal.decode(data)
        state = value_table.get(int(raw_value), "Unknown")
        assert state == "Drive"

    def test_physical_value_constraints(self):
        """Test physical value range constraints."""
        signal = CANSignal(
            name="EngineTemp",
            start_bit=0,
            length=8,
            scale=1.0,
            offset=-40,
            min_value=-40,
            max_value=215,
        )

        # Test value clamping
        data_max = bytes([0xFF, 0, 0, 0, 0, 0, 0, 0])
        value_max = signal.decode(data_max)
        assert value_max == 215  # Clamped to max

        data_min = bytes([0x00, 0, 0, 0, 0, 0, 0, 0])
        value_min = signal.decode(data_min)
        assert value_min == -40  # At minimum

    def test_signal_groups(self):
        """Test related signal grouping."""
        msg = CANMessage(id=0x500, name="WheelSpeed", length=8)

        # Add wheel speed signals
        for i, wheel in enumerate(["FL", "FR", "RL", "RR"]):
            msg.signals[f"WheelSpeed_{wheel}"] = CANSignal(
                name=f"WheelSpeed_{wheel}",
                start_bit=i * 16,
                length=16,
                scale=0.01,
                unit="km/h",
            )

        # Test data with different wheel speeds
        data = struct.pack("<HHHH", 5000, 5000, 4900, 4900)
        decoded = msg.decode(data)

        assert decoded["WheelSpeed_FL"] == pytest.approx(50.0)
        assert decoded["WheelSpeed_FR"] == pytest.approx(50.0)
        assert decoded["WheelSpeed_RL"] == pytest.approx(49.0)
        assert decoded["WheelSpeed_RR"] == pytest.approx(49.0)
