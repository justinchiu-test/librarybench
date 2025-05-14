# CLI Form Library Refactoring Plan

## Current State Analysis

The CLI Form library currently exists as three separate implementations, each customized for a specific persona:

1. **Clinical Researcher** (`clinical_researcher.form_system`) - Focused on patient data collection with strict validation rules
2. **Security Officer** (`security_officer.incident_form`) - Focused on security incident reporting with masked fields and audit logging
3. **Product Manager** (`product_manager.survey`) - Focused on user surveys with export capabilities and field plugins

Despite having different focuses, these implementations share significant functionality:

| Feature | Clinical Researcher | Security Officer | Product Manager |
|---------|---------------------|------------------|-----------------|
| TextField | ✓ | ✓ | ✓ |
| DateTimePicker | ✓ | ✓ | ✓ |
| Validation | ✓ | ✓ | ✓ |
| Rendering | ✓ | ✓ | ✓ |
| Wizard Layout | ✓ | ✓ | ✓ |
| Accessibility | ✓ | ✓ | ✓ |
| Audit Logging | ✓ | ✓ | ✓ |
| Export | | | ✓ |
| Plugin System | | ✓ | ✓ |

This duplication leads to maintenance challenges and inconsistent feature implementation across personas.

## Goals for Refactoring

1. Create a unified library that eliminates code duplication
2. Maintain all existing functionality across all personas
3. Ensure backward compatibility for existing code
4. Establish a clear, modular structure that supports future extensions
5. Improve testability and documentation

## Proposed Module Structure

```
cli_form/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── fields.py          # Base field types (TextField, DateTimePicker, etc.)
│   ├── validation.py      # Input validation functionality
│   ├── renderer.py        # CLI rendering systems
│   ├── layout.py          # Layout engines (including WizardLayout)
│   └── accessibility.py   # Accessibility features
├── plugins/
│   ├── __init__.py
│   └── registry.py        # Plugin registration system
├── extensions/
│   ├── __init__.py
│   ├── security.py        # Security-specific features (masking, etc.)
│   ├── export.py          # Data export functionality
│   ├── audit.py           # Audit logging
│   └── medical.py         # Medical-specific validation rules
├── adapters/              # Backward compatibility adapters
│   ├── __init__.py
│   ├── clinical_researcher.py
│   ├── security_officer.py
│   └── product_manager.py
└── utils/
    ├── __init__.py
    └── formatters.py      # Helper functions for formatting
```

## Implementation Strategy

### Phase 1: Core Components

1. Implement the base `fields.py` module with common field types
   - Unified TextField with support for regex patterns, length limits, placeholder text
   - Unified DateTimePicker with consistent date/time handling

2. Implement validation logic in `validation.py`
   - Generic validation framework supporting different rule types
   - Support for required fields, pattern matching, range validation

3. Create rendering system in `renderer.py`
   - Base renderer class
   - Curses-based implementation

### Phase 2: Layout and Accessibility

1. Implement `layout.py` with layout engines
   - WizardLayout for multi-page forms
   - Support for navigation between pages

2. Implement accessibility features in `accessibility.py`
   - Accessibility mode toggle
   - Screen reader compatible output

### Phase 3: Extensions and Plugins

1. Implement plugin system in `plugins/registry.py`
   - Plugin registration
   - Plugin discovery and loading

2. Create extension modules
   - Security features (field masking, etc.)
   - Export functionality (JSON, YAML)
   - Audit logging

### Phase 4: Adapters for Backward Compatibility

Create adapter modules to maintain backward compatibility with existing code:
   - Map legacy functions to new unified API
   - Preserve existing function signatures
   - Redirect calls to new implementations

### Phase 5: Testing and Documentation

1. Comprehensive test suite covering all functionality
2. Documentation for the new unified API
3. Migration guides for users of existing implementations

### Phase 6: Additional Features

Implement any remaining persona-specific features not covered in the main refactoring.

## Migration Strategy

To ensure a smooth transition:

1. The unified library will coexist with existing implementations
2. Adapter modules will provide backward compatibility
3. New code should use the unified library directly
4. Existing code can be migrated incrementally

## Testing Strategy

1. **Unit Tests**: Test each component in isolation
2. **Integration Tests**: Test components working together
3. **Migration Tests**: Ensure adapter modules correctly map to new implementations
4. **Regression Tests**: Verify that all existing functionality works as expected
5. **Compatibility Tests**: Ensure backward compatibility with existing code

## Timeline

| Phase | Description | Estimated Duration |
|-------|-------------|-------------------|
| 1 | Core Components | 1 week |
| 2 | Layout and Accessibility | 1 week |
| 3 | Extensions and Plugins | 1 week |
| 4 | Adapters | 1 week |
| 5 | Testing and Documentation | 1 week |
| 6 | Additional Features | 1 week |

Total estimated time: 6 weeks

## Future Improvements

After the initial refactoring, additional improvements can be considered:

1. Enhanced accessibility features
2. More field types and validators
3. Additional export formats
4. Advanced layout options
5. Interactive form builder
6. Internationalization support

## Conclusion

This refactoring will significantly improve the maintainability of the CLI Form library while preserving all existing functionality. The modular structure will make it easier to add new features in the future, and the backward compatibility layer will ensure a smooth transition for existing users.