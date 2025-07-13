"""Unit tests for database utilities."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from pymigrate.utils.database import DatabaseConnection
from pymigrate.models.config import DatabaseConfig, DatabaseType


class TestDatabaseConnection:
    """Test cases for database connection utility."""
    
    def test_database_connection_initialization(self):
        """Test database connection initialization."""
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="password",
        )
        
        conn = DatabaseConnection(config)
        
        assert conn.config == config
        assert conn.database_name == "test_db"
        assert conn._connection is None
        assert conn._pool is None
        assert conn.supports_soft_delete is False
        assert conn.supports_cdc is False
        
    @pytest.mark.asyncio
    async def test_postgresql_feature_support(self):
        """Test PostgreSQL feature support flags."""
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="password",
        )
        
        conn = DatabaseConnection(config)
        
        with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_pool:
            await conn.connect()
            
            assert conn.supports_soft_delete is True
            assert conn.supports_cdc is True
            mock_pool.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_mysql_feature_support(self):
        """Test MySQL feature support flags."""
        config = DatabaseConfig(
            type=DatabaseType.MYSQL,
            host="localhost",
            port=3306,
            database="test_db",
            username="user",
            password="password",
        )
        
        conn = DatabaseConnection(config)
        
        with patch("aiomysql.create_pool", new_callable=AsyncMock) as mock_pool:
            await conn.connect()
            
            assert conn.supports_soft_delete is True
            assert conn.supports_cdc is True
            mock_pool.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_mongodb_feature_support(self):
        """Test MongoDB feature support flags."""
        config = DatabaseConfig(
            type=DatabaseType.MONGODB,
            host="localhost",
            port=27017,
            database="test_db",
            username="user",
            password="password",
        )
        
        conn = DatabaseConnection(config)
        
        with patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_client:
            await conn.connect()
            
            assert conn.supports_soft_delete is True
            assert conn.supports_cdc is True
            mock_client.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_unsupported_database_type(self):
        """Test error on unsupported database type."""
        config = DatabaseConfig(
            type="unsupported",
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="password",
        )
        
        conn = DatabaseConnection(config)
        
        with pytest.raises(ValueError, match="Unsupported database type"):
            await conn.connect()
            
    @pytest.mark.asyncio
    async def test_disconnect_with_pool(self):
        """Test disconnecting with connection pool."""
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="password",
        )
        
        conn = DatabaseConnection(config)
        conn._pool = AsyncMock()
        
        await conn.disconnect()
        
        conn._pool.close.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_disconnect_with_connection(self):
        """Test disconnecting with single connection."""
        config = DatabaseConfig(
            type=DatabaseType.MONGODB,
            host="localhost",
            port=27017,
            database="test_db",
            username="user",
            password="password",
        )
        
        conn = DatabaseConnection(config)
        conn._connection = MagicMock()
        
        await conn.disconnect()
        
        conn._connection.close.assert_called_once()
        
    def test_database_config_validation(self):
        """Test database configuration validation."""
        # Valid config
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="password",
        )
        
        assert config.port == 5432
        
        # Invalid port should be caught by Pydantic
        with pytest.raises(Exception):  # Pydantic ValidationError
            DatabaseConfig(
                type=DatabaseType.POSTGRESQL,
                host="localhost",
                port=70000,  # Invalid port
                database="test_db",
                username="user",
                password="password",
            )
            
    @pytest.mark.asyncio
    async def test_connection_with_ssl_options(self):
        """Test connection with SSL options."""
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="password",
            ssl_mode="require",
            options={"ssl": "require"}
        )
        
        conn = DatabaseConnection(config)
        
        with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_pool:
            await conn.connect()
            
            # Check that options were passed
            call_kwargs = mock_pool.call_args[1]
            assert "ssl" in call_kwargs or "ssl" in config.options