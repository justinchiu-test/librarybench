# Personal Blog Generator

A static site generator tailored specifically for independent bloggers who want to maintain full control over their content while minimizing technical overhead.

## Overview

This project is a Python library for generating personal blogs from simple markdown files, with a focus on content creation workflows, social media integration, and media-rich presentations. It allows bloggers to focus on writing while automating the technical aspects of running a professionally styled blog.

## Persona Description

Marcus writes a personal blog about urban gardening and sustainable living, sharing articles, tutorials, and photo galleries. He wants a simple way to publish his content with minimal technical overhead while maintaining full ownership of his platform.

## Key Requirements

1. **Content Calendar and Publishing System**: Implement a scheduling system for managing drafts, scheduling future posts, and organizing content by publication date. This is essential for Marcus to plan his editorial calendar, maintain a consistent publishing schedule, and separate work-in-progress from published content without needing a database.

2. **Social Sharing Optimization**: Automatically generate appropriate metadata and preview information for social platforms when content is shared. As Marcus relies on social media to build his audience, having his posts display correctly with compelling previews when shared on platforms like Twitter, Facebook, and Pinterest is critical for engagement.

3. **Content Analytics Tools**: Provide reading time estimation, readability scoring, and content structure analysis to help improve article quality. These writing analytics help Marcus evaluate and improve his content before publishing, ensuring his articles are accessible to his target audience and properly structured for readability.

4. **Photo Gallery System**: Create responsive, optimized photo galleries with lazy loading and appropriate image sizing for different devices. Marcus's gardening blog is highly visual, with tutorials and examples often requiring multiple detailed images that must load efficiently across various devices without degrading performance.

5. **Comments Integration**: Provide a system to integrate third-party commenting solutions or implement a static site commenting system. Community engagement is central to Marcus's blog, allowing readers to ask questions about gardening techniques, share their experiences, and build a community around sustainable living.

## Technical Requirements

- **Testability Requirements**:
  - Content generation must be deterministic and idempotent for consistent testing
  - Image processing workflows must be testable with sample image inputs
  - Scheduled content and draft management must be verifiable through file state
  - Metadata generation for social sharing should be tested with expected output formats
  - Comment system integration points must be testable with mock data

- **Performance Expectations**:
  - Full site generation must complete in under 30 seconds for blogs with up to 500 posts
  - Image optimization should reduce file sizes by at least 40% without visible quality loss
  - Page load times should score at least 90 on Google PageSpeed Insights
  - Incremental builds (changing/adding single post) should complete in under 5 seconds

- **Integration Points**:
  - Third-party comment systems (e.g., Disqus, Isso, or custom static solutions)
  - Social media platforms for metadata validation
  - Image optimization libraries for gallery processing
  - Content analysis tools for readability and structure checking
  - RSS/Atom feed standards for content syndication

- **Key Constraints**:
  - All functionality must work without a database
  - Comment system must not require server-side processing
  - Image processing must be local without external API dependencies
  - Generated sites must be deployable to any static hosting service
  - Social sharing must work without client-side JavaScript

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **Content Management System**:
   - Process Markdown files with frontmatter for metadata
   - Handle draft status and scheduled publication dates
   - Organize posts by categories, tags, and series
   - Maintain an editorial calendar with content status tracking

2. **Media Processing Pipeline**:
   - Optimize images for web delivery with appropriate compression
   - Generate multiple image sizes for responsive design
   - Create gallery layouts with consistent styling and navigation
   - Support captions, alt text, and metadata for images

3. **Social Media Integration**:
   - Generate OpenGraph, Twitter Card, and other platform-specific metadata
   - Create optimized share images and preview text
   - Validate social metadata against platform requirements
   - Generate appropriate schema.org markup for better search results

4. **Content Enhancement Tools**:
   - Calculate reading time based on content length and complexity
   - Analyze readability using established metrics (Flesch-Kincaid, etc.)
   - Check content structure for SEO best practices
   - Suggest improvements for headings, paragraph length, and keyword usage

5. **Commenting System**:
   - Provide integration points for third-party comment services
   - Implement or connect to a static site commenting solution
   - Support comment moderation through content files
   - Generate appropriate markup for accessibility and SEO

## Testing Requirements

- **Key Functionalities to Verify**:
  - Accurate conversion of markdown to HTML with proper styling
  - Correct scheduling of posts based on publication dates
  - Image optimization that maintains quality while reducing file size
  - Proper generation of metadata for social sharing
  - Functional integration with commenting systems

- **Critical User Scenarios**:
  - Blogger adds a new post with embedded images and schedules it for future publication
  - Reader shares content on social media platforms and sees proper previews
  - Blogger organizes content with tags and categories for proper navigation
  - Blogger receives and moderates comments on published articles
  - Blogger reviews content analytics to improve article structure

- **Performance Benchmarks**:
  - Build time for sites with varying numbers of posts (50, 200, 500)
  - Image processing time for galleries of different sizes
  - Page load performance with lazy-loaded images
  - Time to first meaningful paint for content-heavy pages

- **Edge Cases and Error Conditions**:
  - Handling of non-standard image formats or corrupted images
  - Processing of extremely long or short content
  - Management of special characters and non-Latin scripts
  - Recovery from interruptions during the build process
  - Handling of malformed markdown or metadata

- **Required Test Coverage**:
  - 90% code coverage for core library functions
  - 100% coverage for social metadata generation
  - 95% coverage for image processing pipeline
  - 95% coverage for content scheduling and status management

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. A blogger can write content in markdown and generate a complete blog without touching HTML or CSS
2. Content can be scheduled for future publication and managed as drafts before publishing
3. Images are automatically optimized and properly displayed in responsive galleries
4. Articles generate appropriate metadata when shared on social platforms
5. Reading time and readability metrics help improve content quality
6. Comments can be integrated without requiring server-side components
7. All tests pass with at least 90% code coverage
8. The generated site can be deployed to any static hosting service without modification

To set up your development environment:
```
uv venv
source .venv/bin/activate
```