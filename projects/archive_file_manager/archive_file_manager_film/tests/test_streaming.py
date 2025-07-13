import asyncio
import pytest
import pytest_asyncio
from pathlib import Path

from film_archive.core.models import StreamRequest
from film_archive.streaming.streamer import ArchiveStreamer


@pytest_asyncio.fixture
async def archive_streamer():
    streamer = ArchiveStreamer(cache_size=10 * 1024 * 1024)  # 10MB cache
    yield streamer
    # Cleanup
    for path in list(streamer._file_handles.keys()):
        await streamer.close_archive_stream(Path(path))


@pytest.fixture
def test_archive(tmp_path):
    # Create a test archive file
    archive_path = tmp_path / "test_archive.zip"
    archive_path.write_bytes(b"X" * 1024 * 1024)  # 1MB test data
    return archive_path


class TestArchiveStreamer:
    @pytest.mark.asyncio
    async def test_open_archive_stream(self, archive_streamer, test_archive):
        archive_info = await archive_streamer.open_archive_stream(test_archive)
        
        assert "handle" in archive_info
        assert archive_info["size"] == 1024 * 1024
        assert archive_info["path"] == test_archive
        
        # Test reopening same archive
        archive_info2 = await archive_streamer.open_archive_stream(test_archive)
        assert archive_info is archive_info2  # Should return same handle
    
    @pytest.mark.asyncio
    async def test_close_archive_stream(self, archive_streamer, test_archive):
        await archive_streamer.open_archive_stream(test_archive)
        assert str(test_archive) in archive_streamer._file_handles
        
        await archive_streamer.close_archive_stream(test_archive)
        assert str(test_archive) not in archive_streamer._file_handles
    
    def test_calculate_byte_range(self, archive_streamer):
        request = StreamRequest(
            archive_path=Path("/test.zip"),
            file_path="video.mp4",
            start_byte=100,
            end_byte=500
        )
        
        start, end = archive_streamer._calculate_byte_range(request, 1000)
        assert start == 100
        assert end == 500
        
        # Test with no end byte
        request.end_byte = None
        start, end = archive_streamer._calculate_byte_range(request, 1000)
        assert start == 100
        assert end == 999
        
        # Test with end byte exceeding file size
        request.end_byte = 2000
        start, end = archive_streamer._calculate_byte_range(request, 1000)
        assert start == 100
        assert end == 999
    
    @pytest.mark.asyncio
    async def test_stream_file_basic(self, archive_streamer, test_archive):
        request = StreamRequest(
            archive_path=test_archive,
            file_path="test.mp4",
            start_byte=0,
            end_byte=1023,
            buffer_size=256
        )
        
        chunks = []
        async for chunk in archive_streamer.stream_file(request):
            chunks.append(chunk)
        
        assert len(chunks) == 4  # 1024 / 256
        assert all(len(chunk) == 256 for chunk in chunks)
        assert b"".join(chunks) == b"X" * 1024
    
    @pytest.mark.asyncio
    async def test_stream_file_with_offset(self, archive_streamer, test_archive):
        request = StreamRequest(
            archive_path=test_archive,
            file_path="test.mp4",
            start_byte=512,
            end_byte=1023,
            buffer_size=128
        )
        
        chunks = []
        async for chunk in archive_streamer.stream_file(request):
            chunks.append(chunk)
        
        total_bytes = sum(len(chunk) for chunk in chunks)
        assert total_bytes == 512
    
    @pytest.mark.asyncio
    async def test_caching(self, archive_streamer, test_archive):
        request = StreamRequest(
            archive_path=test_archive,
            file_path="test.mp4",
            start_byte=0,
            end_byte=511,
            buffer_size=512
        )
        
        # First stream - should cache
        chunks1 = []
        async for chunk in archive_streamer.stream_file(request):
            chunks1.append(chunk)
        
        cache_key = f"{test_archive}:0:512"
        assert cache_key in archive_streamer._cache
        
        # Second stream - should use cache
        chunks2 = []
        async for chunk in archive_streamer.stream_file(request):
            chunks2.append(chunk)
        
        assert chunks1 == chunks2
    
    def test_calculate_bitrate_for_smooth_playback(self, archive_streamer):
        file_size = 1024 * 1024 * 1024  # 1GB
        duration = 600  # 10 minutes
        network_bandwidth = 100 * 1024 * 1024  # 100 Mbps
        
        bitrate = archive_streamer.calculate_bitrate_for_smooth_playback(
            file_size, duration, network_bandwidth
        )
        
        # Should be 80% of network bandwidth or file bitrate, whichever is lower
        file_bitrate = (file_size * 8) / duration
        safe_bandwidth = network_bandwidth * 0.8
        
        assert bitrate == int(min(file_bitrate, safe_bandwidth))
    
    @pytest.mark.asyncio
    async def test_create_http_range_response(self, archive_streamer, test_archive):
        request = StreamRequest(
            archive_path=test_archive,
            file_path="test.mp4"
        )
        
        # Test with range header
        response = await archive_streamer.create_http_range_response(
            request, "bytes=100-500"
        )
        
        assert response["status"] == 206
        assert response["headers"]["Content-Length"] == "401"
        assert response["headers"]["Content-Range"] == f"bytes 100-500/{1024*1024}"
        assert response["start"] == 100
        assert response["end"] == 500
        
        # Test without range header
        response = await archive_streamer.create_http_range_response(request)
        
        assert response["start"] == 0
        assert response["end"] == 1024 * 1024 - 1
    
    @pytest.mark.asyncio
    async def test_seek_to_frame(self, archive_streamer, test_archive):
        frame_number = 1000
        frame_rate = 24.0
        
        request = await archive_streamer.seek_to_frame(
            test_archive,
            "video.mp4",
            frame_number,
            frame_rate
        )
        
        assert isinstance(request, StreamRequest)
        assert request.archive_path == test_archive
        assert request.start_byte >= 0
        assert request.end_byte > request.start_byte
    
    def test_get_adaptive_buffer_size(self, archive_streamer):
        # Test with low latency, high bandwidth
        buffer_size = archive_streamer.get_adaptive_buffer_size(
            100 * 1024 * 1024,  # 100 Mbps
            10  # 10ms latency
        )
        
        assert buffer_size >= 64 * 1024  # At least 64KB
        assert buffer_size <= 10 * 1024 * 1024  # At most 10MB
        
        # Test with high latency
        buffer_size = archive_streamer.get_adaptive_buffer_size(
            10 * 1024 * 1024,  # 10 Mbps
            100  # 100ms latency
        )
        
        assert buffer_size > 64 * 1024
    
    @pytest.mark.asyncio
    async def test_get_stream_statistics(self, archive_streamer, test_archive):
        # Open a stream
        await archive_streamer.open_archive_stream(test_archive)
        
        # Add some cache entries
        archive_streamer._cache["test_key"] = b"X" * 1000
        
        stats = await archive_streamer.get_stream_statistics()
        
        assert stats["open_streams"] == 1
        assert stats["cache_size_bytes"] == 1000
        assert stats["cache_entries"] == 1
        assert stats["max_connections"] == 10


class TestStreamingPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_streams(self, tmp_path):
        archive_streamer = ArchiveStreamer()  # Create local instance
        
        # Create multiple test archives
        archives = []
        for i in range(5):
            archive_path = tmp_path / f"archive_{i}.zip"
            archive_path.write_bytes(b"Y" * 1024 * 100)  # 100KB each
            archives.append(archive_path)
        
        # Stream from all archives concurrently
        async def stream_archive(archive_path):
            request = StreamRequest(
                archive_path=archive_path,
                file_path="test.mp4",
                start_byte=0,
                end_byte=1024 * 100 - 1,
                buffer_size=8192  # Larger buffer
            )
            
            data = b""
            async for chunk in archive_streamer.stream_file(request):
                data += chunk
            return data
        
        results = await asyncio.gather(*[
            stream_archive(archive) for archive in archives
        ])
        
        assert len(results) == 5
        # Each archive is 100KB
        for i, data in enumerate(results):
            assert len(data) == 1024 * 100, f"Archive {i} returned {len(data)} bytes, expected {1024 * 100}"
    
    @pytest.mark.asyncio
    async def test_prefetch_performance(self, tmp_path):
        # Create larger test file
        archive_path = tmp_path / "large_archive.zip"
        archive_path.write_bytes(b"Z" * 1024 * 1024 * 10)  # 10MB
        
        request = StreamRequest(
            archive_path=archive_path,
            file_path="video.mp4",
            buffer_size=1024 * 100  # 100KB chunks
        )
        archive_streamer = ArchiveStreamer()  # Create local instance
        
        import time
        start_time = time.time()
        
        total_size = 0
        async for chunk in archive_streamer.stream_file(request):
            total_size += len(chunk)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert total_size == 1024 * 1024 * 10
        # Should stream 10MB quickly with prefetching
        assert duration < 2.0  # seconds