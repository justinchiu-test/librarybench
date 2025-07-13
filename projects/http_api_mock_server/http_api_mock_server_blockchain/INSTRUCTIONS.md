# PyMockAPI - Blockchain RPC Mock Server

## Overview
A specialized HTTP API mock server designed for blockchain developers to mock Web3 RPC endpoints and smart contract interactions. This implementation focuses on simulating blockchain behaviors including transaction mining, event emissions, and gas estimations, enabling comprehensive testing of decentralized application (dApp) frontends.

## Persona Description
A blockchain developer testing dApp frontends who needs to mock blockchain RPC endpoints and smart contract interactions. He requires specialized mocking for Web3 protocols and transaction simulations.

## Key Requirements

1. **Ethereum JSON-RPC method simulation with block progression**
   - Essential for testing dApp interactions with blockchain nodes
   - Enables realistic blockchain state progression and queries

2. **Transaction mining simulation with configurable confirmation times**
   - Critical for testing transaction lifecycle and user experience
   - Allows validation of pending state handling and confirmations

3. **Smart contract event emission with log filtering**
   - Vital for testing event-driven dApp functionality
   - Enables verification of event listeners and state updates

4. **Gas estimation mocking with dynamic pricing**
   - Required for testing transaction cost calculations
   - Ensures proper handling of gas price fluctuations

5. **Multiple chain simulation for cross-chain testing**
   - Essential for testing multi-chain dApps
   - Allows validation of chain switching and compatibility

## Technical Requirements

### Testability Requirements
- All blockchain behaviors must be deterministic and controllable
- RPC responses must match Ethereum JSON-RPC specification
- Event emissions must be queryable and verifiable
- Gas calculations must be predictable

### Performance Expectations
- RPC method responses within 50ms
- Support for 100+ concurrent Web3 connections
- Block generation at configurable intervals
- Event filtering with minimal latency

### Integration Points
- Ethereum JSON-RPC 2.0 compliant endpoints
- WebSocket support for event subscriptions
- REST API for test configuration
- Block explorer-like query APIs

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must be compatible with standard Web3 libraries
- Should support common Ethereum standards (ERC-20, ERC-721)

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **JSON-RPC Engine**: Complete implementation of Ethereum JSON-RPC methods including eth_call, eth_sendTransaction, eth_getBalance, with automatic block progression and state management.

2. **Transaction Pool Manager**: Realistic transaction lifecycle simulation with mempool behavior, mining delays, confirmation counts, and reorganization support.

3. **Event Emitter System**: Smart contract event generation with proper log indexing, bloom filters, topic filtering, and historical event queries.

4. **Gas Oracle**: Dynamic gas price simulation with EIP-1559 support, priority fees, base fee calculations, and gas limit estimation.

5. **Multi-Chain Router**: Support for multiple blockchain simulations with different chain IDs, consensus rules, native currencies, and network parameters.

## Testing Requirements

### Key Functionalities to Verify
- JSON-RPC methods return spec-compliant responses
- Transactions progress through correct lifecycle states
- Events are emitted with proper indexing and filtering
- Gas estimations accurately reflect transaction complexity
- Multi-chain routing works with standard libraries

### Critical User Scenarios
- Sending transactions and monitoring confirmations
- Subscribing to smart contract events
- Estimating gas for complex transactions
- Switching between different blockchain networks
- Querying historical blockchain data

### Performance Benchmarks
- RPC response time under 50ms
- Support 100+ concurrent connections
- Process 1000+ transactions per second
- Event emission latency under 100ms
- Block generation at precise intervals

### Edge Cases and Error Conditions
- Handling invalid transaction signatures
- Transaction reversion and error messages
- Event log overflow conditions
- Gas price spike scenarios
- Chain reorganization handling

### Required Test Coverage
- Minimum 95% code coverage for all core modules
- 100% coverage for RPC method implementations
- Specification compliance tests
- Integration tests with Web3 libraries
- Multi-chain scenario tests

**IMPORTANT**:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- REQUIRED: Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria

The implementation will be considered successful when:

1. All standard Ethereum JSON-RPC methods are supported
2. Transaction lifecycle accurately mimics real blockchain behavior
3. Smart contract events work identically to real implementations
4. Gas estimations provide realistic cost predictions
5. Multi-chain support enables comprehensive dApp testing

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:
1. Create a virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in editable mode with `uv pip install -e .`
4. Install test dependencies including pytest-json-report

## Validation

The final implementation must be validated by:
1. Running all tests with pytest-json-report
2. Generating and providing the pytest_results.json file
3. Demonstrating all five key requirements are fully implemented
4. Showing compatibility with standard Web3 libraries

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.