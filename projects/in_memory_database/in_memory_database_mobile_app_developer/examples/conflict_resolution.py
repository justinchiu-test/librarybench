"""Example demonstrating conflict resolution in MobileSyncDB."""

import os
import asyncio
import logging
from typing import Dict, Any, List

from in_memory_database_mobile_app_developer.api import MobileSyncDB
from in_memory_database_mobile_app_developer.conflict import ConflictStrategy


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def run_conflict_example():
    """Run an example demonstrating conflict resolution."""
    # Create the database
    db = MobileSyncDB()
    
    # Create a table
    db.create_table(
        name="documents",
        schema={
            "id": "string",
            "title": "string",
            "content": "string",
            "author": "string",
            "version": "integer",
            "last_modified": "string",
            "tags": "json",
        },
        primary_key="id",
        nullable_fields=["tags"],
        indexes=["author"],
    )
    
    # Insert a document
    db.insert(
        table_name="documents",
        data={
            "id": "doc1",
            "title": "Original Title",
            "content": "Original content here.",
            "author": "Alice",
            "version": 1,
            "last_modified": "2023-01-01T12:00:00Z",
            "tags": ["draft", "important"],
        },
        client_id="server",
    )
    
    # Create a conflict resolver for demo
    resolver = db.conflict_resolver
    
    # Set up different field-specific strategies
    logger.info("Setting up field-specific conflict resolution strategies...")
    
    # Title: Server wins
    resolver.set_field_strategy(
        table_name="documents",
        field_name="title",
        strategy=ConflictStrategy.SERVER_WINS.value,
        description="Server always has the authoritative title",
    )
    
    # Content: Client wins
    resolver.set_field_strategy(
        table_name="documents",
        field_name="content",
        strategy=ConflictStrategy.CLIENT_WINS.value,
        description="Client edits to content are preserved",
    )
    
    # Version: Custom merge to increment
    def merge_version(server_value, client_value):
        return max(server_value, client_value) + 1
    
    resolver.set_field_strategy(
        table_name="documents",
        field_name="version",
        strategy=merge_version,
        description="Always increment version on conflict",
    )
    
    # Tags: Custom merge to combine
    def merge_tags(server_tags, client_tags):
        if not server_tags:
            return client_tags
        if not client_tags:
            return server_tags
        # Combine tags without duplicates
        return list(set(server_tags + client_tags))
    
    resolver.set_field_strategy(
        table_name="documents",
        field_name="tags",
        strategy=merge_tags,
        description="Combine tags from both versions",
    )
    
    # Simulate server-side update
    logger.info("Simulating server-side update...")
    db.update(
        table_name="documents",
        pk="doc1",
        data={
            "title": "Server Updated Title",
            "content": "Content updated by server.",
            "version": 2,
            "last_modified": "2023-01-02T12:00:00Z",
            "tags": ["draft", "reviewed"],
        },
        client_id="server",
    )
    
    # Simulate a client update to the original version
    # (This creates a conflict because it's based on the original)
    logger.info("Simulating client-side update (creating conflict)...")
    client_data = {
        "id": "doc1",
        "title": "Client Updated Title",
        "content": "Content updated by client.",
        "author": "Alice (edited)",
        "version": 2,
        "last_modified": "2023-01-02T13:00:00Z",  # Client edit is newer
        "tags": ["draft", "client-edited"],
    }
    
    # Get the server's version
    server_record = db.get("documents", "doc1")
    logger.info(f"Server version: {server_record}")
    
    # Detect and resolve the conflict
    logger.info("Detecting and resolving conflict...")
    
    # Get server and client versions for the same record
    conflict = db.conflict_detector.detect_conflict(
        table_name="documents",
        record_id="doc1",
        server_record=db.db.get_table("documents").get_with_metadata("doc1"),
        client_record=db.conflict_detector.resolver._apply_client_wins(
            db.conflict_detector.create_client_record("doc1", client_data)
        ),
    )
    
    if conflict:
        logger.info(f"Conflict detected with fields: {conflict.field_conflicts}")
        
        # Resolve using the merge strategy
        resolved = db.conflict_detector.resolve_conflict(
            conflict=conflict,
            strategy=ConflictStrategy.MERGE.value,
        )
        
        if resolved:
            logger.info("Conflict resolved successfully!")
            logger.info(f"Resolved document: {resolved.data}")
            
            # Check that each field was resolved according to its strategy
            logger.info("Checking resolution results:")
            logger.info(f"Title (server wins): {resolved.data['title'] == server_record['title']}")
            logger.info(f"Content (client wins): {resolved.data['content'] == client_data['content']}")
            logger.info(f"Version (custom merge): {resolved.data['version'] == 3}")  # Should be incremented
            
            # Check combined tags
            combined_tags = set(server_record['tags'] + client_data['tags'])
            logger.info(f"Tags (combined): {set(resolved.data['tags']) == combined_tags}")
        else:
            logger.error("Failed to resolve conflict!")
    else:
        logger.info("No conflict detected.")
    
    logger.info("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_conflict_example())