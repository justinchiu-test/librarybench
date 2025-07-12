import asyncio
import io
import mmap
import os
from pathlib import Path
from typing import AsyncIterator, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import aiofiles

from film_archive.core.models import StreamRequest


class ArchiveStreamer:
    """Provides streaming access to archived media files"""
    
    def __init__(
        self, 
        cache_size: int = 100 * 1024 * 1024,  # 100MB cache
        prefetch_size: int = 10 * 1024 * 1024,  # 10MB prefetch
        max_connections: int = 10
    ):
        self.cache_size = cache_size
        self.prefetch_size = prefetch_size
        self.max_connections = max_connections
        self._cache: Dict[str, bytes] = {}
        self._file_handles: Dict[str, any] = {}
        self._lock = asyncio.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_connections)
    
    async def open_archive_stream(self, archive_path: Path) -> Dict[str, any]:
        """Open archive for streaming access"""
        async with self._lock:
            if str(archive_path) not in self._file_handles:
                # Open file handle for streaming
                handle = await aiofiles.open(archive_path, 'rb')
                self._file_handles[str(archive_path)] = {
                    "handle": handle,
                    "size": archive_path.stat().st_size,
                    "path": archive_path
                }
        
        return self._file_handles[str(archive_path)]
    
    async def close_archive_stream(self, archive_path: Path):
        """Close archive stream and cleanup resources"""
        async with self._lock:
            key = str(archive_path)
            if key in self._file_handles:
                await self._file_handles[key]["handle"].close()
                del self._file_handles[key]
                
                # Clear cache entries for this archive
                cache_keys_to_remove = [
                    k for k in self._cache.keys() 
                    if k.startswith(key)
                ]
                for k in cache_keys_to_remove:
                    del self._cache[k]
    
    def _calculate_byte_range(
        self, 
        request: StreamRequest, 
        file_size: int
    ) -> Tuple[int, int]:
        """Calculate actual byte range for streaming"""
        start = request.start_byte
        end = request.end_byte if request.end_byte else file_size - 1
        
        # Validate range
        if file_size == 0:
            return 0, 0  # Empty file
            
        if start >= file_size:
            raise ValueError(f"Start byte {start} exceeds file size {file_size}")
        
        end = min(end, file_size - 1)
        
        return start, end
    
    async def _read_with_cache(
        self, 
        file_handle: any, 
        start: int, 
        size: int, 
        cache_key: str
    ) -> bytes:
        """Read data with caching support"""
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Read from file
        await file_handle.seek(start)
        data = await file_handle.read(size)
        
        # Update cache if within size limit
        if len(data) <= self.cache_size // 10:  # Cache chunks up to 10% of total cache
            async with self._lock:
                self._cache[cache_key] = data
                
                # Evict old entries if cache is full
                while sum(len(v) for v in self._cache.values()) > self.cache_size:
                    # Remove oldest entry (simple FIFO)
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
        
        return data
    
    async def stream_file(
        self, 
        request: StreamRequest
    ) -> AsyncIterator[bytes]:
        """Stream file data from archive"""
        # Open archive stream
        archive_info = await self.open_archive_stream(request.archive_path)
        file_handle = archive_info["handle"]
        
        # Calculate byte range
        start, end = self._calculate_byte_range(request, archive_info["size"])
        total_size = end - start + 1
        
        # Stream data in chunks
        current_pos = start
        while current_pos <= end:
            chunk_size = min(request.buffer_size, end - current_pos + 1)
            cache_key = f"{request.archive_path}:{current_pos}:{chunk_size}"
            
            # Read chunk with caching
            chunk = await self._read_with_cache(
                file_handle, 
                current_pos, 
                chunk_size, 
                cache_key
            )
            
            if not chunk:
                break
            
            yield chunk
            current_pos += len(chunk)
            
            # Prefetch next chunk asynchronously
            if current_pos <= end:
                next_chunk_size = min(self.prefetch_size, end - current_pos + 1)
                next_cache_key = f"{request.archive_path}:{current_pos}:{next_chunk_size}"
                asyncio.create_task(
                    self._read_with_cache(
                        file_handle, 
                        current_pos, 
                        next_chunk_size, 
                        next_cache_key
                    )
                )
    
    def calculate_bitrate_for_smooth_playback(
        self, 
        file_size: int, 
        duration_seconds: float, 
        network_bandwidth: int
    ) -> int:
        """Calculate optimal bitrate for smooth streaming"""
        file_bitrate = int((file_size * 8) / duration_seconds)
        
        # Use 80% of available bandwidth for safety margin
        safe_bandwidth = int(network_bandwidth * 0.8)
        
        return min(file_bitrate, safe_bandwidth)
    
    async def create_http_range_response(
        self, 
        request: StreamRequest, 
        range_header: Optional[str] = None
    ) -> Dict[str, any]:
        """Create HTTP range response for streaming"""
        archive_info = await self.open_archive_stream(request.archive_path)
        file_size = archive_info["size"]
        
        # Parse range header
        if range_header:
            # Format: "bytes=start-end"
            range_spec = range_header.replace("bytes=", "")
            parts = range_spec.split("-")
            
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else file_size - 1
        else:
            start = request.start_byte
            end = request.end_byte if request.end_byte else file_size - 1
        
        # Validate range
        start = max(0, min(start, file_size - 1))
        end = max(start, min(end, file_size - 1))
        
        content_length = end - start + 1
        
        return {
            "status": 206,  # Partial Content
            "headers": {
                "Content-Type": "video/mp4",
                "Content-Length": str(content_length),
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Cache-Control": "no-cache"
            },
            "start": start,
            "end": end,
            "total_size": file_size
        }
    
    async def seek_to_frame(
        self, 
        archive_path: Path, 
        file_path: str, 
        frame_number: int, 
        frame_rate: float, 
        frame_size_estimate: int = 100_000
    ) -> StreamRequest:
        """Create stream request for specific frame position"""
        # Calculate approximate byte position
        # This is a simplified estimation - real implementation would use index
        time_offset = frame_number / frame_rate
        
        # Estimate byte position (simplified - assumes constant bitrate)
        archive_info = await self.open_archive_stream(archive_path)
        file_size = archive_info["size"]
        
        # For testing, use a simple linear approximation
        estimated_position = int(time_offset * frame_size_estimate * frame_rate)
        
        # Ensure we don't exceed file bounds
        start_byte = min(estimated_position, file_size - frame_size_estimate)
        start_byte = max(0, start_byte)
        
        return StreamRequest(
            archive_path=archive_path,
            file_path=file_path,
            start_byte=start_byte,
            end_byte=start_byte + frame_size_estimate
        )
    
    def get_adaptive_buffer_size(
        self, 
        network_bandwidth: int, 
        latency_ms: int
    ) -> int:
        """Calculate adaptive buffer size based on network conditions"""
        # Buffer for latency compensation
        latency_buffer = int((network_bandwidth / 8) * (latency_ms / 1000))
        
        # Add safety margin
        safety_factor = 2.0
        buffer_size = int(latency_buffer * safety_factor)
        
        # Clamp to reasonable limits
        min_buffer = 64 * 1024    # 64KB minimum
        max_buffer = 10 * 1024 * 1024  # 10MB maximum
        
        return max(min_buffer, min(buffer_size, max_buffer))
    
    async def get_stream_statistics(self) -> Dict[str, any]:
        """Get streaming performance statistics"""
        return {
            "open_streams": len(self._file_handles),
            "cache_size_bytes": sum(len(v) for v in self._cache.values()),
            "cache_entries": len(self._cache),
            "max_connections": self.max_connections
        }
    
    def __del__(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=False)
        # Note: In real implementation, would properly close all file handles