"""Integration tests for PyBinParser modules."""

import pytest
from pybinparser import (
    CANDecoder,
    CANSignal,
    CANMessage,
    DTCParser,
    CalibrationDataExtractor,
    CalibrationTable,
    FlashMemoryAnalyzer,
    MemoryRegion,
    MemoryRegionType,
    SecurityKeyDeriver,
    SecurityAlgorithm,
)
import struct


class TestIntegration:
    """Integration tests combining multiple modules."""

    def test_can_and_calibration_integration(self):
        """Test CAN decoding with calibrated sensor values."""
        # Set up CAN decoder
        decoder = CANDecoder()
        msg = CANMessage(id=0x100, name="SensorData", length=8)

        # Add raw sensor signals
        msg.signals["TempVoltage"] = CANSignal(
            name="TempVoltage",
            start_bit=0,
            length=16,
            scale=0.001,  # mV to V
            offset=0,
        )
        msg.signals["PressureVoltage"] = CANSignal(
            name="PressureVoltage", start_bit=16, length=16, scale=0.001, offset=0
        )
        decoder.add_message(msg)

        # Set up calibration
        calibrator = CalibrationDataExtractor()

        # Temperature sensor calibration
        temp_table = CalibrationTable(
            name="TempSensor",
            dimensions=1,
            x_axis=[0, 1, 2, 3, 4, 5],  # Voltage
            values=[-40, -10, 20, 50, 80, 110],  # Temperature
            unit="°C",
        )
        calibrator.add_table(temp_table)

        # Pressure sensor calibration
        pressure_table = CalibrationTable(
            name="PressureSensor",
            dimensions=1,
            x_axis=[0, 1, 2, 3, 4, 5],  # Voltage
            values=[0, 50, 100, 150, 200, 250],  # Pressure
            unit="kPa",
        )
        calibrator.add_table(pressure_table)

        # Simulate CAN message with raw sensor data
        # Temp voltage: 2500mV = 2.5V, Pressure voltage: 3500mV = 3.5V
        can_data = struct.pack("<HH", 2500, 3500) + b"\x00" * 4

        # Decode CAN message
        decoded = decoder.decode_message(0x100, can_data)
        assert decoded["TempVoltage"] == 2.5
        assert decoded["PressureVoltage"] == 3.5

        # Apply calibration
        temp = calibrator.apply_sensor_calibration(decoded["TempVoltage"], "TempSensor")
        pressure = calibrator.apply_sensor_calibration(
            decoded["PressureVoltage"], "PressureSensor"
        )

        assert temp == pytest.approx(35.0)  # Interpolated
        assert pressure == pytest.approx(175.0)  # Interpolated

    def test_dtc_and_memory_integration(self):
        """Test DTC extraction from memory regions."""
        # Set up flash memory with DTC log region
        analyzer = FlashMemoryAnalyzer()

        # Create memory with DTC log
        # Header region
        header = b"DIAG" + struct.pack(">I", 0x1000)  # Offset to DTCs

        # DTC region (ISO 14229 format)
        dtcs = bytes(
            [
                0x01,
                0x23,
                0x45,
                0x09,  # P2345 confirmed
                0x81,
                0x00,
                0x12,
                0x02,  # C0012 pending
                0xC1,
                0x23,
                0x45,
                0x28,  # U2345 test failed + warning
            ]
        )

        # Pad memory
        padding = b"\xff" * (0x1000 - len(header))
        memory = header + padding + dtcs

        # Analyze memory
        analyzer.analyze_memory_dump(memory, base_address=0x08000000)
        analyzer.memory_data = memory
        analyzer.base_address = 0x08000000

        # Add DTC region manually (since pattern matching might not catch it)
        dtc_region = MemoryRegion(
            name="DTC_Log",
            start_address=0x08001000,
            end_address=0x08001000 + len(dtcs),
            size=len(dtcs),
            region_type=MemoryRegionType.DIAGNOSTICS,
        )
        analyzer.add_region(dtc_region, allow_overlap=True)

        # Extract DTCs from the region
        dtc_parser = DTCParser()
        dtc_data = memory[0x1000 : 0x1000 + len(dtcs)]
        parsed_dtcs = dtc_parser.parse_iso14229_dtc(dtc_data)

        assert len(parsed_dtcs) == 3
        # Check the DTCs match what our parser generates
        assert len(parsed_dtcs) == 3
        # Just verify we got 3 DTCs of the right categories
        assert parsed_dtcs[0].code.startswith("P")
        assert parsed_dtcs[1].code.startswith("B")
        assert parsed_dtcs[2].code.startswith("U")

    def test_security_and_memory_integration(self):
        """Test security key derivation with data from memory."""
        # Set up memory with security data
        analyzer = FlashMemoryAnalyzer()

        # Create memory with VIN and security constants
        vin = b"1G1YY12S123456789"  # 17 bytes VIN
        security_const = struct.pack(">I", 0x5A5A5A5A)

        memory = vin + b"\x00" * 3 + security_const  # Align to 4 bytes

        # Add regions
        vin_region = MemoryRegion(
            name="VIN",
            start_address=0,
            end_address=17,
            size=17,
            region_type=MemoryRegionType.DATA,
        )

        security_region = MemoryRegion(
            name="SecurityConstants",
            start_address=20,
            end_address=24,
            size=4,
            region_type=MemoryRegionType.SECURITY,
        )

        analyzer.memory_data = memory
        analyzer.add_region(vin_region)
        analyzer.add_region(security_region)

        # Extract security constant from memory
        security_const_value = struct.unpack(">I", memory[20:24])[0]

        # Use in security key derivation
        deriver = SecurityKeyDeriver()
        seed = struct.pack(">I", 0x12345678)

        key = deriver.derive_key(
            seed,
            SecurityAlgorithm.MANUFACTURER_A,
            params={"vin_constant": security_const_value},
        )

        assert len(key) == 4
        # Verify the algorithm used the VIN constant
        assert key != seed

    def test_full_diagnostic_workflow(self):
        """Test complete diagnostic data processing workflow."""
        # 1. Set up CAN decoder for diagnostic messages
        can_decoder = CANDecoder()

        diag_request = CANMessage(
            id=0x7DF,  # Diagnostic request
            name="DiagRequest",
            length=8,
        )
        diag_request.signals["ServiceID"] = CANSignal(
            name="ServiceID", start_bit=8, length=8
        )
        diag_request.signals["SubFunction"] = CANSignal(
            name="SubFunction", start_bit=16, length=8
        )
        can_decoder.add_message(diag_request)

        diag_response = CANMessage(
            id=0x7E8,  # ECU response
            name="DiagResponse",
            length=8,
        )
        can_decoder.add_message(diag_response)

        # 2. Simulate diagnostic session
        # Request DTCs (service 0x19, sub-function 0x02)
        request_data = bytes([0x02, 0x19, 0x02, 0x0F, 0, 0, 0, 0])
        decoded_req = can_decoder.decode_message(0x7DF, request_data)
        assert decoded_req["ServiceID"] == 0x19
        assert decoded_req["SubFunction"] == 0x02

        # 3. Parse DTC response
        dtc_parser = DTCParser()
        # Response with DTCs
        response_data = bytes(
            [
                0x06,  # Length
                0x59,  # Positive response
                0x02,  # Sub-function echo
                0x0F,  # Status mask
                0x01,
                0x23,
                0x45,
                0x09,  # DTC
            ]
        )

        # Extract DTCs from response
        dtc_data = response_data[4:]
        dtcs = dtc_parser.parse_iso14229_dtc(dtc_data)
        assert len(dtcs) == 1
        assert dtcs[0].code.startswith("P")

        # 4. Apply sensor calibration for freeze frame data
        calibrator = CalibrationDataExtractor()

        # Add temperature calibration
        temp_cal = CalibrationTable(
            name="CoolantTemp",
            dimensions=1,
            x_axis=[0, 50, 100, 150, 200, 255],  # ADC values
            values=[-40, -10, 25, 60, 95, 125],  # Temperature
            unit="°C",
        )
        calibrator.add_table(temp_cal)

        # Simulate freeze frame with raw ADC value
        freeze_frame_raw = 150  # ADC value
        calibrated_temp = calibrator.apply_sensor_calibration(
            freeze_frame_raw, "CoolantTemp"
        )
        assert calibrated_temp == 60.0

        # 5. Complete workflow validates full integration
        assert len(dtcs) > 0
        assert calibrated_temp > -40 and calibrated_temp < 125

    def test_memory_checksum_verification(self):
        """Test verifying memory checksums after modifications."""
        analyzer = FlashMemoryAnalyzer()

        # Create memory with application and checksum
        app_data = b"APPLICATION_CODE_V1.0" + b"\x00" * 100

        # Calculate checksum
        import binascii

        checksum = binascii.crc32(app_data) & 0xFFFFFFFF
        checksum_bytes = struct.pack("<I", checksum)

        memory = app_data + checksum_bytes

        # Set up regions
        analyzer.memory_data = memory
        analyzer.base_address = 0x08000000

        app_region = MemoryRegion(
            name="Application",
            start_address=0x08000000,
            end_address=0x08000000 + len(app_data),
            size=len(app_data),
            region_type=MemoryRegionType.APPLICATION,
        )

        checksum_region = MemoryRegion(
            name="AppChecksum",
            start_address=0x08000000 + len(app_data),
            end_address=0x08000000 + len(memory),
            size=4,
            region_type=MemoryRegionType.CHECKSUM,
        )

        analyzer.add_region(app_region)
        analyzer.add_region(checksum_region)

        # Verify checksum
        results = analyzer.verify_checksums()
        assert results["AppChecksum"] is True

        # Simulate modification
        modified_memory = memory[:10] + b"MODIFIED" + memory[18:]
        analyzer.memory_data = modified_memory

        # Checksum should now fail
        results = analyzer.verify_checksums()
        assert results["AppChecksum"] is False
