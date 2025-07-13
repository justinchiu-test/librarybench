import hashlib
import io
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from film_archive.core.models import (
    MediaFile, ProxyFile, ProxyResolution, VideoCodec
)


class ProxyGenerator:
    """Generates low-resolution proxy files for video media"""
    
    RESOLUTION_SETTINGS = {
        ProxyResolution.THUMBNAIL: {
            "width": 320,
            "height": 180,
            "bitrate": 500_000,  # 500 kbps
            "fps": 12
        },
        ProxyResolution.PREVIEW: {
            "width": 854,
            "height": 480,
            "bitrate": 1_500_000,  # 1.5 Mbps
            "fps": 24
        },
        ProxyResolution.EDITORIAL: {
            "width": 1920,
            "height": 1080,
            "bitrate": 5_000_000,  # 5 Mbps
            "fps": 24
        }
    }
    
    def __init__(self, temp_dir: Optional[Path] = None, max_workers: int = 4):
        self.temp_dir = temp_dir or Path("/tmp/film_archive_proxies")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def _calculate_dimensions(
        self, 
        original_width: int, 
        original_height: int, 
        target_resolution: ProxyResolution
    ) -> Tuple[int, int]:
        """Calculate proxy dimensions maintaining aspect ratio"""
        settings = self.RESOLUTION_SETTINGS[target_resolution]
        target_width = settings["width"]
        target_height = settings["height"]
        
        aspect_ratio = original_width / original_height
        target_aspect = target_width / target_height
        
        if aspect_ratio > target_aspect:
            height = int(target_width / aspect_ratio)
            height = height - (height % 2)  # Ensure even
            return target_width, height
        else:
            width = int(target_height * aspect_ratio)
            width = width - (width % 2)  # Ensure even
            return width, target_height
    
    def _generate_proxy_data(
        self, 
        media_file: MediaFile, 
        resolution: ProxyResolution
    ) -> bytes:
        """Generate simulated proxy data for testing"""
        settings = self.RESOLUTION_SETTINGS[resolution]
        width, height = self._calculate_dimensions(
            media_file.resolution[0], 
            media_file.resolution[1], 
            resolution
        )
        
        # Simulate proxy generation with deterministic data
        proxy_identifier = f"{media_file.file_path}_{resolution}_{width}x{height}"
        proxy_hash = hashlib.sha256(proxy_identifier.encode()).digest()
        
        # Calculate approximate proxy size based on duration and bitrate
        if media_file.duration:
            duration_seconds = media_file.duration.total_frames / media_file.frame_rate
            proxy_size = int((settings["bitrate"] * duration_seconds) / 8)
        else:
            proxy_size = 1024 * 1024  # 1MB default
        
        # Generate deterministic proxy data
        data = bytearray()
        while len(data) < proxy_size:
            data.extend(proxy_hash)
        
        return bytes(data[:proxy_size])
    
    async def generate_proxy(
        self, 
        media_file: MediaFile, 
        resolution: ProxyResolution
    ) -> ProxyFile:
        """Generate a single proxy file"""
        proxy_filename = f"{media_file.file_path.stem}_{resolution.value}.mp4"
        proxy_path = self.temp_dir / proxy_filename
        
        # Generate proxy data in thread pool
        loop = asyncio.get_event_loop()
        proxy_data = await loop.run_in_executor(
            self.executor, 
            self._generate_proxy_data, 
            media_file, 
            resolution
        )
        
        # Write proxy data
        proxy_path.write_bytes(proxy_data)
        
        settings = self.RESOLUTION_SETTINGS[resolution]
        
        return ProxyFile(
            original_file=media_file.file_path,
            proxy_path=proxy_path,
            resolution=resolution,
            size=len(proxy_data),
            codec=VideoCodec.H264,
            bitrate=settings["bitrate"]
        )
    
    async def generate_proxies(
        self, 
        media_file: MediaFile, 
        resolutions: List[ProxyResolution]
    ) -> List[ProxyFile]:
        """Generate multiple proxy resolutions for a media file"""
        tasks = [
            self.generate_proxy(media_file, resolution)
            for resolution in resolutions
        ]
        return await asyncio.gather(*tasks)
    
    def embed_proxy_in_archive(
        self, 
        archive_data: io.BytesIO, 
        proxy_file: ProxyFile
    ) -> Dict[str, any]:
        """Embed proxy as a separate stream in archive"""
        # Read proxy data
        proxy_data = proxy_file.proxy_path.read_bytes()
        
        # Create proxy stream metadata
        proxy_metadata = {
            "stream_id": f"proxy_{proxy_file.resolution.value}",
            "original_file": str(proxy_file.original_file),
            "resolution": proxy_file.resolution.value,
            "codec": proxy_file.codec.value,
            "bitrate": proxy_file.bitrate,
            "size": proxy_file.size,
            "offset": archive_data.tell()
        }
        
        # Write proxy stream marker
        marker = b"PROXY_STREAM_START"
        archive_data.write(marker)
        archive_data.write(len(proxy_data).to_bytes(8, 'big'))
        
        # Write proxy data
        archive_data.write(proxy_data)
        
        # Write end marker
        archive_data.write(b"PROXY_STREAM_END")
        
        return proxy_metadata
    
    def extract_proxy_from_archive(
        self, 
        archive_data: io.BytesIO, 
        proxy_metadata: Dict[str, any]
    ) -> bytes:
        """Extract proxy stream from archive"""
        # Seek to proxy offset
        archive_data.seek(proxy_metadata["offset"])
        
        # Read and verify marker
        marker = archive_data.read(18)  # len("PROXY_STREAM_START")
        if marker != b"PROXY_STREAM_START":
            raise ValueError("Invalid proxy stream marker")
        
        # Read proxy size
        size_bytes = archive_data.read(8)
        proxy_size = int.from_bytes(size_bytes, 'big')
        
        # Read proxy data
        proxy_data = archive_data.read(proxy_size)
        
        # Verify end marker
        end_marker = archive_data.read(16)  # len("PROXY_STREAM_END")
        if end_marker != b"PROXY_STREAM_END":
            raise ValueError("Invalid proxy stream end marker")
        
        return proxy_data
    
    def select_optimal_proxy(
        self, 
        available_proxies: List[ProxyFile], 
        target_bandwidth: int,
        display_resolution: Tuple[int, int]
    ) -> Optional[ProxyFile]:
        """Select best proxy based on bandwidth and display constraints"""
        if not available_proxies:
            return None
        
        # Filter proxies that fit within bandwidth
        suitable_proxies = [
            p for p in available_proxies 
            if p.bitrate <= target_bandwidth
        ]
        
        if not suitable_proxies:
            # Return lowest bitrate proxy if none fit
            return min(available_proxies, key=lambda p: p.bitrate)
        
        # Sort by resolution preference
        resolution_order = [
            ProxyResolution.EDITORIAL,
            ProxyResolution.PREVIEW,
            ProxyResolution.THUMBNAIL
        ]
        
        # Select highest quality that fits
        for resolution in resolution_order:
            for proxy in suitable_proxies:
                if proxy.resolution == resolution:
                    return proxy
        
        return suitable_proxies[0]
    
    def cleanup_temp_files(self):
        """Remove temporary proxy files"""
        for file in self.temp_dir.glob("*.mp4"):
            file.unlink()
    
    async def cleanup_temp_files_async(self):
        """Clean up temporary files"""
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("*"):
                file.unlink()
            self.temp_dir.rmdir()
    
    def calculate_proxy_bitrate(self, resolution: ProxyResolution) -> int:
        """Calculate bitrate for proxy resolution"""
        bitrates = {
            ProxyResolution.THUMBNAIL: 500_000,     # 500 kbps
            ProxyResolution.PREVIEW: 1_500_000,     # 1.5 Mbps
            ProxyResolution.EDITORIAL: 5_000_000    # 5 Mbps
        }
        return bitrates[resolution]
    
    def __del__(self):
        """Cleanup on deletion"""
        self.executor.shutdown(wait=False)
        self.cleanup_temp_files()