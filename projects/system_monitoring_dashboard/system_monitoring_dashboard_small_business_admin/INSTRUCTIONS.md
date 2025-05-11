# Small Business Monitoring Dashboard

A lightweight, resource-efficient system monitoring solution designed specifically for growing e-commerce businesses with limited IT resources.

## Overview

The Small Business Monitoring Dashboard is a specialized implementation of the PyMonitor system that focuses on providing essential server and service monitoring capabilities without requiring significant system resources or technical expertise. It's designed for businesses that can't afford enterprise monitoring solutions but still need reliable insights into their critical infrastructure.

## Persona Description

Marcus manages IT infrastructure for a growing e-commerce business with limited technical resources. He needs to monitor critical servers and services without dedicating an entire system or significant budget to enterprise-grade monitoring solutions.

## Key Requirements

1. **Small Footprint Agent with Minimal Resource Impact** - Implement a lightweight monitoring agent that consumes less than 2% of CPU and 100MB of memory on production systems. This is critical for Marcus as he cannot afford to degrade the performance of production servers that directly impact customer experience and sales.

2. **Business Hours Alerting Profiles** - Create a flexible alerting system that can apply different threshold rules during business and non-business hours. Marcus needs this because performance issues during peak business hours require immediate attention, while after-hours alerts can be less sensitive to avoid unnecessary emergency responses.

3. **Non-Technical Summary Reports** - Develop a reporting module that can generate easy-to-understand system health reports for sharing with non-technical management. This allows Marcus to communicate system status effectively to business stakeholders who need visibility into IT operations but lack technical knowledge.

4. **Service Availability Checks** - Implement functionality to monitor availability of critical business applications and payment processing services beyond basic system metrics. For an e-commerce business, these service-level checks are essential as they directly impact revenue generation and customer satisfaction.

5. **Single-Admin Deployment Capability** - Design an installation and configuration system that doesn't require specialized knowledge or a team of administrators to set up. As the sole IT administrator, Marcus needs to be able to deploy and configure the monitoring system without external assistance or extensive training.

## Technical Requirements

### Testability Requirements
- All components must be unit-testable with pytest
- Metrics collection must support mocking for testing without actual system impacts
- Alert logic must be testable with simulated threshold breaches
- Service checks must support mock services for validation

### Performance Expectations
- Agent must use less than 2% CPU and 100MB RAM on monitored systems
- Collection intervals should be configurable but default to once per minute
- Database storage should efficiently handle 30 days of metrics with pruning mechanisms
- Report generation should complete in under 30 seconds regardless of data volume

### Integration Points
- Email integration for alerts and reports
- Webhook support for connecting to business systems
- SMTP server configuration for email delivery
- HTTP/HTTPS for service availability checks
- Standard Python libraries for system metrics collection

### Key Constraints
- Must work across Linux, Windows, and macOS systems common in small business environments
- Database storage must be lightweight (SQLite, file-based, etc.)
- All components must be deployable by a single administrator
- No dependencies on external monitoring services or cloud platforms
- Must operate with minimal configuration on standard networks

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Small Business Monitoring Dashboard must implement the following core functionality:

1. **Resource-Efficient Metrics Collection**
   - CPU, memory, disk, and network utilization monitoring
   - Process-level metrics for key business applications
   - Service status checks for web servers, databases, and payment systems
   - Configurable collection intervals with adaptive sampling

2. **Business-Aware Alerting System**
   - Time-sensitive threshold configuration (business hours vs. non-business hours)
   - Multi-channel notifications (email, log, webhook)
   - Alert severity classification and routing
   - Alert acknowledgment and resolution tracking

3. **Management Reporting System**
   - Business-focused system health summaries
   - Resource utilization trends with predictive warnings
   - Service availability statistics and uptime reporting
   - Incident history and resolution metrics

4. **Simplified Administration**
   - Configuration through simple YAML/JSON files
   - Default templates for common small business setups
   - Validation of configuration before deployment
   - Automated agent deployment to monitored systems

5. **Historical Data Management**
   - Efficient storage of historical metrics
   - Data retention policies with configurable timeframes
   - Data summarization for long-term trend analysis
   - Export capabilities for compliance and audit purposes

## Testing Requirements

The implementation must include comprehensive tests that validate:

### Key Functionalities Verification
- Metrics collection accuracy compared to known system states
- Alert triggering based on threshold configurations
- Report generation with expected content and format
- Service availability detection for both healthy and failed services
- Configuration loading and validation

### Critical User Scenarios
- Setting up monitors for standard e-commerce components
- Receiving and managing alerts during business hours vs. after hours
- Generating management reports on schedule and on-demand
- Adding new services to the monitoring configuration
- Deploying monitoring to new systems in the environment

### Performance Benchmarks
- CPU and memory usage of the agent under various system loads
- Database storage efficiency for 1, 7, and 30 days of metrics
- Alert latency from threshold breach to notification delivery
- Report generation time for various time ranges and metrics
- Configuration changes propagation time

### Edge Cases and Error Handling
- Network failures between monitoring components
- Database corruption or access issues
- Invalid configuration scenarios
- System resource exhaustion on monitored hosts
- Handling of rapidly flapping service states

### Required Test Coverage
- 95% code coverage for core monitoring functionality
- 100% coverage of alert logic and threshold evaluation
- 100% coverage of configuration parsing and validation
- 90% coverage of reporting functionality

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. A single administrator can deploy the complete monitoring solution within 1 hour to a standard small business environment
2. System resource utilization stays below 2% CPU and 100MB RAM on all monitored systems
3. Critical service outages are detected and reported within 1 minute during business hours
4. Management reports are understandable by non-technical stakeholders without explanation
5. Alert thresholds can be separately configured for business hours and non-business hours
6. All functionality can be managed through configuration files without requiring code changes
7. Historical data retention and management operates automatically without administrator intervention
8. All components pass their respective test suites with required coverage levels

---

To set up your development environment:

1. Create a virtual environment:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the required dependencies
   ```
   uv pip install -e .
   ```