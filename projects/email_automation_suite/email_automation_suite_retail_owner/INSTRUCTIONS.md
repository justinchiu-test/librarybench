# Retail Shop Owner Email Automation Suite

## Overview
RetailMail is a specialized email automation library designed for boutique retail store owners who manage customer inquiries, order processing, and supplier communications. It enables efficient handling of order-related communications, personalized customer interactions based on purchase history, inventory management with suppliers, and targeted promotional campaigns, allowing retail owners to maintain excellent customer service while efficiently managing their business operations.

## Persona Description
Priya runs a boutique retail store and handles customer inquiries, order confirmations, and supplier communications. Her primary goal is to maintain excellent customer service through prompt, personalized emails while efficiently managing inventory-related communications with suppliers.

## Key Requirements

1. **Order Status Tracking and Notification System**
   - Create automated notifications for order processing stages (confirmation, shipping, delivery)
   - Track package shipments and generate delivery update emails
   - Manage customer inquiries related to order status
   - This feature is critical because it keeps customers informed about their orders automatically, reducing "where is my order" inquiries while improving customer satisfaction through proactive communication about their purchases

2. **Customer Purchase History Integration**
   - Maintain customer purchase records and preferences
   - Generate personalized product recommendations based on purchase patterns
   - Create targeted follow-up communications for repeat customers
   - This feature is essential because it allows for highly personalized customer communications that drive repeat business, increasing customer lifetime value through tailored product suggestions that align with their demonstrated preferences

3. **Inventory Management and Supplier Communication**
   - Monitor inventory levels and trigger alerts at defined thresholds
   - Generate automated reorder emails to suppliers
   - Track order status with suppliers and manage follow-ups
   - This feature is vital because it prevents stockouts by automating the reordering process, reducing the manual overhead of supplier communications while ensuring inventory is maintained at optimal levels

4. **Customer Feedback Collection and Analysis**
   - Create post-purchase feedback request sequences
   - Process and categorize feedback by sentiment and product category
   - Generate aggregate reports on customer satisfaction
   - This feature is important because it systematically collects customer insights that drive product and service improvements, while the sentiment analysis helps quickly identify and address any negative customer experiences

5. **Promotional Campaign Management**
   - Schedule and send targeted promotional campaigns based on customer segments
   - Track campaign performance metrics (open rates, conversion rates)
   - A/B test email variations for optimization
   - This feature improves marketing effectiveness by targeting promotions to the right customer segments, while performance tracking enables data-driven refinement of marketing strategies to maximize return on investment

## Technical Requirements

### Testability Requirements
- All email generation functions must be testable with mock customer and order data
- Recommendation algorithms must be verifiable with test purchase history
- Inventory threshold monitoring must be testable with simulated inventory changes
- Feedback analysis must produce consistent results with test feedback data
- Campaign tracking must generate accurate metrics with test campaign data

### Performance Expectations
- Order notification generation should process at least 100 orders per minute
- Customer purchase analysis should handle databases of at least 10,000 customers efficiently
- Inventory monitoring should check at least 1,000 product SKUs in under 5 seconds
- Feedback categorization should process at least 50 submissions per second
- Campaign sending should handle distribution to at least 5,000 recipients per hour

### Integration Points
- IMAP and SMTP libraries for email retrieval and sending
- Template engine for dynamic content generation
- SQLite or similar database for customer, order, and inventory data
- Basic NLP tools for feedback sentiment analysis
- Analytics libraries for campaign performance metrics

### Key Constraints
- All emails must be mobile-responsive and display correctly across devices
- Customer data must be handled securely and in compliance with privacy regulations
- The implementation must be resilient to varying email client capabilities
- Promotional sending must respect anti-spam regulations and sending limits
- The system must operate efficiently without requiring excessive computational resources

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core of the Retail Shop Owner Email Automation Suite should provide:

1. **Order Management Module**
   - Processing order information from sales systems
   - Generating appropriate notifications based on order status
   - Tracking shipments and delivery status
   - Handling customer inquiries about existing orders

2. **Customer Relationship Engine**
   - Maintaining customer profiles with purchase history
   - Analyzing purchase patterns for personalization
   - Generating relevant product recommendations
   - Supporting customer segmentation for targeted communications

3. **Inventory Control System**
   - Monitoring product inventory levels
   - Triggering alerts based on configured thresholds
   - Generating supplier orders with appropriate details
   - Tracking supplier response and order fulfillment

4. **Feedback Processing Engine**
   - Creating and sending feedback request emails
   - Processing customer responses and categorizing feedback
   - Performing basic sentiment analysis on feedback text
   - Generating actionable reports from customer insights

5. **Marketing Campaign Manager**
   - Creating and scheduling promotional campaigns
   - Targeting campaigns to appropriate customer segments
   - Tracking campaign performance metrics
   - Supporting A/B testing for campaign optimization

## Testing Requirements

### Key Functionalities to Verify
- Order status notification generation for different order states
- Recommendation accuracy based on customer purchase history
- Inventory threshold detection and supplier notification
- Feedback sentiment categorization accuracy
- Campaign targeting and delivery to correct customer segments

### Critical User Scenarios
- Processing a new order through all notification stages
- Generating personalized product recommendations for repeat customers
- Detecting low inventory and sending reorder emails to suppliers
- Collecting and categorizing customer feedback after purchases
- Creating and sending targeted promotional campaigns to specific customer segments

### Performance Benchmarks
- Order processing should handle at least 1000 orders per day without degradation
- Customer recommendation generation should complete in under 200ms per customer
- Inventory monitoring should efficiently check 1000+ SKUs in under 5 seconds
- Feedback analysis should achieve 85% accuracy on sentiment classification
- Campaign delivery should support sending to at least 5000 recipients per hour

### Edge Cases and Error Conditions
- Handling orders with multiple shipments or partial fulfillment
- Processing recommendations for customers with limited purchase history
- Managing inventory for products with supplier shortages or discontinuations
- Dealing with ambiguous or mixed-sentiment feedback
- Handling bounced emails or undeliverable promotional messages

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of order notification functions
- 100% coverage of inventory threshold monitoring
- 100% coverage of recommendation generation algorithm
- Minimum 95% coverage of campaign targeting logic

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

- Order status notifications are correctly generated for all order stages
- Product recommendations relevantly match customer purchase patterns
- Inventory alerts are triggered at appropriate thresholds
- Feedback is accurately categorized by sentiment and product
- Promotional campaigns are correctly targeted to appropriate customer segments
- All performance benchmarks are met under load testing
- The system correctly handles all specified edge cases and error conditions

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Getting Started
To set up the development environment:
1. Create a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: When testing your implementation, you MUST run tests with pytest-json-report and provide the pytest_results.json file:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

Providing the pytest_results.json file is MANDATORY for demonstrating that your implementation meets the requirements.