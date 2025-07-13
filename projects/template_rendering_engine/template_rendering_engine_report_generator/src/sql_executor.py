"""SQL query executor with connection pooling and parameterization support."""

from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager
import threading
from queue import Queue
import time
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, text, pool
from sqlalchemy.engine import Engine, Connection
import pandas as pd


class DatabaseConfig(BaseModel):
    """Configuration for database connection."""

    connection_string: str
    pool_size: int = Field(default=5, ge=1, le=50)
    max_overflow: int = Field(default=10, ge=0, le=100)
    pool_timeout: float = Field(default=30.0, gt=0)
    pool_recycle: int = Field(default=3600, gt=0)

    @field_validator("connection_string")
    def validate_connection_string(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Connection string must be a non-empty string")
        return v


class QueryResult(BaseModel):
    """Result of a SQL query execution."""

    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time: float
    query: str
    parameters: Optional[Dict[str, Any]] = None


class SQLExecutor:
    """SQL query executor with connection pooling."""

    def __init__(self, config: DatabaseConfig):
        """Initialize the SQL executor with configuration."""
        self.config = config
        self._engine: Optional[Engine] = None
        self._lock = threading.Lock()
        self._connection_pool: Optional[Queue] = None

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with connection pooling."""
        return create_engine(
            self.config.connection_string,
            poolclass=pool.QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=True,
        )

    @property
    def engine(self) -> Engine:
        """Get or create the database engine."""
        if self._engine is None:
            with self._lock:
                if self._engine is None:
                    self._engine = self._create_engine()
        return self._engine

    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        fetch_size: Optional[int] = None,
    ) -> QueryResult:
        """Execute a SQL query with optional parameters."""
        start_time = time.time()

        with self.get_connection() as conn:
            # Prepare the query with parameters
            stmt = text(query)
            if parameters:
                stmt = stmt.bindparams(**parameters)

            # Execute the query
            result = conn.execute(stmt)

            # Fetch results
            if result.returns_rows:
                if fetch_size:
                    rows = result.fetchmany(fetch_size)
                else:
                    rows = result.fetchall()

                # Convert to list of dicts
                columns = list(result.keys())
                data = [dict(zip(columns, row)) for row in rows]
                row_count = len(data)
            else:
                data = []
                columns = []
                row_count = result.rowcount if result.rowcount > 0 else 0

        execution_time = time.time() - start_time

        return QueryResult(
            data=data,
            columns=columns,
            row_count=row_count,
            execution_time=execution_time,
            query=query,
            parameters=parameters,
        )

    def execute_query_streaming(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1000,
    ):
        """Execute a query and yield results in chunks for memory efficiency."""
        with self.get_connection() as conn:
            stmt = text(query)
            if parameters:
                stmt = stmt.bindparams(**parameters)

            result = conn.execution_options(stream_results=True).execute(stmt)

            if result.returns_rows:
                columns = list(result.keys())

                while True:
                    rows = result.fetchmany(chunk_size)
                    if not rows:
                        break

                    data = [dict(zip(columns, row)) for row in rows]
                    yield QueryResult(
                        data=data,
                        columns=columns,
                        row_count=len(data),
                        execution_time=0.0,  # Not tracked for streaming
                        query=query,
                        parameters=parameters,
                    )

    def execute_query_to_dataframe(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """Execute a query and return results as a pandas DataFrame."""
        result = self.execute_query(query, parameters)

        if result.data:
            return pd.DataFrame(result.data)
        else:
            return pd.DataFrame(columns=result.columns)

    def close(self):
        """Close the database engine and cleanup resources."""
        if self._engine:
            self._engine.dispose()
            self._engine = None


class MultiSourceExecutor:
    """Executor for handling multiple data sources."""

    def __init__(self):
        """Initialize the multi-source executor."""
        self._executors: Dict[str, SQLExecutor] = {}
        self._lock = threading.Lock()

    def add_source(self, name: str, config: DatabaseConfig):
        """Add a new data source."""
        with self._lock:
            if name in self._executors:
                raise ValueError(f"Data source '{name}' already exists")
            self._executors[name] = SQLExecutor(config)

    def remove_source(self, name: str):
        """Remove a data source."""
        with self._lock:
            if name in self._executors:
                self._executors[name].close()
                del self._executors[name]

    def execute_query(
        self,
        source: str,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> QueryResult:
        """Execute a query on a specific data source."""
        if source not in self._executors:
            raise ValueError(f"Data source '{source}' not found")

        return self._executors[source].execute_query(query, parameters)

    def execute_cross_source_query(
        self,
        queries: Dict[str, str],
        parameters: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, QueryResult]:
        """Execute queries across multiple sources."""
        results = {}

        for source, query in queries.items():
            if source not in self._executors:
                raise ValueError(f"Data source '{source}' not found")

            source_params = parameters.get(source) if parameters else None
            results[source] = self._executors[source].execute_query(
                query, source_params
            )

        return results

    def close_all(self):
        """Close all data sources."""
        with self._lock:
            for executor in self._executors.values():
                executor.close()
            self._executors.clear()
