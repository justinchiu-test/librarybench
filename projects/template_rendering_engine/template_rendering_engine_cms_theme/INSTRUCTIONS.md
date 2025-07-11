# PyTemplate for CMS Theme Development

## Overview
A specialized template rendering engine for creating flexible, customizable CMS themes with a robust widget system, theme inheritance, and safe end-user customization capabilities while maintaining design integrity.

## Persona Description
A theme developer creating customizable CMS themes who needs a flexible template system with widget support. She requires templates that can be customized by end-users without breaking the design.

## Key Requirements
1. **Widget/component slot system with fallbacks**: Implement a flexible slot system where widgets can be placed, rearranged, and configured with automatic fallback to default content when widgets are missing. This is critical for creating themes that remain functional even when users remove or misconfigure components.

2. **Theme inheritance with override mechanisms**: Support multi-level theme inheritance where child themes can selectively override parent theme templates, styles, and components. This enables theme variations and white-label solutions while maintaining a consistent base.

3. **User-safe template subset for customization**: Provide a restricted template language subset that end-users can safely use without accessing dangerous functions or breaking the site. This is essential for allowing customization while preventing security vulnerabilities and site crashes.

4. **Responsive design helper functions**: Include built-in helpers for responsive layouts, breakpoints, and device-specific rendering that work across the widget system. This ensures themes look professional on all devices without requiring users to understand responsive design.

5. **Theme preview with live reload**: Generate real-time previews of theme changes with automatic reload as users modify templates, styles, or widget configurations. This is crucial for providing immediate feedback during theme customization.

## Technical Requirements
- **Testability**: All theme rendering and customization logic must be testable via pytest
- **Performance**: Must handle complex themes with 50+ widgets efficiently
- **Integration**: Clean API for CMS integration with various content types and data models
- **Key Constraints**: No UI components; must sandbox user customizations; maintain theme upgrade paths

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The template engine must provide:
- Widget registry system with dependency management
- Slot-based layout engine with nested slot support
- Theme inheritance resolver with override tracking
- Safe template sandbox with whitelisted functions
- Responsive design toolkit with breakpoint management
- Live preview generator with incremental updates
- Theme validation system checking for common issues
- Widget configuration schema with validation

## Testing Requirements
All components must be thoroughly tested with pytest, including:
- **Widget system tests**: Verify correct widget loading, placement, and fallback behavior
- **Theme inheritance tests**: Validate proper override resolution and inheritance chains
- **Sandbox tests**: Ensure user templates cannot access dangerous functions
- **Responsive helper tests**: Verify correct behavior across different screen sizes
- **Preview generation tests**: Validate accurate and fast preview updates
- **Performance tests**: Benchmark rendering of complex themes with many widgets
- **Security tests**: Attempt to break sandbox with malicious templates
- **Compatibility tests**: Ensure themes work with different CMS versions

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
The implementation is successful when:
- Widget system handles complex layouts with 50+ widgets smoothly
- Theme inheritance allows 5+ levels without performance degradation
- User customizations cannot break the site or access sensitive data
- Responsive helpers generate correct layouts for mobile, tablet, and desktop
- Live preview updates in under 500ms for typical changes
- Themes remain upgradeable after user customizations
- All security sandbox tests pass without vulnerabilities
- All tests pass with comprehensive theme system validation

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
1. Create a new virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Run tests with pytest-json-report to generate the required results file