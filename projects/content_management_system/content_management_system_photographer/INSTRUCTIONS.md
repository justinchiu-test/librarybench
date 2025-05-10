# Photography Portfolio CMS

A specialized content management system designed for professional photographers to showcase their work and manage client interactions.

## Overview

Photography Portfolio CMS is a comprehensive image management library tailored for professional photographers. It enables photographers to showcase their work in visually striking galleries, organize thousands of images efficiently, maintain separate client-specific private collections, protect their intellectual property, and optimize images for web performance.

## Persona Description

Mei showcases her photography portfolio to attract clients for weddings, events, and portraits. Her primary goal is to display her work in visually striking galleries while efficiently organizing thousands of images and maintaining separate client-specific private collections.

## Key Requirements

1. **Portfolio Showcase with Category Customization**: Develop a flexible gallery system that allows for customized viewing experiences by photography category (weddings, portraits, events, etc.). This is critical for Mei as it enables her to present different styles of work in appropriate contexts, curating the viewer experience based on the type of photography to best highlight her versatility and expertise.

2. **Client Proofing Portal**: Create a comprehensive client image review system with selection and commenting tools for clients to provide feedback on images. This feature is essential as it streamlines Mei's client workflow, allowing clients to easily review photo sessions, select their preferred images, and communicate specific editing requests without requiring in-person meetings.

3. **Image Protection Controls**: Implement robust watermarking and download prevention mechanisms to protect intellectual property. This functionality is vital for Mei's business as it prevents unauthorized use of her preview images while still allowing clients to review their photos, ensuring her work is not used commercially without proper licensing or payment.

4. **Photography Metadata Management**: Develop a comprehensive system for storing, editing, and searching images based on photography-specific metadata (camera settings, location, subject, style, etc.). This capability is crucial for efficiently managing a library of thousands of images, enabling Mei to quickly find specific photos based on technical or subject criteria across her extensive collection.

5. **Automated Image Optimization**: Create an image processing pipeline that automatically prepares images for web display while preserving quality. This feature is important for ensuring fast loading times and responsive behavior across devices, providing a professional user experience that properly showcases Mei's work without requiring manual resizing and optimization of each image.

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% coverage
- Image processing operations must be testable with fixture images
- Watermarking algorithms must be verifiable through test cases
- Metadata extraction and management must be thoroughly tested
- Gallery generation must be validated for correctness

### Performance Expectations
- Gallery loading operations must complete within 300ms
- Image optimization should process a standard image within 2s
- Metadata searches should return results within 200ms
- Client portal operations should handle sessions with 1000+ images
- The system should efficiently manage libraries of 50,000+ images

### Integration Points
- Support for common storage backends (local filesystem, SQLite, optional cloud storage)
- Image format conversion and processing
- EXIF and IPTC metadata extraction and management
- Export capabilities for backup and archiving
- Optional email integration for client notifications

### Key Constraints
- All code must be pure Python with minimal dependencies
- Image processing should use established libraries (Pillow, etc.)
- No JavaScript dependencies or browser-specific code
- No direct coupling to web frameworks, though adaptors can be provided
- Must support offline content management and batch processing

## Core Functionality

The library must provide the following core components:

1. **Portfolio Management System**:
   - Gallery creation and organization
   - Category-based presentation rules
   - Image sequencing and arrangement
   - Featured image selection
   - Portfolio analytics (views, engagement)

2. **Client Management**:
   - Client profile and session management
   - Private gallery creation and access control
   - Selection and favorites tracking
   - Client commenting and feedback
   - Delivery status tracking

3. **Image Protection Framework**:
   - Watermarking with customizable options
   - Download prevention mechanisms
   - Usage rights management
   - Protection level configuration
   - Infringement detection utilities

4. **Metadata System**:
   - EXIF/IPTC data extraction and storage
   - Custom metadata fields and tagging
   - Advanced search capabilities
   - Batch metadata operations
   - Hierarchical categorization

5. **Image Processing Pipeline**:
   - Automatic resizing for different display contexts
   - Quality-preserving compression
   - Format conversion
   - Thumbnail generation
   - Color profile management

6. **Storage Management**:
   - Efficient image storage strategies
   - Version control for edited images
   - Backup and archiving utilities
   - Storage usage analytics
   - Duplicate detection

## Testing Requirements

### Key Functionalities to Verify
- Creation, organization, and presentation of portfolio galleries
- Client access, selection, and feedback mechanisms
- Effective watermarking and image protection
- Accurate metadata extraction, storage, and searching
- Proper image optimization for web display

### Critical User Scenarios
- Creating a new portfolio category with customized display settings
- Setting up a client proofing gallery with selection capabilities
- Applying and customizing watermarks for different usage contexts
- Managing and searching a large image collection by metadata
- Processing a batch of images for optimized web display

### Performance Benchmarks
- Gallery loading times with varying numbers of images
- Image processing speed for different resolution images
- Search performance with large metadata databases
- System behavior with concurrent client access
- Storage efficiency with growing image collections

### Edge Cases and Error Conditions
- Handling corrupt or incomplete image files
- Managing metadata for images lacking standard EXIF data
- Recovery from interrupted batch processing operations
- Behavior with unusual image dimensions or formats
- Handling client selections across multiple sessions

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core components
- 100% coverage of image protection mechanisms
- All error handling paths must be tested
- Performance tests for gallery generation and image processing
- Security tests for access control mechanisms

## Success Criteria

The implementation will be considered successful when:

1. Photographers can create and organize visually striking portfolio galleries by category
2. Clients can securely access private galleries, select images, and provide feedback
3. Images are properly protected with watermarks and download prevention
4. A large library of images can be efficiently searched using photography-specific metadata
5. Images are automatically optimized for web display without sacrificing quality
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