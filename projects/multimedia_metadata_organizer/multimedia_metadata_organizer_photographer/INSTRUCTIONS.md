# Professional Photographer's Multimedia Metadata Management System

## Overview
A specialized metadata organization system designed specifically for commercial photographers who need to efficiently catalog, search, and deliver thousands of images to different clients while maintaining a consistent organizational system across their growing archives.

## Persona Description
Isabella is a commercial photographer who shoots thousands of images monthly for different clients across various industries. She needs to efficiently catalog, search, and deliver photos to clients while maintaining a consistent organization system for her growing archives.

## Key Requirements
1. **Client-project hierarchy automation**: A system that automatically creates standardized folder structures from shoot metadata. This feature is critical for Isabella because it eliminates manual organization of thousands of images per month and ensures consistent file structure across all client projects, saving hours of administrative work.

2. **Deliverable preparation tools**: Functionality to generate client-ready files with appropriate metadata and watermarking. This feature is essential because it streamlines the delivery process by automatically preparing files according to client-specific requirements, reducing the risk of delivering incorrect versions or improperly formatted files.

3. **Usage rights tracking**: A mechanism for flagging images with specific licensing restrictions or expiration dates. This feature is vital for avoiding costly licensing violations by clearly marking which images have restricted usage and alerting when licenses are approaching expiration, protecting both the photographer and clients from potential legal issues.

4. **Equipment-specific metadata extraction**: Tools to identify which camera gear produces the best results. This capability is important because it helps Isabella optimize her equipment investments by analyzing which lenses, cameras, and settings consistently produce the highest quality results for specific types of shoots.

5. **Client portal integration**: Functionality for generating secure sharing links with customized metadata visibility. This feature is crucial because it provides a professional delivery mechanism where clients can easily browse and select images while only seeing the metadata fields relevant to them, not the photographer's internal categorization.

## Technical Requirements
- **Testability requirements**:
  - All metadata extraction and transformation functions must be independently testable
  - Client hierarchy creation logic must be testable with mock file systems
  - Usage rights and license validation must be verifiable with test cases covering various scenarios
  - Performance tests must confirm the system can handle processing at least 10,000 images within a reasonable timeframe

- **Performance expectations**:
  - Metadata extraction should process at least 1,000 images per minute on standard hardware
  - Search operations should return results in under 2 seconds for collections up to 1 million images
  - Batch operations should utilize multi-core processing for optimal performance
  - Memory usage should scale efficiently with large collections

- **Integration points**:
  - Standard metadata formats including EXIF, IPTC, and XMP
  - Common image file formats (RAW, DNG, JPEG, TIFF, PNG)
  - Export APIs for client portal systems
  - Calendar systems for tracking license expiration dates

- **Key constraints**:
  - Implementation must be in Python with no external UI components
  - All functionality must be exposed through well-defined APIs
  - No modification of original image data, only metadata
  - Storage efficiency for large image collections

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide a comprehensive API for managing a professional photographer's workflow:

1. **Metadata Extraction Engine**: Extract, parse, and standardize metadata from multiple image formats including professional camera RAW files. Map proprietary metadata fields to standardized formats.

2. **Client-Project Organization System**: Define, create, and manage hierarchical organization schemes based on clients, projects, shoots, and deliverables. Apply consistent naming conventions and metadata tagging.

3. **Rights Management Module**: Track usage permissions, licensing terms, model releases, and expiration dates. Generate alerts for expiring licenses and provide status checks for any image.

4. **Delivery Preparation System**: Create client deliverable packages with appropriate metadata, watermarking, and format conversion. Generate secure sharing links with controlled metadata visibility.

5. **Analytics Engine**: Analyze equipment usage patterns to identify which gear produces optimal results in different shooting conditions. Generate reports on collection composition and client project statistics.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate extraction of metadata from various file formats
  - Correct application of client-project organization rules
  - Precise tracking of image usage rights and expiration dates
  - Proper generation of client deliverables with appropriate metadata
  - Accurate analysis of equipment performance patterns

- **Critical user scenarios that should be tested**:
  - Processing a complete client photoshoot from import to delivery
  - Searching for images with specific metadata criteria
  - Managing license expiration and renewal workflows
  - Generating client deliverables with correct watermarking and metadata
  - Analyzing equipment performance across different projects

- **Performance benchmarks that must be met**:
  - Metadata extraction from 5,000 high-resolution RAW images in under 10 minutes
  - Search performance under 2 seconds for specific metadata queries
  - Export of 100 client-ready images with watermarking in under 5 minutes
  - Memory usage scaling linearly with collection size

- **Edge cases and error conditions that must be handled properly**:
  - Corrupted image files with partial metadata
  - Inconsistent metadata across a batch of images
  - Conflicting client-project hierarchies
  - Files with missing critical metadata fields
  - Duplicate images with different metadata

- **Required test coverage metrics**:
  - 95% code coverage for core metadata processing functions
  - 90% coverage for organization and hierarchy management
  - 95% coverage for rights management and licensing tracking
  - 90% coverage for analytics and reporting functions

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if it meets the following criteria:

1. Demonstrates at least a 70% reduction in time required to organize client photoshoots compared to manual methods
2. Successfully tracks licensing and usage rights with no missed expirations in test scenarios
3. Correctly generates client deliverables with appropriate metadata and watermarking
4. Produces accurate reports identifying which equipment produces optimal results
5. Maintains performance benchmarks with collections of 100,000+ images
6. Passes all test cases with the required coverage metrics
7. Provides a clean, well-documented API that could be integrated with existing systems

## Project Setup
To set up the development environment:

1. Create a virtual environment and initialize the project using `uv`:
   ```
   uv init --lib
   ```

2. Install the necessary dependencies:
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

5. Format the code:
   ```
   uv run ruff format
   ```

6. Lint the code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```

8. Run a Python script:
   ```
   uv run python script.py
   ```