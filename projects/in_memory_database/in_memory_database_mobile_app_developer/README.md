# MobileSyncDB: In-Memory Database for Mobile App Backend Synchronization

MobileSyncDB is a specialized in-memory database designed for mobile app backend infrastructure, focusing on efficient data synchronization between server and mobile clients with intermittent connectivity.

## Features

- **Differential Sync Protocol**: Only transmit changed data since last sync
- **Conflict Resolution Strategies**: Configurable approaches for handling concurrent modifications
- **Payload Compression**: Data type-specific algorithms optimized for mobile data transfer
- **Automatic Schema Migration**: Version-controlled schema changes with backwards compatibility
- **Battery-Aware Operation**: Configurable performance profiles based on device power status

## Installation

```bash
pip install in_memory_database_mobile_app_developer
```

Or with UV:

```bash
uv pip install in_memory_database_mobile_app_developer
```

## Quick Start

```python
from in_memory_database_mobile_app_developer import MobileSyncDB

# Initialize server database
db = MobileSyncDB(max_memory_mb=100)

# Create a table
db.create_table(
    "users",
    {
        "id": "string",
        "username": "string",
        "email": "string",
        "last_login": "datetime",
        "preferences": "json",
    },
    primary_key="id"
)

# Insert data
db.insert("users", {
    "id": "user123",
    "username": "miguel_dev",
    "email": "miguel@example.com",
    "last_login": "2023-04-01T12:00:00Z",
    "preferences": {"theme": "dark", "notifications": True}
})

# Initialize sync server
sync_server = db.create_sync_server(
    port=8080,
    compression_level="balanced",
    conflict_strategy="last_write_wins"
)

# Start server
sync_server.start()
```

Client-side usage:

```python
from in_memory_database_mobile_app_developer import MobileSyncClient

# Initialize client
client = MobileSyncClient(
    server_url="http://localhost:8080",
    client_id="mobile_device_123",
    local_storage_path="./local_db",
    battery_mode="auto"  # Adjusts sync behavior based on device battery status
)

# Perform initial sync
await client.sync()

# Make local changes
client.update("users", "user123", {"preferences": {"theme": "light"}})

# Sync changes back to server
await client.sync()
```

## Development

1. Clone the repository
2. Set up the development environment:

```bash
uv sync
```

3. Run tests:

```bash
uv run pytest
```

## License

MIT