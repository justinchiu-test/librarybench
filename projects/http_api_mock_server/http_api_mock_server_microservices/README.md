# PyMockAPI - Microservices Mesh Mock Server

A specialized HTTP API mock server designed for microservices developers to simulate complex service mesh environments. This implementation focuses on mocking multiple interdependent services, service discovery patterns, and distributed system behaviors to enable comprehensive testing of microservices architectures.

## Features

### 1. Service Registry & Discovery
- Dynamic service registration and deregistration
- Health checking with configurable intervals
- Service tagging and metadata support
- Query services by name, tags, or health status

### 2. Dependency Management
- Define and manage complex service dependency graphs
- Circular dependency detection
- Topological ordering for deployment sequences
- Critical service identification

### 3. Circuit Breaker Engine
- Per-endpoint circuit breaker configuration
- Automatic state transitions (CLOSED → OPEN → HALF_OPEN)
- Configurable failure thresholds and timeout periods
- Manual circuit breaker control

### 4. Distributed Tracing
- W3C Trace Context compliant
- Automatic span creation and correlation
- Service dependency extraction from traces
- Trace visualization as graph structures

### 5. Chaos Engineering
- Multiple chaos scenarios:
  - Service outages
  - Network latency injection
  - Network partitions
  - Response errors
  - Cascade failures
- Controlled failure injection with duration support
- Real-time chaos metrics

## Installation

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install in development mode
uv pip install -e .

# Install test dependencies
uv pip install -e ".[dev]"
```

## Usage

### Starting the Server

```python
from pymockapi.mock_server import MockServer

# Create and start server
server = MockServer(host="127.0.0.1", port=8080)
await server.start()
```

Or run directly:

```bash
python -m pymockapi
```

### Service Registration

```python
import aiohttp

# Register a service
async with aiohttp.ClientSession() as session:
    service_data = {
        "service_id": "user-service",
        "name": "User Service",
        "endpoint": "/api/users",
        "port": 8081,
        "tags": ["production", "critical"]
    }
    
    async with session.post("http://localhost:8080/registry/register", 
                          json=service_data) as resp:
        result = await resp.json()
```

### Defining Dependencies

```python
# Define service dependency
dependency_data = {
    "from_service": "api-gateway",
    "to_service": "user-service",
    "required": True,
    "timeout_ms": 5000,
    "circuit_breaker_enabled": True
}

async with session.post("http://localhost:8080/dependencies", 
                      json=dependency_data) as resp:
    result = await resp.json()
```

### Configuring Mock Responses

```python
# Configure mock response for a service
mock_config = {
    "path": "users",
    "status": 200,
    "body": {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    },
    "headers": {"X-Total-Count": "2"},
    "delay_ms": 100
}

async with session.post("http://localhost:8080/mock/user-service/configure", 
                      json=mock_config) as resp:
    result = await resp.json()
```

### Creating Chaos Events

```python
# Simulate cascade failure
chaos_data = {
    "initial_service": "database",
    "failure_probability": 0.8,
    "max_depth": 3
}

async with session.post("http://localhost:8080/chaos/cascade-failure", 
                      json=chaos_data) as resp:
    event = await resp.json()
    event_id = event["event_id"]

# Stop chaos event
async with session.delete(f"http://localhost:8080/chaos/events/{event_id}") as resp:
    result = await resp.json()
```

### Distributed Tracing

```python
# Make request with trace propagation
headers = {"traceparent": "00-0123456789abcdef0123456789abcdef-0123456789abcdef-01"}

async with session.get("http://localhost:8080/mock/user-service/users", 
                     headers=headers) as resp:
    # Response includes trace propagation
    new_traceparent = resp.headers["traceparent"]
```

## API Endpoints

### Service Registry
- `POST /registry/register` - Register a new service
- `DELETE /registry/{service_id}` - Deregister a service
- `GET /registry/{service_id}` - Get service details
- `GET /registry` - List all services
- `PUT /registry/{service_id}/heartbeat` - Update service heartbeat

### Dependency Management
- `POST /dependencies` - Add service dependency
- `DELETE /dependencies/{from_service}/{to_service}` - Remove dependency
- `GET /dependencies/{service_id}` - Get service dependencies
- `GET /dependencies/graph` - Get complete dependency graph

### Circuit Breakers
- `POST /circuit-breakers` - Register circuit breaker
- `GET /circuit-breakers` - Get all circuit breaker states
- `POST /circuit-breakers/{service_id}/{endpoint}/reset` - Reset circuit breaker

### Tracing
- `GET /traces/{trace_id}` - Get trace information
- `GET /traces` - Get trace statistics

### Chaos Engineering
- `POST /chaos/events` - Create chaos event
- `DELETE /chaos/events/{event_id}` - Stop chaos event
- `GET /chaos/events` - List active chaos events
- `POST /chaos/cascade-failure` - Simulate cascade failure

### Mock Services
- `POST /mock/{service_id}/configure` - Configure mock response
- `* /mock/{service_id}/{path}` - Handle mock service requests

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pymockapi

# Run specific test module
pytest tests/test_service_registry.py

# Run integration tests only
pytest tests/test_integration.py

# Generate JSON report (required for validation)
pytest --json-report --json-report-file=pytest_results.json
```

## Architecture

The system is composed of several core components:

1. **Service Registry**: Maintains service information and health status
2. **Dependency Manager**: Manages service relationships using a directed graph
3. **Circuit Breaker Engine**: Implements resilience patterns for each service endpoint
4. **Tracing System**: Handles distributed trace context propagation
5. **Chaos Controller**: Orchestrates failure injection scenarios
6. **Mock Server**: HTTP server integrating all components

## Performance

The system is designed to handle:
- 50+ mock services simultaneously
- Service discovery updates within 100ms
- Circuit breaker state changes within 50ms
- Trace header processing with <5ms overhead
- 1000+ requests/second across all services

## Example: Microservices Testing

```python
# Set up a typical microservices architecture
services = [
    {"service_id": "frontend", "name": "Frontend", "port": 3000},
    {"service_id": "api-gateway", "name": "API Gateway", "port": 8080},
    {"service_id": "user-service", "name": "User Service", "port": 8081},
    {"service_id": "order-service", "name": "Order Service", "port": 8082},
    {"service_id": "database", "name": "Database", "port": 5432}
]

# Register all services
for service in services:
    await register_service(service)

# Define dependencies
dependencies = [
    {"from": "frontend", "to": "api-gateway"},
    {"from": "api-gateway", "to": "user-service"},
    {"from": "api-gateway", "to": "order-service"},
    {"from": "user-service", "to": "database"},
    {"from": "order-service", "to": "database"}
]

for dep in dependencies:
    await add_dependency(dep)

# Test cascade failure from database
await simulate_cascade_failure("database", failure_probability=0.7)
```

## License

This project is part of the PyMockAPI suite for testing microservices architectures.