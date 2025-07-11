# PyMigrate Financial Time-Series Migration Framework

## Overview
A specialized data migration framework designed for financial analysts migrating high-frequency trading data between systems while preserving microsecond-precision timestamps and maintaining strict transaction ordering. This implementation ensures temporal consistency, regulatory compliance, and zero data loss for critical financial operations.

## Persona Description
A financial analyst migrating trading data between systems who needs to preserve microsecond-precision timestamps and maintain data order. She requires guarantees about temporal consistency and transaction atomicity.

## Key Requirements

1. **Time-series aware migration with tick data ordering preservation**
   - Critical for maintaining market data integrity where order of events determines trade outcomes. Preserves microsecond-level timestamps and ensures chronological ordering across all migrated records, preventing temporal anomalies that could affect analysis or compliance.

2. **Market hours-aware scheduling to avoid active trading periods**
   - Intelligently schedules migrations around market hours, holidays, and trading halts. Considers multiple market timezones and trading calendars to minimize impact on real-time trading systems and ensure data consistency.

3. **Transaction boundary detection for atomic financial operations**
   - Identifies and preserves transaction boundaries to maintain financial integrity. Ensures related trades, orders, and settlements migrate as atomic units, preventing partial transaction states that could corrupt financial records.

4. **Currency and decimal precision conversion with rounding rules**
   - Handles currency conversions and decimal precision requirements across different financial systems. Implements jurisdiction-specific rounding rules and maintains audit trails for all numerical transformations to ensure regulatory compliance.

5. **Regulatory reporting integration for migration audit trails**
   - Generates comprehensive audit reports compliant with financial regulations (MiFID II, Dodd-Frank, RegNMS). Provides timestamped evidence of data lineage, transformations, and integrity checks required for regulatory audits.

## Technical Requirements

### Testability Requirements
- All components must be testable via pytest without manual intervention
- Mock trading systems with realistic market data
- Time manipulation for market hours testing
- Precision validation for financial calculations

### Performance Expectations
- Maintain microsecond timestamp precision throughout migration
- Process 1M+ trades per hour without ordering violations
- Sub-millisecond transaction boundary detection
- Support for 10+ decimal precision in calculations

### Integration Points
- FIX protocol message handling and generation
- Market data feed formats (ITCH, OUCH, FIX/FAST)
- Regulatory reporting APIs (ARM, TRS, CAT)
- Time synchronization services (NTP, PTP)

### Key Constraints
- Zero tolerance for timestamp corruption or reordering
- Maintain numerical precision for all financial values
- Support for leap seconds and market time adjustments
- Compliance with financial data retention requirements

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Temporal Integrity Engine**: Preserves microsecond timestamps with timezone awareness, maintains strict chronological ordering across partitions, handles leap seconds and time adjustments correctly, and provides temporal conflict resolution mechanisms

2. **Market Calendar Scheduler**: Integrates with global market calendars and holidays, calculates optimal migration windows automatically, supports dynamic rescheduling for market events, and provides pre/post market data handling rules

3. **Transaction Atomicity Manager**: Detects transaction boundaries using business logic, groups related financial operations together, implements two-phase commit for migrations, and maintains referential integrity across systems

4. **Precision Arithmetic Processor**: Handles arbitrary precision decimal calculations, implements regulatory-compliant rounding rules, maintains currency conversion accuracy, and provides audit trails for all transformations

5. **Regulatory Compliance Reporter**: Generates timestamped audit trails for all operations, produces regulatory-specific report formats, maintains immutable record of all changes, and integrates with compliance management systems

## Testing Requirements

### Key Functionalities to Verify
- Timestamp preservation with microsecond accuracy
- Market hours scheduling avoiding all trading windows
- Transaction atomicity across complex trade scenarios
- Decimal precision maintained through all operations
- Regulatory reports meeting compliance requirements

### Critical User Scenarios
- Migrating high-frequency trading data during market volatility
- Handling multi-leg option trades as atomic transactions
- Processing corporate actions affecting historical prices
- Managing currency conversions during forex migrations
- Generating audit reports for regulatory examinations

### Performance Benchmarks
- Process 1M trades maintaining chronological order
- Detect transaction boundaries in <1ms per trade
- Schedule migrations avoiding 99.9% of market hours
- Maintain 15 decimal places precision in calculations
- Generate compliance reports for 1M records in <5 minutes

### Edge Cases and Error Conditions
- Clock drift between source and target systems
- Trades occurring at market open/close boundaries
- Circular dependencies in transaction references
- Precision loss in extreme value calculations
- Regulatory rule changes during migration

### Required Test Coverage
- Minimum 95% code coverage for financial calculations
- Temporal ordering tests with microsecond precision
- Market calendar accuracy across all supported markets
- Transaction atomicity under failure conditions
- Regulatory report completeness validation

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

The implementation is successful when:

1. **All tests pass** when run with pytest, with 95%+ code coverage for financial components
2. **A valid pytest_results.json file** is generated showing all tests passing
3. **Temporal integrity** maintains microsecond precision and ordering
4. **Market scheduling** avoids 99.9% of active trading windows
5. **Transaction atomicity** preserves all multi-part transactions
6. **Precision handling** maintains accuracy to 15 decimal places
7. **Regulatory compliance** generates complete audit trails

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:

```bash
cd /path/to/data_migration_framework_financial_analyst
uv venv
source .venv/bin/activate
uv pip install -e .
```

Install the project and run tests:

```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

**REMINDER**: The pytest_results.json file is MANDATORY and must be included to demonstrate that all tests pass successfully.