# PyBinParser - Network Protocol Decoder

## Overview
A binary parser specialized for network engineers analyzing proprietary protocols from packet captures. This tool decodes custom binary protocols used by IoT devices and industrial systems, enabling security analysis and troubleshooting of undocumented network communications.

## Persona Description
A network engineer who captures and analyzes proprietary protocol data from packet captures. They need to decode custom binary protocols used by IoT devices and industrial systems.

## Key Requirements
1. **Stream Reassembly**: Reconstruct complete protocol messages from fragmented network packets, handling out-of-order delivery, retransmissions, and packet loss common in real-world captures. Critical for analyzing protocols that span multiple packets.

2. **State Machine Modeling**: Build and track protocol state machines by analyzing packet sequences, identifying handshakes, session establishment, and state transitions to understand protocol flow and behavior.

3. **Field Correlation Analysis**: Discover relationships between fields across multiple packets by statistical analysis, identifying sequence numbers, acknowledgments, and correlated data fields that define protocol behavior.

4. **Protocol Grammar Extraction**: Automatically derive protocol grammar rules from captured sessions, generating formal specifications that can parse future communications and detect protocol violations.

5. **Real-Time Stream Parsing**: Parse network capture streams in real-time during live capture sessions, enabling immediate protocol analysis and alerting on anomalous behavior without post-processing delays.

## Technical Requirements
- **Testability**: All parsing and analysis functions must be testable via pytest
- **Performance**: Real-time processing of gigabit network streams
- **Protocol Support**: Handle TCP, UDP, and custom transport protocols
- **State Tracking**: Maintain per-connection state for thousands of concurrent flows
- **No UI Components**: Library implementation for integration with existing tools

## Core Functionality
The parser must provide:
- Multi-protocol stream reassembly engine
- State machine inference and tracking
- Statistical correlation analysis
- Grammar extraction algorithms
- Real-time parsing pipeline
- Protocol anomaly detection
- Session reconstruction from pcap files
- Export to common analysis formats

## Testing Requirements
Comprehensive test coverage must include:
- **Stream Reassembly**: Test with fragmented, out-of-order packets
- **State Machines**: Verify correct state tracking across sessions
- **Correlation Analysis**: Validate field relationship discovery
- **Grammar Extraction**: Test grammar generation accuracy
- **Real-Time Performance**: Verify processing speed requirements
- **Protocol Variations**: Handle malformed and non-compliant packets
- **Scalability**: Test with thousands of concurrent connections
- **Edge Cases**: Handle packet loss, duplicates, corrupted data

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- Stream reassembly correctly handles all fragmentation scenarios
- State machines accurately model protocol behavior
- Field correlation identifies all relationships in test protocols
- Grammar extraction produces parseable specifications
- Real-time parsing meets gigabit throughput requirements
- The tool correctly handles malformed and adversarial inputs
- Performance scales linearly with connection count

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```