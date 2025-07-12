"""Consistency validator for data migration."""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import uuid4
import hashlib
import json

from pymigrate.models.data import ConsistencyReport
from pymigrate.validator.checksum import ChecksumValidator
from pymigrate.validator.reconciliation import DataReconciler
from pymigrate.utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class ConsistencyValidator:
    """Validates data consistency between source and target systems."""
    
    def __init__(
        self,
        source_conn: DatabaseConnection,
        target_conn: DatabaseConnection
    ):
        """Initialize consistency validator."""
        self.source_conn = source_conn
        self.target_conn = target_conn
        self.checksum_validator = ChecksumValidator()
        self.reconciler = DataReconciler()
        self._validation_history: List[ConsistencyReport] = []
        
    async def validate_consistency(
        self,
        tables: Optional[List[str]] = None,
        sample_size: Optional[int] = None,
        deep_check: bool = True
    ) -> ConsistencyReport:
        """Perform consistency validation between source and target."""
        validation_id = str(uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Starting consistency validation {validation_id}")
        
        # Get tables to validate
        if not tables:
            tables = await self._get_common_tables()
            
        discrepancies = []
        total_records = 0
        consistent_records = 0
        inconsistent_records = 0
        checksum_mismatches = []
        
        # Validate each table
        for table in tables:
            table_result = await self._validate_table(
                table,
                sample_size,
                deep_check
            )
            
            total_records += table_result["total_records"]
            consistent_records += table_result["consistent_records"]
            inconsistent_records += table_result["inconsistent_records"]
            
            if table_result["discrepancies"]:
                discrepancies.extend(table_result["discrepancies"])
                
            if table_result["checksum_mismatches"]:
                checksum_mismatches.extend(table_result["checksum_mismatches"])
                
        # Calculate validation duration
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Create report
        report = ConsistencyReport(
            validation_id=validation_id,
            timestamp=start_time,
            tables_checked=tables,
            total_records=total_records,
            consistent_records=consistent_records,
            inconsistent_records=inconsistent_records,
            discrepancies=discrepancies,
            validation_duration_ms=duration_ms,
            checksum_mismatches=checksum_mismatches
        )
        
        self._validation_history.append(report)
        
        logger.info(
            f"Validation complete. Consistency: {report.consistency_percentage:.2f}%"
        )
        
        return report
        
    async def _get_common_tables(self) -> List[str]:
        """Get tables that exist in both source and target."""
        source_tables = set(await self.source_conn.get_all_tables())
        target_tables = set(await self.target_conn.get_all_tables())
        
        common_tables = list(source_tables.intersection(target_tables))
        
        if source_tables - target_tables:
            logger.warning(
                f"Tables only in source: {source_tables - target_tables}"
            )
            
        if target_tables - source_tables:
            logger.warning(
                f"Tables only in target: {target_tables - source_tables}"
            )
            
        return common_tables
        
    async def _validate_table(
        self,
        table: str,
        sample_size: Optional[int],
        deep_check: bool
    ) -> Dict[str, Any]:
        """Validate consistency for a single table."""
        logger.info(f"Validating table: {table}")
        
        # Get record counts
        source_count = await self.source_conn.get_table_count(table)
        target_count = await self.target_conn.get_table_count(table)
        
        result = {
            "table": table,
            "total_records": source_count,
            "consistent_records": 0,
            "inconsistent_records": 0,
            "discrepancies": [],
            "checksum_mismatches": []
        }
        
        # Check count mismatch
        if source_count != target_count:
            result["discrepancies"].append({
                "type": "count_mismatch",
                "table": table,
                "source_count": source_count,
                "target_count": target_count,
                "difference": abs(source_count - target_count)
            })
            
        if deep_check and source_count > 0:
            # Determine sample size
            if sample_size is None:
                # Use adaptive sampling
                if source_count <= 10000:
                    sample_size = source_count  # Check all records
                elif source_count <= 100000:
                    sample_size = 10000
                else:
                    sample_size = int(source_count * 0.1)  # 10% sample
                    
            # Validate records
            validation_result = await self._validate_records(
                table,
                min(sample_size, source_count)
            )
            
            result["consistent_records"] = validation_result["consistent"]
            result["inconsistent_records"] = validation_result["inconsistent"]
            
            if validation_result["discrepancies"]:
                result["discrepancies"].extend(validation_result["discrepancies"])
                
            if validation_result["checksum_mismatches"]:
                result["checksum_mismatches"].extend(
                    validation_result["checksum_mismatches"]
                )
        else:
            # For shallow check, assume consistent if counts match
            if source_count == target_count:
                result["consistent_records"] = source_count
                
        return result
        
    async def _validate_records(
        self,
        table: str,
        sample_size: int
    ) -> Dict[str, Any]:
        """Validate individual records in a table."""
        # Get primary key column
        pk_column = await self.source_conn.get_primary_key(table)
        
        if not pk_column:
            logger.warning(f"No primary key found for table {table}")
            return {
                "consistent": 0,
                "inconsistent": sample_size,
                "discrepancies": [{
                    "type": "no_primary_key",
                    "table": table
                }],
                "checksum_mismatches": []
            }
            
        # Get sample records from source
        source_records = await self.source_conn.get_sample_records(
            table,
            sample_size
        )
        
        consistent = 0
        inconsistent = 0
        discrepancies = []
        checksum_mismatches = []
        
        # Batch fetch target records for efficiency
        pk_values = [r[pk_column] for r in source_records]
        target_records_dict = await self._batch_fetch_target_records(
            table,
            pk_column,
            pk_values
        )
        
        # Compare records
        for source_record in source_records:
            pk_value = source_record[pk_column]
            target_record = target_records_dict.get(pk_value)
            
            if not target_record:
                inconsistent += 1
                discrepancies.append({
                    "type": "missing_in_target",
                    "table": table,
                    "primary_key": pk_value
                })
                continue
                
            # Compare checksums
            source_checksum = self.checksum_validator.calculate_checksum(
                source_record
            )
            target_checksum = self.checksum_validator.calculate_checksum(
                target_record
            )
            
            if source_checksum != target_checksum:
                inconsistent += 1
                
                # Find specific differences
                differences = self._find_differences(
                    source_record,
                    target_record
                )
                
                checksum_mismatches.append({
                    "table": table,
                    "primary_key": pk_value,
                    "source_checksum": source_checksum,
                    "target_checksum": target_checksum,
                    "differences": differences
                })
            else:
                consistent += 1
                
        # Check for extra records in target
        target_only_count = await self._check_target_only_records(
            table,
            pk_column,
            pk_values
        )
        
        if target_only_count > 0:
            discrepancies.append({
                "type": "extra_in_target",
                "table": table,
                "count": target_only_count
            })
            
        return {
            "consistent": consistent,
            "inconsistent": inconsistent,
            "discrepancies": discrepancies,
            "checksum_mismatches": checksum_mismatches
        }
        
    async def _batch_fetch_target_records(
        self,
        table: str,
        pk_column: str,
        pk_values: List[Any]
    ) -> Dict[Any, Dict[str, Any]]:
        """Batch fetch records from target database."""
        # Fetch in batches to avoid query size limits
        batch_size = 1000
        all_records = {}
        
        for i in range(0, len(pk_values), batch_size):
            batch_values = pk_values[i:i + batch_size]
            records = await self.target_conn.get_records_by_ids(
                table,
                pk_column,
                batch_values
            )
            
            for record in records:
                all_records[record[pk_column]] = record
                
        return all_records
        
    async def _check_target_only_records(
        self,
        table: str,
        pk_column: str,
        source_pk_values: List[Any]
    ) -> int:
        """Check for records that exist only in target."""
        # This is a simplified check - in production, implement proper set difference
        target_count = await self.target_conn.get_table_count(table)
        
        if target_count > len(source_pk_values):
            return target_count - len(source_pk_values)
            
        return 0
        
    def _find_differences(
        self,
        source_record: Dict[str, Any],
        target_record: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find specific differences between records."""
        differences = []
        
        all_keys = set(source_record.keys()) | set(target_record.keys())
        
        for key in all_keys:
            source_val = source_record.get(key)
            target_val = target_record.get(key)
            
            if source_val != target_val:
                differences.append({
                    "field": key,
                    "source_value": source_val,
                    "target_value": target_val
                })
                
        return differences
        
    async def continuous_validation(
        self,
        tables: List[str],
        interval_seconds: int = 300,
        alert_threshold: float = 0.95
    ) -> None:
        """Run continuous validation with alerts."""
        logger.info(
            f"Starting continuous validation every {interval_seconds} seconds"
        )
        
        while True:
            try:
                report = await self.validate_consistency(
                    tables=tables,
                    deep_check=True
                )
                
                # Check if consistency dropped below threshold
                if report.consistency_percentage < alert_threshold * 100:
                    await self._send_alert(report)
                    
                # Sleep until next validation
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in continuous validation: {e}")
                await asyncio.sleep(interval_seconds)
                
    async def _send_alert(self, report: ConsistencyReport) -> None:
        """Send alert for consistency issues."""
        logger.warning(
            f"ALERT: Data consistency dropped to {report.consistency_percentage:.2f}%"
        )
        
        # In production, integrate with alerting system
        # For now, just log the most critical issues
        critical_issues = []
        
        for discrepancy in report.discrepancies:
            if discrepancy["type"] == "count_mismatch":
                diff = discrepancy["difference"]
                if diff > 100:
                    critical_issues.append(
                        f"Table {discrepancy['table']}: {diff} record difference"
                    )
                    
        if critical_issues:
            logger.error(f"Critical issues: {', '.join(critical_issues)}")
            
    async def reconcile_discrepancies(
        self,
        report: ConsistencyReport,
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """Reconcile discrepancies found during validation."""
        return await self.reconciler.reconcile(
            self.source_conn,
            self.target_conn,
            report,
            auto_fix=auto_fix
        )
        
    def get_validation_history(
        self,
        limit: int = 100
    ) -> List[ConsistencyReport]:
        """Get validation history."""
        return self._validation_history[-limit:]
        
    def get_consistency_trends(self) -> Dict[str, Any]:
        """Analyze consistency trends over time."""
        if not self._validation_history:
            return {}
            
        recent_reports = self._validation_history[-24:]  # Last 24 validations
        
        percentages = [r.consistency_percentage for r in recent_reports]
        
        return {
            "current": percentages[-1] if percentages else 0,
            "average": sum(percentages) / len(percentages) if percentages else 0,
            "min": min(percentages) if percentages else 0,
            "max": max(percentages) if percentages else 0,
            "trend": "improving" if len(percentages) > 1 and percentages[-1] > percentages[0] else "declining",
            "samples": len(percentages)
        }