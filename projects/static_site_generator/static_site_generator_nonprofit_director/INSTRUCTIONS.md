# Non-profit Organization Site Generator

A specialized static site generator for non-profit organizations to showcase their mission, programs, impact, and fundraising initiatives with minimal technical overhead.

## Overview

This project is a Python library for generating comprehensive websites for non-profit organizations from structured content sources. It focuses on impact storytelling, donation facilitation, volunteer engagement, event promotion, and funding transparency to address the unique needs of mission-driven organizations.

## Persona Description

Amara leads a small environmental non-profit and needs to maintain their organization's website with limited technical resources, showcasing their mission, programs, impact stories, and donation opportunities.

## Key Requirements

1. **Impact Story Template System**: Implement a framework for creating and displaying compelling impact narratives with consistent formatting. This feature is essential for Amara to effectively communicate her organization's environmental work through stories that demonstrate concrete outcomes, beneficiaries, and progress toward mission goals without requiring design skills for each new story.

2. **Donation Integration Framework**: Create a system for generating static payment links for various fundraising campaigns and purposes. With limited resources for maintaining complex technical systems, this feature allows Amara to facilitate donations through multiple channels and campaigns without requiring server-side payment processing, relying instead on established payment providers while tracking campaign performance.

3. **Volunteer Opportunity Management**: Develop a system for presenting volunteer positions with detailed information and signup processes. As volunteers are critical to Amara's organization, this feature helps her recruit and manage volunteer involvement by clearly communicating role descriptions, time commitments, skills needed, and application procedures through a structured, easily-updatable system.

4. **Event Promotion and Archiving System**: Implement functionality for promoting upcoming events with registration links and automatically archiving past events. This allows Amara to build community engagement through events, provide clear information about upcoming opportunities to participate, and maintain a historical record of past activities that demonstrates the organization's ongoing impact.

5. **Grant and Funding Information Organizer**: Create a system for transparently presenting grant and funding information organized by project with progress updates. Transparency in funding is important for non-profit credibility, making this feature crucial for Amara to demonstrate financial accountability by clearly showing funding sources, allocation to specific projects, and concrete outcomes achieved with donated funds.

## Technical Requirements

- **Testability Requirements**:
  - Impact story templates must render consistently with various content types
  - Donation link generation must be secure and verifiable
  - Volunteer opportunity listings must display all required information fields
  - Event promotion system must correctly transition events to archives based on dates
  - Funding information must accurately represent relationships between grants and projects

- **Performance Expectations**:
  - Full site generation must complete in under 30 seconds
  - Image optimization for impact stories should reduce file sizes by at least 50%
  - Page load time should not exceed 2 seconds on standard connections
  - Incremental builds for content updates should complete in under 10 seconds
  - Generated site must be under 5MB total (excluding high-resolution images)

- **Integration Points**:
  - Payment processors (PayPal, Stripe, etc.) for donation links
  - Calendar systems for event management
  - Email collection systems for volunteer signups
  - Social media platforms for sharing impact stories
  - Analytics services for campaign tracking

- **Key Constraints**:
  - All functionality must work without server-side processing
  - Donation processing must happen through established third-party providers
  - Content must be updatable by non-technical staff
  - Site must be accessible according to WCAG 2.1 AA standards
  - Solution must require minimal ongoing technical maintenance

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **Impact Storytelling System**:
   - Process structured impact story data with consistent metadata
   - Apply templates with appropriate layouts for different story types
   - Handle media-rich content with optimized images and quotes
   - Support story categorization and filtering
   - Create story archives and featured story highlighting

2. **Donation Management Framework**:
   - Generate secure, trackable donation links for various campaigns
   - Create campaign-specific landing pages with impact goals
   - Track and display fundraising progress toward goals
   - Support multiple donation methods and amounts
   - Generate appropriate thank-you pages and confirmation content

3. **Volunteer Engagement System**:
   - Process structured volunteer opportunity data
   - Generate position listings with complete information
   - Create application/signup flows that connect to external forms
   - Track and display volunteer needs by project or department
   - Support recurring and one-time volunteer opportunities

4. **Event Management System**:
   - Process event information with proper date handling
   - Generate event promotional pages with registration links
   - Automatically transition past events to an accessible archive
   - Support recurring events and event series
   - Create event calendars and category-based event filtering

5. **Funding Transparency Framework**:
   - Process grant and donation allocation data
   - Generate project-based funding breakdowns
   - Create visual representations of funding allocation
   - Support progress updates on funded initiatives
   - Track and display impact metrics related to funding

## Testing Requirements

- **Key Functionalities to Verify**:
  - Proper rendering of impact stories with different content types
  - Secure generation of donation links with correct parameters
  - Complete display of volunteer opportunity information
  - Accurate event promotion and automatic archiving
  - Correct representation of funding information by project

- **Critical User Scenarios**:
  - Organization adds a new impact story with multimedia content
  - Potential donor navigates donation options for specific campaigns
  - Prospective volunteer reviews opportunities and application process
  - Community member looks for information about upcoming events
  - Stakeholder reviews funding allocation and project progress

- **Performance Benchmarks**:
  - Site generation time for organizations of different sizes
  - Image optimization time and quality results
  - Page load time with various connection speeds
  - Build time for incremental content updates
  - Memory usage during site generation process

- **Edge Cases and Error Conditions**:
  - Handling of impact stories with missing media or information
  - Management of expired or invalid donation campaigns
  - Processing of volunteer opportunities with complex requirements
  - Handling of canceled or rescheduled events
  - Representation of complex funding relationships and reallocations

- **Required Test Coverage**:
  - 90% code coverage for impact story generation
  - 95% coverage for donation link creation
  - 90% coverage for volunteer opportunity management
  - 90% coverage for event system with date-based transitions
  - 90% coverage for funding information organization

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Impact stories effectively communicate program outcomes with consistent presentation
2. Donation links work correctly with various payment providers and campaign tracking
3. Volunteer opportunities are clearly presented with all necessary information
4. Events are properly promoted and automatically archived after completion
5. Funding information transparently shows allocation and impacts by project
6. Non-technical staff can update all content through structured data files
7. All tests pass with at least 90% code coverage
8. The full site can be regenerated in under 30 seconds

To set up your development environment:
```
uv venv
source .venv/bin/activate
```