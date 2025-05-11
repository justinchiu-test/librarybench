# Infrastructure-as-Code Text Editor

A specialized text editor library designed for DevOps engineers working with infrastructure code across multiple cloud platforms.

## Overview

This project implements a text editor library specifically designed for DevOps engineers who write and maintain infrastructure-as-code across multiple cloud platforms. It provides cloud resource validation, environment-aware configuration rendering, secret detection, infrastructure drift detection, and visualization capabilities for infrastructure code.

## Persona Description

Sophia writes and maintains infrastructure-as-code across multiple cloud platforms. She needs specialized editing features for YAML, Terraform, and other configuration formats with awareness of deployment contexts.

## Key Requirements

1. **Cloud Resource Validation**: Implement a validation system that checks infrastructure code syntax against provider-specific schemas. This is critical for Sophia to catch configuration errors before deployment, preventing failed infrastructure updates and reducing debugging time across AWS, Azure, GCP, and other cloud providers.

2. **Environment Variable Awareness**: Develop functionality that shows different renderings of configuration files based on environment variables and deployment targets. This allows Sophia to preview how templates will render in different environments (dev, staging, production), ensuring consistent behavior across deployment targets.

3. **Secret Detection**: Create a system that identifies sensitive information (API keys, passwords, tokens) accidentally included in configuration files. This protects Sophia from inadvertently committing secrets to repositories, preventing security breaches and adhering to security best practices in infrastructure management.

4. **Infrastructure Drift Detection**: Implement comparison between infrastructure code and actual deployed resources to identify discrepancies. This helps Sophia detect when manual changes have been made to environments, ensuring infrastructure remains in the desired state and preventing "configuration drift" that leads to inconsistent environments.

5. **Infrastructure Visualization**: Develop capabilities to render visual representations of infrastructure resources and their relationships from Terraform, CloudFormation, or other IaC formats. This provides Sophia with clear visual understanding of complex infrastructure designs, helping identify resource relationships and potential issues.

## Technical Requirements

### Testability Requirements
- Validation rules must be testable with sample infrastructure code
- Environment variable rendering must be verifiable with different variable sets
- Secret detection must be testable with known patterns of sensitive information
- Drift detection must be mockable for testing without actual cloud resources
- Visualization output must be verifiable through structured representation

### Performance Expectations
- Validation should complete within 2 seconds for files up to 5MB
- Environment variable rendering should update in under 100ms when variables change
- Secret detection should scan at a rate of at least 10MB per second
- Drift detection queries should complete within configured timeouts (default 30s)
- Visualization generation should complete in under 3 seconds for moderately complex infrastructures

### Integration Points
- Cloud provider APIs for schema validation and drift detection
- Infrastructure-as-code parsers (Terraform, CloudFormation, etc.)
- Secret scanning patterns and rules
- Environment variable management systems
- Infrastructure visualization engines

### Key Constraints
- No UI/UX components; all functionality should be implemented as library code
- Must support multiple cloud providers (AWS, Azure, GCP at minimum)
- Must handle infrastructure code in multiple formats (Terraform, CloudFormation, etc.)
- Operations should be efficient with large infrastructure definitions
- Compatible with Python 3.8+ ecosystem

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The library should implement a text editor core with the following functionality:

1. A validation system that:
   - Parses infrastructure code in multiple formats
   - Validates syntax against provider-specific schemas
   - Provides detailed error information for invalid configurations
   - Supports validation rules for multiple cloud providers

2. An environment rendering system that:
   - Resolves variables in configuration templates
   - Shows different renderings based on environment contexts
   - Highlights differences between environment-specific renderings
   - Detects potential environment-specific issues

3. A secret detection system that:
   - Scans code for common secret patterns
   - Identifies potentially sensitive information
   - Provides secure alternatives or best practices
   - Integrates with existing secret management approaches

4. A drift detection system that:
   - Compares infrastructure code with actual deployed resources
   - Identifies differences between defined and actual state
   - Provides detailed reporting on discrepancies
   - Supports multiple cloud provider APIs

5. A visualization system that:
   - Generates structural representations of infrastructure from code
   - Shows relationships between resources
   - Identifies potential issues or optimizations
   - Supports different infrastructure-as-code formats

## Testing Requirements

### Key Functionalities to Verify
- Validation correctly identifies valid and invalid infrastructure configurations
- Environment variable rendering properly resolves variables in different contexts
- Secret detection accurately identifies sensitive information patterns
- Drift detection successfully compares code with simulated actual resources
- Visualization correctly represents infrastructure relationships from code

### Critical User Scenarios
- Validating a Terraform configuration against AWS provider schemas
- Viewing a configuration rendered with different environment variables
- Detecting accidentally committed API keys in infrastructure code
- Comparing infrastructure code with actual deployed resources
- Visualizing the resource relationships in a complex infrastructure stack

### Performance Benchmarks
- Validation should process at least 5,000 lines of infrastructure code per second
- Environment rendering should handle at least 100 variable substitutions per second
- Secret detection should identify at least 95% of common secret patterns
- Drift detection should support comparison of at least 500 resources in under 30 seconds
- Visualization should handle infrastructure definitions with up to 200 interconnected resources

### Edge Cases and Error Conditions
- Handling very large infrastructure definitions (10MB+)
- Managing incomplete or invalid infrastructure code
- Dealing with rate limits or timeouts from cloud provider APIs
- Processing infrastructure spanning multiple providers or accounts
- Handling custom or non-standard resource types

### Required Test Coverage Metrics
- Minimum 90% code coverage across all core modules
- 100% coverage of validation and secret detection rules
- Complete coverage of all public API methods
- All supported cloud providers must have validation tests
- All supported infrastructure formats must have parsing tests

IMPORTANT:
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

The implementation will be considered successful if:

1. Cloud resource validation correctly identifies valid and invalid infrastructure configurations
2. Environment variable awareness properly shows how configurations will render in different environments
3. Secret detection successfully identifies sensitive information in infrastructure code
4. Infrastructure drift detection accurately compares infrastructure code with actual resources
5. Infrastructure visualization provides clear representation of resources and their relationships

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:

1. Create a virtual environment:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: For running tests and generating the required json report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing pytest_results.json is a critical requirement for project completion.