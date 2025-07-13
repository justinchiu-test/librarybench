# Memory Profiler Tool - Startup Founder Lisa Instructions

You are tasked with implementing a memory profiler tool specifically designed for Lisa, a technical founder whose SaaS application needs to scale efficiently on limited infrastructure. She needs to understand memory usage patterns to optimize hosting costs and improve multi-tenancy.

## Core Requirements

### 1. Per-tenant memory usage isolation and reporting
- Track memory usage by tenant identifier
- Isolate tenant-specific memory allocations
- Generate per-tenant memory reports
- Identify memory-intensive tenants
- Monitor cross-tenant memory leaks

### 2. Memory-based pricing tier recommendations
- Calculate memory costs per pricing tier
- Identify optimal tier boundaries
- Model tier upgrade triggers
- Generate pricing optimization reports
- Predict revenue impact of tier changes

### 3. Tenant memory quota enforcement mechanisms
- Implement soft and hard memory limits
- Track quota utilization in real-time
- Generate quota violation alerts
- Provide graceful degradation strategies
- Calculate fair quota distributions

### 4. Memory usage trends for investor metrics
- Generate growth trajectory visualizations
- Calculate memory efficiency KPIs
- Track infrastructure cost per customer
- Project future memory requirements
- Create investor-ready dashboards

### 5. Cost-per-customer memory analysis
- Calculate true memory cost per tenant
- Identify profitable vs costly customers
- Track memory ROI by customer segment
- Generate customer efficiency scores
- Optimize resource allocation strategies

## Implementation Guidelines

- Use Python exclusively for all implementations
- No UI components - focus on programmatic APIs and CLI tools
- All output should be text-based (JSON, CSV, or formatted text)
- Design for multi-tenant SaaS architectures
- Support cloud cost optimization

## Testing Requirements

All tests must be written using pytest and follow these guidelines:
- Generate detailed test reports using pytest-json-report
- Test multi-tenant isolation mechanisms
- Validate quota enforcement accuracy
- Test with realistic tenant distributions
- Ensure scalability to thousands of tenants

## Project Structure

```
memory_profiler_tool_startup_founder/
├── src/
│   ├── __init__.py
│   ├── tenant_isolator.py    # Tenant memory isolation
│   ├── pricing_optimizer.py  # Pricing tier analysis
│   ├── quota_enforcer.py     # Memory quota management
│   ├── investor_metrics.py   # Growth and KPI tracking
│   └── cost_analyzer.py      # Customer cost analysis
├── tests/
│   ├── __init__.py
│   ├── test_tenant_isolator.py
│   ├── test_pricing_optimizer.py
│   ├── test_quota_enforcer.py
│   ├── test_investor_metrics.py
│   └── test_cost_analyzer.py
├── requirements.txt
└── README.md
```

Remember: This tool must help startup founders make data-driven decisions about resource allocation, pricing strategies, and infrastructure scaling while maintaining efficient multi-tenant operations.