# Personal Blogging Platform Generator

A content-focused static site generator optimized for independent bloggers who want to maintain full control over their publishing platform.

## Overview

This project provides a specialized static site generator designed for independent bloggers who want to publish articles, tutorials, and photo galleries with minimal technical overhead while maintaining full ownership of their platform. The system automates the transformation of content into a visually appealing, optimized blog with robust content management features.

## Persona Description

Marcus writes a personal blog about urban gardening and sustainable living, sharing articles, tutorials, and photo galleries. He wants a simple way to publish his content with minimal technical overhead while maintaining full ownership of his platform.

## Key Requirements

1. **Content Calendar with Draft Management**: Support scheduled publishing and draft post management for editorial planning.
   - As a solo content creator, Marcus needs tools to plan his editorial calendar, manage works in progress, and schedule posts for automatic publishing, allowing him to maintain a consistent publishing schedule without manual intervention.
   - The system should provide status tracking for content (draft, scheduled, published) and automation for publishing scheduled content.

2. **Social Sharing Optimization**: Automatically generate metadata for link previews on social platforms.
   - Proper sharing is crucial for Marcus's audience growth, so his content needs to present optimally when shared on social media with automatic generation of appropriate Open Graph and Twitter Card metadata.
   - This feature should extract relevant images, descriptions, and titles from content to create compelling social previews.

3. **Reading Time Estimation and Readability Scoring**: Calculate reading time and analyze content readability.
   - To help Marcus improve his articles' structure and reader experience, the system should automatically calculate reading time estimates and provide readability metrics (like Flesch-Kincaid scores).
   - These metrics should be calculated automatically during the build process and be available for display with each article.

4. **Photo Gallery Templates**: Support gallery creation with lazy loading and responsive images.
   - As Marcus frequently shares photo documentation of his gardening projects, he needs efficient ways to organize and display photo galleries with proper image optimization for various screen sizes.
   - The system should automate image processing, responsive sizing, and gallery layout generation.

5. **Comment Integration**: Support for third-party comment systems or static site commenting solutions.
   - Reader engagement is important for building community around Marcus's blog, requiring seamless integration with comment systems that work with static sites.
   - This should include support for various commenting options without requiring server-side processing.

## Technical Requirements

### Testability Requirements
- All content processing functions must be testable with sample markdown/content files
- Image processing pipeline must verify correct optimization and responsive image generation
- Scheduled publishing mechanism must be testable with simulated timestamps
- Readability analysis must produce consistent scores for sample content
- Metadata generation must be verifiable for correctness and completeness

### Performance Expectations
- Full site generation should complete in under 10 seconds for a typical blog (100 posts)
- Image processing should handle at least 50 high-resolution images per minute
- Content analysis (reading time, readability) should process 10,000 words per second
- Incremental builds should update changed content in under 3 seconds

### Integration Points
- Image processing libraries for optimization and responsive variants
- Readability analysis algorithms
- Social metadata standards (Open Graph, Twitter Cards)
- Third-party commenting systems (Disqus, Utterances, etc.)
- RSS/Atom feed generation

### Key Constraints
- Must operate without a database or server-side processing
- Must generate completely static output deployable to any web hosting service
- Must process content written in Markdown with frontmatter
- Must optimize images without requiring manual preprocessing
- Must support incremental builds to minimize processing time for small changes

## Core Functionality

The system should implement a comprehensive platform for blog content management and publishing:

1. **Content Management System**
   - Parse and process Markdown content with YAML/TOML frontmatter
   - Support draft status and future publication dates
   - Organize content by categories, tags, and series
   - Implement content relationships (related posts, series navigation)

2. **Publishing Pipeline**
   - Schedule content based on publication dates
   - Filter content based on status (draft, published, scheduled)
   - Generate proper permalinks and URL structures
   - Create archives, category pages, and tag indexes

3. **Image Processing System**
   - Optimize images for web delivery (compression, format conversion)
   - Generate responsive image variants for different viewport sizes
   - Create thumbnails for previews and galleries
   - Implement lazy loading for improved performance

4. **Content Enhancement**
   - Calculate reading time based on content length and complexity
   - Analyze readability using established algorithms
   - Generate appropriate metadata for social sharing
   - Create content snippets/excerpts for listings and previews

5. **Engagement Features**
   - Integrate with third-party commenting systems
   - Generate share links for social platforms
   - Support newsletter subscription forms
   - Create RSS/Atom feeds for content distribution

## Testing Requirements

### Key Functionalities to Verify
- Content processing with correct metadata extraction
- Scheduled publishing functionality
- Image optimization and responsive image generation
- Reading time calculation and readability scoring
- Social metadata generation for optimal sharing

### Critical User Scenarios
- Creating a new blog post with images and proper metadata
- Scheduling a post for future publication
- Creating a photo gallery with multiple images
- Updating existing content while preserving URLs and metadata
- Organizing content with categories and tags

### Performance Benchmarks
- Process 100 blog posts (average 1000 words each) in under 10 seconds
- Optimize and generate responsive variants for 100 images in under 60 seconds
- Complete incremental builds for single post changes in under 3 seconds
- Generate metadata and perform readability analysis at a rate of 10,000 words per second

### Edge Cases and Error Conditions
- Handling malformed or incomplete frontmatter
- Recovering from image processing errors
- Handling exceptionally long or short content
- Managing content with missing required metadata
- Dealing with unsupported image formats or corrupted images

### Required Test Coverage Metrics
- Minimum 90% line coverage for core content processing components
- 100% coverage for critical features (scheduling, image processing)
- Integration tests for the full generation pipeline
- Performance tests for all processing-intensive operations

## Success Criteria

The implementation will be considered successful if it:

1. Enables Marcus to maintain a complete editorial calendar with drafts and scheduled publishing
2. Optimizes content sharing with complete social metadata generation for all content types
3. Provides accurate reading time estimates (within 10% of actual reading time) and useful readability metrics
4. Automatically optimizes and formats images for galleries with responsive sizing and lazy loading
5. Successfully integrates with at least two third-party commenting systems
6. Processes a typical blog (100 posts, 500 images) in under 30 seconds
7. Achieves all required test coverage metrics with a clean test suite

## Getting Started

To set up the development environment:

1. Initialize the project using `uv init --lib` in your project directory
2. Install dependencies using `uv sync`
3. Run Python scripts with `uv run python your_script.py`
4. Run tests with `uv run pytest`

When implementing this library, focus on creating well-defined APIs that provide all the required functionality without any user interface components. All features should be implementable as pure Python modules and classes that can be thoroughly tested using pytest.