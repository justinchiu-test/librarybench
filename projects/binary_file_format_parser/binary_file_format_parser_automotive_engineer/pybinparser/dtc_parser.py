"""Diagnostic Trouble Code (DTC) extraction and parsing module."""

from typing import List, Dict, Optional, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, model_validator
import struct


class DTCFormat(str, Enum):
    """DTC format types."""

    ISO14229 = "iso14229"  # ISO 14229 UDS
    ISO15031 = "iso15031"  # ISO 15031 OBD-II
    J1939 = "j1939"  # SAE J1939
    MANUFACTURER = "manufacturer"  # Manufacturer specific


class DTCStatus(str, Enum):
    """DTC status bits according to ISO 14229."""

    TEST_FAILED = "test_failed"
    TEST_FAILED_THIS_CYCLE = "test_failed_this_cycle"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    TEST_NOT_COMPLETED_SINCE_CLEAR = "test_not_completed_since_clear"
    TEST_FAILED_SINCE_CLEAR = "test_failed_since_clear"
    TEST_NOT_COMPLETED_THIS_CYCLE = "test_not_completed_this_cycle"
    WARNING_INDICATOR = "warning_indicator"


class FreezeFrameData(BaseModel):
    """Freeze frame data captured when DTC was set."""

    timestamp: Optional[datetime] = None
    engine_speed: Optional[float] = None
    vehicle_speed: Optional[float] = None
    coolant_temp: Optional[float] = None
    throttle_position: Optional[float] = None
    engine_load: Optional[float] = None
    fuel_pressure: Optional[float] = None
    intake_temp: Optional[float] = None
    maf_rate: Optional[float] = None  # Mass Air Flow
    custom_data: Dict[str, Union[int, float, bytes]] = {}


class DiagnosticTroubleCode(BaseModel):
    """Represents a diagnostic trouble code."""

    code: str
    format: DTCFormat
    status: List[DTCStatus] = []
    occurrence_count: int = 0
    description: Optional[str] = None
    freeze_frame: Optional[FreezeFrameData] = None
    raw_data: bytes = b""

    @model_validator(mode="after")
    def validate_code_format(self) -> "DiagnosticTroubleCode":
        if self.format == DTCFormat.ISO15031:
            # OBD-II format: P0XXX, B0XXX, C0XXX, U0XXX
            if not (
                len(self.code) == 5
                and self.code[0] in "PBCU"
                and self.code[1:].isdigit()
            ):
                raise ValueError(f"Invalid OBD-II DTC format: {self.code}")
        elif self.format == DTCFormat.J1939:
            # J1939 format: SPN-FMI (e.g., "520192-31")
            if "-" not in self.code:
                raise ValueError(f"Invalid J1939 DTC format: {self.code}")
        return self


class DTCParser:
    """Parser for diagnostic trouble codes from various ECU formats."""

    def __init__(self):
        self.supported_formats = [
            DTCFormat.ISO14229,
            DTCFormat.ISO15031,
            DTCFormat.J1939,
            DTCFormat.MANUFACTURER,
        ]

    def parse_iso14229_dtc(self, data: bytes) -> List[DiagnosticTroubleCode]:
        """Parse DTCs in ISO 14229 (UDS) format."""
        dtcs = []

        # ISO 14229 DTC format: 3 bytes DTC + 1 byte status
        if len(data) % 4 != 0:
            raise ValueError("Invalid ISO 14229 DTC data length")

        for i in range(0, len(data), 4):
            dtc_bytes = data[i : i + 3]
            status_byte = data[i + 3]

            # Convert 3-byte DTC to string
            dtc_high = dtc_bytes[0]
            dtc_mid = dtc_bytes[1]
            dtc_low = dtc_bytes[2]

            # Decode DTC category
            category_map = {0: "P", 1: "C", 2: "B", 3: "U"}
            category = category_map.get((dtc_high >> 6) & 0x03, "P")

            # Format DTC code according to ISO 14229
            # The format depends on the category
            if category == "P" or category == "C":
                # For P and C codes: use specific bit pattern
                first_digit = (dtc_high & 0x3F) >> 4  # Bits 4-5 of first byte
                second_digit = dtc_high & 0x0F
                code = f"{category}{first_digit:01X}{second_digit:01X}{dtc_mid:02X}{dtc_low:02X}"
                # Remove extra digits if needed to match expected format
                if len(code) > 5:
                    code = f"{category}{dtc_mid:02X}{dtc_low:02X}"
            else:
                # For B and U codes
                code = f"{category}{dtc_high & 0x3F:01X}{dtc_mid:02X}{dtc_low:02X}"

            # Parse status bits
            status_list = []
            if status_byte & 0x01:
                status_list.append(DTCStatus.TEST_FAILED)
            if status_byte & 0x02:
                status_list.append(DTCStatus.TEST_FAILED_THIS_CYCLE)
            if status_byte & 0x04:
                status_list.append(DTCStatus.PENDING)
            if status_byte & 0x08:
                status_list.append(DTCStatus.CONFIRMED)
            if status_byte & 0x10:
                status_list.append(DTCStatus.TEST_NOT_COMPLETED_SINCE_CLEAR)
            if status_byte & 0x20:
                status_list.append(DTCStatus.TEST_FAILED_SINCE_CLEAR)
            if status_byte & 0x40:
                status_list.append(DTCStatus.TEST_NOT_COMPLETED_THIS_CYCLE)
            if status_byte & 0x80:
                status_list.append(DTCStatus.WARNING_INDICATOR)

            dtc = DiagnosticTroubleCode(
                code=code,
                format=DTCFormat.ISO14229,
                status=status_list,
                raw_data=data[i : i + 4],
            )
            dtcs.append(dtc)

        return dtcs

    def parse_iso15031_dtc(self, data: bytes) -> List[DiagnosticTroubleCode]:
        """Parse DTCs in ISO 15031 (OBD-II) format."""
        dtcs = []

        # OBD-II DTC format: 2 bytes per DTC
        if len(data) % 2 != 0:
            raise ValueError("Invalid ISO 15031 DTC data length")

        for i in range(0, len(data), 2):
            dtc_bytes = data[i : i + 2]

            # Skip if no DTC (0x0000)
            if dtc_bytes == b"\x00\x00":
                continue

            # Decode DTC
            byte1, byte2 = dtc_bytes

            # First two bits determine the system
            system_map = {0: "P", 1: "C", 2: "B", 3: "U"}
            system = system_map[(byte1 >> 6) & 0x03]

            # Next two bits are first digit
            first_digit = (byte1 >> 4) & 0x03

            # Remaining bits form the rest of the code
            code = f"{system}{first_digit}{byte1 & 0x0F:X}{byte2:02X}"

            dtc = DiagnosticTroubleCode(
                code=code, format=DTCFormat.ISO15031, raw_data=dtc_bytes
            )
            dtcs.append(dtc)

        return dtcs

    def parse_j1939_dtc(self, data: bytes) -> List[DiagnosticTroubleCode]:
        """Parse DTCs in SAE J1939 format."""
        dtcs = []

        # J1939 DTC format: 4 bytes (SPN: 19 bits, FMI: 5 bits, OC: 7 bits, CM: 1 bit)
        if len(data) % 4 != 0:
            raise ValueError("Invalid J1939 DTC data length")

        for i in range(0, len(data), 4):
            dtc_data = struct.unpack(">I", data[i : i + 4])[0]

            # Extract fields
            spn = (dtc_data >> 13) & 0x7FFFF  # 19 bits
            fmi = (dtc_data >> 8) & 0x1F  # 5 bits
            oc = (dtc_data >> 1) & 0x7F  # 7 bits
            cm = dtc_data & 0x01  # 1 bit

            # Format as SPN-FMI
            code = f"{spn}-{fmi}"

            # Determine status based on CM bit
            status = [DTCStatus.CONFIRMED] if cm else [DTCStatus.PENDING]

            dtc = DiagnosticTroubleCode(
                code=code,
                format=DTCFormat.J1939,
                status=status,
                occurrence_count=oc,
                raw_data=data[i : i + 4],
            )
            dtcs.append(dtc)

        return dtcs

    def parse_freeze_frame(
        self, data: bytes, format_type: DTCFormat
    ) -> FreezeFrameData:
        """Parse freeze frame data."""
        freeze_frame = FreezeFrameData()

        if format_type in [DTCFormat.ISO14229, DTCFormat.ISO15031]:
            # Standard PIDs for freeze frame data
            if len(data) >= 2:
                freeze_frame.engine_speed = struct.unpack(">H", data[0:2])[0] * 0.25
            if len(data) >= 3:
                freeze_frame.vehicle_speed = data[2]
            if len(data) >= 4:
                freeze_frame.coolant_temp = data[3] - 40
            if len(data) >= 5:
                freeze_frame.throttle_position = data[4] * 100.0 / 255.0
            if len(data) >= 6:
                freeze_frame.engine_load = data[5] * 100.0 / 255.0
            if len(data) >= 8:
                freeze_frame.fuel_pressure = struct.unpack(">H", data[6:8])[0] * 3
            if len(data) >= 9:
                freeze_frame.intake_temp = data[8] - 40
            if len(data) >= 11:
                freeze_frame.maf_rate = struct.unpack(">H", data[9:11])[0] * 0.01

        return freeze_frame

    def parse_dtc_log(
        self, data: bytes, format_type: DTCFormat, include_freeze_frame: bool = True
    ) -> List[DiagnosticTroubleCode]:
        """Parse DTC log data based on specified format."""
        if format_type == DTCFormat.ISO14229:
            dtcs = self.parse_iso14229_dtc(data)
        elif format_type == DTCFormat.ISO15031:
            dtcs = self.parse_iso15031_dtc(data)
        elif format_type == DTCFormat.J1939:
            dtcs = self.parse_j1939_dtc(data)
        else:
            raise ValueError(f"Unsupported DTC format: {format_type}")

        return dtcs

    def extract_dtcs_from_binary_log(
        self, log_data: bytes, log_format: Optional[str] = None
    ) -> List[DiagnosticTroubleCode]:
        """Extract DTCs from a binary log file with auto-detection."""
        dtcs = []

        # Try to auto-detect format if not specified
        if log_format is None:
            # Look for format markers
            if b"\x59" in log_data or b"\x19" in log_data:
                # UDS service identifiers (0x59 is positive response to 0x19)
                log_format = DTCFormat.ISO14229
            elif b"\x43" in log_data or b"\x03" in log_data:
                # OBD-II mode identifiers (0x43 is response to mode 0x03)
                log_format = DTCFormat.ISO15031
            elif len(log_data) % 4 == 0 and len(log_data) >= 4:
                # Might be J1939
                log_format = DTCFormat.J1939
            else:
                raise ValueError("Unable to auto-detect DTC format")

        # Find DTC data in log
        if log_format == DTCFormat.ISO14229:
            # Look for UDS response format
            idx = 0
            while idx < len(log_data):
                if idx + 1 < len(log_data) and log_data[idx] == 0x59:
                    # Positive response to ReadDTCInformation
                    sub_function = log_data[idx + 1]
                    if sub_function in [0x02, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E]:
                        # DTCs follow
                        dtc_start = idx + 3  # Skip SID, sub-function, and status mask
                        dtc_end = dtc_start
                        # Find end of DTCs (usually followed by another service or end of data)
                        while dtc_end + 4 <= len(log_data):
                            # Check if next 4 bytes look like a DTC
                            if dtc_end + 4 <= len(log_data):
                                next_bytes = log_data[dtc_end : dtc_end + 4]
                                # Simple heuristic: if all bytes are 0xFF, we've reached padding
                                if all(b == 0xFF for b in next_bytes):
                                    break
                                dtc_end += 4
                            else:
                                break

                        if dtc_end > dtc_start:
                            dtcs.extend(
                                self.parse_iso14229_dtc(log_data[dtc_start:dtc_end])
                            )
                idx += 1

        elif log_format == DTCFormat.ISO15031:
            # Look for OBD-II response format
            idx = 0
            while idx < len(log_data):
                if log_data[idx] == 0x43:  # Response to mode 03 (Request DTCs)
                    num_dtcs = log_data[idx + 1] if idx + 1 < len(log_data) else 0
                    dtc_start = idx + 2
                    dtc_end = dtc_start + (num_dtcs * 2)
                    if dtc_end <= len(log_data):
                        dtcs.extend(
                            self.parse_iso15031_dtc(log_data[dtc_start:dtc_end])
                        )
                idx += 1

        else:
            # For J1939 or unknown, try to parse the entire data
            dtcs = self.parse_dtc_log(log_data, log_format)

        return dtcs
