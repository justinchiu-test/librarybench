"""Configuration and fixtures for pytest."""

import pytest
import logging

# Set up logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Reduce log noise from libraries during tests
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# Fixture for marking performance tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "performance: mark test as a performance benchmark")
    config.addinivalue_line("markers", "integration: mark test as an integration test")


# Test utility functions
@pytest.fixture
def get_random_test_data():
    """Get random test data of different sizes and types."""
    import random
    import string
    import json
    
    def _generate(size="small", data_type="text"):
        """Generate random test data."""
        if data_type == "text":
            if size == "small":
                return "".join(random.choice(string.ascii_letters) for _ in range(100))
            elif size == "medium":
                return "".join(random.choice(string.ascii_letters) for _ in range(1000))
            else:  # large
                return "".join(random.choice(string.ascii_letters) for _ in range(10000))
        
        elif data_type == "json":
            if size == "small":
                return {"id": "test", "values": [random.randint(1, 100) for _ in range(10)]}
            elif size == "medium":
                return {"id": "test", "values": [random.randint(1, 100) for _ in range(100)], 
                        "metadata": {f"key_{i}": f"value_{i}" for i in range(100)}}
            else:  # large
                return {"id": "test", "values": [random.randint(1, 100) for _ in range(1000)],
                        "metadata": {f"key_{i}": f"value_{i}" for i in range(1000)},
                        "extra": [{"id": i, "data": "".join(random.choice(string.ascii_letters) for _ in range(100))} 
                                 for i in range(100)]}
        
        elif data_type == "binary":
            if size == "small":
                return bytes([random.randint(0, 255) for _ in range(100)])
            elif size == "medium":
                return bytes([random.randint(0, 255) for _ in range(1000)])
            else:  # large
                return bytes([random.randint(0, 255) for _ in range(10000)])
        
        else:  # numeric
            if size == "small":
                return [random.randint(1, 1000) for _ in range(100)]
            elif size == "medium":
                return [random.randint(1, 1000) for _ in range(1000)]
            else:  # large
                return [random.randint(1, 1000) for _ in range(10000)]
    
    return _generate