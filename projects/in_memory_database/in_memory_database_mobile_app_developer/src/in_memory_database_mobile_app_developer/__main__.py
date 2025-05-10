"""Main entry point for MobileSyncDB CLI."""

import argparse
import logging
import json
import os
import sys
from typing import Dict, Any, List

from .api import MobileSyncDB
from .conflict import ConflictStrategy
from .battery import PowerMode, BatteryStatus


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    logging.basicConfig(
        level=levels.get(level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_db_command(args: argparse.Namespace) -> None:
    """Handle create-db command."""
    db = MobileSyncDB(
        max_memory_mb=args.max_memory,
        conflict_strategy=args.conflict_strategy,
        compression_profile=args.compression,
        power_mode=args.power_mode,
        storage_path=args.storage_path,
    )
    
    print(f"Created in-memory database with storage path: {args.storage_path}")
    
    if args.save:
        db.save_to_storage()
        print(f"Database saved to {args.storage_path}")


def create_table_command(args: argparse.Namespace) -> None:
    """Handle create-table command."""
    db = MobileSyncDB(storage_path=args.storage_path)
    
    # Parse schema
    schema = {}
    for field_def in args.fields:
        name, type_name = field_def.split(":")
        schema[name] = type_name
    
    # Parse nullable fields
    nullable_fields = args.nullable.split(",") if args.nullable else []
    
    # Parse default values
    default_values = {}
    if args.defaults:
        for default_def in args.defaults:
            name, value = default_def.split("=")
            # Try to convert to appropriate type
            try:
                if value.lower() == "true":
                    default_values[name] = True
                elif value.lower() == "false":
                    default_values[name] = False
                elif value.lower() == "null":
                    default_values[name] = None
                elif "." in value:
                    default_values[name] = float(value)
                else:
                    default_values[name] = int(value)
            except (ValueError, TypeError):
                default_values[name] = value
    
    # Parse indexes
    indexes = args.indexes.split(",") if args.indexes else []
    
    # Create the table
    db.create_table(
        name=args.name,
        schema=schema,
        primary_key=args.primary_key,
        nullable_fields=nullable_fields,
        default_values=default_values,
        indexes=indexes,
    )
    
    print(f"Created table '{args.name}' with schema:")
    print(json.dumps(db.get_schema(args.name), indent=2))
    
    if args.save:
        db.save_to_storage()


def insert_record_command(args: argparse.Namespace) -> None:
    """Handle insert-record command."""
    db = MobileSyncDB(storage_path=args.storage_path)
    
    # Parse data
    data = {}
    for field_def in args.data:
        name, value = field_def.split("=")
        # Try to convert to appropriate type
        try:
            if value.lower() == "true":
                data[name] = True
            elif value.lower() == "false":
                data[name] = False
            elif value.lower() == "null":
                data[name] = None
            elif "." in value:
                data[name] = float(value)
            else:
                data[name] = int(value)
        except (ValueError, TypeError):
            data[name] = value
    
    # Insert the record
    record_id = db.insert(args.table, data, args.client_id)
    
    print(f"Inserted record '{record_id}' into table '{args.table}'")
    
    if args.save:
        db.save_to_storage()


def get_record_command(args: argparse.Namespace) -> None:
    """Handle get-record command."""
    db = MobileSyncDB(storage_path=args.storage_path)
    
    try:
        record = db.get(args.table, args.id)
        print(json.dumps(record, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def list_records_command(args: argparse.Namespace) -> None:
    """Handle list-records command."""
    db = MobileSyncDB(storage_path=args.storage_path)
    
    try:
        records = db.get_all(args.table, args.limit, args.offset)
        if not records:
            print(f"No records found in table '{args.table}'")
        else:
            print(f"Found {len(records)} records in table '{args.table}':")
            for record in records:
                print(json.dumps(record, indent=2))
                print("-" * 40)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def update_record_command(args: argparse.Namespace) -> None:
    """Handle update-record command."""
    db = MobileSyncDB(storage_path=args.storage_path)
    
    # Parse data
    data = {}
    for field_def in args.data:
        name, value = field_def.split("=")
        # Try to convert to appropriate type
        try:
            if value.lower() == "true":
                data[name] = True
            elif value.lower() == "false":
                data[name] = False
            elif value.lower() == "null":
                data[name] = None
            elif "." in value:
                data[name] = float(value)
            else:
                data[name] = int(value)
        except (ValueError, TypeError):
            data[name] = value
    
    try:
        db.update(args.table, args.id, data, args.client_id)
        print(f"Updated record '{args.id}' in table '{args.table}'")
        
        if args.save:
            db.save_to_storage()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def delete_record_command(args: argparse.Namespace) -> None:
    """Handle delete-record command."""
    db = MobileSyncDB(storage_path=args.storage_path)
    
    try:
        db.delete(args.table, args.id, args.client_id)
        print(f"Deleted record '{args.id}' from table '{args.table}'")
        
        if args.save:
            db.save_to_storage()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def main() -> None:
    """Run the CLI application."""
    parser = argparse.ArgumentParser(description="MobileSyncDB CLI")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # create-db command
    create_db_parser = subparsers.add_parser("create-db", help="Create a new database")
    create_db_parser.add_argument("--storage-path", type=str, required=True, help="Path to store database files")
    create_db_parser.add_argument("--max-memory", type=int, default=None, help="Maximum memory usage in MB")
    create_db_parser.add_argument(
        "--conflict-strategy",
        type=str,
        default=ConflictStrategy.LAST_WRITE_WINS.value,
        choices=[s.value for s in ConflictStrategy],
        help="Default conflict resolution strategy",
    )
    create_db_parser.add_argument(
        "--compression",
        type=str,
        default="balanced",
        choices=["high_compression", "balanced", "fast", "no_compression"],
        help="Default compression profile",
    )
    create_db_parser.add_argument(
        "--power-mode",
        type=str,
        default=PowerMode.AUTO.value,
        choices=[m.value for m in PowerMode],
        help="Power mode for battery-aware operations",
    )
    create_db_parser.add_argument("--save", action="store_true", help="Save the database to storage")
    
    # create-table command
    create_table_parser = subparsers.add_parser("create-table", help="Create a new table")
    create_table_parser.add_argument("--storage-path", type=str, required=True, help="Path to store database files")
    create_table_parser.add_argument("--name", type=str, required=True, help="Table name")
    create_table_parser.add_argument(
        "--fields",
        type=str,
        nargs="+",
        required=True,
        help="Field definitions (name:type)",
    )
    create_table_parser.add_argument("--primary-key", type=str, required=True, help="Primary key field")
    create_table_parser.add_argument("--nullable", type=str, default="", help="Comma-separated list of nullable fields")
    create_table_parser.add_argument(
        "--defaults",
        type=str,
        nargs="*",
        help="Default values (name=value)",
    )
    create_table_parser.add_argument("--indexes", type=str, default="", help="Comma-separated list of indexed fields")
    create_table_parser.add_argument("--save", action="store_true", help="Save the database to storage")
    
    # insert-record command
    insert_record_parser = subparsers.add_parser("insert-record", help="Insert a record")
    insert_record_parser.add_argument("--storage-path", type=str, required=True, help="Path to store database files")
    insert_record_parser.add_argument("--table", type=str, required=True, help="Table name")
    insert_record_parser.add_argument(
        "--data",
        type=str,
        nargs="+",
        required=True,
        help="Field values (name=value)",
    )
    insert_record_parser.add_argument("--client-id", type=str, default=None, help="Client ID")
    insert_record_parser.add_argument("--save", action="store_true", help="Save the database to storage")
    
    # get-record command
    get_record_parser = subparsers.add_parser("get-record", help="Get a record")
    get_record_parser.add_argument("--storage-path", type=str, required=True, help="Path to store database files")
    get_record_parser.add_argument("--table", type=str, required=True, help="Table name")
    get_record_parser.add_argument("--id", type=str, required=True, help="Record ID")
    
    # list-records command
    list_records_parser = subparsers.add_parser("list-records", help="List records")
    list_records_parser.add_argument("--storage-path", type=str, required=True, help="Path to store database files")
    list_records_parser.add_argument("--table", type=str, required=True, help="Table name")
    list_records_parser.add_argument("--limit", type=int, default=None, help="Maximum number of records to return")
    list_records_parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")
    
    # update-record command
    update_record_parser = subparsers.add_parser("update-record", help="Update a record")
    update_record_parser.add_argument("--storage-path", type=str, required=True, help="Path to store database files")
    update_record_parser.add_argument("--table", type=str, required=True, help="Table name")
    update_record_parser.add_argument("--id", type=str, required=True, help="Record ID")
    update_record_parser.add_argument(
        "--data",
        type=str,
        nargs="+",
        required=True,
        help="Field values (name=value)",
    )
    update_record_parser.add_argument("--client-id", type=str, default=None, help="Client ID")
    update_record_parser.add_argument("--save", action="store_true", help="Save the database to storage")
    
    # delete-record command
    delete_record_parser = subparsers.add_parser("delete-record", help="Delete a record")
    delete_record_parser.add_argument("--storage-path", type=str, required=True, help="Path to store database files")
    delete_record_parser.add_argument("--table", type=str, required=True, help="Table name")
    delete_record_parser.add_argument("--id", type=str, required=True, help="Record ID")
    delete_record_parser.add_argument("--client-id", type=str, default=None, help="Client ID")
    delete_record_parser.add_argument("--save", action="store_true", help="Save the database to storage")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    
    # Handle commands
    if args.command == "create-db":
        create_db_command(args)
    elif args.command == "create-table":
        create_table_command(args)
    elif args.command == "insert-record":
        insert_record_command(args)
    elif args.command == "get-record":
        get_record_command(args)
    elif args.command == "list-records":
        list_records_command(args)
    elif args.command == "update-record":
        update_record_command(args)
    elif args.command == "delete-record":
        delete_record_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()