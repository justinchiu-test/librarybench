# Bakery Showcase CMS

A specialized content management system designed for bakery owners to easily showcase their products and promotions.

## Overview

Bakery Showcase CMS is a specialized content management library tailored for small bakery businesses. It enables bakery owners to create, manage, and update their digital menu, showcase seasonal specialties, and connect with customers through reviews and special order capabilities, all without requiring technical expertise.

## Persona Description

Sophia runs a small family bakery and wants to showcase her products and share seasonal specialties with customers. Her primary goal is to easily update her menu and special offers without technical assistance while maintaining a visually appealing site that reflects her brand's warm, artisanal aesthetic.

## Key Requirements

1. **Visual Menu Builder**: Create a programmatic API for building and organizing bakery menu items with food-specific templates for different product types (bread, pastries, cakes, etc.). This is critical as it allows Sophia to quickly reorganize her offerings and update prices without having to modify complex code or HTML directly.

2. **Time-based Content Scheduling**: Develop a scheduling system that automatically publishes and unpublishes content based on calendar dates. This feature is essential for the bakery's seasonal offerings, holiday specials, and limited-time promotions, enabling Sophia to prepare content in advance.

3. **Customer Review Management**: Implement a review collection, storage, and moderation system with filtering capabilities. This allows Sophia to build trust with new customers by showcasing authentic feedback while having controls to address any inappropriate content.

4. **Mobile-optimized Image Management**: Create an image processing subsystem that automatically optimizes, resizes, and enhances product photos for different display contexts. For a bakery, appealing visual presentation is crucial to sales, making this feature vital for Sophia's business.

5. **Custom Order Form Builder**: Develop a flexible form creation system that allows for special request fields and order specifications. This enables Sophia to collect detailed information for custom cake orders, catering requests, and special dietary needs, enhancing her business capabilities.

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% coverage
- Image processing functions must be testable without requiring actual image files (using binary data or test fixtures)
- Time-based content scheduling must be testable with mocked time functions
- Form validation must be comprehensively tested with a wide range of inputs
- API responses must be consistent and testable

### Performance Expectations
- Menu rendering operations must complete within 100ms
- Image processing operations should be optimized for speed (max 1s per image)
- The system should handle at least 100 concurrent content requests
- Database operations should be optimized for small datasets (typical bakery would have <200 products)
- Content scheduling checks should have minimal overhead (<50ms)

### Integration Points
- Support for common storage backends (local filesystem, SQLite, optional cloud storage)
- API endpoints for all core functions
- Content export in structured formats (JSON, CSV)
- Webhook support for integration with notification systems
- Optional email integration for order notifications

### Key Constraints
- All code must be pure Python with minimal dependencies
- No JavaScript dependencies or browser-specific code
- No direct coupling to web frameworks, though adaptors can be provided
- All content must be serializable for backup/restore
- Must work offline for content creation and management

## Core Functionality

The library must provide the following core components:

1. **Content Management Core**:
   - Data models for bakery-specific content types (menu items, specials, etc.)
   - CRUD operations for all content types
   - Version history and change tracking
   - Content categorization and organization

2. **Menu Management System**:
   - Product categorization (bread, pastries, cakes, etc.)
   - Price management and special pricing rules
   - Ingredient and allergen tracking
   - Availability management

3. **Scheduling System**:
   - Date-based content publication
   - Recurring schedules for regular specials
   - Season and holiday-based content triggers
   - Preview of scheduled content changes

4. **Review System**:
   - Review collection and storage
   - Moderation workflow
   - Rating aggregation
   - Response management

5. **Media Management**:
   - Image storage and categorization
   - Automatic image optimization
   - Thumbnail generation
   - Metadata management (alt text, descriptions)

6. **Order Forms**:
   - Form field definition and validation
   - Custom field types for bakery-specific information
   - Form submission handling and storage
   - Form analytics

## Testing Requirements

### Key Functionalities to Verify
- Creation, retrieval, update, and deletion of all content types
- Correct scheduling behavior for time-based content
- Image optimization and transformation capabilities
- Review submission, retrieval, and moderation flows
- Form creation, validation, and submission handling

### Critical User Scenarios
- Adding new seasonal menu items with time-based availability
- Processing and displaying customer reviews with moderation
- Creating custom order forms for special occasions
- Managing a complete product catalog with categories
- Scheduling holiday-specific promotions

### Performance Benchmarks
- Menu rendering time under different catalog sizes
- Image processing time for various image sizes and transformations
- Content retrieval time when filtering by different criteria
- System behavior under concurrent operations
- Memory usage patterns during bulk operations

### Edge Cases and Error Conditions
- Handling malformed input data in all API functions
- Proper rollback of transactions when operations fail
- Behavior when scheduled content dates conflict
- Recovery from corrupted image files
- Form handling with missing or invalid form fields

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core components
- 100% coverage of public APIs
- All error handling paths must be tested
- Performance tests for critical operations
- Security tests for user input validation

## Success Criteria

The implementation will be considered successful when:

1. A bakery owner can manage their entire product catalog without writing any code
2. Seasonal content automatically appears and disappears based on configured dates
3. Customer reviews can be collected, moderated, and displayed with minimal effort
4. Product images are automatically optimized for both desktop and mobile viewing
5. Custom order forms can be created that capture all necessary information for special orders
6. All operations can be performed programmatically through a well-documented API
7. The entire system can be thoroughly tested using pytest with high coverage
8. Performance meets or exceeds the specified benchmarks

## Setup and Development

To set up your development environment:

1. Create a new Python library project:
   ```
   uv init --lib
   ```

2. Install necessary development dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a specific test:
   ```
   uv run pytest path/to/test.py::test_function_name
   ```

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```

Remember to adhere to the code style guidelines in the project's CLAUDE.md file, including proper type hints, docstrings, and error handling.