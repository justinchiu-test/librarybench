"""PyBinParser - Automotive Diagnostics Decoder

A binary parser designed for vehicle systems engineers analyzing proprietary
diagnostic data and firmware from various manufacturers.
"""

from .can_decoder import CANDecoder, CANSignal, CANMessage, ByteOrder
from .dtc_parser import DTCParser, DiagnosticTroubleCode, DTCFormat, DTCStatus
from .calibration import CalibrationDataExtractor, CalibrationTable, InterpolationMethod
from .flash_memory import FlashMemoryAnalyzer, MemoryRegion, MemoryRegionType
from .security import SecurityKeyDeriver, SecurityAlgorithm, SecurityLevel

__version__ = "0.1.0"
__all__ = [
    "CANDecoder",
    "CANSignal",
    "CANMessage",
    "ByteOrder",
    "DTCParser",
    "DiagnosticTroubleCode",
    "DTCFormat",
    "DTCStatus",
    "CalibrationDataExtractor",
    "CalibrationTable",
    "InterpolationMethod",
    "FlashMemoryAnalyzer",
    "MemoryRegion",
    "MemoryRegionType",
    "SecurityKeyDeriver",
    "SecurityAlgorithm",
    "SecurityLevel",
]
