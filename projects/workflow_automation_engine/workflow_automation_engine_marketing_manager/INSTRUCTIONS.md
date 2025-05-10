# Marketing Campaign Automation Engine

A specialized workflow automation engine for coordinating digital marketing campaigns across multiple channels with natural language workflow definition capabilities.

## Overview

This project implements a Python library for defining, executing, and monitoring digital marketing campaign workflows across multiple platforms and channels. The system provides natural language workflow definition, marketing platform integration, audience segmentation logic, campaign timing coordination, and performance metrics collection specifically designed for marketing automation needs.

## Persona Description

Carlos coordinates digital marketing campaigns across multiple channels and platforms. He needs to automate content publication, audience targeting, and analytics collection without deep technical expertise.

## Key Requirements

1. **Natural Language Workflow Definition**: Implement functionality allowing non-technical users to describe automation needs in plain language.
   - Critical for Carlos because he and his team lack programming expertise but need to define complex campaign workflows.
   - System should interpret natural language descriptions and convert them into executable workflow definitions.

2. **Marketing Platform Integration**: Develop connections with common advertising and content systems.
   - Essential for Carlos to automate actions across the multiple marketing platforms his team uses without manual intervention.
   - Must support authentication, data exchange, and action execution across various marketing APIs and services.

3. **Audience Segmentation Logic**: Create implementation of complex targeting rules across channels.
   - Vital for Carlos to deliver personalized content to specific audience segments based on demographics, behavior, and engagement history.
   - Should enable definition and execution of sophisticated segmentation rules that work consistently across different marketing platforms.

4. **Campaign Timing Coordination**: Implement scheduling of actions across global time zones.
   - Necessary for Carlos to optimize campaign timing for different audience segments around the world.
   - Must coordinate scheduled actions across platforms with awareness of time zones, local preferences, and platform-specific timing constraints.

5. **Performance Metrics Collection**: Develop automatic gathering and visualization of campaign results.
   - Critical for Carlos to measure campaign effectiveness and ROI without manual data collection and analysis.
   - Should aggregate metrics from multiple platforms into unified reports and visualizations with minimal setup.

## Technical Requirements

### Testability Requirements
- All components must be fully testable with pytest without requiring actual marketing platform accounts
- Mock objects must be available for all external platforms and APIs
- Natural language processing must be testable with deterministic sample inputs
- Segmentation logic must be verifiable with sample audience data
- Performance metrics collection must be testable with simulated campaign data

### Performance Expectations
- Support for managing campaigns across at least 10 different marketing platforms
- Natural language processing that completes in under 3 seconds for typical workflow descriptions
- Ability to apply segmentation rules to audiences of 1M+ profiles
- Campaign coordination with timing precision within 1 minute
- Metrics collection and aggregation that scales to handle 10M+ individual engagement events

### Integration Points
- Social media advertising platforms (Facebook, Instagram, Twitter, LinkedIn, etc.)
- Email marketing systems (Mailchimp, SendGrid, HubSpot, etc.)
- Content management systems (WordPress, Drupal, etc.)
- Analytics platforms (Google Analytics, Adobe Analytics, etc.)
- Customer data platforms and CRM systems

### Key Constraints
- No UI components - all functionality must be accessible via Python API
- Must handle API rate limits and quotas gracefully
- All platform credentials must be stored securely
- System should operate without storing personally identifiable information when possible
- Must adapt to frequent changes in external platform APIs

## Core Functionality

The system must provide a Python library that enables:

1. **Natural Language Workflow Definition**: A system that:
   - Interprets plain language descriptions of marketing workflows
   - Extracts key entities, actions, conditions, and timing requirements
   - Converts natural language to structured workflow definitions
   - Provides validation and suggestions for ambiguous instructions
   - Supports iterative refinement of workflow definitions

2. **Platform Integration Framework**: A comprehensive integration system that:
   - Connects to multiple marketing platforms via their APIs
   - Manages authentication and credentials securely
   - Normalizes data formats across different platforms
   - Provides a unified interface for common marketing actions
   - Adapts to changes in platform APIs with minimal disruption

3. **Audience Segmentation Engine**: A powerful segmentation system that:
   - Defines audience segments using complex criteria combinations
   - Applies consistent segmentation rules across platforms
   - Translates segments to platform-specific targeting parameters
   - Estimates segment sizes before campaign execution
   - Tracks segment performance across campaigns

4. **Campaign Coordination System**: A sophisticated scheduling mechanism that:
   - Manages campaign timing across multiple time zones
   - Coordinates actions across different platforms
   - Handles dependencies between campaign elements
   - Optimizes delivery timing based on audience engagement patterns
   - Provides real-time monitoring of campaign execution

5. **Metrics Collection and Analysis**: A comprehensive analytics system that:
   - Gathers performance data from all integrated platforms
   - Normalizes metrics for cross-platform comparison
   - Aggregates results at various levels (campaign, channel, segment, etc.)
   - Generates visualizations for key performance indicators
   - Provides insights and recommendations for campaign optimization

## Testing Requirements

### Key Functionalities to Verify
- Accurate interpretation of natural language workflow descriptions
- Proper integration with marketing platform APIs
- Correct application of audience segmentation rules
- Precise coordination of campaign actions across time zones
- Comprehensive collection and aggregation of performance metrics

### Critical User Scenarios
- Multi-channel product launch campaign with coordinated timing
- Audience re-engagement campaign with complex segmentation
- A/B testing workflow across multiple platforms
- Event-triggered email sequence with conditional paths
- Cross-platform campaign with unified performance reporting

### Performance Benchmarks
- Natural language processing with response time under 3 seconds
- Segmentation rules applied to 1M profiles in under 30 seconds
- Campaign coordination with timing accuracy within 1 minute
- Metrics collection from 10 platforms completed in under 5 minutes
- Dashboard generation with 20+ metrics in under 10 seconds

### Edge Cases and Error Conditions
- Handling of ambiguous or contradictory natural language instructions
- Proper behavior when marketing platforms experience downtime
- Recovery from interrupted campaign execution
- Appropriate action when audience segments return zero matches
- Handling of unexpected changes in platform APIs or response formats

### Required Test Coverage Metrics
- Minimum 90% line coverage for core workflow engine
- 100% coverage of natural language interpretation logic
- 100% coverage of platform integration interfaces
- All segmentation rule combinations must be tested
- Comprehensive testing of time zone handling edge cases

## Success Criteria

The implementation will be considered successful if it demonstrates:

1. The ability to accurately convert natural language descriptions into executable workflows
2. Reliable integration with multiple marketing platforms for automated action execution
3. Effective audience segmentation that works consistently across platforms
4. Precise campaign timing coordination across global time zones
5. Comprehensive performance metrics collection and visualization
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

To execute sample marketing workflows during development:

```python
import marketflow

# Define platforms with mock credentials for testing
platforms = marketflow.PlatformRegistry()
platforms.register("email", "mailchimp", {"api_key": "test_key"})
platforms.register("social", "facebook", {"app_id": "test_id", "app_secret": "test_secret"})
platforms.register("ads", "google_ads", {"client_id": "test_client", "client_secret": "test_secret"})
platforms.register("analytics", "google_analytics", {"view_id": "test_view"})

# Define a workflow using natural language
nl_processor = marketflow.NaturalLanguageProcessor()
workflow_description = """
Launch a product announcement campaign on Monday at 9 AM local time for each region.
Send an email to all subscribers who have opened our emails in the last 30 days.
Post product images on Instagram and Facebook with a link to the landing page.
Start Facebook and Google ad campaigns targeting previous customers aged 25-45 who live in urban areas.
After 24 hours, send a follow-up email to people who clicked on the first email but didn't purchase.
Collect click-through rates, ad impressions, and conversion metrics from all platforms.
Generate a performance report comparing results across channels and regions.
"""

# Convert natural language to workflow definition
workflow = nl_processor.create_workflow(workflow_description, name="product_launch")

# Review the generated workflow
print("Generated workflow steps:")
for step in workflow.steps:
    print(f"- {step.description} on {step.platforms} at {step.timing}")

# Define audience segments
segments = marketflow.SegmentRegistry()
segments.define("active_subscribers", {
    "criteria": [
        {"field": "email_engagement", "operator": "opened", "value": "any", "timeframe": "30d"}
    ]
})
segments.define("target_customers", {
    "criteria": [
        {"field": "purchase_history", "operator": "has_purchased", "value": "any"},
        {"field": "demographics.age", "operator": "between", "value": [25, 45]},
        {"field": "demographics.location_type", "operator": "equals", "value": "urban"}
    ]
})
segments.define("email_clickers_no_purchase", {
    "criteria": [
        {"field": "email_engagement", "operator": "clicked", "value": "campaign:product_launch"},
        {"field": "purchase", "operator": "not_completed", "value": "product:new_launch", "timeframe": "24h"}
    ]
})

# Apply segments to workflow
workflow.apply_segment("email_announcement", "active_subscribers")
workflow.apply_segment("ad_campaigns", "target_customers")
workflow.apply_segment("follow_up_email", "email_clickers_no_purchase")

# Configure time zone handling
workflow.set_time_coordination({
    "reference_time": "2023-10-15 09:00:00",
    "local_time_by_region": True,
    "regions": ["America/New_York", "Europe/London", "Asia/Tokyo"]
})

# Configure metrics collection
workflow.configure_metrics({
    "collection_frequency": "hourly",
    "metrics": [
        {"name": "email_open_rate", "source": "mailchimp", "field": "opens.rate"},
        {"name": "email_click_rate", "source": "mailchimp", "field": "clicks.rate"},
        {"name": "ad_impressions", "source": ["facebook", "google_ads"], "field": "impressions"},
        {"name": "ad_clicks", "source": ["facebook", "google_ads"], "field": "clicks"},
        {"name": "conversion_rate", "source": "google_analytics", "field": "conversion_rate"}
    ],
    "dimensions": ["platform", "region", "segment", "time"]
})

# Execute the workflow (with mock execution for testing)
engine = marketflow.Engine(platforms, segments)
execution = engine.execute(workflow, dry_run=True)

# Preview the execution plan
print("\nExecution plan:")
for action in execution.planned_actions:
    print(f"- {action.time}: {action.description} on {action.platform} targeting {action.segment}")

# In a real scenario, monitor and collect results
if not execution.is_dry_run:
    results = execution.collect_metrics()
    report = marketflow.Report(results)
    print("\nCampaign performance summary:")
    print(f"Overall conversion rate: {report.get_metric('conversion_rate')}%")
    print(f"Best performing platform: {report.get_best_platform()}")
    print(f"Best performing region: {report.get_best_region()}")
```