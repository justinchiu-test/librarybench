import asyncio
import pytest
from pathlib import Path
import json
import xml.etree.ElementTree as ET

from film_archive.core.models import TapeArchive, TapeFormat
from film_archive.tape.lto_manager import LTOTapeManager


@pytest.fixture
def lto_manager(tmp_path):
    return LTOTapeManager(tape_staging_dir=tmp_path)


@pytest.fixture
def test_files(tmp_path):
    files = []
    for i in range(5):
        file_path = tmp_path / f"media_file_{i}.mov"
        # Create files of different sizes
        file_path.write_bytes(b"X" * (1024 * 1024 * (i + 1)))  # 1MB, 2MB, etc.
        files.append(file_path)
    return files


class TestLTOTapeManager:
    def test_create_ltfs_label(self, lto_manager):
        label_data = lto_manager._create_ltfs_label(
            "TAPE001",
            TapeFormat.LTO8,
            "ProjectArchive_2024"
        )
        
        # Parse XML
        root = ET.fromstring(label_data)
        
        assert root.tag == "ltfslabel"
        assert root.get("version") == "2.4.0"
        
        creator = root.find("creator")
        assert creator.text == "FilmArchiveSystem"
        
        volumeuuid = root.find("volumeuuid")
        assert len(volumeuuid.text) == 64  # SHA-256 hash
        
        blocksize = root.find("blocksize")
        assert blocksize.text == "524288"
        
        compression = root.find("compression")
        assert compression.text == "true"
    
    def test_create_ltfs_index(self, lto_manager):
        files = [
            {
                "name": "project/scene_001.mov",
                "size": 1024 * 1024 * 1024,
                "startblock": 1000,
                "modifytime": "2024-01-01T12:00:00.000Z"
            },
            {
                "name": "project/scene_002.mov",
                "size": 2 * 1024 * 1024 * 1024,
                "startblock": 3000,
                "modifytime": "2024-01-01T13:00:00.000Z"
            }
        ]
        
        index_data = lto_manager._create_ltfs_index("TAPE001", files)
        
        # Parse XML
        root = ET.fromstring(index_data)
        
        assert root.tag == "ltfsindex"
        assert root.get("version") == "2.4.0"
        
        directory = root.find("directory")
        assert directory.find("name").text == "/"
        
        file_elements = directory.findall("file")
        assert len(file_elements) == 2
        
        # Check first file
        assert file_elements[0].find("name").text == "project/scene_001.mov"
        assert file_elements[0].find("length").text == str(1024 * 1024 * 1024)
    
    @pytest.mark.asyncio
    async def test_prepare_tape_archive(self, lto_manager, test_files):
        tape_archive = await lto_manager.prepare_tape_archive(
            "TAPE001",
            TapeFormat.LTO8,
            test_files
        )
        
        assert tape_archive.tape_id == "TAPE001"
        assert tape_archive.format == TapeFormat.LTO8
        assert tape_archive.capacity_bytes == 12_000_000_000_000
        
        # Calculate expected size (1+2+3+4+5 = 15MB)
        expected_size = sum((i + 1) * 1024 * 1024 for i in range(5))
        assert tape_archive.used_bytes == expected_size
        assert tape_archive.total_spans == 1  # Should fit on one tape
    
    @pytest.mark.asyncio
    async def test_prepare_tape_archive_spanning(self, lto_manager, tmp_path):
        # Create files that exceed single tape capacity
        huge_files = []
        for i in range(3):
            file_path = tmp_path / f"huge_file_{i}.mov"
            # Create small file
            file_path.write_bytes(b"H")
            huge_files.append(file_path)
        
        # Mock the file sizes for the test
        import unittest.mock
        with unittest.mock.patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 5 * 1024**4  # 5TB each
            
            tape_archive = await lto_manager.prepare_tape_archive(
                "TAPE002",
                TapeFormat.LTO8,
                huge_files
            )
        
        # 15TB total, 12TB per tape = 2 tapes needed
        assert tape_archive.total_spans == 2
        assert tape_archive.used_bytes == tape_archive.capacity_bytes
    
    @pytest.mark.asyncio
    async def test_write_to_tape(self, lto_manager, test_files):
        tape_archive = TapeArchive(
            tape_id="TAPE003",
            format=TapeFormat.LTO8,
            capacity_bytes=12_000_000_000_000,
            used_bytes=0
        )
        
        # Prepare files with archive paths
        files_to_write = [
            (test_files[i], f"archive/media/file_{i}.mov")
            for i in range(3)
        ]
        
        result = await lto_manager.write_to_tape(
            tape_archive,
            files_to_write,
            verify=True
        )
        
        assert result["tape_id"] == "TAPE003"
        assert len(result["written_files"]) == 3
        assert len(result["errors"]) == 0
        assert result["verified"] == True
        assert result["write_speed_mbps"] > 0
        
        # Check staging area
        tape_staging = lto_manager.staging_dir / "TAPE003"
        assert tape_staging.exists()
        
        # Check LTFS files
        assert (tape_staging / "ltfs_label.xml").exists()
        assert (tape_staging / "ltfs_index.xml").exists()
        
        # Check catalog was created
        assert tape_archive.catalog_path is not None
        assert tape_archive.catalog_path.exists()
        
        # Check verification checksum
        assert tape_archive.verification_checksum is not None
        assert len(tape_archive.verification_checksum) == 64
    
    @pytest.mark.asyncio
    async def test_write_to_tape_with_errors(self, lto_manager, test_files, tmp_path):
        tape_archive = TapeArchive(
            tape_id="TAPE004",
            format=TapeFormat.LTO8,
            capacity_bytes=10 * 1024 * 1024,  # Only 10MB capacity
            used_bytes=0
        )
        
        # Include non-existent file
        files_to_write = [
            (test_files[0], "archive/file_0.mov"),
            (Path("/nonexistent/file.mov"), "archive/missing.mov"),
            (test_files[4], "archive/file_4.mov")  # 5MB - won't fit
        ]
        
        result = await lto_manager.write_to_tape(
            tape_archive,
            files_to_write,
            verify=False
        )
        
        assert len(result["errors"]) >= 1  # At least the missing file error
        assert "File not found" in result["errors"][0]
        assert len(result["written_files"]) >= 1  # At least one file written
    
    def test_calculate_tape_checksum(self, lto_manager, tmp_path):
        tape_staging = tmp_path / "test_tape"
        tape_staging.mkdir()
        
        # Create some files
        (tape_staging / "file1.mov").write_bytes(b"DATA1")
        (tape_staging / "file2.mov").write_bytes(b"DATA2")
        
        checksum1 = lto_manager._calculate_tape_checksum(tape_staging)
        assert len(checksum1) == 64
        
        # Same files should produce same checksum
        checksum2 = lto_manager._calculate_tape_checksum(tape_staging)
        assert checksum1 == checksum2
        
        # Adding a file should change checksum
        (tape_staging / "file3.mov").write_bytes(b"DATA3")
        checksum3 = lto_manager._calculate_tape_checksum(tape_staging)
        assert checksum3 != checksum1
    
    def test_calculate_tape_span_distribution(self, lto_manager):
        # Files with sizes
        files = [
            (Path("file1.mov"), 4 * 1024**4),  # 4TB
            (Path("file2.mov"), 3 * 1024**4),  # 3TB
            (Path("file3.mov"), 5 * 1024**4),  # 5TB
            (Path("file4.mov"), 2 * 1024**4),  # 2TB
            (Path("file5.mov"), 6 * 1024**4),  # 6TB
        ]
        
        spans = lto_manager.calculate_tape_span_distribution(
            files,
            TapeFormat.LTO8  # 12TB capacity
        )
        
        # The algorithm should distribute files efficiently
        assert len(spans) >= 2  # At least 2 tapes needed for 20TB total
        
        # Verify all files are assigned
        all_indices = []
        for span in spans:
            all_indices.extend(span)
        assert sorted(all_indices) == [0, 1, 2, 3, 4]
    
    @pytest.mark.asyncio
    async def test_restore_from_tape(self, lto_manager, tmp_path):
        # Create a catalog
        catalog = {
            "tape_id": "TAPE005",
            "files": [
                {"path": "project/scene_001.mov", "size_mb": 1000},
                {"path": "project/scene_002.mov", "size_mb": 2000},
                {"path": "project/vfx/comp_001.exr", "size_mb": 500},
                {"path": "audio/mix_final.wav", "size_mb": 100}
            ]
        }
        
        catalog_path = lto_manager.staging_dir / "TAPE005_catalog.json"
        catalog_path.write_text(json.dumps(catalog))
        
        restore_dir = tmp_path / "restored"
        
        # Restore specific patterns
        result = await lto_manager.restore_from_tape(
            "TAPE005",
            ["project/scene*.mov", "audio/*.wav"],
            restore_dir
        )
        
        assert result["tape_id"] == "TAPE005"
        assert len(result["restored_files"]) == 3
        assert "project/scene_001.mov" in result["restored_files"]
        assert "project/scene_002.mov" in result["restored_files"]
        assert "audio/mix_final.wav" in result["restored_files"]
        
        # Check restored files exist
        assert (restore_dir / "project/scene_001.mov").exists()
        assert (restore_dir / "audio/mix_final.wav").exists()
    
    def test_estimate_tape_requirements(self, lto_manager):
        # 100TB of data
        total_size = 100 * 1024**4
        
        estimate = lto_manager.estimate_tape_requirements(
            total_size,
            TapeFormat.LTO8
        )
        
        assert estimate["format"] == "lto8"
        # With 3% overhead, effective capacity is ~11.64TB per tape
        # 100TB / 11.64TB = ~8.59, rounded up to 9 tapes
        assert estimate["tapes_needed"] >= 9
        assert estimate["capacity_per_tape_tb"] == 12.0
        assert estimate["total_capacity_needed_tb"] == 100.0
        assert estimate["estimated_write_time_hours"] > 0
        assert estimate["total_time_with_verification_hours"] > estimate["estimated_write_time_hours"]
        assert estimate["cost_estimate_usd"] >= 9 * 150
    
    def test_estimate_tape_requirements_lto9(self, lto_manager):
        # 100TB of data with LTO-9
        total_size = 100 * 1024**4
        
        estimate = lto_manager.estimate_tape_requirements(
            total_size,
            TapeFormat.LTO9
        )
        
        assert estimate["format"] == "lto9"
        # With 3% overhead, effective capacity is ~17.46TB per tape
        # 100TB / 17.46TB = ~5.73, rounded up to 6 tapes
        assert estimate["tapes_needed"] >= 6
        assert estimate["capacity_per_tape_tb"] == 18.0


class TestLTOPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_tape_operations(self, lto_manager, tmp_path):
        # Create multiple tape archives
        tape_archives = []
        for i in range(3):
            tape_archives.append(
                TapeArchive(
                    tape_id=f"TAPE{i:03d}",
                    format=TapeFormat.LTO8,
                    capacity_bytes=12_000_000_000_000,
                    used_bytes=0
                )
            )
        
        # Create test files
        test_file = tmp_path / "test_media.mov"
        test_file.write_bytes(b"M" * (10 * 1024 * 1024))  # 10MB
        
        import time
        start_time = time.time()
        
        # Write to multiple tapes concurrently
        tasks = []
        for tape in tape_archives:
            task = lto_manager.write_to_tape(
                tape,
                [(test_file, "media/test.mov")],
                verify=False
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert all(r["tape_id"] in ["TAPE000", "TAPE001", "TAPE002"] for r in results)
        assert all(len(r["written_files"]) == 1 for r in results)
        
        # Should complete reasonably quickly
        assert duration < 5.0  # seconds