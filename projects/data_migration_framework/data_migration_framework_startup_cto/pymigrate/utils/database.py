"""Database connection and operations utilities."""

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import asyncio

from pymigrate.models.config import DatabaseConfig, DatabaseType

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Abstract database connection with common operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database connection."""
        self.config = config
        self.database_name = config.database
        self._connection = None
        self._pool = None
        self.supports_soft_delete = False
        self.supports_cdc = False
        
    async def connect(self) -> None:
        """Establish database connection."""
        if self.config.type == DatabaseType.POSTGRESQL:
            import asyncpg
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                **self.config.options
            )
            self.supports_soft_delete = True
            self.supports_cdc = True
            
        elif self.config.type == DatabaseType.MYSQL:
            import aiomysql
            self._pool = await aiomysql.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                db=self.config.database,
                **self.config.options
            )
            self.supports_soft_delete = True
            self.supports_cdc = True
            
        elif self.config.type == DatabaseType.MONGODB:
            from motor.motor_asyncio import AsyncIOMotorClient
            self._connection = AsyncIOMotorClient(
                f"mongodb://{self.config.username}:{self.config.password}@"
                f"{self.config.host}:{self.config.port}/{self.config.database}"
            )
            self.supports_soft_delete = True
            self.supports_cdc = True
            
        else:
            raise ValueError(f"Unsupported database type: {self.config.type}")
            
        logger.info(f"Connected to {self.config.type} database")
        
    async def disconnect(self) -> None:
        """Close database connection."""
        if self._pool:
            await self._pool.close()
        elif self._connection:
            self._connection.close()
            
    async def get_all_tables(self) -> List[str]:
        """Get all tables in the database."""
        if self.config.type == DatabaseType.POSTGRESQL:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                """)
                return [row['tablename'] for row in rows]
                
        elif self.config.type == DatabaseType.MYSQL:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = %s",
                        (self.config.database,)
                    )
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]
                    
        elif self.config.type == DatabaseType.MONGODB:
            db = self._connection[self.config.database]
            return await db.list_collection_names()
            
        return []
        
    async def get_table_count(self, table: str) -> int:
        """Get row count for a table."""
        if self.config.type == DatabaseType.POSTGRESQL:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(f"SELECT COUNT(*) FROM {table}")
                return row[0]
                
        elif self.config.type == DatabaseType.MYSQL:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                    row = await cursor.fetchone()
                    return row[0]
                    
        elif self.config.type == DatabaseType.MONGODB:
            db = self._connection[self.config.database]
            collection = db[table]
            return await collection.count_documents({})
            
        return 0
        
    async def get_table_columns(self, table: str) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        columns = []
        
        if self.config.type == DatabaseType.POSTGRESQL:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = $1
                    ORDER BY ordinal_position
                """, table)
                
                for row in rows:
                    columns.append({
                        "name": row["column_name"],
                        "type": row["data_type"],
                        "nullable": row["is_nullable"] == "YES",
                        "default": row["column_default"],
                        "max_length": row["character_maximum_length"]
                    })
                    
        elif self.config.type == DatabaseType.MYSQL:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("""
                        SELECT 
                            column_name,
                            data_type,
                            is_nullable,
                            column_default,
                            character_maximum_length
                        FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = %s
                        ORDER BY ordinal_position
                    """, (table, self.config.database))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        columns.append({
                            "name": row[0],
                            "type": row[1],
                            "nullable": row[2] == "YES",
                            "default": row[3],
                            "max_length": row[4]
                        })
                        
        elif self.config.type == DatabaseType.MONGODB:
            # For MongoDB, sample documents to infer schema
            db = self._connection[self.config.database]
            collection = db[table]
            sample = await collection.find_one()
            
            if sample:
                for key, value in sample.items():
                    columns.append({
                        "name": key,
                        "type": type(value).__name__,
                        "nullable": True,
                        "default": None,
                        "max_length": None
                    })
                    
        return columns
        
    async def get_primary_key(self, table: str) -> Optional[str]:
        """Get primary key column for a table."""
        if self.config.type == DatabaseType.POSTGRESQL:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid
                        AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = $1::regclass
                        AND i.indisprimary
                """, table)
                
                return row["attname"] if row else None
                
        elif self.config.type == DatabaseType.MYSQL:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("""
                        SELECT column_name
                        FROM information_schema.key_column_usage
                        WHERE table_name = %s 
                            AND table_schema = %s
                            AND constraint_name = 'PRIMARY'
                        ORDER BY ordinal_position
                        LIMIT 1
                    """, (table, self.config.database))
                    
                    row = await cursor.fetchone()
                    return row[0] if row else None
                    
        elif self.config.type == DatabaseType.MONGODB:
            # MongoDB uses _id by default
            return "_id"
            
        return None
        
    async def get_foreign_keys(self, table: str) -> List[Dict[str, Any]]:
        """Get foreign key relationships for a table."""
        foreign_keys = []
        
        if self.config.type == DatabaseType.POSTGRESQL:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT
                        tc.constraint_name,
                        kcu.column_name,
                        ccu.table_name AS referenced_table,
                        ccu.column_name AS referenced_column
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = $1
                """, table)
                
                for row in rows:
                    foreign_keys.append({
                        "constraint_name": row["constraint_name"],
                        "column": row["column_name"],
                        "referenced_table": row["referenced_table"],
                        "referenced_column": row["referenced_column"]
                    })
                    
        elif self.config.type == DatabaseType.MYSQL:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("""
                        SELECT
                            constraint_name,
                            column_name,
                            referenced_table_name,
                            referenced_column_name
                        FROM information_schema.key_column_usage
                        WHERE table_name = %s
                            AND table_schema = %s
                            AND referenced_table_name IS NOT NULL
                    """, (table, self.config.database))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        foreign_keys.append({
                            "constraint_name": row[0],
                            "column": row[1],
                            "referenced_table": row[2],
                            "referenced_column": row[3]
                        })
                        
        # MongoDB doesn't have explicit foreign keys
        
        return foreign_keys
        
    async def get_record(
        self,
        table: str,
        pk_value: Any,
        pk_column: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """Get a single record by primary key."""
        if self.config.type == DatabaseType.POSTGRESQL:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    f"SELECT * FROM {table} WHERE {pk_column} = $1",
                    pk_value
                )
                return dict(row) if row else None
                
        elif self.config.type == DatabaseType.MYSQL:
            import aiomysql
            async with self._pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(
                        f"SELECT * FROM `{table}` WHERE `{pk_column}` = %s",
                        (pk_value,)
                    )
                    return await cursor.fetchone()
                    
        elif self.config.type == DatabaseType.MONGODB:
            db = self._connection[self.config.database]
            collection = db[table]
            return await collection.find_one({pk_column: pk_value})
            
        return None
        
    async def insert(self, table: str, data: Dict[str, Any]) -> None:
        """Insert a record into a table."""
        if self.config.type == DatabaseType.POSTGRESQL:
            columns = list(data.keys())
            values = list(data.values())
            placeholders = [f"${i+1}" for i in range(len(values))]
            
            query = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            async with self._pool.acquire() as conn:
                await conn.execute(query, *values)
                
        elif self.config.type == DatabaseType.MYSQL:
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ["%s"] * len(values)
            
            query = f"""
                INSERT INTO `{table}` ({', '.join(f'`{c}`' for c in columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, values)
                    await conn.commit()
                    
        elif self.config.type == DatabaseType.MONGODB:
            db = self._connection[self.config.database]
            collection = db[table]
            await collection.insert_one(data)
            
    async def update(
        self,
        table: str,
        pk_value: Any,
        data: Dict[str, Any],
        pk_column: str = "id"
    ) -> None:
        """Update a record in a table."""
        if self.config.type == DatabaseType.POSTGRESQL:
            set_clauses = []
            values = []
            
            for i, (col, val) in enumerate(data.items()):
                if col != pk_column:
                    set_clauses.append(f"{col} = ${i+1}")
                    values.append(val)
                    
            values.append(pk_value)
            
            query = f"""
                UPDATE {table}
                SET {', '.join(set_clauses)}
                WHERE {pk_column} = ${len(values)}
            """
            
            async with self._pool.acquire() as conn:
                await conn.execute(query, *values)
                
        elif self.config.type == DatabaseType.MYSQL:
            set_clauses = []
            values = []
            
            for col, val in data.items():
                if col != pk_column:
                    set_clauses.append(f"`{col}` = %s")
                    values.append(val)
                    
            values.append(pk_value)
            
            query = f"""
                UPDATE `{table}`
                SET {', '.join(set_clauses)}
                WHERE `{pk_column}` = %s
            """
            
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, values)
                    await conn.commit()
                    
        elif self.config.type == DatabaseType.MONGODB:
            db = self._connection[self.config.database]
            collection = db[table]
            await collection.update_one(
                {pk_column: pk_value},
                {"$set": data}
            )
            
    async def delete(
        self,
        table: str,
        pk_value: Any,
        pk_column: str = "id"
    ) -> None:
        """Delete a record from a table."""
        if self.config.type == DatabaseType.POSTGRESQL:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    f"DELETE FROM {table} WHERE {pk_column} = $1",
                    pk_value
                )
                
        elif self.config.type == DatabaseType.MYSQL:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"DELETE FROM `{table}` WHERE `{pk_column}` = %s",
                        (pk_value,)
                    )
                    await conn.commit()
                    
        elif self.config.type == DatabaseType.MONGODB:
            db = self._connection[self.config.database]
            collection = db[table]
            await collection.delete_one({pk_column: pk_value})
            
    async def get_sample_records(
        self,
        table: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get sample records from a table."""
        if self.config.type == DatabaseType.POSTGRESQL:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    f"SELECT * FROM {table} LIMIT $1",
                    limit
                )
                return [dict(row) for row in rows]
                
        elif self.config.type == DatabaseType.MYSQL:
            import aiomysql
            async with self._pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(
                        f"SELECT * FROM `{table}` LIMIT %s",
                        (limit,)
                    )
                    return await cursor.fetchall()
                    
        elif self.config.type == DatabaseType.MONGODB:
            db = self._connection[self.config.database]
            collection = db[table]
            cursor = collection.find().limit(limit)
            return await cursor.to_list(length=limit)
            
        return []
        
    # Additional methods would be implemented for:
    # - get_tracked_tables()
    # - query_change_log()
    # - get_table_size_mb()
    # - get_stored_procedures()
    # - get_query_logs()
    # - etc.


async def get_database_connection(config: DatabaseConfig) -> DatabaseConnection:
    """Factory function to create database connections."""
    connection = DatabaseConnection(config)
    await connection.connect()
    return connection