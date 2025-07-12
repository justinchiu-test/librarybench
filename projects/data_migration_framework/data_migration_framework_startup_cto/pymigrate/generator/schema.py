"""Schema generation for database tables."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date, time
from decimal import Decimal

from pymigrate.utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class SchemaGenerator:
    """Generates JSON schemas from database tables."""
    
    # Type mapping from SQL to JSON Schema
    TYPE_MAPPING = {
        "integer": "integer",
        "bigint": "integer",
        "smallint": "integer",
        "tinyint": "integer",
        "int": "integer",
        "numeric": "number",
        "decimal": "number",
        "float": "number",
        "double": "number",
        "real": "number",
        "varchar": "string",
        "char": "string",
        "text": "string",
        "longtext": "string",
        "mediumtext": "string",
        "tinytext": "string",
        "boolean": "boolean",
        "bool": "boolean",
        "date": "string",
        "datetime": "string",
        "timestamp": "string",
        "time": "string",
        "json": "object",
        "jsonb": "object",
        "uuid": "string",
        "binary": "string",
        "varbinary": "string",
        "blob": "string",
    }
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize schema generator."""
        self.connection = connection
        
    async def generate_schema(self, table_name: str) -> Dict[str, Any]:
        """Generate JSON schema for a database table."""
        logger.info(f"Generating schema for table: {table_name}")
        
        # Get table columns
        columns = await self.connection.get_table_columns(table_name)
        
        # Get constraints
        constraints = await self.connection.get_table_constraints(table_name)
        
        # Build schema
        schema = {
            "type": "object",
            "title": self._to_title_case(table_name),
            "description": f"Schema for {table_name} table",
            "properties": {},
            "required": []
        }
        
        # Process each column
        for column in columns:
            col_name = column["name"]
            col_type = column["type"].lower()
            
            # Generate property schema
            prop_schema = self._generate_property_schema(column)
            schema["properties"][col_name] = prop_schema
            
            # Check if required
            if column.get("nullable") is False and col_name != "id":
                schema["required"].append(col_name)
                
        # Add validation rules from constraints
        self._add_constraint_validations(schema, constraints)
        
        return schema
        
    def _generate_property_schema(
        self, 
        column: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate schema for a single column."""
        col_type = column["type"].lower()
        
        # Extract base type and parameters
        base_type, params = self._parse_column_type(col_type)
        
        # Map to JSON schema type
        json_type = self.TYPE_MAPPING.get(base_type, "string")
        
        prop_schema = {
            "type": json_type,
            "description": column.get("comment", f"{column['name']} field")
        }
        
        # Add format for specific types
        if base_type in ["date"]:
            prop_schema["format"] = "date"
        elif base_type in ["datetime", "timestamp"]:
            prop_schema["format"] = "date-time"
        elif base_type == "time":
            prop_schema["format"] = "time"
        elif base_type == "uuid":
            prop_schema["format"] = "uuid"
        elif base_type in ["email", "url"] and "email" in column["name"].lower():
            prop_schema["format"] = "email"
        elif base_type in ["email", "url"] and "url" in column["name"].lower():
            prop_schema["format"] = "uri"
            
        # Add constraints
        if params:
            if "length" in params:
                if json_type == "string":
                    prop_schema["maxLength"] = params["length"]
            elif "precision" in params and "scale" in params:
                # For decimal types
                prop_schema["multipleOf"] = 10 ** (-params["scale"])
                
        # Add enum values if specified
        if column.get("enum_values"):
            prop_schema["enum"] = column["enum_values"]
            
        # Add default value
        if column.get("default") is not None:
            prop_schema["default"] = column["default"]
            
        # Add examples
        prop_schema["examples"] = [self._generate_example(base_type, column["name"])]
        
        return prop_schema
        
    def _parse_column_type(self, col_type: str) -> tuple:
        """Parse column type string to extract base type and parameters."""
        import re
        
        # Match type(params) pattern
        match = re.match(r"(\w+)(?:\(([^)]+)\))?", col_type)
        
        if not match:
            return col_type, {}
            
        base_type = match.group(1)
        params_str = match.group(2)
        
        params = {}
        if params_str:
            # Parse parameters
            parts = params_str.split(",")
            if len(parts) == 1:
                # Single parameter (e.g., varchar(255))
                try:
                    params["length"] = int(parts[0])
                except ValueError:
                    pass
            elif len(parts) == 2:
                # Two parameters (e.g., decimal(10,2))
                try:
                    params["precision"] = int(parts[0])
                    params["scale"] = int(parts[1])
                except ValueError:
                    pass
                    
        return base_type, params
        
    def _add_constraint_validations(
        self,
        schema: Dict[str, Any],
        constraints: List[Dict[str, Any]]
    ) -> None:
        """Add validation rules based on database constraints."""
        for constraint in constraints:
            if constraint["type"] == "unique":
                # Mark as unique in description
                for col in constraint["columns"]:
                    if col in schema["properties"]:
                        desc = schema["properties"][col].get("description", "")
                        schema["properties"][col]["description"] = f"{desc} (unique)"
                        
            elif constraint["type"] == "check":
                # Add pattern or range validation
                # This would require parsing the check constraint
                pass
                
            elif constraint["type"] == "foreign_key":
                # Add reference information
                for col in constraint["columns"]:
                    if col in schema["properties"]:
                        schema["properties"][col]["$ref"] = f"#/components/schemas/{constraint['referenced_table']}"
                        
    def _generate_example(self, base_type: str, field_name: str) -> Any:
        """Generate example value for a field."""
        if "email" in field_name.lower():
            return "user@example.com"
        elif "phone" in field_name.lower():
            return "+1234567890"
        elif "url" in field_name.lower() or "link" in field_name.lower():
            return "https://example.com"
        elif "name" in field_name.lower():
            return "John Doe"
        elif base_type in ["integer", "bigint", "smallint", "int"]:
            return 123
        elif base_type in ["numeric", "decimal", "float", "double"]:
            return 123.45
        elif base_type in ["boolean", "bool"]:
            return True
        elif base_type == "date":
            return "2024-01-01"
        elif base_type in ["datetime", "timestamp"]:
            return "2024-01-01T12:00:00Z"
        elif base_type == "time":
            return "12:00:00"
        elif base_type == "uuid":
            return "550e8400-e29b-41d4-a716-446655440000"
        elif base_type in ["json", "jsonb"]:
            return {"key": "value"}
        else:
            return "example_value"
            
    def _to_title_case(self, snake_case: str) -> str:
        """Convert snake_case to Title Case."""
        return " ".join(word.capitalize() for word in snake_case.split("_"))
        
    async def generate_validation_rules(
        self,
        table_name: str
    ) -> Dict[str, Any]:
        """Generate additional validation rules for a table."""
        rules = {}
        
        # Get business rules from comments or metadata
        metadata = await self.connection.get_table_metadata(table_name)
        
        if metadata.get("validation_rules"):
            rules.update(metadata["validation_rules"])
            
        # Infer rules from data patterns
        sample_data = await self.connection.get_sample_data(table_name, limit=1000)
        
        if sample_data:
            for column in sample_data[0].keys():
                column_values = [row.get(column) for row in sample_data if row.get(column)]
                
                if column_values:
                    # Infer patterns
                    if all(isinstance(v, str) for v in column_values):
                        # Check for common patterns
                        if all("@" in v for v in column_values):
                            rules[column] = {"format": "email"}
                        elif all(v.startswith("http") for v in column_values):
                            rules[column] = {"format": "uri"}
                            
        return rules