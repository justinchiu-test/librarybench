# Professional Portfolio Site Generator

A specialized static site generator designed for small business owners to create and maintain professional websites showcasing their services, portfolio, and client testimonials without developer dependency.

## Overview

This project implements a Python library for generating professional business websites that highlight portfolio projects, client testimonials, and service offerings. It focuses on the needs of small business owners who want to maintain control over their web presence while ensuring professional presentation and search engine optimization.

## Persona Description

Elena runs a boutique design studio and needs a professional website that showcases her portfolio, services, and client testimonials. She wants to update content herself without depending on web developers for every change.

## Key Requirements

1. **Portfolio Project Templates**: Create a flexible system for showcasing portfolio projects with consistent layouts but customizable content for each project.
   - Critical for Elena because her design work needs to be displayed professionally with consistent branding, while allowing each project to highlight its unique aspects and results.
   - Must include support for various media types, project metadata, and categorization.

2. **Client Testimonial Management**: Implement a system for managing client testimonials with an approval workflow before publication.
   - Essential for Elena because positive client feedback is a powerful marketing tool, but she needs to collect, review, and obtain approval before showcasing testimonials on her site.
   - Should include metadata for attribution, dates, and related projects.

3. **Contact Form Generation**: Create functionality for generating contact forms that work without requiring server-side processing.
   - Important for Elena because potential clients need an easy way to reach her, but she doesn't want to maintain server-side infrastructure for form processing.
   - Must integrate with third-party form processors or email services.

4. **SEO Optimization Tools**: Provide tools to analyze content for search engine visibility and suggest improvements.
   - Valuable for Elena because being discoverable online is crucial for her business, but she doesn't have specialized SEO expertise.
   - Should provide actionable recommendations for improving content visibility.

5. **Local Business Schema Markup**: Generate structured data markup for local businesses to enhance search engine results.
   - Critical for Elena because proper schema markup improves how her business appears in search results with business hours, location, services, and ratings prominently displayed.
   - Must comply with schema.org standards for local businesses.

## Technical Requirements

### Testability Requirements
- All components must be individually testable through well-defined interfaces
- Implement fixtures for testing with sample portfolio projects and testimonials
- Support snapshot testing for generated HTML and schema markup
- Test suites must validate SEO metrics against established benchmarks
- Support mocking of external services for form processing

### Performance Expectations
- Generate a complete business site with 25+ projects in under 15 seconds
- Image optimization pipelines should process high-resolution portfolio images efficiently
- Schema markup generation should be validated against official schemas with no errors
- SEO analysis should provide actionable feedback in under 5 seconds per page
- Generated sites should achieve 90+ scores on Google PageSpeed Insights (to be simulated in tests)

### Integration Points
- Third-party form processing services
- Schema.org specifications and validation tools
- SEO analysis libraries and algorithms
- Image optimization and transformation libraries
- Content delivery networks for optimized asset delivery

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must generate completely static HTML that works without any server-side processing
- Output must be fully accessible and SEO-optimized
- Contact forms must function without requiring dedicated servers
- Must work with both local file systems and content management workflows
- Generated sites must be easily deployable to standard hosting providers

## Core Functionality

The Professional Portfolio Site Generator should provide a comprehensive Python library with the following core capabilities:

1. **Portfolio Management System**
   - Process portfolio project data from structured formats (YAML, JSON, etc.)
   - Support for custom fields and metadata for different project types
   - Handle media assets with proper optimization and responsive design
   - Implement categorization, filtering, and sorting of projects
   - Generate consistent portfolio layouts with customizable elements

2. **Testimonial Management**
   - Process testimonial entries with attribution and metadata
   - Support for approval workflow states (pending, approved, featured)
   - Link testimonials to relevant portfolio projects
   - Generate displays with proper formatting and attribution
   - Support for featuring selected testimonials prominently

3. **Static Form Generation**
   - Create HTML forms that work without server-side processing
   - Integrate with third-party form processors (Formspree, Netlify Forms, etc.)
   - Implement client-side validation with accessible error messages
   - Generate necessary configuration for form processing
   - Support for custom form fields and layouts

4. **SEO Optimization Engine**
   - Analyze content for keyword usage and optimization opportunities
   - Check meta tags, headings, and content structure
   - Verify image alt text and accessibility features
   - Generate sitemaps and robots.txt
   - Provide actionable recommendations for improvement

5. **Schema Markup Generator**
   - Create JSON-LD structured data for local businesses
   - Support for services, opening hours, location, and contact info
   - Generate reviews and aggregate ratings markup
   - Implement organization and breadcrumb schemas
   - Validate output against Schema.org specifications

## Testing Requirements

### Key Functionalities to Verify

1. **Portfolio Generation**
   - Test creation of portfolio collections from various data sources
   - Verify proper rendering of different project types and categories
   - Test image processing and optimization
   - Confirm navigation and filtering mechanisms
   - Verify responsive layouts for various screen sizes

2. **Testimonial System**
   - Test testimonial processing with various approval states
   - Verify proper attribution and formatting
   - Test linking of testimonials to portfolio projects
   - Confirm featured testimonial selection logic
   - Verify accessibility compliance for testimonial displays

3. **Contact Form Functionality**
   - Test form HTML generation with various field configurations
   - Verify client-side validation functionality
   - Test integration with supported form processors
   - Confirm accessible error messaging
   - Verify form submission simulation

4. **SEO Analysis and Optimization**
   - Test content analysis algorithms against known benchmarks
   - Verify meta tag generation and optimization
   - Test sitemap and robots.txt creation
   - Confirm keyword analysis functionality
   - Verify recommendation engine accuracy

5. **Schema Markup**
   - Test generation of local business schema
   - Verify correct formatting of JSON-LD output
   - Test validation against Schema.org specifications
   - Confirm inclusion of all required business attributes
   - Verify review and rating markup generation

### Critical User Scenarios

1. Adding a new portfolio project and seeing it properly categorized and displayed
2. Processing and approving a new client testimonial
3. Configuring and testing a contact form without server infrastructure
4. Analyzing a page for SEO opportunities and implementing recommendations
5. Setting up complete local business schema for improved search listings

### Performance Benchmarks

- Full site build with 25+ portfolio projects should complete in under 15 seconds
- Image processing should optimize 50+ portfolio images in under 30 seconds
- Schema markup generation should complete in under 1 second
- SEO analysis should process a typical page in under 3 seconds
- Memory usage should not exceed 500MB for typical business site generation

### Edge Cases and Error Conditions

- Test handling of missing portfolio images
- Verify graceful handling of incomplete project metadata
- Test behavior with malformed testimonial data
- Verify proper error reporting for invalid schema configurations
- Test with unusually large portfolio collections
- Validate behavior with special characters in business information

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for schema markup generation
- 100% coverage for form generation logic
- Integration tests for the entire build pipeline
- Performance tests for both small and large portfolio sites

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

The Professional Portfolio Site Generator will be considered successful if it:

1. Correctly generates portfolio project showcases with consistent layout but customizable content
2. Properly manages client testimonials with appropriate approval workflows
3. Creates functional contact forms that work without server-side processing
4. Provides accurate SEO analysis and actionable recommendations
5. Generates valid, comprehensive schema markup for local businesses
6. Builds sites efficiently with proper asset optimization
7. Produces accessible, SEO-friendly HTML output
8. Creates all necessary site structure elements (portfolio categories, service pages, etc.)

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up your development environment:

1. Create a virtual environment using UV:
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

4. CRITICAL: When testing, you must generate the pytest_results.json file:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

This file is MANDATORY proof that all tests pass and must be included with your implementation.