# Non-profit Organization Site Generator

A specialized static site generator optimized for creating and maintaining mission-driven websites for non-profit organizations with limited technical resources.

## Overview

This project provides a mission-focused static site generator that enables non-profit organizations to create, maintain, and update their websites with limited technical resources. The system automates the generation of content showcasing the organization's mission, programs, impact stories, donation opportunities, and volunteer information.

## Persona Description

Amara leads a small environmental non-profit and needs to maintain their organization's website with limited technical resources, showcasing their mission, programs, impact stories, and donation opportunities.

## Key Requirements

1. **Impact Story Templates**: Create formatted stories highlighting the organization's work.
   - Impact stories are essential for communicating Amara's organization's mission and effectiveness to supporters, requiring a structured yet flexible system for creating compelling narratives.
   - These templates must support various media types, testimonials, statistics, and clear calls to action while maintaining consistent formatting.

2. **Donation Integration**: Generate static payment links for various fundraising campaigns.
   - Financial sustainability is crucial for Amara's small non-profit, so the website must effectively facilitate donations through various channels without requiring complex payment infrastructure.
   - This feature should support multiple donation methods, campaign-specific links, suggested donation amounts, and integration with popular payment processors.

3. **Volunteer Opportunity Management**: Organize and display volunteer positions with signup information.
   - Volunteers are a critical resource for Amara's organization, requiring clear presentation of opportunities, requirements, and application processes.
   - The system must organize volunteer roles by category, location, and skill requirements with appropriate application instructions and status tracking.

4. **Event Promotion**: Create event listings with registration links and automatic archiving.
   - Events are key engagement and fundraising opportunities for the organization, requiring effective promotion and management on the website.
   - This feature should support upcoming event listings, registration processes, calendar integration, and automatic archiving of past events with results and media.

5. **Grant and Funding Information**: Organize funding details by project with progress updates.
   - Transparency about funding sources and project progress is important for donor trust, so Amara needs to clearly present grant information and outcomes.
   - The system should organize funding information by project, showing grant sources, amounts, timelines, and progress toward goals.

## Technical Requirements

### Testability Requirements
- Impact story template rendering must be testable with sample story data
- Donation link generation must verify correct integration with payment processors
- Volunteer opportunity management must validate role organization and status changes
- Event promotion must verify correct chronological handling and archiving
- Funding information must validate project relationship and progress tracking

### Performance Expectations
- Complete site generation should finish in under 10 seconds for a typical non-profit site
- Impact story processing should handle 100+ stories with media in under 5 seconds
- Donation link generation should create 50+ campaign-specific links in under 3 seconds
- Event management should process 100+ upcoming and past events in under 5 seconds
- Incremental builds should update changed content in under 2 seconds

### Integration Points
- Payment processors for donation links (PayPal, Stripe, etc.)
- Calendar systems for event export (iCalendar)
- Email signup services for newsletters and volunteer alerts
- Social media platforms for sharing content
- Media optimization services for impact story assets

### Key Constraints
- Must operate without a database or server-side processing
- Must generate completely static output deployable to low-cost hosting
- Must be maintainable by non-technical staff with minimal training
- Must be extremely efficient in terms of hosting resources
- Must support mobile devices as primary access method for many users

## Core Functionality

The system should implement a comprehensive platform for non-profit website generation:

1. **Impact Communication System**
   - Process structured impact story content
   - Generate compelling narrative formats with media
   - Create consistent layouts highlighting key outcomes
   - Support categorization and filtering of impact stories

2. **Donation Management**
   - Generate payment links for various processors
   - Create campaign-specific donation pathways
   - Implement tiered donation suggestions
   - Support recurring donation options

3. **Volunteer Coordination Framework**
   - Process volunteer opportunity information
   - Generate role listings with requirements and time commitments
   - Create application instructions and processes
   - Support filtering opportunities by location, skills, or commitment

4. **Event System**
   - Process upcoming and past event information
   - Generate chronological event listings
   - Create event detail pages with registration options
   - Automatically archive past events with outcomes

5. **Funding Transparency**
   - Process grant and funding information
   - Create project-based funding presentations
   - Generate visual progress indicators
   - Support detailed funding breakdown by source

## Testing Requirements

### Key Functionalities to Verify
- Impact story template rendering with various content types
- Donation link generation for different campaigns and processors
- Volunteer opportunity presentation and organization
- Event listings with proper chronological handling
- Project funding information with accurate progress tracking

### Critical User Scenarios
- Creating a new impact story with multimedia elements
- Setting up a new fundraising campaign with donation options
- Adding and updating volunteer opportunities
- Creating and promoting upcoming events
- Tracking and displaying grant funding for projects

### Performance Benchmarks
- Process 100 impact stories in under 5 seconds
- Generate 50 donation campaign links in under 3 seconds
- Organize 30 volunteer opportunities in under 2 seconds
- Process 100 events (past and upcoming) in under 5 seconds
- Complete full site generation for a typical non-profit in under 10 seconds

### Edge Cases and Error Conditions
- Handling missing or incomplete impact story elements
- Managing integration with unavailable payment processors
- Processing volunteer opportunities with complex requirements
- Dealing with recurring or multi-day events
- Visualizing complex funding arrangements across multiple projects

### Required Test Coverage Metrics
- Minimum 90% line coverage for core processing components
- 100% coverage for donation link generation functionality
- Integration tests for payment processor endpoint generation
- Validation tests for all public-facing content
- Performance tests for full site generation process

## Success Criteria

The implementation will be considered successful if it:

1. Creates compelling impact stories with consistent formatting while accommodating different content needs
2. Generates functional donation links for at least 3 different payment processors with campaign-specific options
3. Presents volunteer opportunities with clear categorization, requirements, and application processes
4. Effectively promotes upcoming events while automatically archiving past events with outcomes
5. Clearly presents grant and funding information organized by project with accurate progress tracking
6. Processes a typical non-profit site (50 impact stories, 10 donation campaigns, 20 volunteer roles) in under 10 seconds
7. Achieves all required test coverage metrics with a clean test suite

## Getting Started

To set up the development environment:

1. Initialize the project using `uv init --lib` in your project directory
2. Install dependencies using `uv sync`
3. Run Python scripts with `uv run python your_script.py`
4. Run tests with `uv run pytest`

When implementing this library, focus on creating well-defined APIs that provide all the required functionality without any user interface components. All features should be implementable as pure Python modules and classes that can be thoroughly tested using pytest.