# PyBinParser - High-Performance Market Data Parser

## Overview
A binary parser optimized for quantitative analysts processing proprietary market data feeds and historical tick data. This tool provides ultra-low latency parsing of binary market data formats, enabling real-time trading systems and historical analysis with nanosecond precision.

## Persona Description
A quantitative analyst working with proprietary market data feeds and historical tick data in binary formats. They need high-performance parsing for real-time trading systems.

## Key Requirements
1. **Zero-Copy Parsing**: Implement memory-efficient parsing that avoids data copying, directly reading from memory-mapped files or network buffers to achieve minimal latency for high-frequency trading applications.

2. **Timestamp Precision Handling**: Parse and maintain nanosecond-precision timestamps without loss of accuracy, supporting various epoch formats and handling time synchronization issues critical for trade execution and analysis.

3. **Market Data Symbol Mapping**: Normalize and map trading symbols across different exchanges and data providers, maintaining consistent instrument identification while preserving original exchange-specific codes.

4. **Order Book Reconstruction**: Rebuild full order book state from binary market data snapshots and incremental updates, maintaining price levels, quantities, and order priorities for accurate market microstructure analysis.

5. **Compression Scheme Detection**: Automatically identify and decompress various compression formats used in historical data archives (LZ4, ZSTD, custom schemes) to access years of tick data efficiently.

## Technical Requirements
- **Testability**: All parsing functions must be testable via pytest
- **Latency**: Sub-microsecond parsing for individual messages
- **Throughput**: Process millions of messages per second
- **Precision**: Maintain full numeric precision for prices and timestamps
- **No UI Components**: Pure library optimized for speed

## Core Functionality
The parser must provide:
- Zero-copy binary data access patterns
- Nanosecond timestamp parsing and arithmetic
- Symbol normalization and mapping engine
- Order book state machine implementation
- Multi-format decompression pipeline
- Message type detection and routing
- Sequence number validation
- Market data integrity checking

## Testing Requirements
Comprehensive test coverage must include:
- **Zero-Copy Performance**: Verify memory efficiency and speed
- **Timestamp Accuracy**: Test nanosecond precision preservation
- **Symbol Mapping**: Validate cross-exchange normalization
- **Order Book State**: Test reconstruction accuracy and consistency
- **Compression Handling**: Verify support for all formats
- **Latency Benchmarks**: Ensure sub-microsecond parsing
- **Throughput Tests**: Validate millions of messages/second
- **Data Integrity**: Test sequence validation and checksums

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- Zero-copy parsing achieves sub-microsecond latencies
- Timestamps maintain full nanosecond precision
- Symbol mapping correctly normalizes across all test exchanges
- Order books reconstruct accurately from all message types
- Compression detection handles all supported formats
- Throughput exceeds 1 million messages per second
- Memory usage remains constant regardless of data volume

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```