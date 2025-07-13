"""Unit tests for API Generator."""

import pytest
from unittest.mock import AsyncMock, patch
import json

from pymigrate.generator.api import APIGenerator
from pymigrate.generator.schema import SchemaGenerator
from pymigrate.generator.endpoint import EndpointBuilder
from pymigrate.models.service import HTTPMethod


class TestAPIGenerator:
    """Test cases for API Generator."""
    
    @pytest.mark.asyncio
    async def test_generator_initialization(self, mock_db_connection):
        """Test API generator initialization."""
        generator = APIGenerator(mock_db_connection)
        
        assert generator.connection == mock_db_connection
        assert isinstance(generator.schema_generator, SchemaGenerator)
        assert isinstance(generator.endpoint_builder, EndpointBuilder)
        
    @pytest.mark.asyncio
    async def test_generate_api_for_service(self, mock_db_connection, sample_service_boundary):
        """Test API generation for a service boundary."""
        generator = APIGenerator(mock_db_connection)
        
        # Mock schema generation
        mock_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
            },
            "required": ["name", "email"],
        }
        
        with patch.object(generator.schema_generator, 'generate_schema', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_schema
            
            api_spec = await generator.generate_api(sample_service_boundary)
            
            assert api_spec["service_name"] == "user_service"
            assert api_spec["version"] == "v1"
            assert len(api_spec["endpoints"]) > 0
            assert "users" in api_spec["schemas"]
            assert "openapi_spec" in api_spec
            
    @pytest.mark.asyncio
    async def test_crud_endpoint_generation(self, mock_db_connection):
        """Test CRUD endpoint generation."""
        generator = APIGenerator(mock_db_connection)
        
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
        }
        
        endpoints = await generator._generate_crud_endpoints(
            "user",  # Changed to singular form
            schema,
            "v1"
        )
        
        # Should generate 6 CRUD endpoints
        assert len(endpoints) == 6
        
        # Check endpoint methods
        methods = {ep.method for ep in endpoints}
        assert HTTPMethod.GET in methods
        assert HTTPMethod.POST in methods
        assert HTTPMethod.PUT in methods
        assert HTTPMethod.DELETE in methods
        assert HTTPMethod.PATCH in methods
        
        # Check paths
        paths = {ep.path for ep in endpoints}
        assert "/api/v1/users" in paths
        assert "/api/v1/users/{id}" in paths
        
    @pytest.mark.asyncio
    async def test_openapi_spec_generation(self, mock_db_connection):
        """Test OpenAPI specification generation."""
        generator = APIGenerator(mock_db_connection)
        
        from pymigrate.models.service import APIEndpoint
        
        endpoints = [
            APIEndpoint(
                path="/api/v1/users",
                method=HTTPMethod.GET,
                description="List users",
                query_parameters=[
                    {
                        "name": "page",
                        "in": "query",
                        "schema": {"type": "integer"},
                    }
                ],
                response_schema={"type": "array"},
            ),
            APIEndpoint(
                path="/api/v1/users/{id}",
                method=HTTPMethod.GET,
                description="Get user by ID",
                response_schema={"type": "object"},
            ),
        ]
        
        schemas = {
            "users": {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
            }
        }
        
        spec = generator._generate_openapi_spec(
            "user_service",
            endpoints,
            schemas,
            "v1"
        )
        
        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "user_service API"
        assert spec["info"]["version"] == "v1"
        assert "/api/v1/users" in spec["paths"]
        assert "Users" in spec["components"]["schemas"]  # PascalCase
        
    @pytest.mark.asyncio
    async def test_fastapi_code_generation(self, mock_db_connection):
        """Test FastAPI code generation."""
        generator = APIGenerator(mock_db_connection)
        
        api_spec = {
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "Test API Description",
            },
            "schemas": {
                "users": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                    "required": ["name", "email"],
                }
            },
        }
        
        code_files = await generator.generate_api_code(api_spec, "fastapi")
        
        assert "main.py" in code_files
        assert "models.py" in code_files
        assert "routers/users.py" in code_files
        
        # Check main.py contains FastAPI app
        assert "from fastapi import FastAPI" in code_files["main.py"]
        assert "app = FastAPI(" in code_files["main.py"]
        
        # Check models.py contains Pydantic models
        assert "from pydantic import BaseModel" in code_files["models.py"]
        assert "class UsersBase(BaseModel):" in code_files["models.py"]
        assert "class UsersCreate(UsersBase):" in code_files["models.py"]
        
        # Check router contains endpoints
        assert "@router.get" in code_files["routers/users.py"]
        assert "@router.post" in code_files["routers/users.py"]
        
    def test_pluralization(self, mock_db_connection):
        """Test table name pluralization."""
        generator = APIGenerator(mock_db_connection)
        
        assert generator._pluralize("user") == "users"
        assert generator._pluralize("category") == "categories"
        assert generator._pluralize("status") == "statuses"
        assert generator._pluralize("data") == "datas"  # Simple rule
        
    def test_pascal_case_conversion(self, mock_db_connection):
        """Test snake_case to PascalCase conversion."""
        generator = APIGenerator(mock_db_connection)
        
        assert generator._to_pascal_case("user_profile") == "UserProfile"
        assert generator._to_pascal_case("order_item") == "OrderItem"
        assert generator._to_pascal_case("simple") == "Simple"
        
    def test_path_parameter_extraction(self, mock_db_connection):
        """Test extraction of path parameters."""
        generator = APIGenerator(mock_db_connection)
        
        assert generator._extract_path_parameters("/api/v1/users/{id}") == ["id"]
        assert generator._extract_path_parameters("/api/v1/users/{userId}/orders/{orderId}") == ["userId", "orderId"]
        assert generator._extract_path_parameters("/api/v1/users") == []
        
    def test_json_to_python_type_conversion(self, mock_db_connection):
        """Test JSON schema to Python type conversion."""
        generator = APIGenerator(mock_db_connection)
        
        assert generator._json_to_python_type({"type": "string"}) == "str"
        assert generator._json_to_python_type({"type": "integer"}) == "int"
        assert generator._json_to_python_type({"type": "number"}) == "float"
        assert generator._json_to_python_type({"type": "boolean"}) == "bool"
        assert generator._json_to_python_type({"type": "array", "items": {"type": "string"}}) == "List[str]"
        assert generator._json_to_python_type({"type": "object"}) == "Dict[str, Any]"
        
    @pytest.mark.asyncio
    async def test_relationship_endpoint_generation(self, mock_db_connection, sample_service_boundary):
        """Test generation of relationship endpoints."""
        generator = APIGenerator(mock_db_connection)
        
        # Modify boundary to have internal relationships
        sample_service_boundary.tables = ["users", "user_profiles", "orders"]
        sample_service_boundary.relationships = {
            "users": ["user_profiles", "orders"],  # Both internal
        }
        
        schemas = {
            "users": {"type": "object"},
            "user_profiles": {"type": "object"},
            "orders": {"type": "object"},
        }
        
        endpoints = await generator._generate_relationship_endpoints(
            sample_service_boundary,
            schemas,
            "v1"
        )
        
        # Should generate endpoints for internal relationships
        assert len(endpoints) > 0
        
        paths = [ep.path for ep in endpoints]
        assert any("user_profiles" in path for path in paths)
        assert any("orders" in path for path in paths)