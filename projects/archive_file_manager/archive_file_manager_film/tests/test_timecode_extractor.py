import asyncio
import pytest
from pathlib import Path
import io

from film_archive.core.models import MediaFile, Timecode, TimecodeRange, VideoCodec
from film_archive.timecode.extractor import TimecodeExtractor


@pytest.fixture
def timecode_extractor(tmp_path):
    return TimecodeExtractor(working_dir=tmp_path)


@pytest.fixture
def sample_media_file():
    return MediaFile(
        file_path=Path("/test/footage.mov"),
        size=10 * 1024 * 1024 * 1024,  # 10GB
        codec=VideoCodec.PRORES_422,
        duration=Timecode(hours=1, minutes=0, seconds=0, frames=0, frame_rate=24.0),
        frame_rate=24.0,
        resolution=(3840, 2160),
        audio_channels=2
    )


class TestTimecodeExtractor:
    def test_parse_edl_timecodes(self, timecode_extractor):
        edl_content = """001  V  C  01:00:00:00 01:00:10:00 00:00:00:00 00:00:10:00
002  V  C  01:00:20:00 01:00:30:00 00:00:10:00 00:00:20:00
003  A  C  01:00:40:00 01:00:45:00 00:00:20:00 00:00:25:00
INVALID LINE
004  B  C  01:01:00:00 01:01:15:00 00:00:25:00 00:00:40:00"""
        
        ranges = timecode_extractor.parse_edl_timecodes(edl_content)
        
        assert len(ranges) == 4
        
        # Check first range
        assert ranges[0].start.hours == 1
        assert ranges[0].start.minutes == 0
        assert ranges[0].start.seconds == 0
        assert ranges[0].start.frames == 0
        
        assert ranges[0].end.hours == 1
        assert ranges[0].end.minutes == 0
        assert ranges[0].end.seconds == 10
        assert ranges[0].end.frames == 0
    
    def test_calculate_byte_ranges(self, timecode_extractor, sample_media_file):
        # Extract 10 seconds from 30 seconds in
        tc_range = TimecodeRange(
            start=Timecode(hours=0, minutes=0, seconds=30, frames=0, frame_rate=24.0),
            end=Timecode(hours=0, minutes=0, seconds=40, frames=0, frame_rate=24.0),
            handles=0
        )
        
        file_size = sample_media_file.size
        start_byte, end_byte = timecode_extractor.calculate_byte_ranges(
            sample_media_file, tc_range, file_size
        )
        
        # Should be approximately 30-40 seconds of 1 hour = 8.33% - 11.11% of file
        assert start_byte >= int(file_size * 0.008)
        assert end_byte <= int(file_size * 0.012)
        assert start_byte < end_byte
    
    def test_calculate_byte_ranges_with_handles(
        self, timecode_extractor, sample_media_file
    ):
        # Extract with 24 frame handles (1 second each side)
        tc_range = TimecodeRange(
            start=Timecode(hours=0, minutes=0, seconds=30, frames=0, frame_rate=24.0),
            end=Timecode(hours=0, minutes=0, seconds=40, frames=0, frame_rate=24.0),
            handles=24
        )
        
        file_size = sample_media_file.size
        start_byte, end_byte = timecode_extractor.calculate_byte_ranges(
            sample_media_file, tc_range, file_size
        )
        
        # With handles, should extract 29-41 seconds (12 seconds total)
        expected_ratio = 12.0 / 3600.0  # 12 seconds of 1 hour
        expected_size = file_size * expected_ratio
        
        actual_size = end_byte - start_byte
        assert actual_size >= expected_size * 0.9  # Allow 10% variance
    
    @pytest.mark.asyncio
    async def test_extract_segment(self, timecode_extractor, sample_media_file, tmp_path):
        # Create test archive data
        archive_data = io.BytesIO(b"A" * sample_media_file.size)
        
        tc_range = TimecodeRange(
            start=Timecode(hours=0, minutes=10, seconds=0, frames=0, frame_rate=24.0),
            end=Timecode(hours=0, minutes=10, seconds=30, frames=0, frame_rate=24.0),
            handles=0
        )
        
        output_path = await timecode_extractor.extract_segment(
            archive_data, sample_media_file, tc_range
        )
        
        assert output_path.exists()
        assert output_path.suffix == ".mp4"
        assert "00100000_00103000" in output_path.name
        
        # Check extracted size is reasonable
        file_size = output_path.stat().st_size
        expected_ratio = 30.0 / 3600.0  # 30 seconds of 1 hour
        expected_size = sample_media_file.size * expected_ratio
        
        assert file_size > 0
        assert file_size <= sample_media_file.size
    
    @pytest.mark.asyncio
    async def test_extract_multiple_segments(
        self, timecode_extractor, sample_media_file
    ):
        archive_data = io.BytesIO(b"B" * sample_media_file.size)
        
        tc_ranges = [
            TimecodeRange(
                start=Timecode(hours=0, minutes=5, seconds=0, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=5, seconds=10, frames=0, frame_rate=24.0),
                handles=0
            ),
            TimecodeRange(
                start=Timecode(hours=0, minutes=20, seconds=0, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=20, seconds=15, frames=0, frame_rate=24.0),
                handles=0
            ),
            TimecodeRange(
                start=Timecode(hours=0, minutes=45, seconds=0, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=45, seconds=5, frames=0, frame_rate=24.0),
                handles=0
            )
        ]
        
        output_paths = await timecode_extractor.extract_multiple_segments(
            archive_data, sample_media_file, tc_ranges
        )
        
        assert len(output_paths) == 3
        assert all(path.exists() for path in output_paths)
    
    def test_merge_overlapping_ranges(self, timecode_extractor):
        ranges = [
            TimecodeRange(
                start=Timecode(hours=0, minutes=0, seconds=0, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=0, seconds=10, frames=0, frame_rate=24.0),
                handles=24  # 1 second
            ),
            TimecodeRange(
                start=Timecode(hours=0, minutes=0, seconds=9, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=0, seconds=20, frames=0, frame_rate=24.0),
                handles=0
            ),
            TimecodeRange(
                start=Timecode(hours=0, minutes=0, seconds=30, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=0, seconds=35, frames=0, frame_rate=24.0),
                handles=0
            )
        ]
        
        merged = timecode_extractor.merge_overlapping_ranges(ranges)
        
        assert len(merged) == 2
        
        # First merged range should cover 0-20 seconds (with handles)
        assert merged[0].start.seconds == 0
        assert merged[0].end.seconds == 20
        assert merged[0].handles == 24
        
        # Second range should remain separate
        assert merged[1].start.seconds == 30
        assert merged[1].end.seconds == 35
    
    def test_calculate_extraction_time(self, timecode_extractor):
        ranges = [
            TimecodeRange(
                start=Timecode(hours=0, minutes=0, seconds=0, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=1, seconds=0, frames=0, frame_rate=24.0),
                handles=0
            ),
            TimecodeRange(
                start=Timecode(hours=0, minutes=10, seconds=0, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=11, seconds=0, frames=0, frame_rate=24.0),
                handles=0
            )
        ]
        
        # 2 minutes of footage at 24fps = 2880 frames
        extraction_time = timecode_extractor.calculate_extraction_time(
            ranges, extraction_speed_mbps=300
        )
        
        assert extraction_time > 0
        assert extraction_time < 60  # Should be under a minute for 2 min of footage
    
    def test_validate_timecode_continuity(self, timecode_extractor, tmp_path):
        # Create test segments
        segments = []
        expected_ranges = []
        
        for i in range(3):
            segment_path = tmp_path / f"segment_{i}.mp4"
            # Create segments with appropriate sizes
            frames = (i + 1) * 240  # 10, 20, 30 seconds worth
            size = frames * 200 * 1024  # ~200KB per frame
            segment_path.write_bytes(b"X" * size)
            segments.append(segment_path)
            
            expected_ranges.append(
                TimecodeRange(
                    start=Timecode(hours=0, minutes=i, seconds=0, frames=0, frame_rate=24.0),
                    end=Timecode(hours=0, minutes=i, seconds=(i+1)*10, frames=0, frame_rate=24.0),
                    handles=0
                )
            )
        
        validation = timecode_extractor.validate_timecode_continuity(
            segments, expected_ranges
        )
        
        assert validation["valid"]
        assert len(validation["segments"]) == 3
        assert all(seg["valid"] for seg in validation["segments"])
        assert len(validation["errors"]) == 0
    
    def test_create_extraction_manifest(
        self, timecode_extractor, sample_media_file, tmp_path
    ):
        ranges = [
            TimecodeRange(
                start=Timecode(hours=0, minutes=5, seconds=0, frames=0, frame_rate=24.0),
                end=Timecode(hours=0, minutes=5, seconds=30, frames=0, frame_rate=24.0),
                handles=12
            )
        ]
        
        extracted_path = tmp_path / "extracted_segment.mp4"
        extracted_path.write_bytes(b"DATA")
        
        manifest = timecode_extractor.create_extraction_manifest(
            sample_media_file, ranges, [extracted_path]
        )
        
        assert manifest["source_file"] == str(sample_media_file.file_path)
        assert manifest["source_codec"] == VideoCodec.PRORES_422.value
        assert manifest["source_frame_rate"] == 24.0
        assert len(manifest["extractions"]) == 1
        
        extraction = manifest["extractions"][0]
        assert extraction["timecode_in"] == "00:05:00:00"
        assert extraction["timecode_out"] == "00:05:30:00"
        assert extraction["handles"] == 12
        assert extraction["output_file"] == str(extracted_path)
        assert extraction["size_bytes"] == 4  # len(b"DATA")
    
    def test_cleanup_extracted_files(self, timecode_extractor, tmp_path):
        # Create test files
        for i in range(5):
            (tmp_path / f"test_extract_{i}.mp4").write_text("data")
        
        assert len(list(tmp_path.glob("*.mp4"))) == 5
        
        timecode_extractor.cleanup_extracted_files()
        
        assert len(list(tmp_path.glob("*.mp4"))) == 0


class TestTimecodePerformance:
    @pytest.mark.asyncio
    async def test_parallel_extraction_performance(
        self, timecode_extractor, sample_media_file
    ):
        archive_data = io.BytesIO(b"C" * (100 * 1024 * 1024))  # 100MB test data
        
        # Create 20 non-overlapping ranges
        tc_ranges = []
        for i in range(20):
            start_seconds = i * 3
            tc_ranges.append(
                TimecodeRange(
                    start=Timecode(
                        hours=0, minutes=0, seconds=start_seconds, 
                        frames=0, frame_rate=24.0
                    ),
                    end=Timecode(
                        hours=0, minutes=0, seconds=start_seconds + 2, 
                        frames=0, frame_rate=24.0
                    ),
                    handles=0
                )
            )
        
        import time
        start_time = time.time()
        
        # Use smaller media file for performance test
        test_media = MediaFile(
            file_path=Path("/test/perf.mov"),
            size=100 * 1024 * 1024,
            codec=VideoCodec.H264,
            duration=Timecode(hours=0, minutes=1, seconds=0, frames=0, frame_rate=24.0),
            frame_rate=24.0,
            resolution=(1920, 1080),
            audio_channels=2
        )
        
        output_paths = await timecode_extractor.extract_multiple_segments(
            archive_data, test_media, tc_ranges
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert len(output_paths) == 20
        # Should complete quickly with parallel processing
        assert duration < 5.0  # seconds