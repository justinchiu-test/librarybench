# Small Business Portfolio Site Generator

A specialized static site generator optimized for small business owners to create and maintain professional business websites with portfolio elements.

## Overview

This project provides a business-focused static site generator that enables small business owners to create, maintain, and update professional websites showcasing their portfolio, services, and client testimonials. The system automates the generation of business-appropriate layouts and features while allowing non-technical users to update content independently.

## Persona Description

Elena runs a boutique design studio and needs a professional website that showcases her portfolio, services, and client testimonials. She wants to update content herself without depending on web developers for every change.

## Key Requirements

1. **Portfolio Project Templates**: Create consistent layout structures for showcasing different portfolio projects.
   - Elena regularly adds new design projects to her portfolio and needs a standardized system to present them consistently while still allowing for customization of content and media for each individual project.
   - The templates must maintain visual and structural consistency while accommodating different content types (images, videos, text descriptions) for various project types.

2. **Client Testimonial Management**: Support collecting, approving, and publishing client feedback.
   - Client testimonials provide critical social proof for Elena's business, so she needs a system to collect submissions, review them before publication, and properly display them on her site.
   - This feature should support structured data for testimonials (client name, company, quote, rating) and implement a workflow from submission to approval to publication.

3. **Contact Form Generation**: Create functional contact forms without server-side processing.
   - As a primary way for prospective clients to reach Elena, contact forms are essential, but they must function without requiring complex server infrastructure.
   - The system should generate forms that can be submitted to third-party services or email endpoints while implementing proper validation and spam protection.

4. **SEO Optimization Tools**: Provide suggestions and implementations for improved search visibility.
   - Being discoverable in search results is crucial for Elena's business growth, so the system must implement comprehensive SEO best practices and provide actionable guidance for content optimization.
   - This feature should analyze content and structure for SEO compliance and generate appropriate metadata, sitemaps, and structured data.

5. **Local Business Schema Markup**: Enhance search results with structured business information.
   - For local clients searching for design services, proper schema markup ensures Elena's business information appears correctly in search results and maps.
   - The system should generate appropriate schema.org markup for local business entities, including services, location, hours, and contact information.

## Technical Requirements

### Testability Requirements
- Portfolio template rendering must be testable with sample project data
- Testimonial management must verify workflow states and transitions
- Contact form generation must validate HTML output and integration with services
- SEO analysis must produce consistent recommendations for sample content
- Schema markup generation must validate against schema.org standards

### Performance Expectations
- Complete site generation should finish in under 5 seconds for a typical business site
- Image processing for portfolio items should handle at least 20 high-resolution images per minute
- SEO analysis should complete for entire site content in under 10 seconds
- Schema markup validation should complete in under 1 second per page

### Integration Points
- Third-party form submission endpoints (Formspree, Netlify Forms, etc.)
- Schema.org validation services
- Image optimization services or libraries
- SEO analysis algorithms and rulesets
- Map embedding services for business location

### Key Constraints
- Must operate without a database or server-side processing
- Must generate completely static output deployable to any web hosting service
- Must support non-technical users updating content via structured files
- Must maintain consistent design across all site sections
- Must validate all generated code against web standards

## Core Functionality

The system should implement a comprehensive platform for business website generation:

1. **Content Management System**
   - Parse and process structured content (YAML, JSON, Markdown)
   - Implement content types for projects, services, testimonials, etc.
   - Provide validation for required fields and content structure
   - Support media management for portfolio assets

2. **Portfolio Management**
   - Process project data into consistent layouts
   - Generate galleries and media showcases
   - Create project listings and category filters
   - Implement project metadata and related projects

3. **Testimonial System**
   - Store and manage testimonial submissions
   - Implement approval workflow states
   - Generate display components with proper attribution
   - Support filtering and featuring of testimonials

4. **Form Generation**
   - Create validated contact forms with proper HTML structure
   - Implement client-side validation logic
   - Configure submission endpoints for serverless operation
   - Generate success/error handling for submissions

5. **SEO Enhancement**
   - Analyze content for SEO best practices
   - Generate appropriate meta tags and structured data
   - Create sitemaps and robots.txt files
   - Implement schema.org markup for business entities

## Testing Requirements

### Key Functionalities to Verify
- Portfolio project template rendering with various content types
- Testimonial collection, approval workflow, and display
- Contact form generation and submission handling
- SEO analysis and recommendation accuracy
- Schema markup generation for local business data

### Critical User Scenarios
- Adding a new portfolio project with multiple media elements
- Processing and publishing a new client testimonial
- Creating and configuring a contact form with validation
- Analyzing a page for SEO improvements
- Updating business information reflected in schema markup

### Performance Benchmarks
- Complete site generation under 5 seconds for 50-page business site
- Process 20 high-resolution portfolio images in under 60 seconds
- Schema validation for 50 pages in under 10 seconds
- SEO analysis at a rate of at least 5 pages per second

### Edge Cases and Error Conditions
- Handling missing or incomplete project data
- Managing invalid testimonial submissions
- Recovering from image processing errors
- Identifying conflicting or invalid SEO metadata
- Detecting and reporting invalid schema markup

### Required Test Coverage Metrics
- Minimum 90% line coverage for core components
- 100% coverage for critical features (form generation, schema markup)
- Integration tests for the full generation pipeline
- Validation tests for all generated HTML, CSS, and JSON

## Success Criteria

The implementation will be considered successful if it:

1. Enables Elena to create and update portfolio projects with consistent layouts but customized content
2. Provides a complete workflow for collecting, reviewing, and publishing client testimonials
3. Generates fully-functional contact forms that work without server-side processing
4. Produces actionable SEO recommendations and implements best practices automatically
5. Generates valid schema.org markup that improves local business search visibility
6. Processes a complete business site with 10 portfolio projects in under 10 seconds
7. Achieves all required test coverage metrics with a clean test suite

## Getting Started

To set up the development environment:

1. Initialize the project using `uv init --lib` in your project directory
2. Install dependencies using `uv sync`
3. Run Python scripts with `uv run python your_script.py`
4. Run tests with `uv run pytest`

When implementing this library, focus on creating well-defined APIs that provide all the required functionality without any user interface components. All features should be implementable as pure Python modules and classes that can be thoroughly tested using pytest.