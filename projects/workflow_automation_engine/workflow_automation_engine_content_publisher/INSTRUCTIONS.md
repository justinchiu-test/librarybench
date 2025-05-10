# Content Publishing Workflow Engine

A specialized workflow automation engine for streamlining content transformation, approval processes, and coordinated multi-platform publishing.

## Overview

This project implements a Python library for defining, executing, and monitoring content publishing workflows across multiple platforms and formats. The system provides automated content transformation, approval workflow implementation, publishing schedule coordination, asset management, and localization workflow capabilities tailored specifically for digital content publishers.

## Persona Description

Amara manages digital content publication across multiple platforms and formats. She needs workflow automation to streamline content transformation, approval processes, and coordinated publishing.

## Key Requirements

1. **Content Transformation**: Implement functionality to automatically convert between different formats and platforms.
   - Critical for Amara because content must be adapted for various platforms with different technical requirements and audience expectations.
   - System should transform content between formats (text, images, video, etc.) and adapt it to platform-specific requirements and constraints.

2. **Approval Workflow Implementation**: Develop a system with role-based review steps and notifications.
   - Essential for Amara to ensure content quality and compliance before publication while maintaining clear accountability.
   - Must route content through configurable approval sequences with appropriate permissions, tracking, and notification at each step.

3. **Publishing Schedule Coordination**: Create functionality for timing releases across different channels.
   - Vital for Amara to maintain consistent messaging across platforms while optimizing for audience engagement on each channel.
   - Should manage complex scheduling requirements including embargoes, sequential releases, and optimal timing for different audiences.

4. **Asset Management**: Implement ensuring all associated files are properly organized and referenced.
   - Necessary for Amara to maintain the relationships between content pieces and their associated assets (images, videos, documents, etc.).
   - Must track asset dependencies, ensure proper organization, and validate references before publication.

5. **Localization Workflow**: Develop handling of translations and regional content variations.
   - Critical for Amara to efficiently manage content across different languages and regions while maintaining consistency.
   - Should coordinate translation processes, manage regional variations, and synchronize updates across localized versions.

## Technical Requirements

### Testability Requirements
- All components must be fully testable with pytest without requiring actual publishing platforms
- Mock publishing endpoints must be available for all supported platforms
- Content transformation must produce deterministic outputs for verification
- Approval workflows must be testable with simulated roles and permissions
- Asset management must be verifiable with known content-asset relationships

### Performance Expectations
- Support for processing at least 100 publishing requests concurrently
- Content transformation completed in under 30 seconds for standard content pieces
- Approval workflow state transitions in under 3 seconds
- Publishing coordination across 10+ platforms with millisecond precision
- Asset dependency analysis for content with 100+ assets in under 5 seconds

### Integration Points
- Content Management Systems (WordPress, Drupal, etc.)
- Social media platforms (Facebook, Twitter, Instagram, LinkedIn, etc.)
- Email marketing systems (Mailchimp, Constant Contact, etc.)
- Digital asset management systems
- Translation and localization services

### Key Constraints
- No UI components - all functionality must be accessible via Python API
- Must handle large media files efficiently
- System should operate with appropriate security for pre-release content
- Must respect rate limits and quotas of publishing platforms
- Should minimize duplicate storage of content and assets

## Core Functionality

The system must provide a Python library that enables:

1. **Content Transformation System**: A comprehensive conversion system that:
   - Transforms content between different formats (text, HTML, markdown, etc.)
   - Adapts content for platform-specific requirements and constraints
   - Optimizes media for different delivery channels
   - Preserves content integrity across transformations
   - Handles rich media including images, videos, and interactive elements

2. **Approval Workflow Engine**: A flexible approval system that:
   - Defines multi-stage approval processes with role-based permissions
   - Routes content through appropriate reviewers and stakeholders
   - Tracks review status, comments, and changes
   - Sends notifications at appropriate workflow stages
   - Implements escalation paths for delayed approvals

3. **Publishing Coordination System**: A sophisticated scheduling mechanism that:
   - Manages publication timing across multiple platforms
   - Implements embargoes and scheduled releases
   - Coordinates sequential or simultaneous multi-platform publishing
   - Optimizes timing based on audience engagement patterns
   - Handles timezone-specific scheduling requirements

4. **Asset Management Framework**: A comprehensive tracking system that:
   - Manages relationships between content and associated assets
   - Ensures proper organization and accessibility of all assets
   - Validates asset references and dependencies before publication
   - Handles versioning of assets and content
   - Optimizes asset delivery for different platforms

5. **Localization System**: A robust translation and localization framework that:
   - Manages translation workflows for content across languages
   - Handles region-specific content variations
   - Synchronizes updates across localized versions
   - Preserves formatting and layout across languages
   - Integrates with translation services and tools

## Testing Requirements

### Key Functionalities to Verify
- Accurate transformation of content across formats and platforms
- Proper execution of approval workflows with appropriate permissions
- Precise coordination of publishing schedules across channels
- Correct management of content-asset relationships and references
- Effective handling of translation and localization processes

### Critical User Scenarios
- Multi-platform product launch with coordinated release timing
- Content approval workflow with multiple stakeholders and revisions
- Rich media article with numerous asset dependencies
- Global campaign with multiple language versions and regional variations
- Automated social media distribution with platform-specific formatting

### Performance Benchmarks
- Content transformation for a standard article completed in under 10 seconds
- Approval workflow transitions processed in under 3 seconds
- Publishing coordination timing precision within 1 second
- Asset dependency analysis for content with 50+ assets in under 3 seconds
- Translation workflow initiation for 5 languages in under 10 seconds

### Edge Cases and Error Conditions
- Handling of unsupported content formats or elements
- Proper behavior when approval workflows deadlock or timeout
- Recovery from failed publishing attempts
- Appropriate action when referenced assets are missing or invalid
- Graceful degradation when translation services are unavailable

### Required Test Coverage Metrics
- Minimum 90% line coverage for core workflow engine
- 100% coverage of content transformation pathways
- 100% coverage of approval workflow state transitions
- All asset management validation rules must be tested
- Complete verification of localization synchronization logic

## Success Criteria

The implementation will be considered successful if it demonstrates:

1. The ability to accurately transform content between formats and platforms
2. Reliable execution of configurable approval workflows with appropriate controls
3. Precise coordination of publishing schedules across multiple channels
4. Comprehensive management of content-asset relationships and dependencies
5. Effective handling of content translation and regional variations
6. All tests pass with the specified coverage metrics
7. Performance meets or exceeds the defined benchmarks

## Getting Started

To set up the development environment:

1. Initialize the project with `uv init --lib`
2. Install dependencies with `uv sync`
3. Run tests with `uv run pytest`
4. Run a single test with `uv run pytest path/to/test.py::test_function_name`
5. Format code with `uv run ruff format`
6. Lint code with `uv run ruff check .`
7. Type check with `uv run pyright`

To execute sample publishing workflows during development:

```python
import publishflow

# Define publishing platforms
platforms = publishflow.PlatformRegistry()
platforms.register("cms", "wordpress", {
    "api_url": "https://example.com/wp-json/wp/v2",
    "auth": publishflow.Auth.basic("username", "password")
})
platforms.register("social", "twitter", {
    "api_key": "key",
    "api_secret": "secret",
    "access_token": "token",
    "access_secret": "token_secret"
})
platforms.register("social", "facebook", {
    "page_id": "page_id",
    "access_token": "access_token"
})
platforms.register("email", "mailchimp", {
    "api_key": "api_key",
    "list_id": "list_id"
})

# Configure asset management
asset_manager = publishflow.AssetManager({
    "storage_path": "/path/to/assets",
    "cdn_base_url": "https://cdn.example.com/assets"
})

# Define content types
content_registry = publishflow.ContentRegistry()
content_registry.define_type("blog_post", {
    "attributes": ["title", "content", "excerpt", "featured_image", "categories", "tags"],
    "required": ["title", "content"],
    "assets": {
        "featured_image": {"type": "image", "formats": ["jpg", "png"], "max_size_mb": 2},
        "content_images": {"type": "image", "formats": ["jpg", "png", "gif"], "max_size_mb": 1},
        "attachments": {"type": "document", "formats": ["pdf", "doc", "docx"], "max_size_mb": 10}
    }
})

# Define approval workflow
approval_workflows = publishflow.WorkflowRegistry()
approval_workflows.define("standard_approval", {
    "steps": [
        {"name": "draft", "roles": ["author"], "transitions": ["submit_for_review"]},
        {"name": "review", "roles": ["editor"], "transitions": ["approve", "request_changes"]},
        {"name": "approved", "roles": ["publisher"], "transitions": ["publish", "schedule"]}
    ],
    "notifications": [
        {"event": "submit_for_review", "recipients": ["editors"], "template": "content_for_review"},
        {"event": "request_changes", "recipients": ["content.author"], "template": "changes_requested"},
        {"event": "approve", "recipients": ["publishers", "content.author"], "template": "content_approved"}
    ]
})

# Define transformation rules
transformation_engine = publishflow.TransformationEngine()
transformation_engine.register_rule("wordpress_to_twitter", {
    "content_type": "blog_post",
    "transforms": [
        {"field": "title", "operations": [{"type": "truncate", "max_length": 100}]},
        {"field": "content", "operations": [
            {"type": "extract_first_paragraph"},
            {"type": "truncate", "max_length": 200},
            {"type": "append", "text": "... Read more: {permalink}"}
        ]},
        {"field": "featured_image", "operations": [
            {"type": "resize", "width": 1200, "height": 675, "mode": "cover"},
            {"type": "optimize", "quality": 85}
        ]}
    ]
})

# Define a publishing workflow
blog_workflow = publishflow.PublishingWorkflow("blog_post_publication")

# Add content definition
blog_workflow.set_content_type("blog_post")
blog_workflow.set_approval_workflow("standard_approval")

# Add asset validation
blog_workflow.add_asset_validation({
    "featured_image": {"required": True, "min_dimensions": {"width": 1200, "height": 630}},
    "content_images": {"max_count": 10, "min_dimensions": {"width": 800, "height": 600}}
})

# Add transformations
blog_workflow.add_transformation("wordpress", {
    "platform": "wordpress",
    "mapping": {
        "title": "content.title",
        "content": "content.content",
        "excerpt": "content.excerpt",
        "featured_media": "content.featured_image.id",
        "categories": "content.categories",
        "tags": "content.tags",
        "status": "'publish'"
    }
})
blog_workflow.add_transformation("twitter", {
    "platform": "twitter",
    "transformation_rule": "wordpress_to_twitter",
    "mapping": {
        "status": "{title} {content}",
        "media_ids": "[content.featured_image.twitter_id]"
    }
})
blog_workflow.add_transformation("facebook", {
    "platform": "facebook",
    "mapping": {
        "message": "{title}",
        "link": "{permalink}",
        "published": "true"
    }
})

# Configure publishing schedule
blog_workflow.set_publishing_schedule({
    "wordpress": {"timing": "immediate", "timezone": "UTC"},
    "twitter": {"timing": "after_wordpress", "delay": "5m"},
    "facebook": {"timing": "after_wordpress", "delay": "10m"}
})

# Configure localization
blog_workflow.configure_localization({
    "languages": ["en", "es", "fr", "de", "ja"],
    "default_language": "en",
    "translation_service": "deepl",
    "translation_workflow": "machine_with_review",
    "synchronization": {
        "strategy": "primary_to_secondary",
        "trigger": "on_publish",
        "fields": ["title", "content", "excerpt"]
    }
})

# Sample content for testing
sample_content = {
    "title": "Introducing Our New Product Line",
    "content": """
    <p>We're excited to announce our new product line, designed with sustainability in mind.</p>
    <p>These products use 50% less energy and are made from recycled materials.</p>
    <img src="product-lineup.jpg" alt="Product Lineup" />
    <h2>Key Features</h2>
    <ul>
        <li>Energy efficient design</li>
        <li>Recycled materials</li>
        <li>Extended warranty</li>
    </ul>
    <p>Available starting next month at all retail locations.</p>
    """,
    "excerpt": "Introducing our new sustainable product line with innovative features and reduced environmental impact.",
    "featured_image": "hero-image.jpg",
    "categories": ["Products", "Sustainability"],
    "tags": ["new release", "eco-friendly", "innovation"]
}

# Load assets
asset_manager.register_asset("hero-image.jpg", "/path/to/hero-image.jpg")
asset_manager.register_asset("product-lineup.jpg", "/path/to/product-lineup.jpg")

# Execute workflow
engine = publishflow.Engine(platforms, asset_manager, content_registry, approval_workflows, transformation_engine)
execution = engine.create_execution(blog_workflow, content=sample_content)

# In a real scenario, this would progress through the workflow stages
# For testing, we can simulate the approval process
execution.transition("submit_for_review", {"comment": "Ready for review"})
execution.transition("approve", {"reviewer": "editor@example.com", "comment": "Looks good!"})
execution.transition("publish", {"publisher": "publisher@example.com"})

# Check results
results = execution.get_results()
print(f"Publishing status: {results.status}")
print(f"WordPress ID: {results.platform_ids['wordpress']}")
print(f"Twitter ID: {results.platform_ids['twitter']}")
print(f"Facebook ID: {results.platform_ids['facebook']}")
print(f"Transformations applied: {len(results.transformations)}")
print(f"Assets published: {len(results.published_assets)}")
print(f"Localization status: {results.localization_status}")
```