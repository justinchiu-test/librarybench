# Business Portfolio Site Generator

A static site generator specialized for small businesses to showcase their services, portfolio, and client testimonials with professional results and simple content management.

## Overview

This project is a Python library for generating business portfolio websites from structured content files. It focuses on creating professional-looking business sites with portfolio showcases, client testimonials, contact capabilities, and SEO optimization, allowing business owners to maintain their web presence without technical expertise.

## Persona Description

Elena runs a boutique design studio and needs a professional website that showcases her portfolio, services, and client testimonials. She wants to update content herself without depending on web developers for every change.

## Key Requirements

1. **Portfolio Project Templating**: Create a flexible system for showcasing portfolio projects with consistent layouts but customizable content for each project. This is crucial for Elena to maintain a cohesive brand presentation while highlighting the unique aspects of each design project, complete with images, descriptions, client information, and results.

2. **Client Testimonial Management**: Implement a testimonial system with an approval workflow before publishing feedback. As client recommendations are critical for Elena's business credibility, she needs to collect, review, and selectively publish testimonials with appropriate attribution and highlighting of key points.

3. **Static Contact Form Generation**: Generate functional contact forms that work without requiring server-side processing. This allows potential clients to reach Elena directly from her website without requiring her to implement and maintain server-side form handling or pay for form processing services.

4. **SEO Optimization Tools**: Provide tools that analyze content and suggest improvements for search engine visibility. Elena's business depends on being found by potential clients, so automated SEO analysis helps her optimize page titles, descriptions, headings, and content to improve her search ranking for relevant design services.

5. **Local Business Schema Markup**: Generate appropriate schema.org markup to enhance search results with business information. This structured data helps search engines understand Elena's business type, location, services, hours, and contact information, improving her local search presence and business information display in search results.

## Technical Requirements

- **Testability Requirements**:
  - Portfolio project generation must be testable with sample project data
  - Testimonial workflow states must be verifiable through file metadata
  - Contact form functionality must be testable without actual form submission
  - SEO suggestions must be reproducible based on content analysis
  - Schema markup generation must validate against schema.org standards

- **Performance Expectations**:
  - Full site generation must complete in under 15 seconds
  - Image optimization for portfolio projects should maintain quality while reducing file size by at least
    50%
  - Generated pages should achieve a minimum 90/100 score on Lighthouse performance metrics
  - Contact form validation should complete client-side in under 100ms

- **Integration Points**:
  - Static form handlers (like Formspree, Netlify Forms, or AWS Lambda)
  - Google Business Profile and other local business directories
  - Social media platforms for business profiles
  - Schema.org validation tools
  - Search engine webmaster tools for site verification

- **Key Constraints**:
  - All site functionality must work without a database or server-side processing
  - SEO recommendations must be based on current best practices
  - Contact forms must function in environments without JavaScript
  - Site generator must be usable by non-technical business owners
  - Output must be compatible with any static web hosting platform

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **Portfolio Management System**:
   - Process structured project data from markdown or YAML files
   - Apply consistent templates with customizable sections per project
   - Handle project categorization and filtering
   - Optimize and resize project images for various display contexts

2. **Testimonial Processing Pipeline**:
   - Manage testimonials with approval status workflow
   - Validate testimonial content and required attributes
   - Support highlighting of key quotes or phrases
   - Generate appropriate markup with proper attribution

3. **Contact Form Generator**:
   - Create HTML forms with client-side validation
   - Generate the necessary integration code for static form handlers
   - Implement anti-spam measures without server-side processing
   - Support customizable form fields and validation rules

4. **SEO Analysis Engine**:
   - Analyze page content for SEO best practices
   - Generate recommendations for title, description, and heading improvements
   - Check keyword density and placement
   - Validate meta tags and structured data

5. **Business Information Markup Generator**:
   - Create schema.org JSON-LD markup for local businesses
   - Generate appropriate OpenGraph and social media metadata
   - Implement structured data for services, hours, and location
   - Validate generated markup against schema.org specifications

## Testing Requirements

- **Key Functionalities to Verify**:
  - Generation of portfolio pages with proper layouts and image optimization
  - Processing of testimonials based on approval status
  - Functional contact forms with proper validation and submission handling
  - Accurate SEO analysis and recommendations
  - Valid schema.org markup generation for business information

- **Critical User Scenarios**:
  - Business owner adds a new portfolio project with multiple images and detailed description
  - Client submits a testimonial that goes through the approval workflow
  - Visitor submits a contact form inquiry
  - Business owner updates service offerings and receives SEO recommendations
  - Search engine indexes the site with enhanced business information

- **Performance Benchmarks**:
  - Site generation time for various content sizes (10, 25, 50 portfolio items)
  - Image processing time for high-resolution portfolio images
  - Page load time for image-heavy portfolio pages
  - Client-side form validation response time

- **Edge Cases and Error Conditions**:
  - Handling of extremely large or improperly formatted images
  - Processing of testimonials with missing required information
  - Recovery from interrupted build processes
  - Handling of invalid structured data inputs
  - Management of special characters in form submissions

- **Required Test Coverage**:
  - 90% code coverage for core library functions
  - 100% coverage for contact form generation and validation
  - 95% coverage for schema markup generation
  - 85% coverage for SEO recommendation engine

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. A business owner can create and update portfolio projects without HTML knowledge
2. Client testimonials can be collected, reviewed, and selectively published
3. Contact forms work correctly without requiring server-side programming
4. SEO recommendations help improve content for better search visibility
5. Business information appears correctly in search engine results
6. The entire site can be regenerated in under 15 seconds
7. All tests pass with at least 90% code coverage
8. The site achieves a minimum 90/100 score on Lighthouse performance, accessibility, SEO, and best practices

To set up your development environment:
```
uv venv
source .venv/bin/activate
```