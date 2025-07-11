# Process Resource Monitor - Mobile App Backend Lead Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Thomas, a backend team lead optimizing server resources for mobile app traffic. The library should correlate process resource usage with user activity patterns and predict resource needs based on user behavior.

## Core Requirements

### 1. API Endpoint Correlation with Process Resource Usage
- Map HTTP/REST API endpoints to backend processes
- Track resource consumption per API endpoint
- Identify resource-intensive API operations
- Monitor API gateway and load balancer process overhead
- Correlate microservice resource usage with API calls

### 2. User Session Impact on Resource Consumption
- Track active user sessions and their resource footprint
- Monitor WebSocket/long-polling connection overhead
- Identify resource usage patterns per user cohort
- Track session state memory consumption
- Analyze concurrent session scaling characteristics

### 3. Peak Traffic Resource Requirement Prediction
- Analyze historical traffic patterns for prediction
- Identify daily, weekly, and seasonal usage patterns
- Predict resource needs for upcoming peak periods
- Model resource requirements for user growth scenarios
- Generate capacity planning recommendations

### 4. Geographic Distribution Impact on Resource Usage
- Monitor resource usage by user geographic location
- Track CDN edge server process efficiency
- Analyze geo-routing impact on backend resources
- Identify region-specific resource bottlenecks
- Optimize resource allocation across regions

### 5. Push Notification Service Resource Monitoring
- Track push notification service process usage
- Monitor notification queue processing efficiency
- Measure notification delivery success vs resource cost
- Identify notification batch optimization opportunities
- Track third-party service integration overhead

## Technical Specifications

### Data Collection
- Integration with API gateway logs and metrics
- Application-level instrumentation via middleware
- User session tracking with anonymized identifiers
- Geographic data enrichment from IP addresses
- Real-time metric streaming for immediate insights

### API Design
```python
# Example usage
monitor = MobileBackendMonitor()

# Configure API endpoint tracking
monitor.configure_endpoints(
    api_gateway="nginx",
    endpoints=[
        "/api/v1/users/*",
        "/api/v1/products/*",
        "/api/v1/orders/*"
    ]
)

# Get endpoint resource usage
endpoint_stats = monitor.get_endpoint_resources(
    time_range="1h",
    group_by="endpoint",
    include_percentiles=True
)

# Analyze user session impact
session_analysis = monitor.analyze_session_impact(
    active_sessions=True,
    resource_metrics=["cpu", "memory", "connections"],
    user_cohorts=["premium", "free"]
)

# Predict peak traffic resources
prediction = monitor.predict_peak_resources(
    forecast_days=7,
    confidence_level=0.95,
    include_safety_margin=True
)

# Get geographic resource distribution
geo_stats = monitor.get_geographic_distribution(
    regions=["north-america", "europe", "asia"],
    metrics=["latency", "resource_usage", "user_count"]
)

# Monitor push notifications
push_stats = monitor.get_push_notification_stats(
    service="fcm",  # or "apns"
    include_delivery_rates=True,
    resource_per_notification=True
)
```

### Testing Requirements
- Load testing with simulated mobile traffic patterns
- API endpoint mapping accuracy validation
- Geographic distribution simulation tests
- Push notification throughput testing
- Use pytest with pytest-json-report for test result formatting
- Test with realistic mobile app usage patterns

### Performance Targets
- Track 10,000+ concurrent user sessions
- Process 100,000 API requests per minute
- Predict resource needs with 90% accuracy
- Update metrics within 5 seconds of API calls
- Generate reports for millions of historical requests

## Implementation Constraints
- Python 3.8+ compatibility required
- Use Python standard library plus: psutil, requests, pandas, scikit-learn
- No GUI components - this is a backend library only
- Support common API gateway integrations
- Privacy-compliant user tracking only

## Deliverables
1. Core Python library with API endpoint tracking
2. User session impact analyzer
3. Machine learning-based traffic prediction engine
4. Geographic resource distribution optimizer
5. CLI tool for capacity planning and cost analysis