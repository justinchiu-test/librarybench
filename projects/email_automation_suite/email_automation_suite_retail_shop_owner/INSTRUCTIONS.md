# MailFlow for Retail - Customer-Centric Order Management System

## Overview
A specialized email automation system tailored for small retail businesses that tracks order status communications, leverages customer purchase history for personalized interactions, manages inventory-related supplier communications, collects customer feedback, and coordinates targeted promotional campaigns.

## Persona Description
Priya runs a boutique retail store and handles customer inquiries, order confirmations, and supplier communications. Her primary goal is to maintain excellent customer service through prompt, personalized emails while efficiently managing inventory-related communications with suppliers.

## Key Requirements

1. **Order Status Tracking System**
   - Automated email notifications for order processing, shipping, and delivery milestones
   - Tracking number integration with delivery status updates
   - Proactive communication for delays or issues
   - This feature is critical for Priya to maintain transparency with customers throughout the order fulfillment process, reducing customer inquiries about order status while building trust through consistent, timely updates at each stage of fulfillment.

2. **Customer Purchase History Integration**
   - Historical purchase data integration for personalized communications
   - Product recommendation engine based on past purchases
   - Anniversary and reorder reminder capabilities
   - This feature enables Priya to create highly relevant communications with personalized product recommendations, increasing repeat business by referencing customers' specific purchase history and preferences rather than sending generic marketing messages.

3. **Inventory Management Communication System**
   - Threshold-based supplier alerts for low stock items
   - Template-based reordering communications
   - Delivery schedule tracking and follow-ups
   - This feature streamlines Priya's inventory management workflow, ensuring timely reordering through automated supplier communications when inventory reaches critical levels, preventing stockouts while maintaining efficient inventory levels.

4. **Customer Feedback Collection and Analysis**
   - Post-purchase feedback request automation
   - Sentiment categorization of customer comments
   - Response templates for different feedback types
   - This feature allows Priya to systematically gather customer opinions about products and service, identifying issues quickly through sentiment analysis while demonstrating commitment to customer satisfaction through prompt responses to feedback.

5. **Targeted Promotion Campaign System**
   - Customer segmentation based on purchase patterns
   - Scheduled promotional email campaigns by segment
   - Performance tracking with conversion metrics
   - This feature enables Priya to execute strategic marketing efforts by targeting specific customer segments with relevant promotions, scheduling campaigns for optimal timing while measuring effectiveness through concrete conversion metrics.

## Technical Requirements

### Testability Requirements
- All components must be testable without requiring actual email server connections
- Mock objects must be available for IMAP/SMTP services
- Order processing must be testable with sample order data
- Inventory threshold notifications must be verifiable with test inventory levels
- Campaign targeting must be testable with sample customer segments

### Performance Expectations
- Processing of new emails should complete within 3 seconds
- Template personalization and sending should complete within 1 second
- Customer segmentation queries should complete within 2 seconds
- The system should handle up to an inventory of 10,000 products and 5,000 customers
- Batch email operations (e.g., promotional campaigns) should process at least 100 emails per minute

### Integration Points
- IMAP and SMTP protocols for email server communication
- Local database for storing product, customer, and order information
- File system for managing product images and promotional assets
- Optional integration with basic inventory management data
- Export/import functionality for backup and migration

### Key Constraints
- Must work with standard email protocols (IMAP/SMTP)
- Must not require third-party services or APIs that incur additional costs
- Must protect customer privacy and comply with retail communication regulations
- Must operate efficiently on standard hardware without requiring cloud resources
- All data must be stored locally with proper backup procedures
- Must accommodate limited technical expertise for system maintenance

## Core Functionality

The system must provide:

1. **Order Processing Communication Engine**
   - Track order status through fulfillment process
   - Generate appropriate notifications for each milestone
   - Integrate shipping tracking information when available
   - Handle exception communications for delays or issues

2. **Customer Relationship Management**
   - Store customer profiles with purchase history
   - Calculate product affinities and recommendations
   - Track communication history and preferences
   - Generate personalized messaging based on past interactions

3. **Inventory Management System**
   - Monitor product stock levels against thresholds
   - Generate supplier communications when needed
   - Track reorder status and expected deliveries
   - Manage product availability notifications

4. **Feedback Management System**
   - Schedule post-purchase feedback requests
   - Process and categorize customer responses
   - Generate appropriate follow-up communications
   - Produce feedback summary reports

5. **Marketing Campaign Manager**
   - Define customer segments based on multiple criteria
   - Schedule and execute targeted campaigns
   - Track open, click-through, and conversion rates
   - Analyze campaign effectiveness by segment

## Testing Requirements

### Key Functionalities to Verify
- Order status notification generation for different fulfillment stages
- Recommendation accuracy based on purchase history
- Inventory threshold detection and supplier notification
- Feedback sentiment categorization accuracy
- Customer segmentation based on multiple criteria

### Critical Scenarios to Test
- Processing a complete order lifecycle from placement to delivery
- Generating personalized recommendations for customers with varied purchase histories
- Managing inventory reordering workflows with supplier communication
- Collecting and processing different types of customer feedback
- Executing targeted campaigns to specific customer segments

### Performance Benchmarks
- Order status update processing within 500ms
- Customer segmentation of 5,000 customers in under 3 seconds
- Batch email campaign delivery to 1,000 recipients in under 10 minutes
- System memory usage under 300MB with full product catalog
- Database query performance with large datasets (10,000+ products, 5,000+ customers)

### Edge Cases and Error Conditions
- Handling order cancellations and returns
- Processing incomplete customer profile information
- Managing product discontinuations and substitutions
- Dealing with undeliverable emails or bounces
- Recovering from interrupted campaign sequences
- Handling supplier communication breakdowns

### Required Test Coverage
- Minimum 90% code coverage for core functionality
- 100% coverage of order status notification logic
- 100% coverage of inventory threshold detection
- 100% coverage of customer segmentation algorithms
- Comprehensive integration tests for end-to-end communication workflows

## Success Criteria

The implementation will be considered successful if it:

1. Reduces customer service inquiries about order status by at least 70%
2. Increases repeat purchase rate by at least 20% through personalized recommendations
3. Eliminates stockouts due to delayed reordering by at least 90%
4. Achieves customer feedback collection from at least 40% of orders
5. Increases email campaign conversion rates by at least 30% through targeting
6. Reduces time spent on routine email communications by at least 15 hours per week
7. Successfully processes 99.5% of orders without manual intervention
8. Enables inventory management with 50% less time investment

## Development Setup

To set up the development environment:

1. Initialize a new project with UV:
   ```
   uv init --lib
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Run the code:
   ```
   uv run python your_script.py
   ```

4. Run tests:
   ```
   uv run pytest
   ```

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```