import pytest
from pathlib import Path
from datetime import datetime, timezone

from film_archive.core.models import (
    ProxyResolution, VideoCodec, TapeFormat, Timecode, MediaFile, 
    ProxyFile, ArchiveMetadata, StreamRequest, TimecodeRange, 
    ArchiveBranch, TapeArchive
)


class TestModels:
    """Test core data models"""
    
    def test_proxy_resolution_enum(self):
        assert ProxyResolution.THUMBNAIL.value == "thumbnail"
        assert ProxyResolution.PREVIEW.value == "preview"
        assert ProxyResolution.EDITORIAL.value == "editorial"
    
    def test_video_codec_enum(self):
        assert VideoCodec.PRORES_422.value == "prores_422"
        assert VideoCodec.PRORES_4444.value == "prores_4444"
        assert VideoCodec.DNXHD.value == "dnxhd"
        assert VideoCodec.H264.value == "h264"
        assert VideoCodec.H265.value == "h265"
    
    def test_tape_format_enum(self):
        assert TapeFormat.LTO8.value == "lto8"
        assert TapeFormat.LTO9.value == "lto9"
    
    def test_timecode_creation(self):
        tc = Timecode(hours=1, minutes=30, seconds=45, frames=12, frame_rate=24.0)
        assert tc.hours == 1
        assert tc.minutes == 30
        assert tc.seconds == 45
        assert tc.frames == 12
        assert tc.frame_rate == 24.0
    
    def test_timecode_total_frames(self):
        tc = Timecode(hours=1, minutes=0, seconds=0, frames=0, frame_rate=24.0)
        assert tc.total_frames == 24 * 60 * 60  # 1 hour at 24fps
        
        tc2 = Timecode(hours=0, minutes=1, seconds=30, frames=12, frame_rate=24.0)
        assert tc2.total_frames == (90 * 24) + 12  # 90 seconds + 12 frames
    
    def test_timecode_from_string(self):
        tc = Timecode.from_string("01:30:45:12", frame_rate=24.0)
        assert tc.hours == 1
        assert tc.minutes == 30
        assert tc.seconds == 45
        assert tc.frames == 12
    
    def test_timecode_from_string_invalid(self):
        with pytest.raises(ValueError, match="Invalid timecode format"):
            Timecode.from_string("1:30:45", frame_rate=24.0)
    
    def test_timecode_string_representation(self):
        tc = Timecode(hours=1, minutes=2, seconds=3, frames=4, frame_rate=24.0)
        assert str(tc) == "01:02:03:04"
    
    def test_media_file_creation(self):
        media = MediaFile(
            file_path=Path("/test/video.mov"),
            size=1024 * 1024 * 1024,
            codec=VideoCodec.PRORES_422,
            frame_rate=24.0,
            resolution=(1920, 1080),
            audio_channels=2
        )
        assert media.file_path == Path("/test/video.mov")
        assert media.size == 1024 * 1024 * 1024
        assert media.codec == VideoCodec.PRORES_422
        assert media.duration is None
        assert media.metadata == {}
    
    def test_proxy_file_creation(self):
        proxy = ProxyFile(
            original_file=Path("/test/original.mov"),
            proxy_path=Path("/test/proxy.mp4"),
            resolution=ProxyResolution.PREVIEW,
            size=10 * 1024 * 1024,
            codec=VideoCodec.H264,
            bitrate=1_500_000
        )
        assert proxy.original_file == Path("/test/original.mov")
        assert proxy.resolution == ProxyResolution.PREVIEW
        assert proxy.bitrate == 1_500_000
    
    def test_archive_metadata_creation(self):
        metadata = ArchiveMetadata(
            archive_id="ARCH001",
            created_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
            total_size=100 * 1024 * 1024 * 1024,
            file_count=150,
            has_proxies=True,
            tape_id="TAPE001"
        )
        assert metadata.archive_id == "ARCH001"
        assert metadata.has_proxies is True
        assert metadata.tape_id == "TAPE001"
        assert metadata.version == "1.0"
        assert metadata.parent_archive is None
    
    def test_stream_request_defaults(self):
        request = StreamRequest(
            archive_path=Path("/archive.zip"),
            file_path="video.mp4"
        )
        assert request.start_byte == 0
        assert request.end_byte is None
        assert request.buffer_size == 8192
    
    def test_timecode_range_duration(self):
        start = Timecode(hours=0, minutes=10, seconds=0, frames=0, frame_rate=24.0)
        end = Timecode(hours=0, minutes=10, seconds=30, frames=0, frame_rate=24.0)
        
        tc_range = TimecodeRange(start=start, end=end, handles=0)
        assert tc_range.duration_frames == 30 * 24  # 30 seconds
        
        # With handles
        tc_range_with_handles = TimecodeRange(start=start, end=end, handles=24)
        assert tc_range_with_handles.duration_frames == (30 * 24) + (2 * 24)
    
    def test_archive_branch_creation(self):
        branch = ArchiveBranch(
            branch_id="branch001",
            parent_id="main",
            created_at=datetime.now(timezone.utc),
            description="Feature branch for VFX updates"
        )
        assert branch.branch_id == "branch001"
        assert branch.parent_id == "main"
        assert branch.changes == []
    
    def test_tape_archive_creation(self):
        tape = TapeArchive(
            tape_id="LTO001",
            format=TapeFormat.LTO8,
            capacity_bytes=12_000_000_000_000,
            used_bytes=8_000_000_000_000
        )
        assert tape.tape_id == "LTO001"
        assert tape.format == TapeFormat.LTO8
        assert tape.span_sequence == 1
        assert tape.total_spans == 1
        assert tape.catalog_path is None
        assert tape.verification_checksum is None
    
    def test_timecode_validation(self):
        # Valid timecode
        tc = Timecode(hours=23, minutes=59, seconds=59, frames=23, frame_rate=24.0)
        assert tc.hours == 23
        
        # Invalid values should raise validation errors
        with pytest.raises(ValueError):
            Timecode(hours=24, minutes=0, seconds=0, frames=0, frame_rate=24.0)
        
        with pytest.raises(ValueError):
            Timecode(hours=0, minutes=60, seconds=0, frames=0, frame_rate=24.0)
        
        with pytest.raises(ValueError):
            Timecode(hours=0, minutes=0, seconds=60, frames=0, frame_rate=24.0)
    
    def test_media_file_with_metadata(self):
        media = MediaFile(
            file_path=Path("/test/video.mov"),
            size=1024 * 1024 * 1024,
            codec=VideoCodec.PRORES_422,
            frame_rate=24.0,
            resolution=(3840, 2160),
            audio_channels=2,
            metadata={
                "camera": "ARRI Alexa",
                "lens": "Cooke S4/i",
                "iso": "800",
                "color_space": "ARRI LogC"
            }
        )
        assert media.metadata["camera"] == "ARRI Alexa"
        assert media.metadata["color_space"] == "ARRI LogC"
        assert len(media.metadata) == 4