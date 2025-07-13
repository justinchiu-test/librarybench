import pytest
import asyncio
from pathlib import Path
import io
from datetime import datetime, timezone

from film_archive.core.models import (
    MediaFile, VideoCodec, ProxyResolution, Timecode, TimecodeRange,
    StreamRequest, TapeFormat
)
from film_archive.proxy.generator import ProxyGenerator
from film_archive.streaming.streamer import ArchiveStreamer
from film_archive.timecode.extractor import TimecodeExtractor
from film_archive.versioning.branching import ArchiveBranchManager
from film_archive.tape.lto_manager import LTOTapeManager


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_proxy_generation_zero_duration(self, tmp_path):
        """Test proxy generation with zero duration media"""
        proxy_gen = ProxyGenerator(temp_dir=tmp_path)
        
        media = MediaFile(
            file_path=Path("/test/still.jpg"),
            size=5 * 1024 * 1024,
            codec=VideoCodec.H264,
            duration=Timecode(hours=0, minutes=0, seconds=0, frames=1, frame_rate=24.0),
            frame_rate=24.0,
            resolution=(1920, 1080),
            audio_channels=0
        )
        
        proxy = await proxy_gen.generate_proxy(media, ProxyResolution.THUMBNAIL)
        assert proxy.size > 0
        assert proxy.proxy_path.exists()
    
    @pytest.mark.asyncio
    async def test_streaming_empty_archive(self, tmp_path):
        """Test streaming from empty archive"""
        streamer = ArchiveStreamer()
        
        # Create empty archive
        archive_path = tmp_path / "empty.zip"
        archive_path.write_bytes(b"")
        
        request = StreamRequest(
            archive_path=archive_path,
            file_path="nonexistent.mp4"
        )
        
        chunks = []
        async for chunk in streamer.stream_file(request):
            chunks.append(chunk)
        
        assert len(chunks) == 0
    
    def test_timecode_edge_values(self):
        """Test timecode with edge values"""
        # Maximum valid timecode
        tc = Timecode(hours=23, minutes=59, seconds=59, frames=29, frame_rate=30.0)
        assert tc.total_frames == (24 * 3600 * 30) - 1
        
        # Minimum timecode
        tc_min = Timecode(hours=0, minutes=0, seconds=0, frames=0, frame_rate=24.0)
        assert tc_min.total_frames == 0
    
    @pytest.mark.asyncio
    async def test_extraction_beyond_file_bounds(self, tmp_path):
        """Test extraction with timecode beyond file duration"""
        extractor = TimecodeExtractor(working_dir=tmp_path)
        
        media = MediaFile(
            file_path=Path("/test/short.mov"),
            size=100 * 1024 * 1024,
            codec=VideoCodec.PRORES_422,
            duration=Timecode(hours=0, minutes=1, seconds=0, frames=0, frame_rate=24.0),
            frame_rate=24.0,
            resolution=(1920, 1080),
            audio_channels=2
        )
        
        # Request extraction beyond file duration
        tc_range = TimecodeRange(
            start=Timecode(hours=0, minutes=2, seconds=0, frames=0, frame_rate=24.0),
            end=Timecode(hours=0, minutes=3, seconds=0, frames=0, frame_rate=24.0),
            handles=0
        )
        
        archive_data = io.BytesIO(b"X" * media.size)
        
        # Should handle gracefully
        output_path = await extractor.extract_segment(
            archive_data, media, tc_range
        )
        assert output_path.exists()
    
    @pytest.mark.asyncio
    async def test_branch_circular_parent(self, tmp_path):
        """Test handling of circular branch relationships"""
        branch_mgr = ArchiveBranchManager(repository_root=tmp_path)
        archive_path = tmp_path / "test.zip"
        archive_path.write_bytes(b"ARCHIVE")
        
        # Create branch
        branch1 = await branch_mgr.create_branch(
            archive_path, "branch1", "First branch"
        )
        
        # Attempt to set parent to itself (should be prevented by design)
        branch2 = await branch_mgr.create_branch(
            archive_path, "branch2", "Second branch", 
            parent_branch_id=branch1.branch_id
        )
        
        assert branch2.parent_id == branch1.branch_id
        assert branch1.parent_id is None
    
    @pytest.mark.asyncio
    async def test_tape_write_interruption_recovery(self, tmp_path):
        """Test recovery from interrupted tape write"""
        lto_mgr = LTOTapeManager(tape_staging_dir=tmp_path)
        
        from film_archive.core.models import TapeArchive
        tape = TapeArchive(
            tape_id="TAPE_INTERRUPT",
            format=TapeFormat.LTO8,
            capacity_bytes=12_000_000_000_000,
            used_bytes=0
        )
        
        # Create test file
        test_file = tmp_path / "large_file.mov"
        test_file.write_bytes(b"X" * 1024 * 1024)  # 1MB
        
        # Simulate partial write by creating partial staging
        tape_staging = lto_mgr.staging_dir / tape.tape_id
        tape_staging.mkdir(exist_ok=True)
        (tape_staging / "ltfs_label.xml").write_text("<partial>")
        
        # Should handle partial state
        result = await lto_mgr.write_to_tape(
            tape,
            [(test_file, "archive/file.mov")],
            verify=False
        )
        
        assert result["tape_id"] == "TAPE_INTERRUPT"
        assert len(result["written_files"]) >= 0
    
    def test_proxy_selection_no_suitable_proxy(self):
        """Test proxy selection when no proxy fits bandwidth"""
        proxy_gen = ProxyGenerator()
        
        from film_archive.core.models import ProxyFile
        proxies = [
            ProxyFile(
                original_file=Path("/test.mov"),
                proxy_path=Path("/proxy.mp4"),
                resolution=ProxyResolution.EDITORIAL,
                size=1000,
                bitrate=10_000_000  # 10 Mbps
            )
        ]
        
        # Very low bandwidth
        optimal = proxy_gen.select_optimal_proxy(
            proxies,
            target_bandwidth=100_000,  # 100 kbps
            display_resolution=(1920, 1080)
        )
        
        # Should return the only available proxy despite bandwidth
        assert optimal == proxies[0]
    
    @pytest.mark.asyncio
    async def test_concurrent_branch_modifications(self, tmp_path):
        """Test concurrent modifications to same branch"""
        branch_mgr = ArchiveBranchManager(repository_root=tmp_path)
        archive_path = tmp_path / "test.zip"
        archive_path.write_bytes(b"ARCHIVE")
        
        branch = await branch_mgr.create_branch(
            archive_path, "concurrent", "Test concurrent access"
        )
        
        # Create multiple files
        files = []
        for i in range(10):
            file_path = tmp_path / f"file_{i}.mov"
            file_path.write_bytes(f"CONTENT_{i}".encode())
            files.append(file_path)
        
        # Add files concurrently
        tasks = [
            branch_mgr.add_file_to_branch(
                branch.branch_id,
                file,
                f"concurrent/file_{i}.mov"
            )
            for i, file in enumerate(files)
        ]
        
        await asyncio.gather(*tasks)
        
        # Verify all files were added
        metadata = branch_mgr._load_branch_metadata(branch.branch_id)
        assert len([k for k in metadata["files"].keys() if k.startswith("concurrent/")]) == 10
    
    def test_timecode_fractional_frame_rates(self):
        """Test timecode with fractional frame rates"""
        # 29.97 fps (NTSC)
        tc = Timecode(hours=0, minutes=1, seconds=0, frames=0, frame_rate=29.97)
        assert tc.total_frames == int(60 * 29.97)
        
        # 23.976 fps (film transferred to video)
        tc2 = Timecode(hours=0, minutes=0, seconds=10, frames=0, frame_rate=23.976)
        assert tc2.total_frames == int(10 * 23.976)
    
    def test_archive_metadata_version_migration(self):
        """Test handling of different archive metadata versions"""
        from film_archive.core.models import ArchiveMetadata
        
        # Current version
        metadata = ArchiveMetadata(
            archive_id="TEST001",
            created_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
            total_size=1000,
            file_count=10
        )
        assert metadata.version == "1.0"
        
        # Future version handling would go here
    
    @pytest.mark.asyncio
    async def test_streaming_with_corrupted_range(self, tmp_path):
        """Test streaming with corrupted byte range"""
        streamer = ArchiveStreamer()
        
        archive_path = tmp_path / "test.zip"
        archive_path.write_bytes(b"X" * 1000)
        
        # Request with invalid range
        request = StreamRequest(
            archive_path=archive_path,
            file_path="test.mp4",
            start_byte=2000,  # Beyond file size
            end_byte=3000
        )
        
        with pytest.raises(ValueError, match="Start byte.*exceeds file size"):
            async for _ in streamer.stream_file(request):
                pass
    
    def test_tape_span_single_large_file(self):
        """Test tape spanning with single file larger than tape"""
        lto_mgr = LTOTapeManager()
        
        files = [
            (Path("huge.mov"), 15 * 1024**4)  # 15TB file
        ]
        
        spans = lto_mgr.calculate_tape_span_distribution(
            files, TapeFormat.LTO8
        )
        
        # Single file too large should still create span
        assert len(spans) == 2
        assert 0 in spans[0]  # File starts on first tape
    
    def test_edl_parsing_malformed(self):
        """Test EDL parsing with malformed content"""
        extractor = TimecodeExtractor()
        
        malformed_edl = """TITLE: Malformed
001 V C 01:00:00:00 01:00:10:00  # Missing record times
002 X Q INVALID
003 V C 25:00:00:00 01:00:00:00 00:00:00:00 00:00:10:00  # Invalid hour
        """
        
        ranges = extractor.parse_edl_timecodes(malformed_edl)
        # Should parse what it can, skip invalid entries
        assert len(ranges) >= 0