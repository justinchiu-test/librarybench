"""Endpoint builder for REST APIs."""

from typing import Dict, Any, List, Optional

from pymigrate.models.service import APIEndpoint, HTTPMethod


class EndpointBuilder:
    """Builds API endpoint specifications."""
    
    def build_list_endpoint(
        self,
        path: str,
        resource_name: str,
        schema: Dict[str, Any]
    ) -> APIEndpoint:
        """Build list/collection endpoint."""
        return APIEndpoint(
            path=path,
            method=HTTPMethod.GET,
            description=f"List all {resource_name} with pagination and filtering",
            query_parameters=[
                {
                    "name": "page",
                    "in": "query",
                    "description": "Page number (1-based)",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 1, "default": 1}
                },
                {
                    "name": "limit",
                    "in": "query",
                    "description": "Number of items per page",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                },
                {
                    "name": "sort",
                    "in": "query",
                    "description": "Sort field and direction (e.g., 'name,-created_at')",
                    "required": False,
                    "schema": {"type": "string"}
                },
                {
                    "name": "filter",
                    "in": "query",
                    "description": "Filter expression (e.g., 'status=active')",
                    "required": False,
                    "schema": {"type": "string"}
                }
            ],
            response_schema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": schema
                    },
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer"},
                            "limit": {"type": "integer"},
                            "total": {"type": "integer"},
                            "pages": {"type": "integer"}
                        }
                    }
                }
            },
            openapi_spec={
                "tags": [resource_name],
                "responses": {
                    "200": {
                        "description": "Success",
                        "headers": {
                            "X-Total-Count": {
                                "description": "Total number of items",
                                "schema": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        )
        
    def build_get_endpoint(
        self,
        path: str,
        resource_name: str,
        schema: Dict[str, Any]
    ) -> APIEndpoint:
        """Build get single resource endpoint."""
        return APIEndpoint(
            path=path,
            method=HTTPMethod.GET,
            description=f"Get {resource_name} by ID",
            response_schema=schema,
            openapi_spec={
                "tags": [resource_name],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "description": f"{resource_name} ID",
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ]
            }
        )
        
    def build_create_endpoint(
        self,
        path: str,
        resource_name: str,
        schema: Dict[str, Any]
    ) -> APIEndpoint:
        """Build create resource endpoint."""
        # Create schema without ID and timestamps
        create_schema = {
            "type": "object",
            "properties": {},
            "required": schema.get("required", [])
        }
        
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop not in ["id", "created_at", "updated_at"]:
                create_schema["properties"][prop] = prop_schema
                
        return APIEndpoint(
            path=path,
            method=HTTPMethod.POST,
            description=f"Create new {resource_name}",
            request_schema=create_schema,
            response_schema=schema,
            headers={
                "Location": f"{path}/{{id}}"
            },
            openapi_spec={
                "tags": [resource_name],
                "responses": {
                    "201": {
                        "description": "Created",
                        "headers": {
                            "Location": {
                                "description": "URL of created resource",
                                "schema": {"type": "string"}
                            }
                        }
                    }
                }
            }
        )
        
    def build_update_endpoint(
        self,
        path: str,
        resource_name: str,
        schema: Dict[str, Any]
    ) -> APIEndpoint:
        """Build update resource endpoint."""
        # Update schema without ID and timestamps
        update_schema = {
            "type": "object",
            "properties": {},
            "required": schema.get("required", [])
        }
        
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop not in ["id", "created_at", "updated_at"]:
                update_schema["properties"][prop] = prop_schema
                
        return APIEndpoint(
            path=path,
            method=HTTPMethod.PUT,
            description=f"Update {resource_name}",
            request_schema=update_schema,
            response_schema=schema,
            openapi_spec={
                "tags": [resource_name]
            }
        )
        
    def build_patch_endpoint(
        self,
        path: str,
        resource_name: str,
        schema: Dict[str, Any]
    ) -> APIEndpoint:
        """Build partial update resource endpoint."""
        # Patch schema - all fields optional
        patch_schema = {
            "type": "object",
            "properties": {}
        }
        
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop not in ["id", "created_at", "updated_at"]:
                # Make all fields optional
                optional_schema = prop_schema.copy()
                if "required" in optional_schema:
                    del optional_schema["required"]
                patch_schema["properties"][prop] = optional_schema
                
        return APIEndpoint(
            path=path,
            method=HTTPMethod.PATCH,
            description=f"Partially update {resource_name}",
            request_schema=patch_schema,
            response_schema=schema,
            openapi_spec={
                "tags": [resource_name],
                "requestBody": {
                    "description": "Fields to update",
                    "required": False
                }
            }
        )
        
    def build_delete_endpoint(
        self,
        path: str,
        resource_name: str
    ) -> APIEndpoint:
        """Build delete resource endpoint."""
        return APIEndpoint(
            path=path,
            method=HTTPMethod.DELETE,
            description=f"Delete {resource_name}",
            response_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "id": {"type": "string"}
                }
            },
            openapi_spec={
                "tags": [resource_name],
                "responses": {
                    "204": {
                        "description": "No Content"
                    }
                }
            }
        )
        
    def build_relationship_endpoint(
        self,
        path: str,
        parent_resource: str,
        child_resource: str,
        schema: Dict[str, Any]
    ) -> APIEndpoint:
        """Build relationship endpoint."""
        return APIEndpoint(
            path=path,
            method=HTTPMethod.GET,
            description=f"Get {child_resource} related to {parent_resource}",
            query_parameters=[
                {
                    "name": "page",
                    "in": "query",
                    "description": "Page number",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 1, "default": 1}
                },
                {
                    "name": "limit",
                    "in": "query",
                    "description": "Items per page",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                }
            ],
            response_schema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": schema
                    },
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer"},
                            "limit": {"type": "integer"},
                            "total": {"type": "integer"}
                        }
                    }
                }
            },
            openapi_spec={
                "tags": [parent_resource, child_resource],
                "description": f"Retrieve {child_resource} associated with a specific {parent_resource}"
            }
        )
        
    def build_bulk_endpoint(
        self,
        path: str,
        resource_name: str,
        schema: Dict[str, Any],
        operation: str = "create"
    ) -> APIEndpoint:
        """Build bulk operation endpoint."""
        if operation == "create":
            method = HTTPMethod.POST
            description = f"Bulk create {resource_name}"
        elif operation == "update":
            method = HTTPMethod.PUT
            description = f"Bulk update {resource_name}"
        elif operation == "delete":
            method = HTTPMethod.DELETE
            description = f"Bulk delete {resource_name}"
        else:
            raise ValueError(f"Unknown bulk operation: {operation}")
            
        return APIEndpoint(
            path=f"{path}/bulk",
            method=method,
            description=description,
            request_schema={
                "type": "array",
                "items": schema if operation != "delete" else {"type": "string"},
                "minItems": 1,
                "maxItems": 1000
            },
            response_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "integer"},
                    "failed": {"type": "integer"},
                    "errors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "index": {"type": "integer"},
                                "error": {"type": "string"}
                            }
                        }
                    }
                }
            },
            openapi_spec={
                "tags": [resource_name],
                "description": f"Perform bulk {operation} operations"
            }
        )