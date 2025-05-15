# Bakery Showcase Content Management System

## Overview
A specialized content management system designed for bakeries to showcase their products, share seasonal specialties, and manage customer-facing information. This system enables bakery owners to easily update their menu and special offers without technical assistance while maintaining a visually appealing site that reflects their brand's warm, artisanal aesthetic.

## Persona Description
Sophia runs a small family bakery and wants to showcase her products and share seasonal specialties with customers. Her primary goal is to easily update her menu and special offers without technical assistance while maintaining a visually appealing site that reflects her brand's warm, artisanal aesthetic.

## Key Requirements

1. **Visual drag-and-drop menu builder with food-specific display templates**
   - Critical for Sophia to organize her baked goods by categories (breads, pastries, cakes) with appropriate templates that highlight key attributes (ingredients, allergens, price)
   - Must allow visual arrangement of products to match in-store display for customer recognition
   - Should support rich product photography with configurable layouts

2. **Time-based content scheduling for seasonal offerings and promotions**
   - Essential for managing holiday specials, seasonal items, and limited-time offers that are core to bakery business
   - Must automatically publish and unpublish content based on predefined schedules
   - Should support recurring schedules for weekly specials and one-time events

3. **Customer review integration with moderation controls**
   - Important for building social proof and loyalty while maintaining control over displayed feedback
   - Must include approval workflow before reviews go public
   - Should support response functionality for owner engagement with customers

4. **Mobile-optimized image management with automatic photo enhancement**
   - Critical as food photography is essential to bakery marketing but Sophia lacks professional photography skills
   - Must optimize images for web performance while maintaining appetizing appearance
   - Should include basic enhancement tools (brightness, contrast, cropping) appropriate for food photography

5. **Order form builder with customizable fields for special requests**
   - Necessary for handling special orders like custom cakes, holiday pre-orders, and catering requests
   - Must allow creation of different forms for different types of orders with appropriate fields
   - Should include validation and notification systems for new orders

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% code coverage
- Integration tests must verify the interaction between content management and scheduling systems
- Performance tests must verify image optimization processes meet performance standards
- Mock external dependencies for testing review submission and moderation

### Performance Expectations
- Menu page load time must not exceed 2 seconds even with 50+ product images
- Image optimization must reduce file sizes by at least 40% without significant quality loss
- System must handle concurrent content editing by up to 3 staff members
- Order forms must process and validate submissions within 1 second

### Integration Points
- API for review system integration with moderation queue
- Webhook support for order form submissions to external notification systems
- Export capability for menu data to printed menu creation tools
- Import interface for bulk product uploads via CSV

### Key Constraints
- All functionality must work without external JavaScript dependencies
- Must not require server-side image processing capabilities
- Data storage must use SQLite for easy backup and portability
- All customer data must be encrypted at rest

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide a Python library with the following core components:

1. **Content Management Core**
   - Product catalog data model with support for categories, attributes, and media
   - Content scheduling engine with time-based publishing rules
   - Content versioning system with history tracking
   - Permission system for different staff roles

2. **Menu Management Module**
   - Product entry with support for food-specific attributes (ingredients, allergens, nutritional info)
   - Menu structure manager (categories, featured items)
   - Pricing and availability controls
   - Template rendering system for different product display formats

3. **Media Management Module**
   - Image upload and storage management
   - Automatic optimization for web delivery
   - Basic enhancement processing (adjusting brightness, contrast, cropping)
   - Image tagging and organization system

4. **Review System**
   - Review submission validation and storage
   - Moderation queue with approval workflow
   - Response management for owner comments
   - Rating aggregation and statistics

5. **Order Management**
   - Form definition and builder functionality
   - Field validation and conditional logic
   - Submission handling and notification
   - Order tracking and status management

## Testing Requirements

### Key Functionalities to Verify
- Menu item creation, update, and deletion with all attributes correctly stored
- Scheduled content appears and disappears at exactly the configured times
- Images are properly optimized and enhanced according to specifications
- Review moderation correctly filters and controls displayed reviews
- Order forms correctly validate input and process submissions

### Critical User Scenarios
- Creating a seasonal menu with scheduled publication dates
- Managing a holiday pre-order campaign with custom order form
- Processing and responding to customer reviews
- Setting up recurring weekly specials with different featured items
- Creating a new product catalog with categorized items and images

### Performance Benchmarks
- Image optimization processing must complete within 3 seconds per image
- Database queries for menu display must complete within 100ms
- Full content publication process must complete within 5 seconds
- System must support at least 100 concurrent order form submissions

### Edge Cases and Error Conditions
- Handling incomplete product information
- Managing conflicting scheduled content
- Processing malformed or spam review submissions
- Recovering from interrupted image uploads
- Handling special characters in custom order requests

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of data validation functions
- 100% coverage of scheduled publication logic
- 100% coverage of order form validation

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

The implementation will be considered successful when:

1. The library provides a comprehensive API for managing bakery product content with support for all required product attributes
2. The scheduling system correctly publishes and unpublishes content based on configured times
3. Image management includes automatic optimization and enhancement appropriate for food photography
4. Review system includes complete moderation workflow with approval controls
5. Order form creation supports all required customization with proper validation

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. Use `uv venv` to create a virtual environment
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```