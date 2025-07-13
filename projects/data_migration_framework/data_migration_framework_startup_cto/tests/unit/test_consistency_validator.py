"""Unit tests for Consistency Validator."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from pymigrate.validator.consistency import ConsistencyValidator
from pymigrate.models.data import ConsistencyReport


class TestConsistencyValidator:
    """Test cases for Consistency Validator."""
    
    @pytest.mark.asyncio
    async def test_validator_initialization(self, mock_db_connection):
        """Test consistency validator initialization."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        assert validator.source_conn == source_conn
        assert validator.target_conn == target_conn
        assert validator._validation_history == []
        
    @pytest.mark.asyncio
    async def test_validate_consistency_all_tables(self, mock_db_connection):
        """Test consistency validation for all tables."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        # Mock table operations
        source_conn.get_all_tables.return_value = ["users", "orders", "products"]
        target_conn.get_all_tables.return_value = ["users", "orders", "products", "logs"]
        
        source_conn.get_table_count.return_value = 1000
        target_conn.get_table_count.return_value = 1000
        
        # Mock sample records
        source_conn.get_sample_records.return_value = [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"},
        ]
        
        # Records will be fetched via _batch_fetch_target_records
        
        report = await validator.validate_consistency()
        
        assert isinstance(report, ConsistencyReport)
        assert len(report.tables_checked) == 3  # Common tables only
        assert report.total_records > 0
        assert report.consistency_percentage >= 0
        assert report.validation_duration_ms > 0
        
    @pytest.mark.asyncio
    async def test_count_mismatch_detection(self, mock_db_connection):
        """Test detection of record count mismatches."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        # Setup count mismatch
        source_conn.get_all_tables.return_value = ["users"]
        target_conn.get_all_tables.return_value = ["users"]
        
        source_conn.get_table_count.return_value = 1000
        target_conn.get_table_count.return_value = 950  # 50 records missing
        
        report = await validator.validate_consistency(tables=["users"])
        
        assert len(report.discrepancies) > 0
        
        count_mismatch = next(
            d for d in report.discrepancies 
            if d["type"] == "count_mismatch"
        )
        
        assert count_mismatch["source_count"] == 1000
        assert count_mismatch["target_count"] == 950
        assert count_mismatch["difference"] == 50
        
    @pytest.mark.asyncio
    async def test_checksum_mismatch_detection(self, mock_db_connection):
        """Test detection of data checksum mismatches."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        # Setup records with different data
        source_conn.get_all_tables.return_value = ["users"]
        target_conn.get_all_tables.return_value = ["users"]
        
        source_conn.get_table_count.return_value = 2
        target_conn.get_table_count.return_value = 2
        
        source_conn.get_sample_records.return_value = [
            {"id": 1, "name": "User 1", "email": "user1@example.com"},
            {"id": 2, "name": "User 2", "email": "user2@example.com"},
        ]
        
        # Different email for user 2
        target_conn.get_records_by_ids.return_value = [
            {"id": 1, "name": "User 1", "email": "user1@example.com"},
            {"id": 2, "name": "User 2", "email": "different@example.com"},
        ]
        
        with patch.object(validator, '_batch_fetch_target_records', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                1: {"id": 1, "name": "User 1", "email": "user1@example.com"},
                2: {"id": 2, "name": "User 2", "email": "different@example.com"},
            }
            
            report = await validator.validate_consistency(
                tables=["users"],
                deep_check=True
            )
            
            assert len(report.checksum_mismatches) > 0
            
            mismatch = report.checksum_mismatches[0]
            assert mismatch["primary_key"] == 2
            assert any(
                d["field"] == "email" 
                for d in mismatch["differences"]
            )
            
    @pytest.mark.asyncio
    async def test_missing_records_detection(self, mock_db_connection):
        """Test detection of missing records in target."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        source_conn.get_all_tables.return_value = ["users"]
        target_conn.get_all_tables.return_value = ["users"]
        
        source_conn.get_table_count.return_value = 3
        target_conn.get_table_count.return_value = 2
        
        source_conn.get_sample_records.return_value = [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"},
            {"id": 3, "name": "User 3"},
        ]
        
        with patch.object(validator, '_batch_fetch_target_records', new_callable=AsyncMock) as mock_fetch:
            # User 3 is missing in target
            mock_fetch.return_value = {
                1: {"id": 1, "name": "User 1"},
                2: {"id": 2, "name": "User 2"},
            }
            
            report = await validator.validate_consistency(
                tables=["users"],
                deep_check=True
            )
            
            missing_discrepancy = next(
                d for d in report.discrepancies
                if d["type"] == "missing_in_target"
            )
            
            assert missing_discrepancy["primary_key"] == 3
            
    @pytest.mark.asyncio
    async def test_consistency_percentage_calculation(self, mock_db_connection):
        """Test consistency percentage calculation."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        # Setup perfect consistency
        source_conn.get_all_tables.return_value = ["users"]
        target_conn.get_all_tables.return_value = ["users"]
        
        source_conn.get_table_count.return_value = 100
        target_conn.get_table_count.return_value = 100
        
        source_conn.get_sample_records.return_value = [
            {"id": i, "name": f"User {i}"} 
            for i in range(1, 101)
        ]
        
        with patch.object(validator, '_batch_fetch_target_records', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                i: {"id": i, "name": f"User {i}"}
                for i in range(1, 101)
            }
            
            report = await validator.validate_consistency(
                tables=["users"],
                deep_check=True
            )
            
            assert report.consistency_percentage == 100.0
            assert report.consistent_records == 100
            assert report.inconsistent_records == 0
            
    @pytest.mark.asyncio
    async def test_adaptive_sampling(self, mock_db_connection):
        """Test adaptive sampling based on table size."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        test_cases = [
            (1000, 1000),      # Small table - check all
            (50000, 10000),    # Medium table - check 10k
            (1000000, 100000), # Large table - check 10%
        ]
        
        for table_size, expected_sample in test_cases:
            source_conn.get_table_count.return_value = table_size
            target_conn.get_table_count.return_value = table_size
            
            source_conn.get_sample_records.return_value = []
            
            # Capture the sample size used
            with patch.object(validator, '_validate_records', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = {
                    "consistent": 0,
                    "inconsistent": 0,
                    "discrepancies": [],
                    "checksum_mismatches": [],
                }
                
                await validator._validate_table(
                    "test_table",
                    sample_size=None,  # Let it auto-determine
                    deep_check=True
                )
                
                # Check that appropriate sample size was used
                call_args = mock_validate.call_args[0]
                actual_sample = call_args[1]
                assert actual_sample == expected_sample
                
    @pytest.mark.asyncio
    async def test_continuous_validation(self, mock_db_connection):
        """Test continuous validation with alerts."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        # Mock a validation that triggers alert
        with patch.object(validator, 'validate_consistency', new_callable=AsyncMock) as mock_validate:
            # Create report with low consistency
            report = ConsistencyReport(
                validation_id="test",
                timestamp=datetime.utcnow(),
                tables_checked=["users"],
                total_records=100,
                consistent_records=90,
                inconsistent_records=10,
                discrepancies=[],
                validation_duration_ms=1000,
                checksum_mismatches=[],
            )
            mock_validate.return_value = report
            
            with patch.object(validator, '_send_alert', new_callable=AsyncMock) as mock_alert:
                # Run one iteration of continuous validation
                with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                    mock_sleep.side_effect = Exception("Stop loop")
                    
                    try:
                        await validator.continuous_validation(
                            tables=["users"],
                            interval_seconds=1,
                            alert_threshold=0.95
                        )
                    except:
                        pass
                    
                    # Alert should be triggered (90% < 95% threshold)
                    mock_alert.assert_called_once()
                    
    @pytest.mark.asyncio
    async def test_validation_history(self, mock_db_connection):
        """Test validation history tracking."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        # Run multiple validations
        for i in range(5):
            with patch.object(validator, '_validate_table', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = {
                    "table": "users",
                    "total_records": 100,
                    "consistent_records": 100 - i,
                    "inconsistent_records": i,
                    "discrepancies": [],
                    "checksum_mismatches": [],
                }
                
                await validator.validate_consistency(tables=["users"])
                
        history = validator.get_validation_history(limit=3)
        
        assert len(history) == 3
        assert all(isinstance(r, ConsistencyReport) for r in history)
        
    def test_consistency_trends(self, mock_db_connection):
        """Test consistency trend analysis."""
        source_conn = mock_db_connection
        target_conn = mock_db_connection
        
        validator = ConsistencyValidator(source_conn, target_conn)
        
        # Add some validation history
        for i in range(5):
            report = ConsistencyReport(
                validation_id=f"test_{i}",
                timestamp=datetime.utcnow() - timedelta(hours=5-i),
                tables_checked=["users"],
                total_records=100,
                consistent_records=90 + i * 2,  # Improving over time
                inconsistent_records=10 - i * 2,
                discrepancies=[],
                validation_duration_ms=1000,
                checksum_mismatches=[],
            )
            validator._validation_history.append(report)
            
        trends = validator.get_consistency_trends()
        
        assert trends["current"] == 98.0  # Last report
        assert trends["average"] > 90.0
        assert trends["trend"] == "improving"
        assert trends["samples"] == 5