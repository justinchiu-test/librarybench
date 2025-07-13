"""Access pattern analysis for database tables."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
import re

from pymigrate.utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class AccessPatternAnalyzer:
    """Analyzes data access patterns to identify service boundaries."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize access pattern analyzer."""
        self.connection = connection
        
    async def analyze_patterns(
        self, 
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze access patterns from query logs."""
        logger.info(f"Analyzing access patterns for last {duration_hours} hours")
        
        # Get query logs
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=duration_hours)
        
        query_logs = await self.connection.get_query_logs(start_time, end_time)
        
        # Analyze patterns
        patterns = {
            "read_patterns": await self._analyze_read_patterns(query_logs),
            "write_patterns": await self._analyze_write_patterns(query_logs),
            "join_patterns": await self._analyze_join_patterns(query_logs),
            "transaction_patterns": await self._analyze_transaction_patterns(query_logs),
            "temporal_patterns": await self._analyze_temporal_patterns(query_logs),
            "patterns": []  # Combined patterns
        }
        
        # Combine insights into service patterns
        patterns["patterns"] = self._combine_patterns(patterns)
        
        return patterns
        
    async def _analyze_read_patterns(
        self, 
        query_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze read access patterns."""
        read_stats = defaultdict(lambda: {
            "count": 0,
            "avg_duration_ms": 0,
            "frequently_with": defaultdict(int)
        })
        
        read_queries = [
            q for q in query_logs 
            if q["query_type"] == "SELECT"
        ]
        
        for query in read_queries:
            tables = self._extract_tables(query["query_text"])
            duration = query.get("duration_ms", 0)
            
            for table in tables:
                stats = read_stats[table]
                stats["count"] += 1
                stats["avg_duration_ms"] = (
                    (stats["avg_duration_ms"] * (stats["count"] - 1) + duration) 
                    / stats["count"]
                )
                
                # Track co-occurrence
                for other_table in tables:
                    if other_table != table:
                        stats["frequently_with"][other_table] += 1
                        
        # Convert to regular dict and calculate percentages
        result = {}
        for table, stats in read_stats.items():
            frequently_with = {
                other: count / stats["count"] 
                for other, count in stats["frequently_with"].items()
                if count / stats["count"] > 0.3  # 30% threshold
            }
            
            result[table] = {
                "count": stats["count"],
                "avg_duration_ms": round(stats["avg_duration_ms"], 2),
                "frequently_accessed_with": frequently_with
            }
            
        return result
        
    async def _analyze_write_patterns(
        self, 
        query_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze write access patterns."""
        write_stats = defaultdict(lambda: {
            "inserts": 0,
            "updates": 0,
            "deletes": 0,
            "in_transactions_with": defaultdict(int)
        })
        
        write_queries = [
            q for q in query_logs 
            if q["query_type"] in ("INSERT", "UPDATE", "DELETE")
        ]
        
        # Group by transaction
        transactions = defaultdict(list)
        for query in write_queries:
            tx_id = query.get("transaction_id", query.get("session_id"))
            if tx_id:
                transactions[tx_id].append(query)
                
        # Analyze each transaction
        for tx_id, queries in transactions.items():
            tables_in_tx = set()
            
            for query in queries:
                tables = self._extract_tables(query["query_text"])
                query_type = query["query_type"]
                
                for table in tables:
                    stats = write_stats[table]
                    
                    if query_type == "INSERT":
                        stats["inserts"] += 1
                    elif query_type == "UPDATE":
                        stats["updates"] += 1
                    elif query_type == "DELETE":
                        stats["deletes"] += 1
                        
                    tables_in_tx.add(table)
                    
            # Track transaction relationships
            for table in tables_in_tx:
                for other in tables_in_tx:
                    if table != other:
                        write_stats[table]["in_transactions_with"][other] += 1
                        
        return dict(write_stats)
        
    async def _analyze_join_patterns(
        self, 
        query_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze table join patterns."""
        join_patterns = defaultdict(lambda: {
            "count": 0,
            "avg_duration_ms": 0,
            "join_types": defaultdict(int)
        })
        
        for query in query_logs:
            if "JOIN" in query["query_text"].upper():
                joins = self._extract_joins(query["query_text"])
                
                for join in joins:
                    key = tuple(sorted([join["left_table"], join["right_table"]]))
                    pattern = join_patterns[key]
                    
                    pattern["count"] += 1
                    pattern["avg_duration_ms"] = (
                        (pattern["avg_duration_ms"] * (pattern["count"] - 1) + 
                         query.get("duration_ms", 0)) / pattern["count"]
                    )
                    pattern["join_types"][join["join_type"]] += 1
                    
        # Convert to list format
        result = []
        for (table1, table2), stats in join_patterns.items():
            result.append({
                "tables": [table1, table2],
                "count": stats["count"],
                "avg_duration_ms": round(stats["avg_duration_ms"], 2),
                "join_types": dict(stats["join_types"])
            })
            
        # Sort by frequency
        result.sort(key=lambda x: x["count"], reverse=True)
        
        return result
        
    async def _analyze_transaction_patterns(
        self, 
        query_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze transaction patterns."""
        transactions = defaultdict(list)
        
        # Group queries by transaction
        for query in query_logs:
            tx_id = query.get("transaction_id")
            if tx_id:
                transactions[tx_id].append(query)
                
        # Analyze transaction patterns
        tx_patterns = defaultdict(lambda: {
            "count": 0,
            "avg_duration_ms": 0,
            "avg_queries": 0
        })
        
        for tx_id, queries in transactions.items():
            if len(queries) < 2:
                continue
                
            # Extract pattern signature
            tables = set()
            operations = []
            
            for query in queries:
                tables.update(self._extract_tables(query["query_text"]))
                operations.append(query["query_type"])
                
            # Create pattern key
            pattern_key = (tuple(sorted(tables)), tuple(operations))
            
            # Update stats
            duration = sum(q.get("duration_ms", 0) for q in queries)
            pattern = tx_patterns[pattern_key]
            
            pattern["count"] += 1
            pattern["avg_duration_ms"] = (
                (pattern["avg_duration_ms"] * (pattern["count"] - 1) + duration) 
                / pattern["count"]
            )
            pattern["avg_queries"] = (
                (pattern["avg_queries"] * (pattern["count"] - 1) + len(queries)) 
                / pattern["count"]
            )
            
        # Convert to list format
        result = []
        for (tables, operations), stats in tx_patterns.items():
            if stats["count"] > 5:  # Minimum threshold
                result.append({
                    "tables": list(tables),
                    "operations": list(operations),
                    "count": stats["count"],
                    "avg_duration_ms": round(stats["avg_duration_ms"], 2),
                    "avg_queries": round(stats["avg_queries"], 1)
                })
                
        return result
        
    async def _analyze_temporal_patterns(
        self, 
        query_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze temporal access patterns."""
        hourly_stats = defaultdict(lambda: defaultdict(int))
        
        for query in query_logs:
            hour = query["timestamp"].hour
            tables = self._extract_tables(query["query_text"])
            
            for table in tables:
                hourly_stats[table][hour] += 1
                
        # Identify peak hours for each table
        result = {}
        for table, hours in hourly_stats.items():
            total = sum(hours.values())
            if total > 0:
                peak_hour = max(hours.items(), key=lambda x: x[1])
                result[table] = {
                    "peak_hour": peak_hour[0],
                    "peak_percentage": round(peak_hour[1] / total * 100, 2),
                    "hourly_distribution": dict(hours)
                }
                
        return result
        
    def _extract_tables(self, query_text: str) -> Set[str]:
        """Extract table names from query text."""
        tables = set()
        
        # Simple regex patterns for table extraction
        # In a real implementation, use a proper SQL parser
        patterns = [
            r"FROM\s+(\w+)",
            r"JOIN\s+(\w+)",
            r"INTO\s+(\w+)",
            r"UPDATE\s+(\w+)",
            r"DELETE\s+FROM\s+(\w+)"
        ]
        
        query_upper = query_text.upper()
        for pattern in patterns:
            matches = re.findall(pattern, query_upper)
            tables.update(match.lower() for match in matches)
            
        return tables
        
    def _extract_joins(self, query_text: str) -> List[Dict[str, Any]]:
        """Extract join information from query."""
        joins = []
        
        # Simple pattern matching - in production use SQL parser
        join_pattern = r"(\w+)\s+(INNER|LEFT|RIGHT|FULL)?\s*JOIN\s+(\w+)"
        
        matches = re.findall(join_pattern, query_text.upper())
        for match in matches:
            joins.append({
                "left_table": match[0].lower(),
                "join_type": match[1] or "INNER",
                "right_table": match[2].lower()
            })
            
        return joins
        
    def _combine_patterns(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine different pattern analyses into service patterns."""
        service_patterns = []
        
        # Find tables that are frequently accessed together
        read_patterns = patterns["read_patterns"]
        
        # Group tables by access patterns
        table_groups = defaultdict(set)
        
        for table, stats in read_patterns.items():
            group_key = tuple(sorted(stats.get("frequently_accessed_with", {}).keys()))
            table_groups[group_key].add(table)
            
        # Create service patterns
        for group_tables, tables in table_groups.items():
            all_tables = set(tables) | set(group_tables)
            
            if len(all_tables) >= 2:
                service_patterns.append({
                    "pattern_type": "frequently_accessed_together",
                    "tables": list(all_tables),
                    "confidence": 0.8
                })
                
        # Add transaction patterns
        for tx_pattern in patterns["transaction_patterns"]:
            if len(tx_pattern["tables"]) >= 2:
                service_patterns.append({
                    "pattern_type": "transactional_boundary",
                    "tables": tx_pattern["tables"],
                    "confidence": 0.9,
                    "details": tx_pattern
                })
                
        return service_patterns