"""Tests for SQL query executor."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
from datetime import datetime

from src.sql_executor import (
    DatabaseConfig,
    QueryResult,
    SQLExecutor,
    MultiSourceExecutor,
)


class TestDatabaseConfig:
    """Test database configuration."""

    def test_valid_config(self):
        """Test creating a valid database config."""
        config = DatabaseConfig(
            connection_string="postgresql://user:pass@localhost/db",
            pool_size=10,
            max_overflow=20,
        )
        assert config.connection_string == "postgresql://user:pass@localhost/db"
        assert config.pool_size == 10
        assert config.max_overflow == 20

    def test_invalid_connection_string(self):
        """Test validation of connection string."""
        with pytest.raises(ValueError):
            DatabaseConfig(connection_string="")

    def test_default_values(self):
        """Test default configuration values."""
        config = DatabaseConfig(connection_string="sqlite:///test.db")
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.pool_timeout == 30.0
        assert config.pool_recycle == 3600


class TestSQLExecutor:
    """Test SQL executor functionality."""

    @pytest.fixture
    def config(self):
        """Create a test database config."""
        return DatabaseConfig(connection_string="sqlite:///:memory:")

    @pytest.fixture
    def executor(self, config):
        """Create a test SQL executor."""
        return SQLExecutor(config)

    def test_initialization(self, executor):
        """Test executor initialization."""
        assert executor._engine is None
        assert executor.config.connection_string == "sqlite:///:memory:"

    @patch("src.sql_executor.create_engine")
    def test_engine_creation(self, mock_create_engine, executor):
        """Test lazy engine creation."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        # First access creates engine
        engine1 = executor.engine
        assert engine1 == mock_engine
        mock_create_engine.assert_called_once()

        # Second access returns same engine
        engine2 = executor.engine
        assert engine2 == mock_engine
        assert mock_create_engine.call_count == 1

    @patch("src.sql_executor.text")
    def test_execute_query_with_results(self, mock_text, executor):
        """Test executing a query that returns results."""
        # Mock the get_connection context manager
        mock_conn = Mock()
        mock_result = Mock()

        # Mock text() function
        mock_stmt = Mock()
        mock_text.return_value = mock_stmt

        # Mock query result
        mock_result.returns_rows = True
        mock_result.keys.return_value = ["id", "name", "value"]
        mock_result.fetchall.return_value = [
            (1, "Item 1", 100),
            (2, "Item 2", 200),
        ]
        mock_conn.execute.return_value = mock_result

        # Mock the get_connection method to return our mock connection
        with patch.object(executor, "get_connection") as mock_get_connection:
            mock_cm = MagicMock()
            mock_cm.__enter__.return_value = mock_conn
            mock_cm.__exit__.return_value = None
            mock_get_connection.return_value = mock_cm

            # Execute query
            result = executor.execute_query("SELECT * FROM items")

        # Verify result
        assert isinstance(result, QueryResult)
        assert len(result.data) == 2
        assert result.columns == ["id", "name", "value"]
        assert result.row_count == 2
        assert result.query == "SELECT * FROM items"
        assert result.data[0] == {"id": 1, "name": "Item 1", "value": 100}

    @patch("src.sql_executor.text")
    def test_execute_query_with_parameters(self, mock_text, executor):
        """Test executing a parameterized query."""
        # Mock the get_connection context manager
        mock_conn = Mock()
        mock_result = Mock()

        # Mock text() function
        mock_stmt = Mock()
        mock_stmt.bindparams.return_value = mock_stmt
        mock_text.return_value = mock_stmt

        # Mock query result
        mock_result.returns_rows = True
        mock_result.keys.return_value = ["id", "name"]
        mock_result.fetchall.return_value = [(1, "Item 1")]
        mock_conn.execute.return_value = mock_result

        # Mock the get_connection method
        with patch.object(executor, "get_connection") as mock_get_connection:
            mock_cm = MagicMock()
            mock_cm.__enter__.return_value = mock_conn
            mock_cm.__exit__.return_value = None
            mock_get_connection.return_value = mock_cm

            # Execute query with parameters
            params = {"item_id": 1}
            result = executor.execute_query(
                "SELECT * FROM items WHERE id = :item_id", parameters=params
            )

        # Verify result
        assert result.parameters == params
        assert len(result.data) == 1

    @patch("src.sql_executor.text")
    def test_execute_query_no_results(self, mock_text, executor):
        """Test executing a query with no results."""
        # Mock the get_connection context manager
        mock_conn = Mock()
        mock_result = Mock()

        # Mock text() function
        mock_text.return_value = Mock()

        # Mock query result (no rows returned)
        mock_result.returns_rows = False
        mock_result.rowcount = 5
        mock_conn.execute.return_value = mock_result

        # Mock the get_connection method
        with patch.object(executor, "get_connection") as mock_get_connection:
            mock_cm = MagicMock()
            mock_cm.__enter__.return_value = mock_conn
            mock_cm.__exit__.return_value = None
            mock_get_connection.return_value = mock_cm

            # Execute INSERT/UPDATE query
            result = executor.execute_query("UPDATE items SET value = 100")

        # Verify result
        assert result.data == []
        assert result.columns == []
        assert result.row_count == 5

    @patch("src.sql_executor.text")
    def test_execute_query_streaming(self, mock_text, executor):
        """Test streaming query execution."""
        # Mock the get_connection context manager
        mock_conn = Mock()
        mock_result = Mock()

        # Mock text() function
        mock_text.return_value = Mock()

        # Mock streaming execution
        mock_conn.execution_options.return_value = mock_conn
        mock_result.returns_rows = True
        mock_result.keys.return_value = ["id", "value"]

        # Simulate chunked results
        chunks = [
            [(1, 100), (2, 200)],
            [(3, 300)],
            [],  # Empty chunk signals end
        ]
        mock_result.fetchmany.side_effect = chunks
        mock_conn.execute.return_value = mock_result

        # Mock the get_connection method
        with patch.object(executor, "get_connection") as mock_get_connection:
            mock_cm = MagicMock()
            mock_cm.__enter__.return_value = mock_conn
            mock_cm.__exit__.return_value = None
            mock_get_connection.return_value = mock_cm

            # Execute streaming query
            results = list(
                executor.execute_query_streaming(
                    "SELECT * FROM large_table", chunk_size=2
                )
            )

        # Verify results
        assert len(results) == 2
        assert results[0].row_count == 2
        assert results[1].row_count == 1

    @patch("pandas.DataFrame")
    @patch("src.sql_executor.text")
    def test_execute_query_to_dataframe(self, mock_text, mock_df, executor):
        """Test executing query and returning as DataFrame."""
        # Mock the get_connection context manager
        mock_conn = Mock()
        mock_result = Mock()

        # Mock text() function
        mock_text.return_value = Mock()

        # Mock query result
        mock_result.returns_rows = True
        mock_result.keys.return_value = ["id", "value"]
        mock_result.fetchall.return_value = [(1, 100), (2, 200)]
        mock_conn.execute.return_value = mock_result

        # Mock DataFrame creation
        mock_df_instance = Mock()
        mock_df.return_value = mock_df_instance

        # Mock the get_connection method
        with patch.object(executor, "get_connection") as mock_get_connection:
            mock_cm = MagicMock()
            mock_cm.__enter__.return_value = mock_conn
            mock_cm.__exit__.return_value = None
            mock_get_connection.return_value = mock_cm

            # Execute query
            df = executor.execute_query_to_dataframe("SELECT * FROM items")

        # Verify DataFrame was created with correct data
        mock_df.assert_called_once()
        call_args = mock_df.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0] == {"id": 1, "value": 100}

    def test_close(self, executor):
        """Test closing the executor."""
        mock_engine = Mock()
        executor._engine = mock_engine

        executor.close()

        mock_engine.dispose.assert_called_once()
        assert executor._engine is None


class TestMultiSourceExecutor:
    """Test multi-source executor functionality."""

    @pytest.fixture
    def multi_executor(self):
        """Create a test multi-source executor."""
        return MultiSourceExecutor()

    def test_add_source(self, multi_executor):
        """Test adding data sources."""
        config1 = DatabaseConfig(connection_string="sqlite:///db1.db")
        config2 = DatabaseConfig(connection_string="sqlite:///db2.db")

        multi_executor.add_source("source1", config1)
        multi_executor.add_source("source2", config2)

        assert "source1" in multi_executor._executors
        assert "source2" in multi_executor._executors

    def test_add_duplicate_source(self, multi_executor):
        """Test adding a duplicate source raises error."""
        config = DatabaseConfig(connection_string="sqlite:///test.db")

        multi_executor.add_source("source1", config)

        with pytest.raises(ValueError, match="already exists"):
            multi_executor.add_source("source1", config)

    def test_remove_source(self, multi_executor):
        """Test removing a data source."""
        config = DatabaseConfig(connection_string="sqlite:///test.db")
        multi_executor.add_source("source1", config)

        # Mock the executor's close method
        mock_executor = multi_executor._executors["source1"]
        mock_executor.close = Mock()

        multi_executor.remove_source("source1")

        assert "source1" not in multi_executor._executors
        mock_executor.close.assert_called_once()

    @patch("src.sql_executor.SQLExecutor.execute_query")
    def test_execute_query_on_source(self, mock_execute, multi_executor):
        """Test executing query on specific source."""
        config = DatabaseConfig(connection_string="sqlite:///test.db")
        multi_executor.add_source("source1", config)

        # Mock query result
        mock_result = QueryResult(
            data=[{"id": 1}],
            columns=["id"],
            row_count=1,
            execution_time=0.1,
            query="SELECT 1 as id",
            parameters=None,
        )
        mock_execute.return_value = mock_result

        # Execute query
        result = multi_executor.execute_query("source1", "SELECT 1 as id")

        assert result == mock_result
        mock_execute.assert_called_once_with("SELECT 1 as id", None)

    def test_execute_query_invalid_source(self, multi_executor):
        """Test executing query on non-existent source."""
        with pytest.raises(ValueError, match="not found"):
            multi_executor.execute_query("invalid_source", "SELECT 1")

    @patch("src.sql_executor.SQLExecutor.execute_query")
    def test_execute_cross_source_query(self, mock_execute, multi_executor):
        """Test executing queries across multiple sources."""
        # Add sources
        config1 = DatabaseConfig(connection_string="sqlite:///db1.db")
        config2 = DatabaseConfig(connection_string="sqlite:///db2.db")
        multi_executor.add_source("source1", config1)
        multi_executor.add_source("source2", config2)

        # Mock results
        result1 = QueryResult(
            data=[{"count": 10}],
            columns=["count"],
            row_count=1,
            execution_time=0.1,
            query="SELECT COUNT(*) as count FROM table1",
            parameters=None,
        )
        result2 = QueryResult(
            data=[{"sum": 1000}],
            columns=["sum"],
            row_count=1,
            execution_time=0.2,
            query="SELECT SUM(value) as sum FROM table2",
            parameters=None,
        )

        mock_execute.side_effect = [result1, result2]

        # Execute cross-source query
        queries = {
            "source1": "SELECT COUNT(*) as count FROM table1",
            "source2": "SELECT SUM(value) as sum FROM table2",
        }
        results = multi_executor.execute_cross_source_query(queries)

        assert "source1" in results
        assert "source2" in results
        assert results["source1"] == result1
        assert results["source2"] == result2

    def test_close_all(self, multi_executor):
        """Test closing all data sources."""
        # Add sources
        config1 = DatabaseConfig(connection_string="sqlite:///db1.db")
        config2 = DatabaseConfig(connection_string="sqlite:///db2.db")
        multi_executor.add_source("source1", config1)
        multi_executor.add_source("source2", config2)

        # Mock close methods
        for executor in multi_executor._executors.values():
            executor.close = Mock()

        multi_executor.close_all()

        assert len(multi_executor._executors) == 0
