"""Basic usage example for MobileSyncDB."""

import os
import asyncio
import logging
from typing import Dict, Any, List

from in_memory_database_mobile_app_developer.api import MobileSyncDB
from in_memory_database_mobile_app_developer.battery import PowerMode, BatteryStatus
from in_memory_database_mobile_app_developer.conflict import ConflictStrategy


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def run_example():
    """Run a basic usage example of MobileSyncDB."""
    # Create storage paths
    server_storage = os.path.join(os.getcwd(), "example_server_db")
    client_storage = os.path.join(os.getcwd(), "example_client_db")
    
    # Create the server database
    logger.info("Creating server database...")
    server_db = MobileSyncDB(
        max_memory_mb=100,
        conflict_strategy=ConflictStrategy.LAST_WRITE_WINS.value,
        compression_profile="balanced",
        power_mode=PowerMode.PERFORMANCE.value,
        storage_path=server_storage,
    )
    
    # Create a table
    logger.info("Creating table...")
    server_db.create_table(
        name="contacts",
        schema={
            "id": "string",
            "name": "string",
            "email": "string",
            "phone": "string",
            "address": "string",
            "is_favorite": "boolean",
            "last_contacted": "string",
            "notes": "string",
        },
        primary_key="id",
        nullable_fields=["phone", "address", "last_contacted", "notes"],
        default_values={"is_favorite": False},
        indexes=["name", "email"],
    )
    
    # Insert some data
    logger.info("Inserting data into server...")
    server_db.insert(
        table_name="contacts",
        data={
            "id": "contact1",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "is_favorite": True,
            "last_contacted": "2023-01-15T10:00:00Z",
            "notes": "Met at conference",
        },
        client_id="server",
    )
    
    server_db.insert(
        table_name="contacts",
        data={
            "id": "contact2",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "555-5678",
            "address": "123 Main St",
            "is_favorite": False,
            "notes": "Referred by John",
        },
        client_id="server",
    )
    
    # Create a client
    logger.info("Creating client...")
    client = server_db.create_client(
        server_url="http://localhost:8080",  # This would be a real URL in production
        client_id="mobile_client_1",
        local_storage_path=client_storage,
        battery_mode=PowerMode.AUTO.value,
    )
    
    # Set up the client database
    logger.info("Setting up client database...")
    client.local_db.create_table(
        name="contacts",
        schema={
            "id": "string",
            "name": "string",
            "email": "string",
            "phone": "string",
            "address": "string",
            "is_favorite": "boolean",
            "last_contacted": "string",
            "notes": "string",
        },
        primary_key="id",
        nullable_fields=["phone", "address", "last_contacted", "notes"],
        default_values={"is_favorite": False},
        indexes=["name", "email"],
    )
    
    # Insert a contact on the client
    logger.info("Inserting data into client...")
    client.insert(
        table_name="contacts",
        data={
            "id": "contact3",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "555-9012",
            "is_favorite": True,
        },
    )
    
    # Update a contact that exists on the server
    logger.info("Updating a contact on the client...")
    client.update(
        table_name="contacts",
        pk="contact2",  # This doesn't exist on client yet, but will after sync
        data={
            "address": "456 Oak Ave",  # Updated address
            "notes": "Moved to new address",
        },
    )
    
    # Simulate changing device battery status
    logger.info("Simulating battery status change...")
    client.local_db.battery_provider.set_status(BatteryStatus.LOW)
    client.local_db.battery_scheduler.update_battery_status()
    logger.info(f"Client power mode adjusted to: {client.get_power_mode()}")
    
    # Perform synchronization
    logger.info("Performing sync...")
    sync_result = await client.sync()
    
    # Show sync results
    logger.info(f"Sync completed with results: {sync_result}")
    
    # Query data on client after sync
    logger.info("Querying contacts on client after sync...")
    all_contacts = client.local_db.get_all("contacts")
    
    for contact in all_contacts:
        logger.info(f"Contact: {contact['name']} ({contact['email']})")
    
    # Clean up
    logger.info("Cleaning up...")
    server_db.shutdown()
    client.shutdown()
    
    if os.path.exists(server_storage):
        import shutil
        shutil.rmtree(server_storage)
    
    if os.path.exists(client_storage):
        import shutil
        shutil.rmtree(client_storage)
    
    logger.info("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_example())