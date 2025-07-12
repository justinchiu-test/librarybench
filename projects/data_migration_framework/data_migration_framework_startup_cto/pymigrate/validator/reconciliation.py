"""Data reconciliation for consistency issues."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from pymigrate.models.data import ConsistencyReport, DataChange, ChangeType
from pymigrate.utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class DataReconciler:
    """Reconciles data discrepancies between systems."""
    
    async def reconcile(
        self,
        source_conn: DatabaseConnection,
        target_conn: DatabaseConnection,
        report: ConsistencyReport,
        auto_fix: bool = False,
        strategy: str = "source_wins"
    ) -> Dict[str, Any]:
        """Reconcile discrepancies found in consistency report."""
        logger.info(f"Starting reconciliation for validation {report.validation_id}")
        
        results = {
            "validation_id": report.validation_id,
            "started_at": datetime.utcnow(),
            "strategy": strategy,
            "auto_fix": auto_fix,
            "fixed": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        # Handle count mismatches
        for discrepancy in report.discrepancies:
            if discrepancy["type"] == "count_mismatch":
                result = await self._reconcile_count_mismatch(
                    source_conn,
                    target_conn,
                    discrepancy,
                    auto_fix,
                    strategy
                )
                results["details"].append(result)
                
                if result["status"] == "fixed":
                    results["fixed"] += result.get("records_affected", 0)
                elif result["status"] == "failed":
                    results["failed"] += 1
                else:
                    results["skipped"] += 1
                    
            elif discrepancy["type"] == "missing_in_target":
                result = await self._reconcile_missing_record(
                    source_conn,
                    target_conn,
                    discrepancy,
                    auto_fix
                )
                results["details"].append(result)
                
                if result["status"] == "fixed":
                    results["fixed"] += 1
                elif result["status"] == "failed":
                    results["failed"] += 1
                else:
                    results["skipped"] += 1
                    
        # Handle checksum mismatches
        for mismatch in report.checksum_mismatches:
            result = await self._reconcile_checksum_mismatch(
                source_conn,
                target_conn,
                mismatch,
                auto_fix,
                strategy
            )
            results["details"].append(result)
            
            if result["status"] == "fixed":
                results["fixed"] += 1
            elif result["status"] == "failed":
                results["failed"] += 1
            else:
                results["skipped"] += 1
                
        results["completed_at"] = datetime.utcnow()
        results["duration_seconds"] = (
            results["completed_at"] - results["started_at"]
        ).total_seconds()
        
        logger.info(
            f"Reconciliation complete. Fixed: {results['fixed']}, "
            f"Failed: {results['failed']}, Skipped: {results['skipped']}"
        )
        
        return results
        
    async def _reconcile_count_mismatch(
        self,
        source_conn: DatabaseConnection,
        target_conn: DatabaseConnection,
        discrepancy: Dict[str, Any],
        auto_fix: bool,
        strategy: str
    ) -> Dict[str, Any]:
        """Reconcile count mismatch between source and target."""
        table = discrepancy["table"]
        source_count = discrepancy["source_count"]
        target_count = discrepancy["target_count"]
        
        logger.info(
            f"Reconciling count mismatch for {table}: "
            f"source={source_count}, target={target_count}"
        )
        
        result = {
            "type": "count_mismatch",
            "table": table,
            "status": "pending",
            "actions": []
        }
        
        if source_count > target_count:
            # Missing records in target
            missing_count = source_count - target_count
            
            if auto_fix:
                try:
                    # Find and copy missing records
                    copied = await self._copy_missing_records(
                        source_conn,
                        target_conn,
                        table,
                        missing_count
                    )
                    
                    result["status"] = "fixed"
                    result["records_affected"] = copied
                    result["actions"].append(
                        f"Copied {copied} missing records to target"
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to copy missing records: {e}")
                    result["status"] = "failed"
                    result["error"] = str(e)
            else:
                result["status"] = "skipped"
                result["recommendation"] = (
                    f"Copy {missing_count} missing records from source to target"
                )
                
        elif target_count > source_count:
            # Extra records in target
            extra_count = target_count - source_count
            
            if strategy == "source_wins" and auto_fix:
                try:
                    # Remove extra records from target
                    removed = await self._remove_extra_records(
                        source_conn,
                        target_conn,
                        table,
                        extra_count
                    )
                    
                    result["status"] = "fixed"
                    result["records_affected"] = removed
                    result["actions"].append(
                        f"Removed {removed} extra records from target"
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to remove extra records: {e}")
                    result["status"] = "failed"
                    result["error"] = str(e)
            else:
                result["status"] = "skipped"
                result["recommendation"] = (
                    f"Review {extra_count} extra records in target"
                )
                
        return result
        
    async def _reconcile_missing_record(
        self,
        source_conn: DatabaseConnection,
        target_conn: DatabaseConnection,
        discrepancy: Dict[str, Any],
        auto_fix: bool
    ) -> Dict[str, Any]:
        """Reconcile a missing record in target."""
        table = discrepancy["table"]
        pk_value = discrepancy["primary_key"]
        
        result = {
            "type": "missing_record",
            "table": table,
            "primary_key": pk_value,
            "status": "pending"
        }
        
        if auto_fix:
            try:
                # Get primary key column
                pk_column = await source_conn.get_primary_key(table)
                
                # Fetch record from source
                source_record = await source_conn.get_record(
                    table,
                    pk_value,
                    pk_column
                )
                
                if source_record:
                    # Insert into target
                    await target_conn.insert(table, source_record)
                    
                    result["status"] = "fixed"
                    result["action"] = "Copied record from source to target"
                else:
                    result["status"] = "failed"
                    result["error"] = "Record not found in source"
                    
            except Exception as e:
                logger.error(f"Failed to copy missing record: {e}")
                result["status"] = "failed"
                result["error"] = str(e)
        else:
            result["status"] = "skipped"
            result["recommendation"] = "Copy record from source to target"
            
        return result
        
    async def _reconcile_checksum_mismatch(
        self,
        source_conn: DatabaseConnection,
        target_conn: DatabaseConnection,
        mismatch: Dict[str, Any],
        auto_fix: bool,
        strategy: str
    ) -> Dict[str, Any]:
        """Reconcile checksum mismatch between records."""
        table = mismatch["table"]
        pk_value = mismatch["primary_key"]
        differences = mismatch["differences"]
        
        result = {
            "type": "checksum_mismatch",
            "table": table,
            "primary_key": pk_value,
            "status": "pending",
            "differences": differences
        }
        
        if auto_fix:
            try:
                if strategy == "source_wins":
                    # Update target with source data
                    pk_column = await source_conn.get_primary_key(table)
                    source_record = await source_conn.get_record(
                        table,
                        pk_value,
                        pk_column
                    )
                    
                    if source_record:
                        await target_conn.update(
                            table,
                            pk_value,
                            source_record,
                            pk_column
                        )
                        
                        result["status"] = "fixed"
                        result["action"] = "Updated target with source data"
                    else:
                        result["status"] = "failed"
                        result["error"] = "Source record not found"
                        
                elif strategy == "target_wins":
                    # Update source with target data
                    pk_column = await target_conn.get_primary_key(table)
                    target_record = await target_conn.get_record(
                        table,
                        pk_value,
                        pk_column
                    )
                    
                    if target_record:
                        await source_conn.update(
                            table,
                            pk_value,
                            target_record,
                            pk_column
                        )
                        
                        result["status"] = "fixed"
                        result["action"] = "Updated source with target data"
                    else:
                        result["status"] = "failed"
                        result["error"] = "Target record not found"
                        
                else:
                    result["status"] = "skipped"
                    result["error"] = f"Unknown strategy: {strategy}"
                    
            except Exception as e:
                logger.error(f"Failed to reconcile checksum mismatch: {e}")
                result["status"] = "failed"
                result["error"] = str(e)
        else:
            result["status"] = "skipped"
            result["recommendation"] = (
                f"Review differences and update based on {strategy} strategy"
            )
            
        return result
        
    async def _copy_missing_records(
        self,
        source_conn: DatabaseConnection,
        target_conn: DatabaseConnection,
        table: str,
        limit: int
    ) -> int:
        """Copy missing records from source to target."""
        # Get primary key
        pk_column = await source_conn.get_primary_key(table)
        
        # Get all PKs from both databases
        source_pks = set(await source_conn.get_all_primary_keys(table, pk_column))
        target_pks = set(await target_conn.get_all_primary_keys(table, pk_column))
        
        # Find missing PKs
        missing_pks = list(source_pks - target_pks)[:limit]
        
        # Copy records
        copied = 0
        for pk in missing_pks:
            try:
                record = await source_conn.get_record(table, pk, pk_column)
                if record:
                    await target_conn.insert(table, record)
                    copied += 1
            except Exception as e:
                logger.error(f"Failed to copy record {pk}: {e}")
                
        return copied
        
    async def _remove_extra_records(
        self,
        source_conn: DatabaseConnection,
        target_conn: DatabaseConnection,
        table: str,
        limit: int
    ) -> int:
        """Remove extra records from target."""
        # Get primary key
        pk_column = await target_conn.get_primary_key(table)
        
        # Get all PKs from both databases
        source_pks = set(await source_conn.get_all_primary_keys(table, pk_column))
        target_pks = set(await target_conn.get_all_primary_keys(table, pk_column))
        
        # Find extra PKs
        extra_pks = list(target_pks - source_pks)[:limit]
        
        # Remove records
        removed = 0
        for pk in extra_pks:
            try:
                await target_conn.delete(table, pk, pk_column)
                removed += 1
            except Exception as e:
                logger.error(f"Failed to remove record {pk}: {e}")
                
        return removed