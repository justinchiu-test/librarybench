"""Schema version management and migration for MobileSyncDB."""

import copy
import json
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple, Callable, Union

from pydantic import BaseModel, Field

from .database import TableSchema, SchemaField, MobileDBEngine, Table
from .exceptions import SchemaVersionError


class SchemaChangeType(Enum):
    """Types of schema changes."""

    ADD_FIELD = "add_field"
    REMOVE_FIELD = "remove_field"
    CHANGE_TYPE = "change_type"
    ADD_INDEX = "add_index"
    REMOVE_INDEX = "remove_index"
    RENAME_FIELD = "rename_field"


class SchemaChange(BaseModel):
    """Represents a single change to a schema."""

    change_type: str
    field_name: str
    details: Dict[str, Any] = Field(default_factory=dict)


class SchemaMigration(BaseModel):
    """Represents a migration between schema versions."""

    table_name: str
    from_version: int
    to_version: int
    changes: List[SchemaChange]
    created_at: float = Field(default_factory=time.time)
    description: Optional[str] = None
    author: Optional[str] = None


class MigrationOperation:
    """Base class for migration operations."""

    def __init__(self, migration: SchemaMigration):
        """Initialize a migration operation."""
        self.migration = migration

    def apply(self, db: MobileDBEngine) -> None:
        """Apply the migration to the database."""
        raise NotImplementedError("Subclasses must implement this method")

    def rollback(self, db: MobileDBEngine) -> None:
        """Roll back the migration."""
        raise NotImplementedError("Subclasses must implement this method")


class AddFieldOperation(MigrationOperation):
    """Operation to add a field to a table schema."""

    def apply(self, db: MobileDBEngine) -> None:
        """Apply the operation to add a field."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.ADD_FIELD.value:
                continue
            
            field_name = change.field_name
            details = change.details
            
            # Create the new field
            new_field = SchemaField(
                name=field_name,
                data_type=details["data_type"],
                nullable=details.get("nullable", True),
                default=details.get("default"),
                is_indexed=details.get("is_indexed", False),
                is_primary_key=False,  # Can't add a primary key in a migration
            )
            
            # Add the field to the schema
            table.schema.fields[field_name] = new_field
            
            # Create index if needed
            if new_field.is_indexed:
                table.schema.indexes.add(field_name)
                table._create_index(field_name)
                
            # Update the schema version
            table.schema.version = self.migration.to_version

    def rollback(self, db: MobileDBEngine) -> None:
        """Roll back the operation to remove added fields."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.ADD_FIELD.value:
                continue
            
            field_name = change.field_name
            
            # Remove index if it exists
            if field_name in table.schema.indexes:
                table._drop_index(field_name)
                table.schema.indexes.remove(field_name)
            
            # Remove the field from the schema
            if field_name in table.schema.fields:
                del table.schema.fields[field_name]
            
            # Remove the field from all records
            for pk, record in table.data.items():
                if field_name in record.data:
                    del record.data[field_name]
        
        # Update the schema version
        table.schema.version = self.migration.from_version


class RemoveFieldOperation(MigrationOperation):
    """Operation to remove a field from a table schema."""

    def apply(self, db: MobileDBEngine) -> None:
        """Apply the operation to remove a field."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.REMOVE_FIELD.value:
                continue
            
            field_name = change.field_name
            
            # Can't remove primary key
            if field_name == table.schema.primary_key:
                raise SchemaVersionError(f"Cannot remove primary key field '{field_name}'")
            
            # Remove index if it exists
            if field_name in table.schema.indexes:
                table._drop_index(field_name)
                table.schema.indexes.remove(field_name)
            
            # Store the field definition in details for potential rollback
            if field_name in table.schema.fields:
                field = table.schema.fields[field_name]
                change.details["data_type"] = field.data_type
                change.details["nullable"] = field.nullable
                change.details["default"] = field.default
                change.details["is_indexed"] = field.is_indexed
                
                # Remove the field from the schema
                del table.schema.fields[field_name]
            
            # Remove the field from all records
            for pk, record in table.data.items():
                if field_name in record.data:
                    del record.data[field_name]
        
        # Update the schema version
        table.schema.version = self.migration.to_version

    def rollback(self, db: MobileDBEngine) -> None:
        """Roll back the operation to add removed fields back."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.REMOVE_FIELD.value:
                continue
            
            field_name = change.field_name
            details = change.details
            
            # Create the field
            new_field = SchemaField(
                name=field_name,
                data_type=details["data_type"],
                nullable=details.get("nullable", True),
                default=details.get("default"),
                is_indexed=details.get("is_indexed", False),
                is_primary_key=False,
            )
            
            # Add the field to the schema
            table.schema.fields[field_name] = new_field
            
            # Create index if needed
            if new_field.is_indexed:
                table.schema.indexes.add(field_name)
                table._create_index(field_name)
        
        # Update the schema version
        table.schema.version = self.migration.from_version


class ChangeTypeOperation(MigrationOperation):
    """Operation to change the type of a field."""

    def apply(self, db: MobileDBEngine) -> None:
        """Apply the operation to change a field's type."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.CHANGE_TYPE.value:
                continue
            
            field_name = change.field_name
            new_type = change.details["new_type"]
            conversion_fn = change.details.get("conversion_function")
            
            # Can't change type of primary key to incompatible type
            if field_name == table.schema.primary_key:
                # Ensure new type is compatible with primary key
                if new_type not in ["string", "integer"]:
                    raise SchemaVersionError(
                        f"Cannot change primary key type to '{new_type}'. "
                        "Primary keys must be string or integer."
                    )
            
            # Store the original type for potential rollback
            if field_name in table.schema.fields:
                change.details["old_type"] = table.schema.fields[field_name].data_type
                
                # Update the field type
                table.schema.fields[field_name].data_type = new_type
            
            # Convert values in all records
            for pk, record in table.data.items():
                if field_name in record.data:
                    # Apply conversion function if provided
                    if conversion_fn:
                        record.data[field_name] = eval(conversion_fn)(record.data[field_name])
        
        # Update the schema version
        table.schema.version = self.migration.to_version

    def rollback(self, db: MobileDBEngine) -> None:
        """Roll back the operation to restore the original type."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.CHANGE_TYPE.value:
                continue
            
            field_name = change.field_name
            old_type = change.details.get("old_type")
            rollback_conversion_fn = change.details.get("rollback_conversion_function")
            
            if field_name in table.schema.fields and old_type:
                # Restore the original type
                table.schema.fields[field_name].data_type = old_type
                
                # Convert values back in all records
                for pk, record in table.data.items():
                    if field_name in record.data and rollback_conversion_fn:
                        record.data[field_name] = eval(rollback_conversion_fn)(record.data[field_name])
        
        # Update the schema version
        table.schema.version = self.migration.from_version


class RenameFieldOperation(MigrationOperation):
    """Operation to rename a field."""

    def apply(self, db: MobileDBEngine) -> None:
        """Apply the operation to rename a field."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.RENAME_FIELD.value:
                continue
            
            old_name = change.field_name
            new_name = change.details["new_name"]
            
            # Can't rename primary key
            if old_name == table.schema.primary_key:
                raise SchemaVersionError(f"Cannot rename primary key field '{old_name}'")
            
            # Check if the field exists
            if old_name not in table.schema.fields:
                raise SchemaVersionError(f"Field '{old_name}' does not exist")
                
            # Check if the new name already exists
            if new_name in table.schema.fields:
                raise SchemaVersionError(f"Field '{new_name}' already exists")
            
            # Rename the field in the schema
            field = table.schema.fields[old_name]
            table.schema.fields[new_name] = field
            table.schema.fields[new_name].name = new_name
            del table.schema.fields[old_name]
            
            # Update indexes
            if old_name in table.schema.indexes:
                table.schema.indexes.remove(old_name)
                table.schema.indexes.add(new_name)
                
                # Create a new index and populate it
                if old_name in table.indexes:
                    table.indexes[new_name] = table.indexes[old_name]
                    del table.indexes[old_name]
            
            # Rename the field in all records
            for pk, record in table.data.items():
                if old_name in record.data:
                    record.data[new_name] = record.data[old_name]
                    del record.data[old_name]
        
        # Update the schema version
        table.schema.version = self.migration.to_version

    def rollback(self, db: MobileDBEngine) -> None:
        """Roll back the operation to restore the original field name."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change in reverse
        for change in reversed(self.migration.changes):
            if change.change_type != SchemaChangeType.RENAME_FIELD.value:
                continue
            
            old_name = change.field_name  # This is the original name
            new_name = change.details["new_name"]  # This is the new name we want to revert
            
            # Rename the field back in the schema
            if new_name in table.schema.fields:
                field = table.schema.fields[new_name]
                table.schema.fields[old_name] = field
                table.schema.fields[old_name].name = old_name
                del table.schema.fields[new_name]
                
                # Update indexes
                if new_name in table.schema.indexes:
                    table.schema.indexes.remove(new_name)
                    table.schema.indexes.add(old_name)
                    
                    # Update the index
                    if new_name in table.indexes:
                        table.indexes[old_name] = table.indexes[new_name]
                        del table.indexes[new_name]
                
                # Rename the field in all records
                for pk, record in table.data.items():
                    if new_name in record.data:
                        record.data[old_name] = record.data[new_name]
                        del record.data[new_name]
        
        # Update the schema version
        table.schema.version = self.migration.from_version


class AddIndexOperation(MigrationOperation):
    """Operation to add an index to a field."""

    def apply(self, db: MobileDBEngine) -> None:
        """Apply the operation to add an index."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.ADD_INDEX.value:
                continue
            
            field_name = change.field_name
            
            # Check if the field exists
            if field_name not in table.schema.fields:
                raise SchemaVersionError(f"Field '{field_name}' does not exist")
            
            # Add the index if it doesn't already exist
            if field_name not in table.schema.indexes:
                table._create_index(field_name)
                table.schema.indexes.add(field_name)
                table.schema.fields[field_name].is_indexed = True
        
        # Update the schema version
        table.schema.version = self.migration.to_version

    def rollback(self, db: MobileDBEngine) -> None:
        """Roll back the operation to remove added indexes."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.ADD_INDEX.value:
                continue
            
            field_name = change.field_name
            
            # Skip if the field is a primary key
            if field_name == table.schema.primary_key:
                continue
            
            # Remove the index if it exists
            if field_name in table.schema.indexes:
                table._drop_index(field_name)
                table.schema.indexes.remove(field_name)
                table.schema.fields[field_name].is_indexed = False
        
        # Update the schema version
        table.schema.version = self.migration.from_version


class RemoveIndexOperation(MigrationOperation):
    """Operation to remove an index from a field."""

    def apply(self, db: MobileDBEngine) -> None:
        """Apply the operation to remove an index."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.REMOVE_INDEX.value:
                continue
            
            field_name = change.field_name
            
            # Skip if the field is a primary key
            if field_name == table.schema.primary_key:
                continue
            
            # Remove the index if it exists
            if field_name in table.schema.indexes:
                table._drop_index(field_name)
                table.schema.indexes.remove(field_name)
                table.schema.fields[field_name].is_indexed = False
        
        # Update the schema version
        table.schema.version = self.migration.to_version

    def rollback(self, db: MobileDBEngine) -> None:
        """Roll back the operation to restore removed indexes."""
        table_name = self.migration.table_name
        table = db.get_table(table_name)
        
        # Process each change
        for change in self.migration.changes:
            if change.change_type != SchemaChangeType.REMOVE_INDEX.value:
                continue
            
            field_name = change.field_name
            
            # Skip if the field is a primary key or doesn't exist
            if field_name not in table.schema.fields:
                continue
            
            # Add the index if it doesn't already exist
            if field_name not in table.schema.indexes:
                table._create_index(field_name)
                table.schema.indexes.add(field_name)
                table.schema.fields[field_name].is_indexed = True
        
        # Update the schema version
        table.schema.version = self.migration.from_version


class SchemaManager:
    """Manages schema versions and migrations."""

    def __init__(self, db: MobileDBEngine):
        """Initialize the schema manager."""
        self.db = db
        self.migrations: Dict[str, List[SchemaMigration]] = {}
        
        # Operation handlers for different change types
        self.operation_handlers = {
            SchemaChangeType.ADD_FIELD.value: AddFieldOperation,
            SchemaChangeType.REMOVE_FIELD.value: RemoveFieldOperation,
            SchemaChangeType.CHANGE_TYPE.value: ChangeTypeOperation,
            SchemaChangeType.RENAME_FIELD.value: RenameFieldOperation,
            SchemaChangeType.ADD_INDEX.value: AddIndexOperation,
            SchemaChangeType.REMOVE_INDEX.value: RemoveIndexOperation,
        }
        
        # Initialize migration history for existing tables
        for table_name in db.tables:
            self.migrations[table_name] = []

    def get_current_version(self, table_name: str) -> int:
        """Get the current schema version for a table."""
        table = self.db.get_table(table_name)
        return table.schema.version

    def create_migration(
        self,
        table_name: str,
        changes: List[Dict[str, Any]],
        description: Optional[str] = None,
        author: Optional[str] = None,
    ) -> SchemaMigration:
        """Create a new schema migration."""
        if table_name not in self.db.tables:
            raise SchemaVersionError(f"Table '{table_name}' does not exist")
        
        # Get the current version
        current_version = self.get_current_version(table_name)
        next_version = current_version + 1
        
        # Convert raw changes to SchemaChange objects
        schema_changes = []
        for change_dict in changes:
            schema_changes.append(SchemaChange(
                change_type=change_dict["type"],
                field_name=change_dict["field"],
                details=change_dict.get("details", {}),
            ))
        
        # Create the migration
        migration = SchemaMigration(
            table_name=table_name,
            from_version=current_version,
            to_version=next_version,
            changes=schema_changes,
            created_at=time.time(),
            description=description,
            author=author,
        )
        
        # Add to migration history
        if table_name not in self.migrations:
            self.migrations[table_name] = []
        
        self.migrations[table_name].append(migration)
        
        return migration

    def _get_operation_for_change_type(
        self,
        change_type: str,
        migration: SchemaMigration,
    ) -> MigrationOperation:
        """Get the appropriate operation handler for a change type."""
        if change_type not in self.operation_handlers:
            raise SchemaVersionError(f"Unsupported change type: {change_type}")
        
        return self.operation_handlers[change_type](migration)

    def _validate_migration(self, migration: SchemaMigration) -> None:
        """Validate that a migration can be applied."""
        table_name = migration.table_name
        
        # Check that the table exists
        if table_name not in self.db.tables:
            raise SchemaVersionError(f"Table '{table_name}' does not exist")
        
        # Check that the from_version matches the current version
        current_version = self.get_current_version(table_name)
        if migration.from_version != current_version:
            raise SchemaVersionError(
                f"Migration from version {migration.from_version} to {migration.to_version} "
                f"cannot be applied. Current version is {current_version}."
            )
        
        # Validate each change
        for change in migration.changes:
            if change.change_type not in self.operation_handlers:
                raise SchemaVersionError(f"Unsupported change type: {change.change_type}")

    def apply_migration(self, migration: SchemaMigration) -> None:
        """Apply a migration to the database."""
        # Validate the migration
        self._validate_migration(migration)
        
        # Group changes by type
        changes_by_type: Dict[str, List[SchemaChange]] = {}
        for change in migration.changes:
            if change.change_type not in changes_by_type:
                changes_by_type[change.change_type] = []
            changes_by_type[change.change_type].append(change)
        
        # Apply changes in the correct order
        # Order matters: add fields before rename, rename before change type, etc.
        change_order = [
            SchemaChangeType.REMOVE_INDEX.value,
            SchemaChangeType.ADD_FIELD.value,
            SchemaChangeType.RENAME_FIELD.value,
            SchemaChangeType.CHANGE_TYPE.value,
            SchemaChangeType.REMOVE_FIELD.value,
            SchemaChangeType.ADD_INDEX.value,
        ]
        
        for change_type in change_order:
            if change_type in changes_by_type:
                # Create a new migration with just this type of changes
                type_migration = SchemaMigration(
                    table_name=migration.table_name,
                    from_version=migration.from_version,
                    to_version=migration.to_version,
                    changes=changes_by_type[change_type],
                )
                
                # Get and apply the appropriate operation
                operation = self._get_operation_for_change_type(change_type, type_migration)
                operation.apply(self.db)

    def rollback_migration(self, table_name: str) -> None:
        """Roll back the latest migration for a table."""
        if table_name not in self.migrations or not self.migrations[table_name]:
            raise SchemaVersionError(f"No migrations to roll back for table '{table_name}'")
        
        # Get the latest migration
        migration = self.migrations[table_name][-1]
        
        # Check that we're not trying to roll back the initial schema
        if migration.from_version == 0:
            raise SchemaVersionError("Cannot roll back initial schema creation")
        
        # Group changes by type
        changes_by_type: Dict[str, List[SchemaChange]] = {}
        for change in migration.changes:
            if change.change_type not in changes_by_type:
                changes_by_type[change.change_type] = []
            changes_by_type[change.change_type].append(change)
        
        # Roll back changes in the reverse order
        rollback_order = [
            SchemaChangeType.ADD_INDEX.value,
            SchemaChangeType.REMOVE_FIELD.value,
            SchemaChangeType.CHANGE_TYPE.value,
            SchemaChangeType.RENAME_FIELD.value,
            SchemaChangeType.ADD_FIELD.value,
            SchemaChangeType.REMOVE_INDEX.value,
        ]
        
        for change_type in rollback_order:
            if change_type in changes_by_type:
                # Create a new migration with just this type of changes
                type_migration = SchemaMigration(
                    table_name=migration.table_name,
                    from_version=migration.from_version,
                    to_version=migration.to_version,
                    changes=changes_by_type[change_type],
                )
                
                # Get and apply the rollback operation
                operation = self._get_operation_for_change_type(change_type, type_migration)
                operation.rollback(self.db)
        
        # Remove the migration from history
        self.migrations[table_name].pop()

    def get_migrations(self, table_name: str) -> List[SchemaMigration]:
        """Get all migrations for a table."""
        if table_name not in self.migrations:
            return []
        return self.migrations[table_name]

    def generate_diff(self, old_schema: TableSchema, new_schema: TableSchema) -> List[Dict[str, Any]]:
        """Generate a diff between two schema versions."""
        changes = []
        
        # Check for field removals
        for field_name in old_schema.fields:
            if field_name not in new_schema.fields:
                changes.append({
                    "type": SchemaChangeType.REMOVE_FIELD.value,
                    "field": field_name,
                })
        
        # Check for field additions and type changes
        for field_name, new_field in new_schema.fields.items():
            if field_name not in old_schema.fields:
                changes.append({
                    "type": SchemaChangeType.ADD_FIELD.value,
                    "field": field_name,
                    "details": {
                        "data_type": new_field.data_type,
                        "nullable": new_field.nullable,
                        "default": new_field.default,
                        "is_indexed": new_field.is_indexed,
                    }
                })
            else:
                old_field = old_schema.fields[field_name]
                
                # Check for type changes
                if old_field.data_type != new_field.data_type:
                    changes.append({
                        "type": SchemaChangeType.CHANGE_TYPE.value,
                        "field": field_name,
                        "details": {
                            "new_type": new_field.data_type,
                            "old_type": old_field.data_type,
                        }
                    })
        
        # Check for index changes
        for field_name in old_schema.indexes:
            if field_name not in new_schema.indexes and field_name != old_schema.primary_key:
                changes.append({
                    "type": SchemaChangeType.REMOVE_INDEX.value,
                    "field": field_name,
                })
        
        for field_name in new_schema.indexes:
            if field_name not in old_schema.indexes and field_name != new_schema.primary_key:
                changes.append({
                    "type": SchemaChangeType.ADD_INDEX.value,
                    "field": field_name,
                })
        
        return changes

    def create_migration_from_diff(
        self,
        table_name: str,
        old_schema: TableSchema,
        new_schema: TableSchema,
        description: Optional[str] = None,
        author: Optional[str] = None,
    ) -> SchemaMigration:
        """Create a migration from a diff between two schema versions."""
        # Generate the diff
        changes = self.generate_diff(old_schema, new_schema)
        
        # Create the migration
        return self.create_migration(
            table_name=table_name,
            changes=changes,
            description=description,
            author=author,
        )

    def export_migrations(self, table_name: str) -> str:
        """Export migrations for a table as JSON."""
        if table_name not in self.migrations:
            return "[]"
        
        return json.dumps(
            [migration.dict() for migration in self.migrations[table_name]],
            indent=2,
        )

    def import_migrations(self, table_name: str, json_data: str) -> None:
        """Import migrations for a table from JSON."""
        migrations_data = json.loads(json_data)
        
        # Convert to SchemaMigration objects
        migrations = [SchemaMigration(**data) for data in migrations_data]
        
        # Store the migrations
        self.migrations[table_name] = migrations