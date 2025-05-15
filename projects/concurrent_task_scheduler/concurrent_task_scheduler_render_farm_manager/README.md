# Render Farm Manager

A comprehensive render farm management system for distributed rendering.

## Test Cases Added

The following test cases have been added to the codebase:

1. **Fault Tolerance**
   - `test_fault_tolerance.py`: Tests system resilience to multiple simultaneous node failures
   - Verifies jobs are properly rescheduled when nodes fail
   - Checks that node failure tracking is properly performed

2. **Resource Borrowing**
   - `test_resource_borrowing.py`: Tests client resource borrowing capabilities
   - Verifies resource sharing between clients with different demand
   - Tests different borrowing limit percentages and their effects

3. **Error Recovery**
   - `test_error_recovery.py`: Tests job recovery via checkpoints after failures
   - Verifies behavior with multiple sequential failures
   - Tests error count threshold handling

4. **Energy Modes**
   - `test_energy_modes.py`: Tests dynamic switching between energy modes
   - Verifies night savings mode functionality for energy-intensive jobs
   - Validates power efficiency considerations in scheduling

5. **Job Dependencies**
   - `test_job_dependencies.py`: Tests proper handling of job dependency chains
   - Verifies child jobs only run after parent jobs complete
   - Tests priority inheritance for dependent jobs
   - Handles circular dependency detection

6. **Audit Logging**
   - `test_audit_logging.py`: Tests comprehensive logging of system operations
   - Verifies proper log level handling
   - Tests performance metrics tracking alongside audit logs

## Implementation Notes

Due to API differences between the test assumptions and actual implementation, test files need to be modified to match the actual model implementations:

1. Replace `RenderClient` with `Client`
2. Use `NodeCapabilities` for node specifications
3. Use `id` instead of `client_id`, `node_id`, etc.
4. Use string literals ("premium", "standard", "basic") instead of enum values
5. Fix manager initialization to use `performance_monitor` instead of `performance_metrics`
6. Add required error parameter to `handle_node_failure` calls

These changes ensure the tests match the actual API of the render farm manager and its components.