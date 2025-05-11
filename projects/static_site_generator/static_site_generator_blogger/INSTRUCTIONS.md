# Personal Blogging Platform Generator

A specialized static site generator designed for independent bloggers to create, manage, and publish content-focused websites with editorial planning features, social optimization, and media galleries.

## Overview

This project implements a Python library for generating blog-centric static websites that prioritize content presentation, reading experience, and social sharing. It focuses on the needs of independent bloggers who want full ownership of their platform while maintaining a professional online presence with minimal technical overhead.

## Persona Description

Marcus writes a personal blog about urban gardening and sustainable living, sharing articles, tutorials, and photo galleries. He wants a simple way to publish his content with minimal technical overhead while maintaining full ownership of his platform.

## Key Requirements

1. **Content Calendar with Publishing Management**: Implement a system for managing draft posts, scheduling future publications, and organizing content by status (draft, scheduled, published, archived).
   - Critical for Marcus because it allows him to plan his editorial calendar, work on multiple posts simultaneously, and maintain a consistent publishing schedule without manual intervention.
   - Must include metadata for publication dates, status tracking, and automated publishing pipeline.

2. **Social Sharing Optimization**: Generate appropriate metadata for optimal display when content is shared on social platforms, including Open Graph tags, Twitter Cards, and structured data.
   - Essential for Marcus because social sharing drives significant traffic to his blog, and properly formatted previews with images and descriptions significantly increase click-through rates.
   - Must generate platform-specific markup for major social networks with customizable templates.

3. **Reading Time Estimation and Readability Analysis**: Calculate estimated reading times for articles and provide readability metrics (like Flesch-Kincaid score) to help improve content structure.
   - Important for Marcus because it helps readers set expectations for article length and helps him ensure his content remains accessible to his target audience.
   - Should analyze text complexity, sentence structure, and word choice to provide actionable feedback.

4. **Optimized Photo Gallery Templates**: Create specialized templates for photo galleries with lazy loading, responsive images for different screen sizes, and proper image optimization.
   - Valuable for Marcus because his gardening content relies heavily on visual elements, and a good gallery experience improves engagement while maintaining performance.
   - Must handle image resizing, format conversion, and delivery optimization.

5. **Comment System Integration**: Support for adding comments to static pages through third-party systems or implementing a static site commenting solution.
   - Critical for Marcus because community engagement and discussion are central to his blog's purpose, and comments must work without requiring server-side processing.
   - Should support multiple commenting platforms with consistent styling and moderation capabilities.

## Technical Requirements

### Testability Requirements
- All components must be individually testable through well-defined interfaces
- Implement fixtures for testing with sample blog content and images
- Support snapshot testing for generated HTML output
- Test suites must validate the structure and correctness of generated social metadata
- Support mocking of time-dependent functions for testing scheduled publishing

### Performance Expectations
- Generate a 100-post blog with images in under 30 seconds
- Image optimization pipelines should process 20+ images per second
- Incremental builds should complete in under 3 seconds for content-only changes
- Reading time and readability analysis should process 1000+ words in under 100ms
- Generated sites should achieve 90+ scores on Google PageSpeed Insights (to be simulated in tests)

### Integration Points
- Social media platform metadata specifications
- Third-party commenting systems APIs
- Image optimization and transformation libraries
- Content delivery networks for optimized asset delivery
- Readability analysis algorithms and libraries

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must generate completely static HTML that works without any server-side processing
- Must optimize images for web delivery while maintaining quality
- Output must be fully accessible and SEO-optimized
- Content management must work efficiently with standard version control systems
- Site generation must be automatable for continuous deployment workflows

## Core Functionality

The Personal Blogging Platform Generator should provide a comprehensive Python library with the following core capabilities:

1. **Content Processing System**
   - Parse and process Markdown files with frontmatter for metadata
   - Support for blog-specific formatting and shortcodes
   - Handle draft status, publication dates, and scheduling
   - Implement tagging, categorization, and content relationships

2. **Content Analysis Tools**
   - Calculate estimated reading times based on content length and complexity
   - Analyze readability using established metrics (Flesch-Kincaid, etc.)
   - Suggest improvements for title formats, headings, and paragraph structure
   - Identify potential SEO improvements for content

3. **Media Management**
   - Process images for responsive delivery (multiple sizes, formats)
   - Implement gallery templates with advanced features
   - Optimize media files for web delivery
   - Generate proper alt text and accessibility features

4. **Social Integration**
   - Generate platform-specific social sharing metadata
   - Create preview cards for various platforms
   - Support custom social images with text overlays
   - Enable structured data for rich search results

5. **Site Structure and Features**
   - Build archive pages, tag pages, and category indexes
   - Generate RSS/Atom feeds for subscription
   - Implement related content suggestions
   - Support for comments integration
   - Create search indexes for client-side search

## Testing Requirements

### Key Functionalities to Verify

1. **Content Processing and Publishing**
   - Test conversion of markdown to properly formatted HTML
   - Verify correct handling of publication dates and draft status
   - Test scheduled publishing mechanism
   - Confirm generation of archives, category pages, and tag pages

2. **Media Optimization and Galleries**
   - Test image resizing and format conversion
   - Verify responsive image generation
   - Test gallery templates with various image counts and orientations
   - Confirm proper lazy loading implementation
   - Verify accessibility compliance for media content

3. **Metadata and Social Integration**
   - Test generation of Open Graph and Twitter Card metadata
   - Verify structured data correctness
   - Test custom social image generation
   - Confirm proper handling of various content types

4. **Content Analysis**
   - Test reading time calculations for various content lengths
   - Verify readability scoring against established benchmarks
   - Test content improvement suggestions
   - Confirm correct operation with multilingual content

5. **Comment System Integration**
   - Test integration with various commenting platforms
   - Verify comment display templates
   - Test comment counts and threading
   - Confirm accessibility of comment sections

### Critical User Scenarios

1. Publishing a new blog post with images and seeing it properly displayed
2. Scheduling multiple posts for future publication
3. Creating and organizing photo galleries with many images
4. Sharing content on social media with proper preview cards
5. Analyzing content for readability and implementing improvements

### Performance Benchmarks

- Full site build with 100 posts should complete in under 30 seconds
- Incremental builds should complete in under 3 seconds
- Image processing should handle 50+ images in under 10 seconds
- Search index generation should process content at 10+ posts/second
- Memory usage should not exceed 500MB for typical blog sizes

### Edge Cases and Error Conditions

- Test handling of malformed markdown
- Verify proper error reporting for missing images
- Test behavior with extremely long posts or very short content
- Verify graceful handling of special characters and Unicode
- Test with missing metadata and incomplete front matter
- Validate behavior with uncommon media types (SVG, WebP, etc.)

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for publishing and scheduling logic
- 100% coverage for social metadata generation
- Integration tests for entire build pipeline
- Performance tests for both small and large blogs

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

The Personal Blogging Platform Generator will be considered successful if it:

1. Correctly manages content with drafts, scheduling, and automatic publishing
2. Produces optimized HTML with proper social sharing metadata for various platforms
3. Accurately calculates reading times and readability scores
4. Successfully processes images for responsive galleries with proper optimization
5. Effectively integrates commenting solutions with the static site workflow
6. Builds sites efficiently with proper incremental build support
7. Generates accessible, SEO-friendly HTML output
8. Creates all necessary site structure elements (archives, categories, tags, feeds)

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