# MobileSyncDB API Reference

## Core Components

### MobileSyncDB Class

The main entry point for the MobileSyncDB library.

```python
from in_memory_database_mobile_app_developer.api import MobileSyncDB

# Initialize the database
db = MobileSyncDB(
    max_memory_mb=100,
    conflict_strategy="last_write_wins",
    compression_profile="balanced",
    power_mode="auto",
    storage_path="./database"
)
```

Parameters:
- `max_memory_mb` (Optional[int]): Maximum memory usage in megabytes.
- `conflict_strategy` (str): Default conflict resolution strategy.
- `compression_profile` (str): Default compression profile.
- `power_mode` (str): Power mode for battery-aware operations.
- `storage_path` (Optional[str]): Path to store database files.

### Table Operations

#### Create Table

```python
db.create_table(
    name="users",
    schema={
        "id": "string",
        "username": "string",
        "email": "string",
        "age": "integer",
        "is_active": "boolean",
    },
    primary_key="id",
    nullable_fields=["age"],
    default_values={"is_active": True},
    indexes=["username", "email"],
)
```

#### Insert Record

```python
record_id = db.insert(
    table_name="users",
    data={
        "id": "user1",
        "username": "john_doe",
        "email": "john@example.com",
        "age": 30,
        "is_active": True,
    },
    client_id="client1",  # Optional: Identify the client making the change
)
```

#### Get Record

```python
record = db.get(table_name="users", pk="user1")
```

#### Update Record

```python
updated_record = db.update(
    table_name="users",
    pk="user1",
    data={"age": 31, "username": "johnny_doe"},
    client_id="client1",  # Optional: Identify the client making the change
)
```

#### Delete Record

```python
db.delete(
    table_name="users",
    pk="user1",
    client_id="client1",  # Optional: Identify the client making the change
)
```

#### Find Records

```python
# Find by conditions
matching_records = db.find(
    table_name="users",
    conditions={"is_active": True},
    limit=10,  # Optional: Limit the number of results
    offset=0,  # Optional: Offset for pagination
)

# Get all records
all_records = db.get_all(
    table_name="users",
    limit=100,  # Optional: Limit the number of results
    offset=0,  # Optional: Offset for pagination
)

# Count records
count = db.count(
    table_name="users",
    conditions={"is_active": True},  # Optional: Count only matching records
)
```

### Synchronization

#### Server-Side

```python
# Create a sync server
sync_server = db.create_sync_server(
    port=8080,
    host="0.0.0.0",
    compression_level="balanced",
    conflict_strategy="last_write_wins",
    session_timeout=3600,
    batch_size=100,
)

# Start the server
sync_server.start()

# Stop the server
sync_server.stop()
```

#### Client-Side

```python
# Create a client
client = db.create_client(
    server_url="http://localhost:8080",
    client_id="mobile_device_123",
    local_storage_path="./local_db",
    battery_mode="auto",
)

# Perform synchronization
sync_result = await client.sync()

# Schedule periodic sync
sync_task_id = client.schedule_periodic_sync(
    tables=["users", "contacts"],  # Optional: Specific tables to sync
    callback=lambda result: print(f"Sync completed: {result}"),  # Optional: Callback function
)

# Stop periodic sync
client.stop_periodic_sync(sync_task_id)
```

### Schema Migration

```python
# Create a schema migration
migration = db.create_schema_migration(
    table_name="users",
    changes=[
        {
            "type": "add_field",
            "field": "full_name",
            "details": {
                "data_type": "string",
                "nullable": True,
                "default": None,
                "is_indexed": False,
            }
        },
        {
            "type": "add_index",
            "field": "age",
        }
    ],
    description="Add full_name field and index on age",
    author="developer_name",
)

# Apply a schema migration
db.apply_schema_migration(
    table_name="users",
    migration_index=-1,  # Apply the latest migration
)

# Roll back a schema migration
db.rollback_schema_migration(table_name="users")
```

### Conflict Resolution

```python
# Set conflict resolution strategy
db.set_conflict_strategy(
    strategy="last_write_wins",  # Global default
)

db.set_conflict_strategy(
    strategy="server_wins",
    table_name="users",  # Table-specific
)

db.set_conflict_strategy(
    strategy="client_wins",
    table_name="users",
    field_name="email",  # Field-specific
)

# Get conflicts
conflicts = db.get_conflicts(
    table_name="users",  # Optional: Filter by table
    record_id="user1",   # Optional: Filter by record
    resolved=False,      # Optional: Filter by resolution status
)

# Resolve a conflict
db.resolve_conflict(
    table_name="users",
    record_id="user1",
    strategy="merge",  # Optional: Strategy to use
    manual_resolution={  # Optional: Manual resolution data
        "id": "user1",
        "username": "merged_username",
        "email": "merged@example.com",
    },
    resolved_by="user",  # Optional: Who resolved the conflict
)
```

### Battery-Aware Operations

```python
# Set power mode
db.set_power_mode("battery_saver")

# Get current power mode
current_mode = db.get_power_mode()

# Set battery status for testing
db.set_battery_status("low")

# Clear cache
db.clear_cache()

# Shutdown
db.shutdown()
```

## Enumerations

### ColumnType
- `STRING`: String values
- `INTEGER`: Integer values
- `FLOAT`: Floating-point values
- `BOOLEAN`: Boolean values
- `DATETIME`: Date and time values
- `JSON`: JSON-compatible values
- `BINARY`: Binary data

### ConflictStrategy
- `LAST_WRITE_WINS`: Latest update wins
- `SERVER_WINS`: Server version always wins
- `CLIENT_WINS`: Client version always wins
- `MANUAL`: Require manual resolution
- `CLIENT_PRIORITY`: Use client priority settings
- `MERGE`: Apply field-specific merge strategies

### PowerMode
- `PERFORMANCE`: Maximum performance, no battery optimizations
- `BALANCED`: Balance between performance and battery life
- `BATTERY_SAVER`: Prioritize battery life over performance
- `EXTREME_SAVER`: Maximize battery life, minimum operations
- `AUTO`: Automatically adjust based on battery status

### BatteryStatus
- `FULL`: Battery is full or device is plugged in
- `HIGH`: Battery level is high (> 70%)
- `MEDIUM`: Battery level is medium (30-70%)
- `LOW`: Battery level is low (10-30%)
- `CRITICAL`: Battery level is critical (< 10%)
- `UNKNOWN`: Battery status is unknown

### SchemaChangeType
- `ADD_FIELD`: Add a new field
- `REMOVE_FIELD`: Remove an existing field
- `CHANGE_TYPE`: Change a field's data type
- `ADD_INDEX`: Add an index to a field
- `REMOVE_INDEX`: Remove an index from a field
- `RENAME_FIELD`: Rename a field