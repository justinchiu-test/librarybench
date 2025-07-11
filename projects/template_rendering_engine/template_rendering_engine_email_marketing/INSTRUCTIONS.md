# PyTemplate for Email Campaign Management

## Overview
A specialized template rendering engine for creating personalized email campaigns with dynamic content generation, A/B testing support, and comprehensive email client compatibility features for marketing professionals.

## Persona Description
A marketing manager creating personalized email campaigns who needs dynamic content generation with A/B testing support. He wants to create sophisticated email templates that adapt to recipient data while ensuring email client compatibility.

## Key Requirements
1. **Email-safe HTML generation with inline CSS conversion**: The engine must automatically convert external stylesheets to inline styles and ensure HTML compatibility across major email clients (Outlook, Gmail, Apple Mail). This is critical because email clients have limited CSS support and inline styles are the only reliable way to ensure consistent rendering.

2. **Dynamic content blocks with personalization tokens**: Support for flexible content blocks that can be personalized based on recipient data (name, preferences, purchase history) with fallback values. This enables highly targeted campaigns that drive better engagement rates.

3. **A/B test variant generation from single template**: Ability to generate multiple variants of an email from a single template definition, with different subject lines, content blocks, or CTAs. This is essential for optimizing campaign performance through systematic testing.

4. **Email client compatibility checking and warnings**: Built-in validation that checks for unsupported HTML/CSS features and provides warnings about potential rendering issues. This prevents campaigns from looking broken in popular email clients.

5. **Preview rendering for multiple email clients**: Generate accurate previews showing how emails will appear in different clients and devices, critical for quality assurance before sending campaigns to thousands of recipients.

## Technical Requirements
- **Testability**: All email generation and validation logic must be testable via pytest, including mock email client rendering rules
- **Performance**: Must handle bulk personalization efficiently, generating thousands of personalized emails per minute
- **Integration**: Clean API for integration with email service providers and marketing automation platforms
- **Key Constraints**: No UI components; must generate standards-compliant HTML emails; support for both HTML and plain text versions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The template engine must provide:
- CSS inliner that converts stylesheets to inline styles while preserving media queries
- Personalization token system with nested data access and default values
- A/B test variant generator with support for multiple variable elements
- Email client compatibility validator with rule sets for major clients
- Preview renderer that simulates email client rendering limitations
- Plain text version generator from HTML templates
- Link tracking and UTM parameter injection
- Dynamic content block system with conditional rendering

## Testing Requirements
All components must be thoroughly tested with pytest, including:
- **CSS inlining tests**: Verify correct conversion of various CSS rules to inline styles
- **Personalization tests**: Validate token replacement with complex data structures and fallbacks
- **A/B variant tests**: Ensure correct generation of multiple variants with proper isolation
- **Compatibility tests**: Validate detection of incompatible HTML/CSS features
- **Preview accuracy tests**: Compare generated previews against known client behaviors
- **Performance tests**: Verify bulk generation meets throughput requirements
- **Edge cases**: Handle missing personalization data, malformed HTML, circular references
- **Character encoding tests**: Ensure proper handling of international characters

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
- CSS inlining produces emails that render consistently across Outlook, Gmail, and Apple Mail
- Personalization handles complex data structures with proper fallback behavior
- A/B test generation creates properly isolated variants for valid testing
- Compatibility checker catches common email client issues with 95% accuracy
- Preview rendering accurately represents major email client behaviors
- Bulk generation processes 10,000 personalized emails in under 60 seconds
- All tests pass with comprehensive coverage of the API

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
1. Create a new virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Run tests with pytest-json-report to generate the required results file