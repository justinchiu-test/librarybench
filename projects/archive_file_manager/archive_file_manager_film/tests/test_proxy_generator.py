import asyncio
import pytest
from pathlib import Path
import io

from film_archive.core.models import MediaFile, ProxyResolution, VideoCodec
from film_archive.proxy.generator import ProxyGenerator


@pytest.fixture
def proxy_generator(tmp_path):
    return ProxyGenerator(temp_dir=tmp_path)


@pytest.fixture
def sample_media_file():
    return MediaFile(
        file_path=Path("/test/video.mov"),
        size=1024 * 1024 * 1024,  # 1GB
        codec=VideoCodec.PRORES_422,
        duration=None,
        frame_rate=24.0,
        resolution=(3840, 2160),  # 4K
        audio_channels=2
    )


@pytest.fixture
def sample_media_file_with_duration():
    from film_archive.core.models import Timecode
    return MediaFile(
        file_path=Path("/test/video_with_duration.mov"),
        size=5 * 1024 * 1024 * 1024,  # 5GB
        codec=VideoCodec.PRORES_4444,
        duration=Timecode(hours=0, minutes=10, seconds=0, frames=0, frame_rate=24.0),
        frame_rate=24.0,
        resolution=(3840, 2160),
        audio_channels=8
    )


class TestProxyGenerator:
    def test_calculate_dimensions_maintain_aspect_ratio(self, proxy_generator):
        # Test 16:9 aspect ratio
        width, height = proxy_generator._calculate_dimensions(
            3840, 2160, ProxyResolution.PREVIEW
        )
        # Width should be even and maintain aspect ratio
        assert width % 2 == 0
        assert height == 480
        assert width / height == pytest.approx(3840 / 2160, rel=0.01)
        
        # Test 2.39:1 aspect ratio (cinema)
        width, height = proxy_generator._calculate_dimensions(
            4096, 1716, ProxyResolution.EDITORIAL
        )
        assert width == 1920
        assert height <= 1080
        assert width % 2 == 0
        assert height % 2 == 0
    
    def test_generate_proxy_data_deterministic(self, proxy_generator, sample_media_file):
        # Generate proxy data twice - should be identical
        data1 = proxy_generator._generate_proxy_data(
            sample_media_file, ProxyResolution.THUMBNAIL
        )
        data2 = proxy_generator._generate_proxy_data(
            sample_media_file, ProxyResolution.THUMBNAIL
        )
        
        assert data1 == data2
        assert len(data1) > 0
    
    def test_generate_proxy_data_with_duration(
        self, proxy_generator, sample_media_file_with_duration
    ):
        data = proxy_generator._generate_proxy_data(
            sample_media_file_with_duration, ProxyResolution.PREVIEW
        )
        
        # Check size is based on duration and bitrate
        settings = proxy_generator.RESOLUTION_SETTINGS[ProxyResolution.PREVIEW]
        expected_size = int((settings["bitrate"] * 600) / 8)  # 10 minutes
        assert len(data) == expected_size
    
    @pytest.mark.asyncio
    async def test_generate_proxy_single(self, proxy_generator, sample_media_file):
        proxy = await proxy_generator.generate_proxy(
            sample_media_file, ProxyResolution.PREVIEW
        )
        
        assert proxy.original_file == sample_media_file.file_path
        assert proxy.resolution == ProxyResolution.PREVIEW
        assert proxy.codec == VideoCodec.H264
        assert proxy.proxy_path.exists()
        assert proxy.size > 0
        assert proxy.bitrate == 1_500_000
    
    @pytest.mark.asyncio
    async def test_generate_proxies_multiple_resolutions(
        self, proxy_generator, sample_media_file_with_duration
    ):
        resolutions = [
            ProxyResolution.THUMBNAIL,
            ProxyResolution.PREVIEW,
            ProxyResolution.EDITORIAL
        ]
        
        proxies = await proxy_generator.generate_proxies(
            sample_media_file_with_duration, resolutions
        )
        
        assert len(proxies) == 3
        
        # Verify each proxy
        for proxy, resolution in zip(proxies, resolutions):
            assert proxy.resolution == resolution
            assert proxy.proxy_path.exists()
            assert proxy.original_file == sample_media_file_with_duration.file_path
        
        # Verify sizes are in expected order
        assert proxies[0].size < proxies[1].size < proxies[2].size
    
    def test_embed_proxy_in_archive(self, proxy_generator, tmp_path):
        # Create a test proxy file
        proxy_path = tmp_path / "test_proxy.mp4"
        proxy_path.write_bytes(b"PROXY_DATA_CONTENT")
        
        from film_archive.core.models import ProxyFile
        proxy_file = ProxyFile(
            original_file=Path("/test/original.mov"),
            proxy_path=proxy_path,
            resolution=ProxyResolution.PREVIEW,
            size=len(b"PROXY_DATA_CONTENT"),
            codec=VideoCodec.H264,
            bitrate=1_500_000
        )
        
        # Embed in archive
        archive_data = io.BytesIO()
        metadata = proxy_generator.embed_proxy_in_archive(archive_data, proxy_file)
        
        assert metadata["stream_id"] == "proxy_preview"
        assert metadata["resolution"] == "preview"
        assert metadata["size"] == len(b"PROXY_DATA_CONTENT")
        assert metadata["offset"] == 0
        
        # Verify archive structure
        archive_data.seek(0)
        assert archive_data.read(18) == b"PROXY_STREAM_START"
    
    def test_extract_proxy_from_archive(self, proxy_generator, tmp_path):
        # Create archive with embedded proxy
        proxy_data = b"EXTRACTED_PROXY_DATA"
        archive_data = io.BytesIO()
        
        # Write proxy stream
        archive_data.write(b"PROXY_STREAM_START")
        archive_data.write(len(proxy_data).to_bytes(8, 'big'))
        archive_data.write(proxy_data)
        archive_data.write(b"PROXY_STREAM_END")
        
        # Create metadata
        metadata = {
            "stream_id": "proxy_preview",
            "offset": 0,
            "size": len(proxy_data)
        }
        
        # Extract proxy
        extracted = proxy_generator.extract_proxy_from_archive(
            archive_data, metadata
        )
        
        assert extracted == proxy_data
    
    def test_select_optimal_proxy_bandwidth_constraint(self, proxy_generator):
        from film_archive.core.models import ProxyFile
        
        # Create proxies with different bitrates
        proxies = [
            ProxyFile(
                original_file=Path("/test.mov"),
                proxy_path=Path("/proxy_thumb.mp4"),
                resolution=ProxyResolution.THUMBNAIL,
                size=1000,
                bitrate=500_000
            ),
            ProxyFile(
                original_file=Path("/test.mov"),
                proxy_path=Path("/proxy_preview.mp4"),
                resolution=ProxyResolution.PREVIEW,
                size=5000,
                bitrate=1_500_000
            ),
            ProxyFile(
                original_file=Path("/test.mov"),
                proxy_path=Path("/proxy_editorial.mp4"),
                resolution=ProxyResolution.EDITORIAL,
                size=10000,
                bitrate=5_000_000
            )
        ]
        
        # Test with limited bandwidth
        optimal = proxy_generator.select_optimal_proxy(
            proxies,
            target_bandwidth=1_000_000,  # 1 Mbps
            display_resolution=(1920, 1080)
        )
        
        assert optimal.resolution == ProxyResolution.THUMBNAIL
        
        # Test with high bandwidth
        optimal = proxy_generator.select_optimal_proxy(
            proxies,
            target_bandwidth=10_000_000,  # 10 Mbps
            display_resolution=(3840, 2160)
        )
        
        assert optimal.resolution == ProxyResolution.EDITORIAL
    
    def test_cleanup_temp_files(self, proxy_generator, tmp_path):
        # Create some temp files
        for i in range(3):
            (tmp_path / f"temp_proxy_{i}.mp4").write_text("data")
        
        assert len(list(tmp_path.glob("*.mp4"))) == 3
        
        proxy_generator.cleanup_temp_files()
        
        assert len(list(tmp_path.glob("*.mp4"))) == 0


class TestProxyPerformance:
    @pytest.mark.asyncio
    async def test_parallel_proxy_generation_performance(
        self, proxy_generator, sample_media_file
    ):
        # Test generating multiple proxies in parallel
        import time
        
        start_time = time.time()
        
        # Generate 10 sets of proxies
        tasks = []
        for i in range(10):
            media_file = MediaFile(
                file_path=Path(f"/test/video_{i}.mov"),
                size=sample_media_file.size,
                codec=sample_media_file.codec,
                frame_rate=sample_media_file.frame_rate,
                resolution=sample_media_file.resolution,
                audio_channels=sample_media_file.audio_channels
            )
            
            task = proxy_generator.generate_proxies(
                media_file,
                [ProxyResolution.THUMBNAIL, ProxyResolution.PREVIEW]
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert len(results) == 10
        assert all(len(proxies) == 2 for proxies in results)
        
        # Should complete in reasonable time (parallel execution)
        assert duration < 5.0  # seconds