"""Privacy-focused query engine for executing queries with privacy safeguards."""

import re
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd

from privacy_query_interpreter.access_logging.logger import (
    AccessLogger, AccessOutcome, AccessType
)
from privacy_query_interpreter.anonymization.anonymizer import (
    DataAnonymizer, AnonymizationMethod
)
from privacy_query_interpreter.data_minimization.minimizer import (
    DataMinimizer, Purpose
)
from privacy_query_interpreter.pii_detection.detector import (
    PIIDetector, PIIMatch
)
from privacy_query_interpreter.policy_enforcement.enforcer import (
    PolicyEnforcer
)
from privacy_query_interpreter.policy_enforcement.policy import (
    PolicyAction
)
from privacy_query_interpreter.query_engine.parser import (
    QueryParser, PrivacyFunction
)


class QueryStatus(str, Enum):
    """Status of query execution."""
    
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"
    MODIFIED = "modified"


class PrivacyQueryEngine:
    """
    Execute and manage SQL queries with privacy controls.
    
    This class integrates all privacy components to execute queries with
    privacy safeguards, including policy enforcement, data minimization,
    access logging, and anonymization.
    """
    
    def __init__(
        self,
        access_logger: Optional[AccessLogger] = None,
        policy_enforcer: Optional[PolicyEnforcer] = None,
        data_minimizer: Optional[DataMinimizer] = None,
        data_anonymizer: Optional[DataAnonymizer] = None,
        pii_detector: Optional[PIIDetector] = None,
        data_sources: Optional[Dict[str, pd.DataFrame]] = None
    ):
        """
        Initialize the privacy query engine.
        
        Args:
            access_logger: Logger for recording access
            policy_enforcer: Enforcer for data access policies
            data_minimizer: Minimizer for data minimization
            data_anonymizer: Anonymizer for sensitive data
            pii_detector: Detector for identifying PII
            data_sources: Dictionary mapping table names to DataFrames
        """
        self.access_logger = access_logger
        self.policy_enforcer = policy_enforcer
        self.data_minimizer = data_minimizer
        self.data_anonymizer = data_anonymizer
        self.pii_detector = pii_detector
        self.data_sources = data_sources or {}
        self.query_parser = QueryParser()
        
        # Query history
        self.query_history = {}
        
        # Privacy extension modifications
        self.anonymization_extensions = {
            func.value: self._handle_anonymize_function
            for func in [
                PrivacyFunction.ANONYMIZE,
                PrivacyFunction.PSEUDONYMIZE,
                PrivacyFunction.MASK,
                PrivacyFunction.REDACT,
                PrivacyFunction.GENERALIZE,
                PrivacyFunction.PERTURB,
                PrivacyFunction.TOKENIZE,
                PrivacyFunction.DIFFERENTIAL
            ]
        }
    
    def execute_query(
        self,
        query: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a SQL query with privacy controls.
        
        Args:
            query: SQL query string
            user_context: User context (user_id, roles, purpose, etc.)
            
        Returns:
            Query result with metadata
        """
        start_time = time.time()
        
        # Generate query ID
        query_id = str(uuid.uuid4())
        
        # Parse the query
        try:
            parsed_query = self.query_parser.parse_query(query)
        except Exception as e:
            return self._create_error_result(
                query_id=query_id,
                query=query,
                user_context=user_context,
                error=f"Query parsing error: {str(e)}",
                execution_time=time.time() - start_time
            )
        
        # Check if this is a SELECT query
        if parsed_query["query_type"] != "SELECT":
            return self._create_error_result(
                query_id=query_id,
                query=query,
                user_context=user_context,
                error="Only SELECT queries are supported",
                execution_time=time.time() - start_time
            )
            
        # Verify that all tables exist
        missing_tables = [t for t in parsed_query["tables"] if t not in self.data_sources]
        if missing_tables:
            return self._create_error_result(
                query_id=query_id,
                query=query,
                user_context=user_context,
                error=f"Tables not found: {', '.join(missing_tables)}",
                execution_time=time.time() - start_time
            )
        
        # Extract query components
        tables = parsed_query["tables"]
        fields = [f["name"] for f in parsed_query["selected_fields"]]
        joins = self.query_parser.extract_table_relationships(query)
        
        # Update status
        query_status = QueryStatus.EXECUTING
        
        # Enforce privacy policies if available
        policy_action = PolicyAction.ALLOW
        policy_reason = None
        
        if self.policy_enforcer:
            is_allowed, action, policy, reason = self.policy_enforcer.enforce_query(
                query_text=query,
                fields=fields,
                data_sources=tables,
                joins=joins,
                user_context=user_context
            )
            
            if not is_allowed:
                if action == PolicyAction.DENY:
                    # Policy enforcement denied the query
                    return self._create_denied_result(
                        query_id=query_id,
                        query=query,
                        user_context=user_context,
                        reason=reason,
                        execution_time=time.time() - start_time
                    )
                # Store policy action for later steps
                policy_action = action
                policy_reason = reason
                query_status = QueryStatus.MODIFIED
        
        # Execute the SQL query
        try:
            result_df = self._execute_sql(parsed_query)
        except Exception as e:
            return self._create_error_result(
                query_id=query_id,
                query=query,
                user_context=user_context,
                error=f"Query execution error: {str(e)}",
                execution_time=time.time() - start_time
            )
        
        # Apply data minimization if necessary
        minimized = False
        if self.data_minimizer and (policy_action == PolicyAction.MINIMIZE or "purpose" in user_context):
            purpose = user_context.get("purpose", "compliance_audit")
            try:
                result_df = self.data_minimizer.apply_to_dataframe(result_df, purpose)
                minimized = True
                query_status = QueryStatus.MODIFIED
            except Exception as e:
                # Log the error but continue processing
                print(f"Data minimization error: {str(e)}")
        
        # Apply anonymization if necessary
        anonymized = False
        if self.data_anonymizer and policy_action == PolicyAction.ANONYMIZE:
            try:
                anonymization_config = self._create_anonymization_config(result_df)
                result_df = self.data_anonymizer.anonymize_dataframe(result_df, anonymization_config)
                anonymized = True
                query_status = QueryStatus.MODIFIED
            except Exception as e:
                # Log the error but continue processing
                print(f"Anonymization error: {str(e)}")
                
        # Also handle any explicit privacy functions in the query
        if self.data_anonymizer and parsed_query["privacy_functions"]:
            modified_df = self._apply_privacy_functions(result_df, parsed_query["privacy_functions"])
            if modified_df is not None:
                result_df = modified_df
                anonymized = True
                query_status = QueryStatus.MODIFIED
        
        # Log the access if a logger is available
        if self.access_logger:
            outcome = AccessOutcome.SUCCESS
            if query_status == QueryStatus.DENIED:
                outcome = AccessOutcome.DENIED
            elif minimized:
                outcome = AccessOutcome.MINIMIZED
            elif anonymized:
                outcome = AccessOutcome.ANONYMIZED
                
            self.access_logger.log_query(
                user_id=user_context.get("user_id", "unknown"),
                query=query,
                data_sources=tables,
                purpose=user_context.get("purpose", ""),
                fields_accessed=list(result_df.columns),
                outcome=outcome,
                execution_time_ms=int((time.time() - start_time) * 1000),
                query_id=query_id,
                contains_pii=self._check_for_pii(result_df)
            )
        
        # Update query history
        self.query_history[query_id] = {
            "query": query,
            "timestamp": time.time(),
            "user_id": user_context.get("user_id", "unknown"),
            "status": query_status,
            "tables": tables,
            "fields": list(result_df.columns),
            "execution_time_ms": int((time.time() - start_time) * 1000)
        }
        
        # Return the result
        return {
            "query_id": query_id,
            "status": query_status.value,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "row_count": len(result_df),
            "column_count": len(result_df.columns),
            "columns": list(result_df.columns),
            "data": result_df.to_dict(orient="records"),
            "minimized": minimized,
            "anonymized": anonymized,
            "privacy_reason": policy_reason
        }
    
    def _execute_sql(self, parsed_query: Dict[str, Any]) -> pd.DataFrame:
        """
        Execute a SQL query on in-memory DataFrames.

        Args:
            parsed_query: Parsed query information

        Returns:
            DataFrame with query results
        """
        # This is a simplified implementation that only handles basic SELECT queries
        # A full implementation would use a SQL engine like SQLite, DuckDB, or pandasql

        # Check for None or invalid parsed_query
        if not parsed_query:
            raise ValueError("Invalid parsed query")

        query_type = parsed_query.get("query_type")
        if query_type != "SELECT":
            raise ValueError(f"Unsupported query type: {query_type}")

        # Get tables
        tables = parsed_query.get("tables", [])
        if not tables:
            raise ValueError("No tables specified in query")

        # Start with the first table
        main_table = tables[0]
        if main_table not in self.data_sources:
            raise ValueError(f"Table not found: {main_table}")

        result = self.data_sources[main_table].copy()
        
        # Apply joins if present
        joins = parsed_query.get("joins", [])
        for join in joins:
            join_table = join.get("table")
            if not join_table or join_table not in self.data_sources:
                raise ValueError(f"Join table not found: {join_table}")

            # Extract tables and fields from the join condition
            condition = join.get("condition")
            if not condition:
                raise ValueError(f"No condition specified for join with {join_table}")

            # Parse the join condition (assuming format "table1.field1 = table2.field2")
            match = re.match(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', condition)
            if not match:
                # Try alternative parsing
                try:
                    # For simpler conditions, try to extract field names
                    parts = condition.split("=")
                    if len(parts) != 2:
                        raise ValueError(f"Invalid join condition: {condition}")

                    left_part = parts[0].strip()
                    right_part = parts[1].strip()

                    left_table_field = left_part.split(".")
                    right_table_field = right_part.split(".")

                    if len(left_table_field) == 2 and len(right_table_field) == 2:
                        left_table, left_field = left_table_field
                        right_table, right_field = right_table_field
                    else:
                        # Can't parse, default to simple join on 'id'
                        left_table = main_table
                        left_field = "id"
                        right_table = join_table
                        right_field = f"{main_table}_id"
                except Exception:
                    # If parsing fails, use default join fields
                    left_table = main_table
                    left_field = "id"
                    right_table = join_table
                    right_field = f"{main_table}_id"
            else:
                left_table, left_field, right_table, right_field = match.groups()

            # Determine which is the main table and which is the join table
            if left_table == main_table:
                left_on = left_field
                right_on = right_field
            else:
                left_on = right_field
                right_on = left_field

            # Perform the join
            join_type = join.get("type", "")
            how = "inner" if "INNER" in join_type else "left"

            try:
                result = pd.merge(
                    result,
                    self.data_sources[join_table],
                    left_on=left_on,
                    right_on=right_on,
                    how=how
                )
            except KeyError:
                # If the join fails due to missing columns, try to join on common columns
                common_cols = set(result.columns) & set(self.data_sources[join_table].columns)
                if common_cols:
                    join_col = list(common_cols)[0]
                    result = pd.merge(
                        result,
                        self.data_sources[join_table],
                        on=join_col,
                        how=how
                    )
                else:
                    raise ValueError(f"Cannot join tables: no common columns between {main_table} and {join_table}")
            
        # Apply WHERE conditions (simplified)
        where_conditions = parsed_query.get("where_conditions", [])
        for condition in where_conditions:
            try:
                # This is a very simplified approach - in a real implementation, you would
                # properly parse and translate the SQL conditions to pandas operations
                # For demonstration, just handle simple equality conditions
                match = re.match(r'(\w+)\.(\w+)\s*=\s*["\'](.*)["\']', condition)
                if match:
                    table, field, value = match.groups()
                    if field in result.columns:
                        result = result[result[field] == value]
                elif "=" in condition:
                    # Try simpler condition parsing
                    parts = condition.split("=", 1)
                    if len(parts) == 2:
                        field_part = parts[0].strip()
                        value_part = parts[1].strip()

                        # Remove table prefix if present
                        if "." in field_part:
                            field_part = field_part.split(".", 1)[1]

                        # Handle quoted value
                        if (value_part.startswith("'") and value_part.endswith("'")) or \
                           (value_part.startswith('"') and value_part.endswith('"')):
                            value_part = value_part[1:-1]

                        if field_part in result.columns:
                            result = result[result[field_part] == value_part]
            except Exception:
                # If condition parsing fails, skip it
                continue

        # Select only the requested fields
        selected_fields = parsed_query.get("selected_fields", [])

        # Handle SELECT *
        if len(selected_fields) == 1 and selected_fields[0].get("name") == "*":
            return result

        # Handle specific fields
        field_names = []
        for field in selected_fields:
            # For simplicity, ignore table prefixes in field names
            field_name = field.get("name")
            if not field_name:
                continue

            if "." in field_name:
                field_name = field_name.split(".", 1)[1]

            field_names.append(field_name)

        # Select only the fields that exist in the result
        valid_field_names = [f for f in field_names if f in result.columns]
        if not valid_field_names:
            # If no valid fields, return all columns as a fallback
            return result

        result = result[valid_field_names]

        # Handle GROUP BY if present
        group_by = parsed_query.get("group_by", [])
        if group_by:
            try:
                # Extract the field names from the GROUP BY clause
                group_fields = []
                for field in group_by:
                    # Remove table prefix if present
                    if "." in field:
                        field = field.split(".", 1)[1]
                    if field in result.columns:
                        group_fields.append(field)

                # Group the data if there are valid fields
                if group_fields:
                    result = result.groupby(group_fields).first().reset_index()
            except Exception:
                # If grouping fails, continue with ungrouped data
                pass

        # Handle ORDER BY if present
        order_by = parsed_query.get("order_by", [])
        if order_by:
            try:
                # Extract the field names from the ORDER BY clause
                order_fields = []
                ascending = []

                for field in order_by:
                    # Check for DESC/ASC
                    is_ascending = True
                    if " DESC" in field.upper():
                        is_ascending = False
                        field = field.split(" ")[0]
                    elif " ASC" in field.upper():
                        field = field.split(" ")[0]

                    # Remove table prefix if present
                    if "." in field:
                        field = field.split(".", 1)[1]

                    # Only include fields that actually exist in the result
                    if field in result.columns:
                        order_fields.append(field)
                        ascending.append(is_ascending)

                # Sort the data if there are valid fields
                if order_fields:
                    result = result.sort_values(by=order_fields, ascending=ascending)
            except Exception:
                # If sorting fails, continue with unsorted data
                pass

        # Handle LIMIT if present
        limit = parsed_query.get("limit")
        if limit is not None:
            try:
                limit = int(limit)
                result = result.head(limit)
            except (ValueError, TypeError):
                # If limit isn't a valid integer, ignore it
                pass

        return result
    
    def _create_error_result(
        self,
        query_id: str,
        query: str,
        user_context: Dict[str, Any],
        error: str,
        execution_time: float
    ) -> Dict[str, Any]:
        """Create an error result structure."""
        # Log the error if a logger is available
        if self.access_logger:
            self.access_logger.log_query(
                user_id=user_context.get("user_id", "unknown"),
                query=query,
                data_sources=[],  # No tables accessed
                purpose=user_context.get("purpose", ""),
                outcome=AccessOutcome.ERROR,
                execution_time_ms=int(execution_time * 1000),
                query_id=query_id,
                metadata={"error": error}
            )
            
        # Update query history
        self.query_history[query_id] = {
            "query": query,
            "timestamp": time.time(),
            "user_id": user_context.get("user_id", "unknown"),
            "status": QueryStatus.FAILED,
            "execution_time_ms": int(execution_time * 1000),
            "error": error
        }
        
        return {
            "query_id": query_id,
            "status": QueryStatus.FAILED.value,
            "execution_time_ms": int(execution_time * 1000),
            "error": error
        }
    
    def _create_denied_result(
        self,
        query_id: str,
        query: str,
        user_context: Dict[str, Any],
        reason: str,
        execution_time: float
    ) -> Dict[str, Any]:
        """Create a denied result structure."""
        # Log the denial if a logger is available
        if self.access_logger:
            self.access_logger.log_query(
                user_id=user_context.get("user_id", "unknown"),
                query=query,
                data_sources=[],  # No tables accessed
                purpose=user_context.get("purpose", ""),
                outcome=AccessOutcome.DENIED,
                execution_time_ms=int(execution_time * 1000),
                query_id=query_id,
                metadata={"reason": reason}
            )
            
        # Update query history
        self.query_history[query_id] = {
            "query": query,
            "timestamp": time.time(),
            "user_id": user_context.get("user_id", "unknown"),
            "status": QueryStatus.DENIED,
            "execution_time_ms": int(execution_time * 1000),
            "reason": reason
        }
        
        return {
            "query_id": query_id,
            "status": QueryStatus.DENIED.value,
            "execution_time_ms": int(execution_time * 1000),
            "reason": reason
        }
    
    def _check_for_pii(self, df: pd.DataFrame) -> bool:
        """
        Check if a DataFrame contains PII.
        
        Args:
            df: DataFrame to check
            
        Returns:
            True if PII is detected
        """
        if not self.pii_detector:
            # Conservative approach - assume it contains PII if we can't check
            return True
            
        # Use the PII detector to scan for PII
        matches = self.pii_detector.detect_in_dataframe(df, sample_size=min(100, len(df)))
        return len(matches) > 0
    
    def _create_anonymization_config(self, df: pd.DataFrame) -> Dict[str, AnonymizationMethod]:
        """
        Create an anonymization configuration for a DataFrame.
        
        Args:
            df: DataFrame to configure anonymization for
            
        Returns:
            Dictionary mapping column names to anonymization methods
        """
        config = {}
        
        # If we have a PII detector, use it to identify sensitive fields
        if self.pii_detector and self.data_anonymizer:
            # Detect PII in the DataFrame
            matches = self.pii_detector.detect_in_dataframe(df, sample_size=min(100, len(df)))
            
            # Group by field name
            for match in matches:
                if match.field_name not in config and match.field_name in df.columns:
                    # Get the appropriate method for this type of PII
                    method = self.data_anonymizer.guess_anonymization_method(
                        match.field_name, match.pii_type, match.sample_value
                    )
                    config[match.field_name] = method
        else:
            # Without a PII detector, use conservative defaults
            for column in df.columns:
                column_lower = column.lower()
                
                # Check common PII fields
                if any(pii_term in column_lower for pii_term in [
                    "name", "email", "phone", "ssn", "social", "address", "zip", "postal",
                    "birth", "age", "gender", "credit", "card", "account", "password",
                    "salary", "income"
                ]):
                    config[column] = AnonymizationMethod.MASK
                    
        return config
    
    def _apply_privacy_functions(
        self,
        df: pd.DataFrame,
        privacy_functions: List[Dict[str, Any]]
    ) -> Optional[pd.DataFrame]:
        """
        Apply privacy functions specified in the query.
        
        Args:
            df: DataFrame to apply functions to
            privacy_functions: List of privacy functions from the parsed query
            
        Returns:
            Modified DataFrame or None if no changes were made
        """
        if not privacy_functions or not self.data_anonymizer:
            return None
            
        # Create a copy of the DataFrame
        result = df.copy()
        modified = False
        
        for func in privacy_functions:
            function_name = func["function"]
            field_name = func["field"]
            args = func["args"]
            
            # Skip if field doesn't exist
            if field_name not in df.columns:
                continue
                
            # Apply the appropriate anonymization method
            handler = self.anonymization_extensions.get(function_name)
            if handler:
                result = handler(result, field_name, args)
                modified = True
                
        return result if modified else None
    
    def _handle_anonymize_function(
        self,
        df: pd.DataFrame,
        field_name: str,
        args: Dict[str, Any]
    ) -> pd.DataFrame:
        """Handle ANONYMIZE function."""
        if not self.data_anonymizer:
            return df
            
        # Determine method to use
        method = AnonymizationMethod.HASH
        if "method" in args:
            method_name = args["method"].upper()
            try:
                method = AnonymizationMethod(method_name)
            except ValueError:
                # Use default method
                pass
                
        # Apply anonymization
        result = df.copy()
        result[field_name] = result[field_name].apply(
            lambda x: self.data_anonymizer.anonymize_value(x, method, field_name=field_name, **args)
        )
        
        return result
    
    def add_data_source(self, name: str, df: pd.DataFrame) -> None:
        """
        Add a DataFrame as a data source.
        
        Args:
            name: Name of the data source
            df: DataFrame to use as a data source
        """
        self.data_sources[name] = df
    
    def remove_data_source(self, name: str) -> bool:
        """
        Remove a data source.
        
        Args:
            name: Name of the data source
            
        Returns:
            True if the data source was removed
        """
        if name in self.data_sources:
            del self.data_sources[name]
            return True
        return False
    
    def get_query_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent query history.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Maximum number of queries to return
            
        Returns:
            List of query history records
        """
        # Get all queries and sort by timestamp (newest first)
        history = sorted(
            self.query_history.values(),
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        # Filter by user ID if specified
        if user_id:
            history = [q for q in history if q.get("user_id") == user_id]
            
        # Limit the number of results
        return history[:limit]