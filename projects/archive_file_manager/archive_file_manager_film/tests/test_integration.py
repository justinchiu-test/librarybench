import asyncio
import pytest
from pathlib import Path
import io

from film_archive.core.models import (
    MediaFile, ProxyResolution, VideoCodec, Timecode, TimecodeRange,
    StreamRequest, TapeFormat
)
from film_archive.proxy.generator import ProxyGenerator
from film_archive.streaming.streamer import ArchiveStreamer
from film_archive.timecode.extractor import TimecodeExtractor
from film_archive.versioning.branching import ArchiveBranchManager
from film_archive.tape.lto_manager import LTOTapeManager


class TestFilmArchiveIntegration:
    """Integration tests for complete film archive workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_archive_workflow(self, tmp_path):
        """Test complete workflow: proxy generation, streaming, extraction, versioning, and tape archive"""
        
        # 1. Setup components
        proxy_gen = ProxyGenerator(temp_dir=tmp_path / "proxies")
        streamer = ArchiveStreamer()
        tc_extractor = TimecodeExtractor(working_dir=tmp_path / "extracts")
        branch_mgr = ArchiveBranchManager(repository_root=tmp_path / "branches")
        lto_mgr = LTOTapeManager(tape_staging_dir=tmp_path / "tapes")
        
        # 2. Create test media file
        media_file = MediaFile(
            file_path=Path("/project/raw_footage/scene_001.mov"),
            size=5 * 1024 * 1024 * 1024,  # 5GB
            codec=VideoCodec.PRORES_422,
            duration=Timecode(hours=0, minutes=10, seconds=0, frames=0, frame_rate=24.0),
            frame_rate=24.0,
            resolution=(3840, 2160),
            audio_channels=8
        )
        
        # 3. Generate proxies
        proxies = await proxy_gen.generate_proxies(
            media_file,
            [ProxyResolution.THUMBNAIL, ProxyResolution.PREVIEW, ProxyResolution.EDITORIAL]
        )
        
        assert len(proxies) == 3
        assert all(p.proxy_path.exists() for p in proxies)
        
        # 4. Create archive with embedded proxies
        archive_data = io.BytesIO()
        archive_data.write(b"MAIN_MEDIA_DATA" * (1024 * 1024))  # Simulate media data
        
        proxy_metadata = []
        for proxy in proxies:
            metadata = proxy_gen.embed_proxy_in_archive(archive_data, proxy)
            proxy_metadata.append(metadata)
        
        # 5. Test streaming from archive
        archive_path = tmp_path / "test_archive.zip"
        archive_path.write_bytes(archive_data.getvalue())
        
        stream_request = StreamRequest(
            archive_path=archive_path,
            file_path="scene_001.mov",
            start_byte=0,
            end_byte=1024 * 1024 - 1,  # First 1MB
            buffer_size=64 * 1024
        )
        
        streamed_data = b""
        async for chunk in streamer.stream_file(stream_request):
            streamed_data += chunk
        
        assert len(streamed_data) == 1024 * 1024
        
        # 6. Extract timecode-based segment
        tc_range = TimecodeRange(
            start=Timecode(hours=0, minutes=1, seconds=0, frames=0, frame_rate=24.0),
            end=Timecode(hours=0, minutes=2, seconds=0, frames=0, frame_rate=24.0),
            handles=24  # 1 second handles
        )
        
        archive_data.seek(0)
        extracted_path = await tc_extractor.extract_segment(
            archive_data, media_file, tc_range
        )
        
        assert extracted_path.exists()
        
        # 7. Create version branch
        branch = await branch_mgr.create_branch(
            archive_path,
            "color-grade-v2",
            "New color grading for scene 001"
        )
        
        # Add modified file to branch
        modified_file = tmp_path / "scene_001_graded.mov"
        modified_file.write_bytes(b"GRADED_DATA")
        
        await branch_mgr.add_file_to_branch(
            branch.branch_id,
            modified_file,
            "project/graded/scene_001.mov"
        )
        
        # 8. Prepare for tape archive
        files_to_archive = [
            archive_path,
            extracted_path,
            modified_file
        ]
        
        tape_archive = await lto_mgr.prepare_tape_archive(
            "FILM2024001",
            TapeFormat.LTO8,
            files_to_archive
        )
        
        assert tape_archive.total_spans == 1
        
        # 9. Write to tape
        write_result = await lto_mgr.write_to_tape(
            tape_archive,
            [(f, f"archive/{f.name}") for f in files_to_archive],
            verify=True
        )
        
        assert write_result["verified"]
        assert len(write_result["written_files"]) == 3
        
        # Cleanup
        await streamer.close_archive_stream(archive_path)
        proxy_gen.cleanup_temp_files()
        tc_extractor.cleanup_extracted_files()
    
    @pytest.mark.asyncio
    async def test_proxy_streaming_performance(self, tmp_path):
        """Test streaming performance with proxy selection"""
        
        proxy_gen = ProxyGenerator(temp_dir=tmp_path / "proxies")
        streamer = ArchiveStreamer()
        
        # Create media file
        media_file = MediaFile(
            file_path=Path("/test/4k_footage.mov"),
            size=20 * 1024 * 1024 * 1024,  # 20GB
            codec=VideoCodec.PRORES_4444,
            duration=Timecode(hours=0, minutes=30, seconds=0, frames=0, frame_rate=24.0),
            frame_rate=24.0,
            resolution=(4096, 2160),
            audio_channels=16
        )
        
        # Generate all proxy resolutions
        proxies = await proxy_gen.generate_proxies(
            media_file,
            list(ProxyResolution)
        )
        
        # Test proxy selection for different bandwidths
        
        # Low bandwidth - should select thumbnail
        selected = proxy_gen.select_optimal_proxy(
            proxies,
            target_bandwidth=1_000_000,  # 1 Mbps
            display_resolution=(1920, 1080)
        )
        assert selected.resolution == ProxyResolution.THUMBNAIL
        
        # Medium bandwidth - should select preview
        selected = proxy_gen.select_optimal_proxy(
            proxies,
            target_bandwidth=2_000_000,  # 2 Mbps
            display_resolution=(1920, 1080)
        )
        assert selected.resolution == ProxyResolution.PREVIEW
        
        # High bandwidth - should select editorial
        selected = proxy_gen.select_optimal_proxy(
            proxies,
            target_bandwidth=10_000_000,  # 10 Mbps
            display_resolution=(3840, 2160)
        )
        assert selected.resolution == ProxyResolution.EDITORIAL
    
    @pytest.mark.asyncio
    async def test_multi_branch_workflow(self, tmp_path):
        """Test complex branching workflow with merges"""
        
        branch_mgr = ArchiveBranchManager(repository_root=tmp_path)
        archive_path = tmp_path / "master_project.zip"
        archive_path.write_bytes(b"MASTER_ARCHIVE")
        
        # Create main branch
        main_branch = await branch_mgr.create_branch(
            archive_path,
            "main",
            "Main production branch"
        )
        
        # Create VFX branch
        vfx_branch = await branch_mgr.create_branch(
            archive_path,
            "vfx-updates",
            "VFX composites update",
            parent_branch_id=main_branch.branch_id
        )
        
        # Create color branch
        color_branch = await branch_mgr.create_branch(
            archive_path,
            "color-grade",
            "Color grading pass",
            parent_branch_id=main_branch.branch_id
        )
        
        # Add files to VFX branch
        vfx_file = tmp_path / "vfx_comp_001.exr"
        vfx_file.write_bytes(b"VFX_DATA")
        await branch_mgr.add_file_to_branch(
            vfx_branch.branch_id,
            vfx_file,
            "vfx/comps/comp_001.exr"
        )
        
        # Add files to color branch
        color_file = tmp_path / "scene_001_graded.mov"
        color_file.write_bytes(b"COLOR_DATA")
        await branch_mgr.add_file_to_branch(
            color_branch.branch_id,
            color_file,
            "color/scene_001.mov"
        )
        
        # Merge VFX into main
        vfx_merge = await branch_mgr.merge_branches(
            vfx_branch.branch_id,
            main_branch.branch_id
        )
        assert len(vfx_merge["merged_files"]) > 0
        assert len(vfx_merge["conflicts"]) == 0
        
        # Merge color into main
        color_merge = await branch_mgr.merge_branches(
            color_branch.branch_id,
            main_branch.branch_id
        )
        assert len(color_merge["merged_files"]) > 0
        
        # Check storage savings
        savings = branch_mgr.calculate_storage_savings()
        assert savings["deduplication_ratio"] >= 1.0
    
    @pytest.mark.asyncio
    async def test_edl_based_extraction_workflow(self, tmp_path):
        """Test EDL-based extraction for editorial workflow"""
        
        tc_extractor = TimecodeExtractor(working_dir=tmp_path / "edl_extracts")
        
        # Create test EDL
        edl_content = """TITLE: Final Cut Sequence
FCM: NON-DROP FRAME

001  V  C  01:00:00:00 01:00:30:00 00:00:00:00 00:00:30:00
* Scene 1 - Wide shot

002  V  C  01:02:15:00 01:02:45:00 00:00:30:00 00:01:00:00
* Scene 2 - Close up

003  V  C  01:05:00:00 01:05:20:00 00:01:00:00 00:01:20:00
* Scene 3 - Action sequence

004  V  C  01:10:30:00 01:11:00:00 00:01:20:00 00:01:50:00
* Scene 4 - Dialogue"""
        
        # Parse EDL
        ranges = tc_extractor.parse_edl_timecodes(edl_content)
        assert len(ranges) == 4
        
        # Merge overlapping ranges
        merged_ranges = tc_extractor.merge_overlapping_ranges(ranges)
        assert len(merged_ranges) <= 4
        
        # Calculate extraction time
        est_time = tc_extractor.calculate_extraction_time(
            merged_ranges,
            extraction_speed_mbps=300
        )
        assert est_time > 0
        
        # Create manifest
        media_file = MediaFile(
            file_path=Path("/edl/source.mov"),
            size=50 * 1024 * 1024 * 1024,
            codec=VideoCodec.PRORES_422,
            frame_rate=24.0,
            resolution=(3840, 2160),
            audio_channels=2
        )
        
        dummy_paths = [tmp_path / f"extract_{i}.mov" for i in range(len(ranges))]
        for p in dummy_paths:
            p.write_bytes(b"EXTRACT")
        
        manifest = tc_extractor.create_extraction_manifest(
            media_file,
            ranges,
            dummy_paths
        )
        
        assert manifest["total_extracted_frames"] > 0
        assert len(manifest["extractions"]) == 4
    
    @pytest.mark.asyncio 
    async def test_tape_spanning_workflow(self, tmp_path):
        """Test large project spanning multiple tapes"""
        
        lto_mgr = LTOTapeManager(tape_staging_dir=tmp_path / "tape_spans")
        
        # Create large project files
        project_files = []
        total_size = 0
        
        for i in range(10):
            file_path = tmp_path / f"raw_footage_{i:03d}.mov"
            # Create small test files
            file_path.write_bytes(b"F" * 1024)  # 1KB files
            project_files.append(file_path)
            total_size += 2 * 1024**4  # Simulate 2TB each for calculation
        
        # Calculate tape requirements
        estimate = lto_mgr.estimate_tape_requirements(
            total_size,
            TapeFormat.LTO8
        )
        
        assert estimate["tapes_needed"] >= 2
        assert estimate["total_capacity_needed_tb"] == 20.0
        
        # Calculate span distribution with simulated sizes
        file_info = [(f, 2 * 1024**4) for f in project_files]  # 2TB each
        spans = lto_mgr.calculate_tape_span_distribution(
            file_info,
            TapeFormat.LTO8
        )
        
        assert len(spans) >= 2
        
        # Verify all files are assigned to spans
        all_indices = set()
        for span in spans:
            all_indices.update(span)
        assert len(all_indices) == 10