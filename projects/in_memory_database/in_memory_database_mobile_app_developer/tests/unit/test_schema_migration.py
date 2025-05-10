"""Unit tests for the schema migration system."""

import pytest
import json
import time
from typing import Dict, Any, List, Tuple

from in_memory_database_mobile_app_developer.database import MobileDBEngine, TableSchema, SchemaField
from in_memory_database_mobile_app_developer.schema import (
    SchemaManager, SchemaMigration, SchemaChange, SchemaChangeType,
    AddFieldOperation, RemoveFieldOperation, ChangeTypeOperation,
    RenameFieldOperation, AddIndexOperation, RemoveIndexOperation
)
from in_memory_database_mobile_app_developer.exceptions import SchemaVersionError


@pytest.fixture
def db_engine() -> MobileDBEngine:
    """Create a database engine for testing."""
    db = MobileDBEngine(max_memory_mb=10)
    
    # Create a test table
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
    
    # Insert some test data
    db.insert(
        table_name="users",
        data={
            "id": "user1",
            "username": "john_doe",
            "email": "john@example.com",
            "age": 30,
            "is_active": True,
        },
    )
    
    db.insert(
        table_name="users",
        data={
            "id": "user2",
            "username": "jane_doe",
            "email": "jane@example.com",
            "age": 25,
            "is_active": True,
        },
    )
    
    return db


@pytest.fixture
def schema_manager(db_engine: MobileDBEngine) -> SchemaManager:
    """Create a schema manager for testing."""
    return SchemaManager(db_engine)


def test_create_migration(schema_manager: SchemaManager) -> None:
    """Test creating a schema migration."""
    # Define changes for the migration
    changes = [
        {
            "type": SchemaChangeType.ADD_FIELD.value,
            "field": "full_name",
            "details": {
                "data_type": "string",
                "nullable": True,
                "default": None,
                "is_indexed": False,
            }
        },
        {
            "type": SchemaChangeType.ADD_INDEX.value,
            "field": "age",
        }
    ]
    
    # Create the migration
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Add full_name field and index on age",
        author="test",
    )
    
    # Check migration properties
    assert migration.table_name == "users"
    assert migration.from_version == 1
    assert migration.to_version == 2
    assert len(migration.changes) == 2
    assert migration.description == "Add full_name field and index on age"
    assert migration.author == "test"
    
    # Check it was added to the migration history
    assert "users" in schema_manager.migrations
    assert len(schema_manager.migrations["users"]) == 1
    assert schema_manager.migrations["users"][0] == migration


def test_apply_migration_add_field(schema_manager: SchemaManager) -> None:
    """Test applying a migration to add a field."""
    # Create a migration to add a field
    changes = [
        {
            "type": SchemaChangeType.ADD_FIELD.value,
            "field": "full_name",
            "details": {
                "data_type": "string",
                "nullable": True,
                "default": None,
                "is_indexed": False,
            }
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Add full_name field",
    )
    
    # Apply the migration
    schema_manager.apply_migration(migration)
    
    # Check the field was added
    schema = schema_manager.db.get_table("users").schema
    assert "full_name" in schema.fields
    assert schema.fields["full_name"].data_type == "string"
    assert schema.fields["full_name"].nullable is True
    
    # Check the schema version was updated
    assert schema.version == 2


def test_apply_migration_remove_field(schema_manager: SchemaManager) -> None:
    """Test applying a migration to remove a field."""
    # Create a migration to remove a field
    changes = [
        {
            "type": SchemaChangeType.REMOVE_FIELD.value,
            "field": "age",
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Remove age field",
    )
    
    # Apply the migration
    schema_manager.apply_migration(migration)
    
    # Check the field was removed
    schema = schema_manager.db.get_table("users").schema
    assert "age" not in schema.fields
    
    # Check the schema version was updated
    assert schema.version == 2
    
    # Check the field was removed from the data
    record = schema_manager.db.get("users", "user1")
    assert "age" not in record


def test_apply_migration_change_type(schema_manager: SchemaManager) -> None:
    """Test applying a migration to change a field type."""
    # Create a migration to change field type
    changes = [
        {
            "type": SchemaChangeType.CHANGE_TYPE.value,
            "field": "age",
            "details": {
                "new_type": "string",
                "old_type": "integer",
                "conversion_function": "lambda x: str(x)",
                "rollback_conversion_function": "lambda x: int(x)",
            }
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Change age to string",
    )
    
    # Apply the migration
    schema_manager.apply_migration(migration)
    
    # Check the field type was changed
    schema = schema_manager.db.get_table("users").schema
    assert schema.fields["age"].data_type == "string"
    
    # Check the schema version was updated
    assert schema.version == 2
    
    # Check the data was converted
    record = schema_manager.db.get("users", "user1")
    assert isinstance(record["age"], str)
    assert record["age"] == "30"


def test_apply_migration_rename_field(schema_manager: SchemaManager) -> None:
    """Test applying a migration to rename a field."""
    # Create a migration to rename a field
    changes = [
        {
            "type": SchemaChangeType.RENAME_FIELD.value,
            "field": "username",
            "details": {
                "new_name": "login_name",
            }
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Rename username to login_name",
    )
    
    # Apply the migration
    schema_manager.apply_migration(migration)
    
    # Check the field was renamed
    schema = schema_manager.db.get_table("users").schema
    assert "username" not in schema.fields
    assert "login_name" in schema.fields
    
    # Check the schema version was updated
    assert schema.version == 2
    
    # Check the field was renamed in the data
    record = schema_manager.db.get("users", "user1")
    assert "username" not in record
    assert "login_name" in record
    assert record["login_name"] == "john_doe"
    
    # Check indexes were updated
    assert "username" not in schema.indexes
    assert "login_name" in schema.indexes


def test_apply_migration_add_index(schema_manager: SchemaManager) -> None:
    """Test applying a migration to add an index."""
    # Create a migration to add an index
    changes = [
        {
            "type": SchemaChangeType.ADD_INDEX.value,
            "field": "age",
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Add index on age",
    )
    
    # Apply the migration
    schema_manager.apply_migration(migration)
    
    # Check the index was added
    schema = schema_manager.db.get_table("users").schema
    assert "age" in schema.indexes
    
    # Check the schema version was updated
    assert schema.version == 2
    
    # Check the index was created in the table
    table = schema_manager.db.get_table("users")
    assert "age" in table.indexes
    
    # Check index contains expected values
    assert 30 in table.indexes["age"]
    assert "user1" in table.indexes["age"][30]


def test_apply_migration_remove_index(schema_manager: SchemaManager) -> None:
    """Test applying a migration to remove an index."""
    # Create a migration to remove an index
    changes = [
        {
            "type": SchemaChangeType.REMOVE_INDEX.value,
            "field": "email",
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Remove index on email",
    )
    
    # Apply the migration
    schema_manager.apply_migration(migration)
    
    # Check the index was removed
    schema = schema_manager.db.get_table("users").schema
    assert "email" not in schema.indexes
    
    # Check the schema version was updated
    assert schema.version == 2
    
    # Check the index was removed from the table
    table = schema_manager.db.get_table("users")
    assert "email" not in table.indexes


def test_apply_multiple_changes(schema_manager: SchemaManager) -> None:
    """Test applying a migration with multiple changes."""
    # Create a migration with multiple changes
    changes = [
        {
            "type": SchemaChangeType.ADD_FIELD.value,
            "field": "full_name",
            "details": {
                "data_type": "string",
                "nullable": True,
                "default": None,
                "is_indexed": False,
            }
        },
        {
            "type": SchemaChangeType.REMOVE_FIELD.value,
            "field": "age",
        },
        {
            "type": SchemaChangeType.RENAME_FIELD.value,
            "field": "username",
            "details": {
                "new_name": "login_name",
            }
        },
        {
            "type": SchemaChangeType.ADD_INDEX.value,
            "field": "is_active",
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Multiple schema changes",
    )
    
    # Apply the migration
    schema_manager.apply_migration(migration)
    
    # Check all changes were applied
    schema = schema_manager.db.get_table("users").schema
    
    # Added field
    assert "full_name" in schema.fields
    
    # Removed field
    assert "age" not in schema.fields
    
    # Renamed field
    assert "username" not in schema.fields
    assert "login_name" in schema.fields
    
    # Added index
    assert "is_active" in schema.indexes
    
    # Check the schema version was updated
    assert schema.version == 2
    
    # Check the data was updated correctly
    record = schema_manager.db.get("users", "user1")
    assert "age" not in record
    assert "username" not in record
    assert "login_name" in record
    assert "full_name" in record  # Added but null
    assert record["login_name"] == "john_doe"


def test_rollback_migration(schema_manager: SchemaManager) -> None:
    """Test rolling back a migration."""
    # First, create and apply a migration to add a field
    changes = [
        {
            "type": SchemaChangeType.ADD_FIELD.value,
            "field": "full_name",
            "details": {
                "data_type": "string",
                "nullable": True,
                "default": None,
                "is_indexed": False,
            }
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Add full_name field",
    )
    
    schema_manager.apply_migration(migration)
    
    # Check the field was added
    schema = schema_manager.db.get_table("users").schema
    assert "full_name" in schema.fields
    assert schema.version == 2
    
    # Now roll back the migration
    schema_manager.rollback_migration("users")
    
    # Check the field was removed
    schema = schema_manager.db.get_table("users").schema
    assert "full_name" not in schema.fields
    
    # Check the schema version was restored
    assert schema.version == 1


def test_rollback_complex_migration(schema_manager: SchemaManager) -> None:
    """Test rolling back a complex migration with multiple changes."""
    # Create a migration with multiple changes
    changes = [
        {
            "type": SchemaChangeType.ADD_FIELD.value,
            "field": "full_name",
            "details": {
                "data_type": "string",
                "nullable": True,
                "default": None,
                "is_indexed": False,
            }
        },
        {
            "type": SchemaChangeType.RENAME_FIELD.value,
            "field": "username",
            "details": {
                "new_name": "login_name",
            }
        },
        {
            "type": SchemaChangeType.ADD_INDEX.value,
            "field": "is_active",
        }
    ]
    
    migration = schema_manager.create_migration(
        table_name="users",
        changes=changes,
        description="Multiple schema changes",
    )
    
    # Apply the migration
    schema_manager.apply_migration(migration)
    
    # Check changes were applied
    schema = schema_manager.db.get_table("users").schema
    assert "full_name" in schema.fields
    assert "username" not in schema.fields
    assert "login_name" in schema.fields
    assert "is_active" in schema.indexes
    
    # Rollback the migration
    schema_manager.rollback_migration("users")
    
    # Check all changes were rolled back
    schema = schema_manager.db.get_table("users").schema
    
    # Added field should be gone
    assert "full_name" not in schema.fields
    
    # Renamed field should be back to original
    assert "username" in schema.fields
    assert "login_name" not in schema.fields
    
    # Added index should be gone
    assert "is_active" not in schema.indexes
    
    # Check the schema version was restored
    assert schema.version == 1
    
    # Check the data was restored correctly
    record = schema_manager.db.get("users", "user1")
    assert "username" in record
    assert "login_name" not in record
    assert record["username"] == "john_doe"


def test_generate_schema_diff(schema_manager: SchemaManager) -> None:
    """Test generating a diff between two schemas."""
    # Get the current schema
    old_schema = schema_manager.db.get_table("users").schema
    
    # Create a new schema with changes
    new_fields = {}
    for name, field in old_schema.fields.items():
        if name != "age":  # Remove age field
            if name == "username":  # Rename username to login_name
                new_field = SchemaField(
                    name="login_name",
                    data_type=field.data_type,
                    nullable=field.nullable,
                    default=field.default,
                    is_primary_key=field.is_primary_key,
                    is_indexed=field.is_indexed,
                )
                new_fields["login_name"] = new_field
            else:
                new_fields[name] = field
    
    # Add a new field
    new_fields["full_name"] = SchemaField(
        name="full_name",
        data_type="string",
        nullable=True,
        default=None,
        is_indexed=False,
        is_primary_key=False,
    )
    
    # Change type of email
    new_fields["email"].data_type = "json"
    
    # Create new schema
    new_schema = TableSchema(
        name=old_schema.name,
        fields=new_fields,
        primary_key=old_schema.primary_key,
        version=old_schema.version + 1,
        indexes=old_schema.indexes.copy(),
    )
    
    # Add new index
    new_schema.indexes.add("full_name")
    
    # Generate diff
    diff = schema_manager.generate_diff(old_schema, new_schema)
    
    # Check diff contains all expected changes
    assert len(diff) >= 4  # At least 4 changes
    
    # Check specific changes
    changes_by_type = {}
    for change in diff:
        if change["type"] not in changes_by_type:
            changes_by_type[change["type"]] = []
        changes_by_type[change["type"]].append(change["field"])
    
    # Check remove field
    assert SchemaChangeType.REMOVE_FIELD.value in changes_by_type
    assert "age" in changes_by_type[SchemaChangeType.REMOVE_FIELD.value]
    
    # Check add field
    assert SchemaChangeType.ADD_FIELD.value in changes_by_type
    assert "full_name" in changes_by_type[SchemaChangeType.ADD_FIELD.value]
    
    # Check add index
    assert SchemaChangeType.ADD_INDEX.value in changes_by_type
    assert "full_name" in changes_by_type[SchemaChangeType.ADD_INDEX.value]
    
    # Check change type
    assert SchemaChangeType.CHANGE_TYPE.value in changes_by_type
    assert "email" in changes_by_type[SchemaChangeType.CHANGE_TYPE.value]


def test_create_migration_from_diff(schema_manager: SchemaManager) -> None:
    """Test creating a migration from a schema diff."""
    # Get the current schema
    old_schema = schema_manager.db.get_table("users").schema
    
    # Create a new schema with changes
    new_fields = {}
    for name, field in old_schema.fields.items():
        new_fields[name] = field
    
    # Add a new field
    new_fields["full_name"] = SchemaField(
        name="full_name",
        data_type="string",
        nullable=True,
        default=None,
        is_indexed=False,
        is_primary_key=False,
    )
    
    # Create new schema
    new_schema = TableSchema(
        name=old_schema.name,
        fields=new_fields,
        primary_key=old_schema.primary_key,
        version=old_schema.version + 1,
        indexes=old_schema.indexes.copy(),
    )
    
    # Create migration from diff
    migration = schema_manager.create_migration_from_diff(
        table_name="users",
        old_schema=old_schema,
        new_schema=new_schema,
        description="Add full_name field",
        author="test",
    )
    
    # Check migration properties
    assert migration.table_name == "users"
    assert migration.from_version == 1
    assert migration.to_version == 2
    assert len(migration.changes) >= 1
    assert migration.description == "Add full_name field"
    assert migration.author == "test"
    
    # Check it contains the expected change
    has_add_field = False
    for change in migration.changes:
        if change.change_type == SchemaChangeType.ADD_FIELD.value and change.field_name == "full_name":
            has_add_field = True
            break
    
    assert has_add_field, "Migration should include adding full_name field"


def test_export_import_migrations(schema_manager: SchemaManager) -> None:
    """Test exporting and importing migrations."""
    # Create a few migrations
    changes1 = [
        {
            "type": SchemaChangeType.ADD_FIELD.value,
            "field": "full_name",
            "details": {
                "data_type": "string",
                "nullable": True,
                "default": None,
                "is_indexed": False,
            }
        }
    ]
    
    migration1 = schema_manager.create_migration(
        table_name="users",
        changes=changes1,
        description="Add full_name field",
        author="test1",
    )
    
    # Apply it to increment the version
    schema_manager.apply_migration(migration1)
    
    # Create a second migration
    changes2 = [
        {
            "type": SchemaChangeType.ADD_FIELD.value,
            "field": "address",
            "details": {
                "data_type": "string",
                "nullable": True,
                "default": None,
                "is_indexed": False,
            }
        }
    ]
    
    migration2 = schema_manager.create_migration(
        table_name="users",
        changes=changes2,
        description="Add address field",
        author="test2",
    )
    
    # Export migrations
    exported_json = schema_manager.export_migrations("users")
    
    # Create a new manager and import migrations
    new_manager = SchemaManager(schema_manager.db)
    new_manager.import_migrations("users", exported_json)
    
    # Check the migrations were imported correctly
    assert len(new_manager.migrations["users"]) == 2
    assert new_manager.migrations["users"][0].description == "Add full_name field"
    assert new_manager.migrations["users"][0].author == "test1"
    assert new_manager.migrations["users"][1].description == "Add address field"
    assert new_manager.migrations["users"][1].author == "test2"
    
    # Check the changes were imported
    assert len(new_manager.migrations["users"][0].changes) == 1
    assert new_manager.migrations["users"][0].changes[0].change_type == SchemaChangeType.ADD_FIELD.value
    assert new_manager.migrations["users"][0].changes[0].field_name == "full_name"