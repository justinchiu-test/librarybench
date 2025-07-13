"""API generator for microservices."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from pymigrate.models.service import ServiceBoundary, APIEndpoint, HTTPMethod
from pymigrate.generator.schema import SchemaGenerator
from pymigrate.generator.endpoint import EndpointBuilder
from pymigrate.utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class APIGenerator:
    """Generates REST API endpoints for migrated microservices."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize API generator."""
        self.connection = connection
        self.schema_generator = SchemaGenerator(connection)
        self.endpoint_builder = EndpointBuilder()
        
    async def generate_api(
        self, 
        service_boundary: ServiceBoundary,
        api_version: str = "v1"
    ) -> Dict[str, Any]:
        """Generate complete API specification for a service."""
        logger.info(f"Generating API for service: {service_boundary.service_name}")
        
        # Generate schemas for all tables
        schemas = {}
        for table in service_boundary.tables:
            schema = await self.schema_generator.generate_schema(table)
            schemas[table] = schema
            
        # Generate endpoints
        endpoints = []
        
        for table in service_boundary.tables:
            # Generate CRUD endpoints
            crud_endpoints = await self._generate_crud_endpoints(
                table, 
                schemas[table], 
                api_version
            )
            endpoints.extend(crud_endpoints)
            
        # Generate relationship endpoints
        relationship_endpoints = await self._generate_relationship_endpoints(
            service_boundary,
            schemas,
            api_version
        )
        endpoints.extend(relationship_endpoints)
        
        # Generate OpenAPI specification
        openapi_spec = self._generate_openapi_spec(
            service_boundary.service_name,
            endpoints,
            schemas,
            api_version
        )
        
        return {
            "service_name": service_boundary.service_name,
            "version": api_version,
            "endpoints": endpoints,
            "schemas": schemas,
            "openapi_spec": openapi_spec
        }
        
    async def _generate_crud_endpoints(
        self,
        table: str,
        schema: Dict[str, Any],
        api_version: str
    ) -> List[APIEndpoint]:
        """Generate CRUD endpoints for a table."""
        resource_name = self._pluralize(table)
        base_path = f"/api/{api_version}/{resource_name}"
        
        endpoints = []
        
        # GET all (with pagination)
        endpoints.append(
            self.endpoint_builder.build_list_endpoint(
                base_path,
                table,
                schema
            )
        )
        
        # GET by ID
        endpoints.append(
            self.endpoint_builder.build_get_endpoint(
                f"{base_path}/{{id}}",
                table,
                schema
            )
        )
        
        # POST (create)
        endpoints.append(
            self.endpoint_builder.build_create_endpoint(
                base_path,
                table,
                schema
            )
        )
        
        # PUT (update)
        endpoints.append(
            self.endpoint_builder.build_update_endpoint(
                f"{base_path}/{{id}}",
                table,
                schema
            )
        )
        
        # DELETE
        endpoints.append(
            self.endpoint_builder.build_delete_endpoint(
                f"{base_path}/{{id}}",
                table
            )
        )
        
        # PATCH (partial update)
        endpoints.append(
            self.endpoint_builder.build_patch_endpoint(
                f"{base_path}/{{id}}",
                table,
                schema
            )
        )
        
        return endpoints
        
    async def _generate_relationship_endpoints(
        self,
        service_boundary: ServiceBoundary,
        schemas: Dict[str, Dict[str, Any]],
        api_version: str
    ) -> List[APIEndpoint]:
        """Generate endpoints for relationships between tables."""
        endpoints = []
        
        for table, related_tables in service_boundary.relationships.items():
            resource_name = self._pluralize(table)
            base_path = f"/api/{api_version}/{resource_name}"
            
            for related_table in related_tables:
                if related_table in service_boundary.tables:
                    # Internal relationship
                    related_resource = self._pluralize(related_table)
                    
                    # GET related resources
                    endpoints.append(
                        self.endpoint_builder.build_relationship_endpoint(
                            f"{base_path}/{{id}}/{related_resource}",
                            table,
                            related_table,
                            schemas.get(related_table, {})
                        )
                    )
                    
        return endpoints
        
    def _generate_openapi_spec(
        self,
        service_name: str,
        endpoints: List[APIEndpoint],
        schemas: Dict[str, Dict[str, Any]],
        api_version: str
    ) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{service_name} API",
                "version": api_version,
                "description": f"REST API for {service_name} microservice"
            },
            "servers": [
                {
                    "url": f"https://api.example.com",
                    "description": "Production server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [
                {"bearerAuth": []}
            ]
        }
        
        # Add schemas
        for table_name, schema in schemas.items():
            spec["components"]["schemas"][self._to_pascal_case(table_name)] = schema
            
        # Add paths
        for endpoint in endpoints:
            path = endpoint.path
            method = endpoint.method.value.lower()
            
            if path not in spec["paths"]:
                spec["paths"][path] = {}
                
            operation = {
                "summary": endpoint.description,
                "operationId": f"{method}_{path.replace('/', '_').strip('_')}",
                "tags": [service_name],
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema or {"type": "object"}
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request"
                    },
                    "401": {
                        "description": "Unauthorized"
                    },
                    "404": {
                        "description": "Not Found"
                    },
                    "500": {
                        "description": "Internal Server Error"
                    }
                }
            }
            
            # Add request body if needed
            if endpoint.request_schema and method in ["post", "put", "patch"]:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
                
            # Add parameters
            if endpoint.query_parameters:
                operation["parameters"] = endpoint.query_parameters
                
            # Add path parameters
            path_params = self._extract_path_parameters(path)
            if path_params:
                if "parameters" not in operation:
                    operation["parameters"] = []
                    
                for param in path_params:
                    operation["parameters"].append({
                        "name": param,
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    })
                    
            spec["paths"][path][method] = operation
            
        return spec
        
    async def generate_api_code(
        self,
        api_spec: Dict[str, Any],
        framework: str = "fastapi"
    ) -> Dict[str, str]:
        """Generate actual API code from specification."""
        if framework == "fastapi":
            return await self._generate_fastapi_code(api_spec)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
            
    async def _generate_fastapi_code(
        self,
        api_spec: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate FastAPI code from API specification."""
        code_files = {}
        
        # Generate main app file
        app_code = '''from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from .models import *
from .database import get_db
from .auth import verify_token

app = FastAPI(
    title="{title}",
    version="{version}",
    description="{description}"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from .routers import {routers}

# Include routers
{router_includes}

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''.format(
            title=api_spec["info"]["title"],
            version=api_spec["info"]["version"],
            description=api_spec["info"]["description"],
            routers=", ".join([f"{name}_router" for name in api_spec["schemas"].keys()]),
            router_includes="\n".join([
                f'app.include_router({name}_router, prefix="/api/v1", tags=["{name}"])'
                for name in api_spec["schemas"].keys()
            ])
        )
        
        code_files["main.py"] = app_code
        
        # Generate model files
        models_code = self._generate_pydantic_models(api_spec["schemas"])
        code_files["models.py"] = models_code
        
        # Generate router files
        for table_name in api_spec["schemas"].keys():
            router_code = self._generate_router_code(table_name, api_spec)
            code_files[f"routers/{table_name}.py"] = router_code
            
        return code_files
        
    def _generate_pydantic_models(
        self,
        schemas: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate Pydantic models from schemas."""
        code = '''from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

'''
        
        for table_name, schema in schemas.items():
            model_name = self._to_pascal_case(table_name)
            
            # Base model
            code += f"class {model_name}Base(BaseModel):\n"
            
            for prop_name, prop_schema in schema.get("properties", {}).items():
                if prop_name not in ["id", "created_at", "updated_at"]:
                    python_type = self._json_to_python_type(prop_schema)
                    required = prop_name in schema.get("required", [])
                    
                    if required:
                        code += f"    {prop_name}: {python_type}\n"
                    else:
                        code += f"    {prop_name}: Optional[{python_type}] = None\n"
                        
            code += "\n"
            
            # Create model
            code += f"class {model_name}Create({model_name}Base):\n"
            code += "    pass\n\n"
            
            # Update model
            code += f"class {model_name}Update({model_name}Base):\n"
            code += "    pass\n\n"
            
            # Response model
            code += f"class {model_name}(BaseModel):\n"
            code += "    id: str\n"
            
            for prop_name, prop_schema in schema.get("properties", {}).items():
                python_type = self._json_to_python_type(prop_schema)
                code += f"    {prop_name}: {python_type}\n"
                
            code += "    created_at: datetime\n"
            code += "    updated_at: datetime\n"
            code += "\n    class Config:\n"
            code += "        from_attributes = True\n\n"
            
        return code
        
    def _generate_router_code(
        self,
        table_name: str,
        api_spec: Dict[str, Any]
    ) -> str:
        """Generate FastAPI router code for a table."""
        model_name = self._to_pascal_case(table_name)
        resource_name = self._pluralize(table_name)
        
        code = f'''from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from ..models import {model_name}, {model_name}Create, {model_name}Update
from ..database import get_db
from ..crud import {table_name} as crud

router = APIRouter()

@router.get("/{resource_name}", response_model=List[{model_name}])
async def list_{resource_name}(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all {resource_name} with pagination."""
    items = crud.get_multi(db, skip=skip, limit=limit)
    return items

@router.get("/{resource_name}/{{id}}", response_model={model_name})
async def get_{table_name}(id: str, db: Session = Depends(get_db)):
    """Get {table_name} by ID."""
    item = crud.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return item

@router.post("/{resource_name}", response_model={model_name})
async def create_{table_name}(
    item: {model_name}Create,
    db: Session = Depends(get_db)
):
    """Create new {table_name}."""
    return crud.create(db, obj_in=item)

@router.put("/{resource_name}/{{id}}", response_model={model_name})
async def update_{table_name}(
    id: str,
    item: {model_name}Update,
    db: Session = Depends(get_db)
):
    """Update {table_name}."""
    db_item = crud.get(db, id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return crud.update(db, db_obj=db_item, obj_in=item)

@router.delete("/{resource_name}/{{id}}")
async def delete_{table_name}(id: str, db: Session = Depends(get_db)):
    """Delete {table_name}."""
    db_item = crud.get(db, id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    crud.remove(db, id=id)
    return {{"message": "{model_name} deleted successfully"}}
'''
        
        return code
        
    def _pluralize(self, word: str) -> str:
        """Simple pluralization."""
        if word.endswith("y"):
            return word[:-1] + "ies"
        elif word.endswith("s"):
            return word + "es"
        else:
            return word + "s"
            
    def _to_pascal_case(self, snake_case: str) -> str:
        """Convert snake_case to PascalCase."""
        return "".join(word.capitalize() for word in snake_case.split("_"))
        
    def _extract_path_parameters(self, path: str) -> List[str]:
        """Extract path parameters from path string."""
        import re
        return re.findall(r"\{(\w+)\}", path)
        
    def _json_to_python_type(self, json_schema: Dict[str, Any]) -> str:
        """Convert JSON schema type to Python type."""
        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "List",
            "object": "Dict[str, Any]"
        }
        
        json_type = json_schema.get("type", "string")
        
        if json_type == "array":
            items_type = self._json_to_python_type(json_schema.get("items", {}))
            return f"List[{items_type}]"
            
        return type_map.get(json_type, "Any")