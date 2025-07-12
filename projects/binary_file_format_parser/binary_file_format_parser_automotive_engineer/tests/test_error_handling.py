"""Tests for error handling and edge cases."""

import pytest
from pybinparser import (
    CANDecoder,
    CANSignal,
    CANMessage,
    DTCParser,
    CalibrationTable,
    FlashMemoryAnalyzer,
    MemoryRegion,
    MemoryRegionType,
    SecurityKeyDeriver,
    SecurityAlgorithm,
)


class TestErrorHandling:
    """Test error handling across all modules."""

    def test_can_invalid_data_length(self):
        """Test CAN decoding with invalid data length."""
        msg = CANMessage(id=0x100, name="Test", length=8)

        # Data too short
        with pytest.raises(ValueError):
            msg.decode(bytes([0x01, 0x02]))  # Only 2 bytes, expects 8

        # Data too long
        with pytest.raises(ValueError):
            msg.decode(bytes(range(10)))  # 10 bytes, expects 8

    def test_can_invalid_signal_position(self):
        """Test invalid signal bit positions."""
        # Signal exceeds frame boundary
        with pytest.raises(ValueError):
            CANSignal(
                name="Invalid",
                start_bit=60,
                length=8,  # Would need bits 60-67, but max is 63
            )

    def test_dtc_invalid_format(self):
        """Test DTC parsing with invalid format."""
        parser = DTCParser()

        # Invalid data length for ISO 14229
        with pytest.raises(ValueError):
            parser.parse_iso14229_dtc(bytes([0x01, 0x02, 0x03]))  # Not multiple of 4

        # Invalid data length for J1939
        with pytest.raises(ValueError):
            parser.parse_j1939_dtc(bytes([0x01, 0x02]))  # Not multiple of 4

    def test_calibration_empty_table(self):
        """Test calibration with empty tables."""
        table = CalibrationTable(name="Empty", dimensions=1, x_axis=[], values=[])

        with pytest.raises(ValueError):
            table.lookup(10.0)  # Can't interpolate empty table

    def test_calibration_out_of_range(self):
        """Test calibration value extrapolation."""
        table = CalibrationTable(
            name="Test", dimensions=1, x_axis=[0, 100], values=[0, 100]
        )

        # Values outside range should clamp
        assert table.lookup(-50) == 0  # Clamped to min
        assert table.lookup(150) == 100  # Clamped to max

    def test_memory_invalid_region(self):
        """Test memory region validation."""
        # End address before start address
        with pytest.raises(ValueError):
            MemoryRegion(
                name="Invalid",
                start_address=0x1000,
                end_address=0x0FFF,
                size=0,
                region_type=MemoryRegionType.DATA,
            )

    def test_memory_region_not_found(self):
        """Test memory operations on non-existent regions."""
        analyzer = FlashMemoryAnalyzer()
        analyzer.memory_data = b"test"

        # Calculate checksum on non-existent region
        with pytest.raises(ValueError):
            analyzer.calculate_checksum("NonExistent")

    def test_security_invalid_seed_length(self):
        """Test security key derivation with invalid seed."""
        deriver = SecurityKeyDeriver()

        # Some algorithms require specific seed lengths
        with pytest.raises(ValueError):
            deriver.derive_key(
                bytes([0x01]),  # 1 byte seed
                SecurityAlgorithm.MANUFACTURER_A,  # Requires 4 bytes
            )

    def test_dtc_auto_detect_failure(self):
        """Test DTC format auto-detection failure."""
        parser = DTCParser()

        # Random data that doesn't match any format
        with pytest.raises(ValueError):
            parser.extract_dtcs_from_binary_log(bytes([0xFF, 0xEE, 0xDD]))

    def test_can_encoding_overflow(self):
        """Test CAN signal encoding with value overflow."""
        signal = CANSignal(
            name="Test",
            start_bit=0,
            length=8,  # Max raw value 255
            scale=1.0,
            offset=0,
        )

        # This would require raw value > 255
        _, mask = signal.encode(300.0)
        # Should handle gracefully (likely saturate)
        assert mask == 0xFF

    def test_corrupt_binary_data(self):
        """Test handling of corrupted binary data."""
        parser = DTCParser()

        # Corrupted UDS response (invalid length)
        corrupt_data = bytes([0x59, 0xFF, 0xFF])  # Incomplete

        # Should handle gracefully
        dtcs = parser.extract_dtcs_from_binary_log(corrupt_data)
        # May return empty or partial results
        assert isinstance(dtcs, list)

    def test_unicode_in_names(self):
        """Test Unicode characters in names."""
        msg = CANMessage(
            id=0x100,
            name="Temperature_°C",  # Unicode degree symbol
            length=8,
        )
        assert "°C" in msg.name

    def test_concurrent_modifications(self):
        """Test concurrent modification scenarios."""
        decoder = CANDecoder()

        msg = CANMessage(id=0x100, name="Test", length=8)
        decoder.add_message(msg)

        # Modify message after adding to decoder
        msg.signals["NewSignal"] = CANSignal(name="NewSignal", start_bit=0, length=8)

        # Decoder should still work
        result = decoder.decode_message(0x100, bytes(8))
        assert result is not None
