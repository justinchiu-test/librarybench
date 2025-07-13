# PyMigrate Infrastructure-as-Code Migration Framework

## Overview
A specialized data migration framework designed for DevOps leads automating database migrations across multiple environments through infrastructure-as-code practices. This implementation integrates seamlessly with CI/CD pipelines, provides GitOps-compatible configurations, and enables cloud-native orchestration for modern DevOps workflows.

## Persona Description
A DevOps lead automating database migrations across multiple environments who needs infrastructure-as-code integration. He wants to version control migration definitions and integrate with CI/CD pipelines.

## Key Requirements

1. **GitOps-compatible migration definitions with version control**
   - Enables declarative migration configurations stored in Git repositories. Supports branching strategies, pull request workflows, and automatic synchronization between Git state and migration state, ensuring full auditability and rollback capabilities.

2. **Environment-specific configuration with secret management**
   - Provides flexible configuration management for dev, staging, and production environments. Integrates with secret management systems (Vault, AWS Secrets Manager, Kubernetes Secrets) to handle sensitive credentials securely without hardcoding.

3. **Kubernetes operator for cloud-native migration orchestration**
   - Implements a custom Kubernetes operator that manages migration lifecycles as custom resources. Enables native Kubernetes deployment patterns, automatic scaling, and self-healing capabilities for migration workloads.

4. **Prometheus metrics export for migration monitoring**
   - Exposes comprehensive metrics about migration progress, performance, and errors. Provides dashboards-ready metrics compatible with Prometheus/Grafana stack for real-time monitoring and alerting on migration health.

5. **Terraform provider for infrastructure provisioning coordination**
   - Offers a custom Terraform provider to manage migrations as infrastructure resources. Coordinates database provisioning, migration execution, and infrastructure dependencies in a single declarative workflow.

## Technical Requirements

### Testability Requirements
- All components must be testable via pytest without manual intervention
- Mock Kubernetes API for operator testing
- Simulated Git operations for GitOps workflows
- Mock secret management systems

### Performance Expectations
- Sub-second Git synchronization for configuration changes
- Support for managing 1000+ migrations across environments
- Prometheus metrics collection with <100ms overhead
- Kubernetes operator reconciliation loop <5 seconds

### Integration Points
- Git providers (GitHub, GitLab, Bitbucket) webhooks
- Kubernetes API and Custom Resource Definitions
- HashiCorp Vault and cloud secret managers
- CI/CD systems (Jenkins, GitLab CI, GitHub Actions)

### Key Constraints
- Stateless operation for horizontal scaling
- Idempotent migrations for reliability
- Zero secrets in logs or Git repositories
- Cloud-agnostic implementation

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **GitOps Configuration Manager**: Parses YAML/JSON migration definitions from Git, implements Git-based state reconciliation, supports environment inheritance and overrides, and provides dry-run capabilities for changes

2. **Environment Configuration Engine**: Manages environment-specific parameters, integrates with multiple secret backends, implements secret rotation handling, and provides configuration validation and defaults

3. **Kubernetes Migration Operator**: Defines Custom Resource Definitions for migrations, implements controller reconciliation logic, manages migration job lifecycle, and provides status reporting and events

4. **Metrics Collector**: Exposes Prometheus-compatible metrics endpoint, tracks migration duration and throughput, monitors error rates and types, and provides custom business metrics hooks

5. **Terraform Provider Implementation**: Implements CRUD operations for migration resources, manages migration state in Terraform, handles dependencies between resources, and provides import capabilities for existing migrations

## Testing Requirements

### Key Functionalities to Verify
- GitOps synchronization correctly applies configurations
- Environment configurations properly isolate secrets
- Kubernetes operator manages migration lifecycle correctly
- Metrics accurately reflect migration state
- Terraform provider maintains proper state

### Critical User Scenarios
- Promoting migrations from dev through staging to production
- Rolling back failed production migrations via Git revert
- Scaling migration workloads during high-load periods
- Monitoring migration performance across all environments
- Coordinating infrastructure and migration changes together

### Performance Benchmarks
- Git sync latency <1 second for configuration updates
- Support 100 concurrent migrations per environment
- Operator handling 1000 migration CRDs efficiently
- Metrics scraping completing in <100ms
- Terraform plan execution in <30 seconds

### Edge Cases and Error Conditions
- Git repository unavailable during sync
- Secret rotation during active migration
- Kubernetes cluster failures mid-migration
- Metrics storage exhaustion
- Terraform state conflicts

### Required Test Coverage
- Minimum 90% code coverage with pytest
- Integration tests for all external systems
- End-to-end GitOps workflow tests
- Chaos engineering tests for operator resilience
- Performance tests under load

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

1. **All tests pass** when run with pytest, with 90%+ code coverage
2. **A valid pytest_results.json file** is generated showing all tests passing
3. **GitOps workflows** synchronize configurations within 1 second
4. **Multi-environment support** handles 10+ environments seamlessly
5. **Kubernetes operator** manages complete migration lifecycle
6. **Metrics** provide comprehensive observability
7. **Terraform provider** enables full IaC workflows

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:

```bash
cd /path/to/data_migration_framework_devops_lead
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