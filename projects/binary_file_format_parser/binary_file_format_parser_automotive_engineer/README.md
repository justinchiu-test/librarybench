# PyBinParser - Automotive Diagnostics Decoder

A comprehensive binary parser designed for vehicle systems engineers analyzing proprietary diagnostic data and firmware from various manufacturers. This tool enables decoding of controller-specific formats without vendor documentation, supporting independent diagnostics and troubleshooting of modern vehicle systems.

## Features

- **CAN Bus Data Structure Mapping**: Decode and map CAN message structures to meaningful vehicle parameters
- **Diagnostic Trouble Code (DTC) Extraction**: Parse DTCs from various ECU binary log formats
- **Sensor Calibration Data Interpretation**: Extract and interpret sensor calibration tables and curves
- **ECU Flash Memory Layout Analysis**: Analyze and map ECU firmware structure
- **Vehicle-Specific Encryption Key Derivation**: Calculate security access keys using vehicle-specific algorithms

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from source
```bash
# Clone the repository
git clone https://github.com/yourusername/pybinparser.git
cd pybinparser

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Install development dependencies (for running tests)
pip install -e ".[dev]"
```

## Usage Examples

### CAN Bus Data Decoding

```python
from pybinparser import CANDecoder, CANSignal, CANMessage, ByteOrder

# Create a CAN decoder
decoder = CANDecoder()

# Define a CAN message
engine_msg = CANMessage(
    id=0x100,
    name="EngineData",
    length=8
)

# Add signals to the message
engine_msg.signals["RPM"] = CANSignal(
    name="RPM",
    start_bit=0,
    length=16,
    byte_order=ByteOrder.INTEL,
    scale=0.25,
    offset=0,
    unit="rpm"
)

engine_msg.signals["Temperature"] = CANSignal(
    name="Temperature",
    start_bit=16,
    length=8,
    scale=1.0,
    offset=-40,
    unit="°C"
)

decoder.add_message(engine_msg)

# Decode CAN data
can_data = bytes([0x10, 0x27, 0x78, 0x00, 0x00, 0x00, 0x00, 0x00])
decoded = decoder.decode_message(0x100, can_data)
print(f"Engine RPM: {decoded['RPM']} rpm")
print(f"Engine Temperature: {decoded['Temperature']} °C")
```

### Diagnostic Trouble Code Extraction

```python
from pybinparser import DTCParser, DTCFormat

# Create DTC parser
parser = DTCParser()

# Parse ISO 14229 (UDS) format DTCs
dtc_data = bytes([
    0x01, 0x23, 0x45, 0x09,  # P2345 with confirmed status
    0x81, 0x00, 0x12, 0x02   # C0012 with pending status
])

dtcs = parser.parse_iso14229_dtc(dtc_data)
for dtc in dtcs:
    print(f"DTC: {dtc.code}, Status: {dtc.status}")

# Extract DTCs from binary log file
with open("ecu_diagnostic_log.bin", "rb") as f:
    log_data = f.read()
    extracted_dtcs = parser.extract_dtcs_from_binary_log(log_data)
```

### Sensor Calibration

```python
from pybinparser import CalibrationDataExtractor, CalibrationTable

# Create calibration extractor
calibrator = CalibrationDataExtractor()

# Define a temperature sensor calibration table
temp_calibration = CalibrationTable(
    name="CoolantTempSensor",
    dimensions=1,
    x_axis=[0, 1, 2, 3, 4, 5],      # Voltage (V)
    values=[-40, -10, 25, 60, 95, 125],  # Temperature (°C)
    unit="°C"
)

calibrator.add_table(temp_calibration)

# Apply calibration to raw sensor reading
raw_voltage = 2.5  # Volts
actual_temp = calibrator.apply_sensor_calibration(raw_voltage, "CoolantTempSensor")
print(f"Calibrated temperature: {actual_temp} °C")
```

### ECU Memory Analysis

```python
from pybinparser import FlashMemoryAnalyzer

# Create memory analyzer
analyzer = FlashMemoryAnalyzer()

# Load and analyze ECU memory dump
with open("ecu_dump.bin", "rb") as f:
    memory_data = f.read()
    
regions = analyzer.analyze_memory_dump(memory_data, base_address=0x08000000)

# Display memory map
print(analyzer.export_memory_map())

# Verify checksums
checksum_results = analyzer.verify_checksums()
for region, valid in checksum_results.items():
    print(f"Checksum for {region}: {'Valid' if valid else 'Invalid'}")
```

### Security Key Derivation

```python
from pybinparser import SecurityKeyDeriver, SecurityAlgorithm, SecurityLevel

# Create security key deriver
deriver = SecurityKeyDeriver()

# Derive key from seed
seed = bytes([0x12, 0x34, 0x56, 0x78])
key = deriver.derive_key(
    seed,
    SecurityAlgorithm.MANUFACTURER_A,
    SecurityLevel.EXTENDED_DIAGNOSTICS,
    params={'vin_constant': 0x5A5A5A5A}
)

print(f"Seed: {seed.hex()}")
print(f"Key: {key.hex()}")
```

## Running Tests

To run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-json-report

# Run all tests
pytest

# Run tests with JSON report (required for validation)
pytest --json-report --json-report-file=pytest_results.json

# Run specific test module
pytest tests/test_can_decoder.py

# Run with verbose output
pytest -v
```

## Architecture

The library is organized into the following modules:

- **can_decoder**: CAN bus message decoding with signal extraction
- **dtc_parser**: Diagnostic trouble code parsing for multiple formats
- **calibration**: Sensor calibration data interpretation with interpolation
- **flash_memory**: ECU memory layout analysis and checksum verification
- **security**: Vehicle-specific security algorithm implementations

## Supported Formats

### CAN Bus
- Standard CAN (11-bit ID)
- Extended CAN (29-bit ID)
- Intel (little-endian) byte order
- Motorola (big-endian) byte order

### Diagnostic Protocols
- ISO 14229 (UDS)
- ISO 15031 (OBD-II)
- SAE J1939

### Security Algorithms
- Fixed bytes XOR
- Bit manipulation
- Addition/Subtraction
- CRC-based
- Hash-based
- Manufacturer-specific algorithms

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for legitimate diagnostic and research purposes only. Always respect manufacturer security protocols and use responsibly.