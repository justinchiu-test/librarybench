# Craft Brewery CMS

A specialized content management system designed for craft breweries to showcase their products, manage tap offerings, and build brand loyalty.

## Overview

Craft Brewery CMS is a comprehensive content management library tailored for craft brewery businesses. It enables brewery owners to showcase their brewery's story, manage current tap offerings, announce upcoming releases, document brewing processes, and build brand loyalty through engaging content experiences while ensuring regulatory compliance.

## Persona Description

Carlos needs to showcase his brewery's story, current tap offerings, and upcoming events to beer enthusiasts. His primary goal is to frequently update beer descriptions and availability while building brand loyalty through an engaging content experience that reflects his brewery's unique personality.

## Key Requirements

1. **Beer Catalog with Custom Attributes**: Develop a flexible product catalog system with customizable attributes for detailed beer characteristics (IBU, ABV, hop varieties, flavor notes, etc.). This is critical for Carlos as craft beer consumers expect detailed information about the flavor profiles, ingredients, and brewing processes that distinguish each unique beer in his rotating selection.

2. **Real-time Tap Room Status Board**: Create a dynamic inventory management system that enables real-time updates to tap room availability. This feature is essential as it allows Carlos to accurately communicate which beers are currently pouring, preventing customer disappointment when visiting the taproom and enabling spontaneous visits when favorite beers come on tap.

3. **Beer Release Countdown and Notifications**: Implement a scheduling and notification system for upcoming beer releases with customizable countdown displays. This functionality is vital for building anticipation around limited releases, driving taproom traffic on release days, and creating a sense of excitement and exclusivity around Carlos's most innovative creations.

4. **Brewing Process Documentation**: Develop a structured content framework for documenting and showcasing brewing processes, recipes, and behind-the-scenes content. This capability is important for storytelling that educates customers about the craft brewing process, creates transparency about ingredients and methods, and builds appreciation for the artisanal nature of Carlos's products.

5. **Age Verification System**: Create a robust age verification system with regional compliance settings to ensure legal viewing of alcohol-related content. This feature is crucial for legal compliance across different jurisdictions, protecting Carlos's business from regulatory issues while still providing an engaging experience for legally-aged visitors.

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% coverage
- Inventory and tap status updates must be thoroughly tested
- Scheduling and countdown logic must be verifiable through test fixtures
- Age verification mechanisms must be validated with comprehensive test cases
- Content rendering must be tested for consistency

### Performance Expectations
- Tap status updates must propagate within 500ms
- Beer catalog searches should return results within 100ms
- Release countdown calculations should process within 50ms
- Content rendering operations must complete within 200ms
- The system should handle at least 100 concurrent requests

### Integration Points
- Support for common storage backends (local filesystem, SQLite, optional cloud storage)
- Inventory management system integration
- Point-of-sale system compatibility
- Social media sharing capabilities
- Event calendar integration

### Key Constraints
- All code must be pure Python with minimal dependencies
- No JavaScript dependencies or browser-specific code
- No direct coupling to web frameworks, though adaptors can be provided
- All content must be serializable for backup/restore
- Must comply with alcohol advertising regulations

## Core Functionality

The library must provide the following core components:

1. **Beer Catalog System**:
   - Beer definition with customizable attributes
   - Categorization and style classification
   - Seasonal and limited release flagging
   - Search and filtering capabilities
   - Related beer recommendations

2. **Tap Room Management**:
   - Current tap lineup tracking
   - Keg level monitoring
   - Tap rotation history
   - Coming soon notifications
   - Special tapping events

3. **Release Management**:
   - Beer release scheduling
   - Countdown configuration
   - Notification system
   - Pre-order capabilities
   - Release analytics

4. **Brewing Documentation**:
   - Recipe and process documentation
   - Ingredient library and sourcing information
   - Batch tracking and tasting notes
   - Brewing timeline visualization
   - Media gallery for brewing process

5. **Compliance System**:
   - Age verification with multiple methods
   - Regional regulation management
   - Compliant content filtering
   - Audit trail for verification events
   - Legal disclaimer management

6. **Brand Experience**:
   - Brand story and history management
   - Brewery team profiles
   - Tasting notes and flavor guides
   - Beer awards and recognition
   - Brewery event calendar

## Testing Requirements

### Key Functionalities to Verify
- Creation, retrieval, update, and deletion of all beer entries
- Accurate tracking and updating of tap room status
- Correct countdown calculations for upcoming releases
- Proper documentation of brewing processes
- Effective enforcement of age verification requirements

### Critical User Scenarios
- Adding a new beer to the catalog with complete characteristics
- Updating tap status when kegs are changed
- Setting up and promoting an upcoming special release
- Documenting the brewing process for a signature beer
- Implementing appropriate age verification for different regions

### Performance Benchmarks
- Catalog search time with growing beer database
- Tap status update propagation time
- System behavior with concurrent status updates
- Content rendering time for complex beer descriptions
- Age verification processing with different compliance rules

### Edge Cases and Error Conditions
- Handling tap status conflicts with multiple updaters
- Managing release countdown for delayed or canceled releases
- Recovery from interrupted content creation
- Behavior when beer attributes change mid-release
- Handling complex regional compliance requirements

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core components
- 100% coverage of compliance-related code
- All error handling paths must be tested
- Performance tests for real-time update operations
- Security tests for age verification mechanisms

## Success Criteria

The implementation will be considered successful when:

1. The brewery's complete beer catalog can be managed with detailed characteristics for each offering
2. Tap room availability is accurately reflected in real-time as kegs are tapped and emptied
3. Upcoming beer releases generate anticipation through effective countdown and notification features
4. Brewing processes and recipes are documented in an engaging, informative manner
5. Age verification effectively restricts underage access while providing a smooth experience for legal users
6. The brewery's unique brand personality is expressed through consistent content presentation
7. All operations can be performed programmatically through a well-documented API
8. The entire system can be thoroughly tested using pytest with high coverage
9. Performance meets or exceeds the specified benchmarks

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