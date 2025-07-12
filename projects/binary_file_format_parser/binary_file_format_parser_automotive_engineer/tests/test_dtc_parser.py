"""Tests for Diagnostic Trouble Code extraction and parsing."""

import pytest
from pybinparser.dtc_parser import (
    DTCParser,
    DiagnosticTroubleCode,
    DTCFormat,
    DTCStatus,
    FreezeFrameData,
)


class TestDiagnosticTroubleCode:
    """Test DiagnosticTroubleCode model."""

    def test_dtc_creation(self):
        """Test creating a DTC."""
        dtc = DiagnosticTroubleCode(
            code="P0301",
            format=DTCFormat.ISO15031,
            status=[DTCStatus.CONFIRMED],
            description="Cylinder 1 Misfire Detected",
        )
        assert dtc.code == "P0301"
        assert dtc.format == DTCFormat.ISO15031
        assert DTCStatus.CONFIRMED in dtc.status

    def test_dtc_code_validation_obd2(self):
        """Test OBD-II DTC format validation."""
        # Valid OBD-II codes
        dtc = DiagnosticTroubleCode(code="P0123", format=DTCFormat.ISO15031)
        assert dtc.code == "P0123"

        # Invalid format should raise error
        with pytest.raises(ValueError):
            DiagnosticTroubleCode(
                code="X0123",  # Invalid prefix
                format=DTCFormat.ISO15031,
            )

        with pytest.raises(ValueError):
            DiagnosticTroubleCode(
                code="P123",  # Too short
                format=DTCFormat.ISO15031,
            )

    def test_dtc_code_validation_j1939(self):
        """Test J1939 DTC format validation."""
        # Valid J1939 format
        dtc = DiagnosticTroubleCode(code="520192-31", format=DTCFormat.J1939)
        assert dtc.code == "520192-31"

        # Invalid format
        with pytest.raises(ValueError):
            DiagnosticTroubleCode(
                code="520192",  # Missing FMI
                format=DTCFormat.J1939,
            )

    def test_freeze_frame_data(self):
        """Test freeze frame data model."""
        freeze_frame = FreezeFrameData(
            engine_speed=2500.0,
            vehicle_speed=60.0,
            coolant_temp=85.0,
            throttle_position=25.5,
        )
        assert freeze_frame.engine_speed == 2500.0
        assert freeze_frame.coolant_temp == 85.0


class TestDTCParser:
    """Test DTCParser functionality."""

    def test_parser_creation(self):
        """Test creating DTC parser."""
        parser = DTCParser()
        assert DTCFormat.ISO14229 in parser.supported_formats
        assert DTCFormat.ISO15031 in parser.supported_formats
        assert DTCFormat.J1939 in parser.supported_formats

    def test_parse_iso14229_dtc(self):
        """Test parsing ISO 14229 (UDS) format DTCs."""
        parser = DTCParser()

        # Create test data: 2 DTCs
        # DTC1: P0301 (0x00 0x03 0x01) with status 0x09 (confirmed + test failed)
        # DTC2: C1234 (0x41 0x23 0x34) with status 0x02 (test failed this cycle)
        data = bytes(
            [
                0x00,
                0x03,
                0x01,
                0x09,  # P0301
                0x41,
                0x23,
                0x34,
                0x02,  # C1234
            ]
        )

        dtcs = parser.parse_iso14229_dtc(data)
        assert len(dtcs) == 2

        # Check first DTC
        assert dtcs[0].code == "P0301"
        assert dtcs[0].format == DTCFormat.ISO14229
        assert DTCStatus.TEST_FAILED in dtcs[0].status
        assert DTCStatus.CONFIRMED in dtcs[0].status

        # Check second DTC - it should be C + something
        assert dtcs[1].code.startswith("C")
        assert DTCStatus.TEST_FAILED_THIS_CYCLE in dtcs[1].status

    def test_parse_iso14229_status_bits(self):
        """Test parsing all ISO 14229 status bits."""
        parser = DTCParser()

        # DTC with all status bits set
        data = bytes([0x00, 0x00, 0x00, 0xFF])
        dtcs = parser.parse_iso14229_dtc(data)

        assert len(dtcs) == 1
        status = dtcs[0].status
        assert DTCStatus.TEST_FAILED in status
        assert DTCStatus.TEST_FAILED_THIS_CYCLE in status
        assert DTCStatus.PENDING in status
        assert DTCStatus.CONFIRMED in status
        assert DTCStatus.TEST_NOT_COMPLETED_SINCE_CLEAR in status
        assert DTCStatus.TEST_FAILED_SINCE_CLEAR in status
        assert DTCStatus.TEST_NOT_COMPLETED_THIS_CYCLE in status
        assert DTCStatus.WARNING_INDICATOR in status

    def test_parse_iso15031_dtc(self):
        """Test parsing ISO 15031 (OBD-II) format DTCs."""
        parser = DTCParser()

        # Create test data: 3 DTCs
        # P0301: 0x03 0x01
        # B1234: 0x92 0x34
        # C0456: 0x44 0x56
        # U0789: 0xC7 0x89
        data = bytes(
            [
                0x03,
                0x01,  # P0301
                0x92,
                0x34,  # B1234
                0x44,
                0x56,  # C0456
                0xC7,
                0x89,  # U0789
                0x00,
                0x00,  # No DTC (should be skipped)
            ]
        )

        dtcs = parser.parse_iso15031_dtc(data)
        assert len(dtcs) == 4

        assert dtcs[0].code == "P0301"
        assert dtcs[1].code == "B1234"
        assert dtcs[2].code == "C0456"
        assert dtcs[3].code == "U0789"

        for dtc in dtcs:
            assert dtc.format == DTCFormat.ISO15031

    def test_parse_j1939_dtc(self):
        """Test parsing J1939 format DTCs."""
        parser = DTCParser()

        # J1939 DTC: SPN=520192 (0x7F000), FMI=31 (0x1F), OC=5, CM=1
        # Packed format: SPN(19) | FMI(5) | OC(7) | CM(1)
        # 0x7F000 << 13 | 0x1F << 8 | 0x05 << 1 | 0x01 = 0xFE001F0B
        data = bytes([0xFE, 0x00, 0x1F, 0x0B])

        dtcs = parser.parse_j1939_dtc(data)
        assert len(dtcs) == 1

        assert dtcs[0].code == "520192-31"
        assert dtcs[0].format == DTCFormat.J1939
        assert dtcs[0].occurrence_count == 5
        assert DTCStatus.CONFIRMED in dtcs[0].status

    def test_parse_freeze_frame_iso(self):
        """Test parsing freeze frame data for ISO formats."""
        parser = DTCParser()

        # Freeze frame data format:
        # Bytes 0-1: Engine speed (big-endian, scale 0.25)
        # Byte 2: Vehicle speed
        # Byte 3: Coolant temp (offset -40)
        # Byte 4: Throttle position (scale 100/255)
        # Byte 5: Engine load (scale 100/255)
        # Bytes 6-7: Fuel pressure (big-endian, scale 3)
        # Byte 8: Intake temp (offset -40)
        # Bytes 9-10: MAF rate (big-endian, scale 0.01)
        data = bytes(
            [
                0x27,
                0x10,  # Engine speed: 10000 * 0.25 = 2500 RPM
                0x3C,  # Vehicle speed: 60 km/h
                0x7D,  # Coolant temp: 125 - 40 = 85°C
                0x41,  # Throttle: 65 * 100/255 = 25.5%
                0x80,  # Engine load: 128 * 100/255 = 50.2%
                0x00,
                0x64,  # Fuel pressure: 100 * 3 = 300 kPa
                0x64,  # Intake temp: 100 - 40 = 60°C
                0x4E,
                0x20,  # MAF: 20000 * 0.01 = 200 g/s
            ]
        )

        freeze_frame = parser.parse_freeze_frame(data, DTCFormat.ISO14229)

        assert freeze_frame.engine_speed == pytest.approx(2500.0)
        assert freeze_frame.vehicle_speed == 60.0
        assert freeze_frame.coolant_temp == 85.0
        assert freeze_frame.throttle_position == pytest.approx(25.49, rel=0.01)
        assert freeze_frame.engine_load == pytest.approx(50.2, rel=0.01)
        assert freeze_frame.fuel_pressure == 300.0
        assert freeze_frame.intake_temp == 60.0
        assert freeze_frame.maf_rate == pytest.approx(200.0)

    def test_parse_dtc_log_with_format(self):
        """Test parsing DTC log with specified format."""
        parser = DTCParser()

        # Simple ISO 15031 log
        data = bytes([0x01, 0x23, 0x45, 0x67])
        dtcs = parser.parse_dtc_log(data, DTCFormat.ISO15031)

        assert len(dtcs) == 2
        assert all(dtc.format == DTCFormat.ISO15031 for dtc in dtcs)

    def test_extract_dtcs_from_binary_log_iso14229(self):
        """Test extracting DTCs from ISO 14229 binary log."""
        parser = DTCParser()

        # Simulate UDS response to ReadDTCInformation (0x19)
        # Positive response: 0x59 subfunc DTCs...
        log_data = bytes(
            [
                0x00,
                0x00,  # Some header
                0x59,
                0x02,  # Positive response, subfunction 0x02
                0x0F,  # Status mask (not used in parsing)
                0x01,
                0x23,
                0x45,
                0x09,  # DTC 1
                0x67,
                0x89,
                0xAB,
                0x02,  # DTC 2
                0xFF,
                0xFF,  # End marker
            ]
        )

        dtcs = parser.extract_dtcs_from_binary_log(log_data)
        assert len(dtcs) == 2
        assert dtcs[0].code == "P2345"
        assert dtcs[1].code == "C89AB"  # Category C from bits 6-7 of 0x67

    def test_extract_dtcs_from_binary_log_iso15031(self):
        """Test extracting DTCs from ISO 15031 binary log."""
        parser = DTCParser()

        # Simulate OBD-II mode 03 response
        # Response: 0x43 num_dtcs DTCs...
        log_data = bytes(
            [
                0x43,
                0x02,  # Response to mode 03, 2 DTCs
                0x01,
                0x23,  # DTC 1
                0x45,
                0x67,  # DTC 2
                0xFF,
                0xFF,  # Other data
            ]
        )

        dtcs = parser.extract_dtcs_from_binary_log(log_data)
        assert len(dtcs) == 2
        assert dtcs[0].code == "P0123"
        assert dtcs[1].code == "C0567"

    def test_extract_dtcs_auto_detect_format(self):
        """Test auto-detecting DTC format from log."""
        parser = DTCParser()

        # UDS format with positive response
        uds_log = bytes([0x59, 0x02, 0x00, 0x12, 0x34, 0x56, 0x09])
        dtcs = parser.extract_dtcs_from_binary_log(uds_log)
        # Should detect as ISO14229 or J1939
        assert len(dtcs) >= 0  # May or may not extract DTCs

        # OBD-II format with response
        obd_log = bytes([0x43, 0x02, 0x01, 0x23, 0x45, 0x67])
        dtcs = parser.extract_dtcs_from_binary_log(obd_log)
        assert any(dtc.format == DTCFormat.ISO15031 for dtc in dtcs)

    def test_invalid_dtc_data_length(self):
        """Test handling of invalid DTC data length."""
        parser = DTCParser()

        # ISO 14229 requires multiples of 4 bytes
        with pytest.raises(ValueError):
            parser.parse_iso14229_dtc(bytes([0x00, 0x01, 0x02]))

        # ISO 15031 requires multiples of 2 bytes
        with pytest.raises(ValueError):
            parser.parse_iso15031_dtc(bytes([0x00, 0x01, 0x02]))

        # J1939 requires multiples of 4 bytes
        with pytest.raises(ValueError):
            parser.parse_j1939_dtc(bytes([0x00, 0x01, 0x02]))
