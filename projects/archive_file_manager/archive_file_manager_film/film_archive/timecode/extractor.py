import asyncio
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import timedelta

from film_archive.core.models import (
    MediaFile, Timecode, TimecodeRange
)


class TimecodeExtractor:
    """Handles timecode-based extraction of media segments"""
    
    def __init__(self, working_dir: Optional[Path] = None):
        self.working_dir = working_dir or Path("/tmp/film_archive_extracts")
        self.working_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_edl_timecodes(self, edl_content: str) -> List[TimecodeRange]:
        """Parse EDL (Edit Decision List) for timecode ranges"""
        ranges = []
        lines = edl_content.strip().split('\n')
        
        for line in lines:
            # Simple EDL parsing - format: "001  V  C  01:00:00:00 01:00:10:00 00:00:00:00 00:00:10:00"
            parts = line.split()
            if len(parts) >= 7 and parts[1] in ['V', 'A', 'B']:  # Video/Audio/Both
                try:
                    source_in = Timecode.from_string(parts[3], frame_rate=24.0)
                    source_out = Timecode.from_string(parts[4], frame_rate=24.0)
                    
                    ranges.append(TimecodeRange(
                        start=source_in,
                        end=source_out,
                        handles=0
                    ))
                except (ValueError, IndexError):
                    continue
        
        return ranges
    
    def calculate_byte_ranges(
        self, 
        media_file: MediaFile, 
        timecode_range: TimecodeRange,
        file_size: int
    ) -> Tuple[int, int]:
        """Calculate byte ranges for timecode extraction"""
        if not media_file.duration:
            raise ValueError("Media file has no duration information")
        
        total_frames = media_file.duration.total_frames
        total_seconds = total_frames / media_file.frame_rate
        
        # Calculate time positions
        start_seconds = timecode_range.start.total_frames / timecode_range.start.frame_rate
        end_seconds = timecode_range.end.total_frames / timecode_range.end.frame_rate
        
        # Add handles (extra frames)
        if timecode_range.handles > 0:
            handle_seconds = timecode_range.handles / timecode_range.start.frame_rate
            start_seconds = max(0, start_seconds - handle_seconds)
            end_seconds = min(total_seconds, end_seconds + handle_seconds)
        
        # Calculate byte positions (simplified - assumes constant bitrate)
        bytes_per_second = file_size / total_seconds
        start_byte = int(start_seconds * bytes_per_second)
        end_byte = int(end_seconds * bytes_per_second)
        
        # Align to frame boundaries (simplified)
        frame_size_estimate = int(bytes_per_second / media_file.frame_rate)
        start_byte = (start_byte // frame_size_estimate) * frame_size_estimate
        end_byte = ((end_byte // frame_size_estimate) + 1) * frame_size_estimate
        
        return start_byte, min(end_byte, file_size - 1)
    
    async def extract_segment(
        self, 
        archive_data: io.BytesIO, 
        media_file: MediaFile,
        timecode_range: TimecodeRange,
        output_path: Optional[Path] = None
    ) -> Path:
        """Extract a segment based on timecode range"""
        # Calculate byte ranges
        archive_data.seek(0, 2)  # Seek to end
        file_size = archive_data.tell()
        archive_data.seek(0)  # Reset to start
        
        start_byte, end_byte = self.calculate_byte_ranges(
            media_file, timecode_range, file_size
        )
        
        # Generate output filename
        if not output_path:
            tc_start = str(timecode_range.start).replace(':', '')
            tc_end = str(timecode_range.end).replace(':', '')
            output_path = self.working_dir / f"{media_file.file_path.stem}_{tc_start}_{tc_end}.mp4"
        
        # Extract segment
        archive_data.seek(start_byte)
        segment_size = end_byte - start_byte + 1
        segment_data = archive_data.read(segment_size)
        
        # Write to output file
        output_path.write_bytes(segment_data)
        
        return output_path
    
    async def extract_multiple_segments(
        self, 
        archive_data: io.BytesIO, 
        media_file: MediaFile,
        timecode_ranges: List[TimecodeRange]
    ) -> List[Path]:
        """Extract multiple segments in parallel"""
        tasks = []
        
        for i, tc_range in enumerate(timecode_ranges):
            # Create separate BytesIO for each task to avoid seek conflicts
            archive_copy = io.BytesIO(archive_data.getvalue())
            
            task = self.extract_segment(
                archive_copy, 
                media_file, 
                tc_range
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    def merge_overlapping_ranges(
        self, 
        ranges: List[TimecodeRange]
    ) -> List[TimecodeRange]:
        """Merge overlapping timecode ranges for efficiency"""
        if not ranges:
            return []
        
        # Sort by start timecode
        sorted_ranges = sorted(ranges, key=lambda r: r.start.total_frames)
        
        merged = [sorted_ranges[0]]
        
        for current in sorted_ranges[1:]:
            last = merged[-1]
            
            # Check for overlap (including handles)
            last_end_with_handles = last.end.total_frames + last.handles
            current_start_with_handles = current.start.total_frames - current.handles
            
            if current_start_with_handles <= last_end_with_handles:
                # Merge ranges
                new_end_frames = max(last.end.total_frames, current.end.total_frames)
                new_end = Timecode(
                    hours=new_end_frames // (3600 * int(current.end.frame_rate)),
                    minutes=(new_end_frames // (60 * int(current.end.frame_rate))) % 60,
                    seconds=(new_end_frames // int(current.end.frame_rate)) % 60,
                    frames=new_end_frames % int(current.end.frame_rate),
                    frame_rate=current.end.frame_rate
                )
                
                merged[-1] = TimecodeRange(
                    start=last.start,
                    end=new_end,
                    handles=max(last.handles, current.handles)
                )
            else:
                merged.append(current)
        
        return merged
    
    def calculate_extraction_time(
        self, 
        timecode_ranges: List[TimecodeRange], 
        extraction_speed_mbps: float = 300
    ) -> float:
        """Estimate extraction time based on ranges and speed"""
        total_frames = sum(r.duration_frames for r in timecode_ranges)
        
        # Assume average frame size (simplified)
        avg_frame_size_mb = 0.5  # 500KB per frame for 4K
        total_size_mb = total_frames * avg_frame_size_mb
        
        # Calculate time
        extraction_time_seconds = total_size_mb / extraction_speed_mbps
        
        # Add overhead for seeking and processing
        overhead_factor = 1.2
        
        return extraction_time_seconds * overhead_factor
    
    def validate_timecode_continuity(
        self, 
        extracted_segments: List[Path], 
        expected_ranges: List[TimecodeRange]
    ) -> Dict[str, any]:
        """Validate that extracted segments maintain timecode continuity"""
        validation_results = {
            "valid": True,
            "segments": [],
            "errors": []
        }
        
        for segment_path, expected_range in zip(extracted_segments, expected_ranges):
            if not segment_path.exists():
                validation_results["valid"] = False
                validation_results["errors"].append(
                    f"Segment {segment_path} does not exist"
                )
                continue
            
            # Simplified validation - check file size is reasonable
            segment_size = segment_path.stat().st_size
            expected_frames = expected_range.duration_frames
            
            # Rough estimate: 100KB-10MB per frame
            min_size = expected_frames * 100 * 1024
            max_size = expected_frames * 10 * 1024 * 1024
            
            segment_info = {
                "path": str(segment_path),
                "size": segment_size,
                "expected_frames": expected_frames,
                "valid": min_size <= segment_size <= max_size
            }
            
            if not segment_info["valid"]:
                validation_results["valid"] = False
                validation_results["errors"].append(
                    f"Segment {segment_path} size {segment_size} outside expected range"
                )
            
            validation_results["segments"].append(segment_info)
        
        return validation_results
    
    def create_extraction_manifest(
        self, 
        media_file: MediaFile, 
        timecode_ranges: List[TimecodeRange],
        extracted_paths: List[Path]
    ) -> Dict[str, any]:
        """Create manifest documenting the extraction"""
        return {
            "source_file": str(media_file.file_path),
            "source_codec": media_file.codec.value,
            "source_frame_rate": media_file.frame_rate,
            "extractions": [
                {
                    "timecode_in": str(tc_range.start),
                    "timecode_out": str(tc_range.end),
                    "handles": tc_range.handles,
                    "output_file": str(path),
                    "size_bytes": path.stat().st_size if path.exists() else 0
                }
                for tc_range, path in zip(timecode_ranges, extracted_paths)
            ],
            "total_extracted_frames": sum(r.duration_frames for r in timecode_ranges)
        }
    
    def cleanup_extracted_files(self):
        """Remove temporary extracted files"""
        for file in self.working_dir.glob("*.mp4"):
            file.unlink()