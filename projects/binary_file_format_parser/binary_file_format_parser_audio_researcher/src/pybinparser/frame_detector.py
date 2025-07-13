"""Audio frame boundary detection module"""

from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field
import struct
from .core import BinaryParser, AudioFrame, AudioFormat


class FrameInfo(BaseModel):
    """Frame detection information"""
    
    sync_pattern: bytes = Field(description="Frame synchronization pattern")
    header_size: int = Field(description="Frame header size in bytes")
    frame_size: Optional[int] = Field(None, description="Fixed frame size if applicable")
    variable_length: bool = Field(default=False, description="Whether frames have variable length")


class FrameDetector:
    """Detects and extracts audio frame boundaries"""
    
    # Common sync patterns for various formats
    SYNC_PATTERNS: Dict[AudioFormat, bytes] = {
        AudioFormat.MP3: b"\xFF\xFB",  # MP3 sync word (11 bits set)
        AudioFormat.AAC: b"\xFF\xF1",  # AAC ADTS sync word
        AudioFormat.FLAC: b"fLaC",     # FLAC stream marker
        AudioFormat.OGG: b"OggS",      # Ogg page header
        AudioFormat.OPUS: b"OpusHead", # Opus header
    }
    
    # Frame header sizes
    HEADER_SIZES: Dict[AudioFormat, int] = {
        AudioFormat.MP3: 4,
        AudioFormat.AAC: 7,
        AudioFormat.FLAC: 4,
        AudioFormat.OGG: 27,
        AudioFormat.OPUS: 19,
    }
    
    def __init__(self, parser: BinaryParser):
        """Initialize frame detector with binary parser"""
        self.parser = parser
        self._detected_format: Optional[AudioFormat] = None
        
    def detect_format(self) -> AudioFormat:
        """Auto-detect audio format from file"""
        self.parser.seek(0)
        header = self.parser.read(32)
        
        # Check for WAV format
        if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
            self._detected_format = AudioFormat.WAV
            return AudioFormat.WAV
            
        # Check sync patterns
        for format_type, pattern in self.SYNC_PATTERNS.items():
            if pattern in header[:len(pattern)]:
                self._detected_format = format_type
                return format_type
                
        # Check for MP3 with ID3v2 tag
        if header[:3] == b"ID3":
            # Skip ID3v2 tag to find MP3 sync
            tag_size = self._get_id3v2_size(header)
            self.parser.seek(tag_size)
            next_header = self.parser.read(2)
            if next_header == b"\xFF\xFB" or (len(next_header) == 2 and (next_header[0] == 0xFF and (next_header[1] & 0xE0) == 0xE0)):
                self._detected_format = AudioFormat.MP3
                return AudioFormat.MP3
                
        self._detected_format = AudioFormat.UNKNOWN
        return AudioFormat.UNKNOWN
        
    def _get_id3v2_size(self, header: bytes) -> int:
        """Calculate ID3v2 tag size"""
        if len(header) < 10 or header[:3] != b"ID3":
            return 0
            
        # Synchsafe integer decoding
        size = ((header[6] & 0x7F) << 21) | \
               ((header[7] & 0x7F) << 14) | \
               ((header[8] & 0x7F) << 7) | \
               (header[9] & 0x7F)
        return size + 10  # Add header size
        
    def find_frames(self, max_frames: Optional[int] = None) -> List[AudioFrame]:
        """Find all audio frames in the file"""
        if self._detected_format is None:
            self.detect_format()
            
        if self._detected_format == AudioFormat.UNKNOWN:
            return []
            
        if self._detected_format == AudioFormat.WAV:
            return self._find_wav_frames(max_frames)
        elif self._detected_format == AudioFormat.MP3:
            return self._find_mp3_frames(max_frames)
        elif self._detected_format == AudioFormat.AAC:
            return self._find_aac_frames(max_frames)
        elif self._detected_format == AudioFormat.FLAC:
            return self._find_flac_frames(max_frames)
        elif self._detected_format == AudioFormat.OGG:
            return self._find_ogg_frames(max_frames)
            
        return []
        
    def _find_mp3_frames(self, max_frames: Optional[int]) -> List[AudioFrame]:
        """Find MP3 frames"""
        frames = []
        self.parser.seek(0)
        
        # Skip ID3v2 if present
        header = self.parser.read(10)
        self.parser.seek(0)
        if header[:3] == b"ID3":
            tag_size = self._get_id3v2_size(header)
            self.parser.seek(tag_size)
            
        frame_count = 0
        while True:
            if max_frames and frame_count >= max_frames:
                break
                
            # Find sync pattern
            sync_pos = self._find_mp3_sync()
            if sync_pos == -1:
                break
                
            self.parser.seek(sync_pos)
            frame_header = self.parser.read(4)
            
            if len(frame_header) < 4:
                break
                
            # Parse MP3 header
            frame_size = self._calculate_mp3_frame_size(frame_header)
            if frame_size <= 0:
                self.parser.seek(sync_pos + 1)
                continue
                
            # Read frame data
            self.parser.seek(sync_pos)
            frame_data = self.parser.read(frame_size)
            
            if len(frame_data) < frame_size:
                break
                
            frames.append(AudioFrame(
                offset=sync_pos,
                size=frame_size,
                header=frame_header,
                data=frame_data[4:],  # Exclude header
                timestamp=self._calculate_mp3_timestamp(frame_count)
            ))
            
            frame_count += 1
            
        return frames
        
    def _find_mp3_sync(self) -> int:
        """Find next MP3 sync pattern"""
        while self.parser.tell() < self.parser.file_size - 1:
            byte1 = self.parser.read_uint8()
            if byte1 == 0xFF:
                pos = self.parser.tell()
                byte2 = self.parser.read_uint8()
                if (byte2 & 0xE0) == 0xE0:  # Valid sync
                    self.parser.seek(pos - 1)
                    return pos - 1
                self.parser.seek(pos)
        return -1
        
    def _calculate_mp3_frame_size(self, header: bytes) -> int:
        """Calculate MP3 frame size from header"""
        if len(header) < 4:
            return 0
            
        # Extract header fields
        version = (header[1] >> 3) & 0x03
        layer = (header[1] >> 1) & 0x03
        bitrate_index = (header[2] >> 4) & 0x0F
        sample_rate_index = (header[2] >> 2) & 0x03
        padding = (header[2] >> 1) & 0x01
        
        # Bitrate tables
        bitrate_v1_l3 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
        sample_rates = [44100, 48000, 32000, 0]
        
        if version == 0x03 and layer == 0x01:  # MPEG1 Layer3
            bitrate = bitrate_v1_l3[bitrate_index] * 1000
            sample_rate = sample_rates[sample_rate_index]
            
            if bitrate == 0 or sample_rate == 0:
                return 0
                
            frame_size = 144 * bitrate // sample_rate + padding
            return frame_size
            
        return 0
        
    def _calculate_mp3_timestamp(self, frame_number: int) -> float:
        """Calculate MP3 frame timestamp"""
        # MP3 frame duration is 1152 samples for Layer III
        samples_per_frame = 1152
        sample_rate = 44100  # Default, should be extracted from header
        return frame_number * samples_per_frame / sample_rate
        
    def _find_aac_frames(self, max_frames: Optional[int]) -> List[AudioFrame]:
        """Find AAC ADTS frames"""
        frames = []
        self.parser.seek(0)
        frame_count = 0
        
        while True:
            if max_frames and frame_count >= max_frames:
                break
                
            # Find ADTS sync
            sync_pos = self.parser.find_pattern(b"\xFF\xF1", self.parser.tell())
            if sync_pos == -1:
                break
                
            self.parser.seek(sync_pos)
            header = self.parser.read(7)
            
            if len(header) < 7:
                break
                
            # Parse ADTS header
            frame_size = ((header[3] & 0x03) << 11) | (header[4] << 3) | (header[5] >> 5)
            
            if frame_size < 7:
                self.parser.seek(sync_pos + 1)
                continue
                
            # Read frame
            self.parser.seek(sync_pos)
            frame_data = self.parser.read(frame_size)
            
            if len(frame_data) < frame_size:
                break
                
            frames.append(AudioFrame(
                offset=sync_pos,
                size=frame_size,
                header=header,
                data=frame_data[7:],
                timestamp=frame_count * 1024 / 44100  # AAC frame is 1024 samples
            ))
            
            frame_count += 1
            
        return frames
        
    def _find_flac_frames(self, max_frames: Optional[int]) -> List[AudioFrame]:
        """Find FLAC frames"""
        frames = []
        self.parser.seek(0)
        
        # Check FLAC signature
        signature = self.parser.read(4)
        if signature != b"fLaC":
            return []
            
        # Skip metadata blocks
        while True:
            block_header = self.parser.read(4)
            if len(block_header) < 4:
                return []
                
            is_last = (block_header[0] & 0x80) != 0
            block_size = struct.unpack(">I", b"\x00" + block_header[1:4])[0]
            
            self.parser.seek(block_size, 1)
            
            if is_last:
                break
                
        # Read audio frames
        frame_count = 0
        while self.parser.tell() < self.parser.file_size:
            if max_frames and frame_count >= max_frames:
                break
                
            frame_start = self.parser.tell()
            
            # FLAC frame header starts with sync code
            sync = self.parser.read(2)
            if len(sync) < 2 or sync[0] != 0xFF or (sync[1] & 0xFC) != 0xF8:
                break
                
            # For simplicity, we'll use a fixed frame size
            # In reality, FLAC frames are variable length
            frame_size = 4096  # Typical FLAC frame size
            
            self.parser.seek(frame_start)
            frame_data = self.parser.read(min(frame_size, self.parser.file_size - frame_start))
            
            frames.append(AudioFrame(
                offset=frame_start,
                size=len(frame_data),
                header=frame_data[:16],
                data=frame_data[16:],
                timestamp=frame_count * 4096 / 44100
            ))
            
            frame_count += 1
            
        return frames
        
    def _find_ogg_frames(self, max_frames: Optional[int]) -> List[AudioFrame]:
        """Find Ogg pages (frames)"""
        frames = []
        self.parser.seek(0)
        frame_count = 0
        
        while True:
            if max_frames and frame_count >= max_frames:
                break
                
            # Find OggS pattern
            sync_pos = self.parser.find_pattern(b"OggS", self.parser.tell())
            if sync_pos == -1:
                break
                
            self.parser.seek(sync_pos)
            header = self.parser.read(27)
            
            if len(header) < 27:
                break
                
            # Parse Ogg page header
            page_segments = header[26]
            
            # Read segment table
            segment_table = self.parser.read(page_segments)
            if len(segment_table) < page_segments:
                break
                
            # Calculate page size
            page_size = sum(segment_table) + 27 + page_segments
            
            # Read page data
            self.parser.seek(sync_pos)
            page_data = self.parser.read(page_size)
            
            if len(page_data) < page_size:
                break
                
            frames.append(AudioFrame(
                offset=sync_pos,
                size=page_size,
                header=header,
                data=page_data[27 + page_segments:],
                timestamp=frame_count * 0.02  # Approximate
            ))
            
            frame_count += 1
            
        return frames
        
    def _find_wav_frames(self, max_frames: Optional[int]) -> List[AudioFrame]:
        """Find WAV data chunks"""
        frames = []
        self.parser.seek(0)
        
        # Read RIFF header
        riff_header = self.parser.read(12)
        if riff_header[:4] != b"RIFF" or riff_header[8:12] != b"WAVE":
            return []
            
        # Find data chunk
        while self.parser.tell() < self.parser.file_size:
            chunk_header = self.parser.read(8)
            if len(chunk_header) < 8:
                break
                
            chunk_id = chunk_header[:4]
            chunk_size = struct.unpack("<I", chunk_header[4:8])[0]
            
            if chunk_id == b"data":
                # WAV typically has one large data chunk
                # We'll treat it as a single frame
                data_start = self.parser.tell()
                frames.append(AudioFrame(
                    offset=data_start - 8,
                    size=chunk_size + 8,
                    header=chunk_header,
                    data=b"",  # Too large to read entirely
                    timestamp=0.0
                ))
                break
            else:
                # Skip chunk
                self.parser.seek(chunk_size, 1)
                
        return frames
        
    def validate_frame_sequence(self, frames: List[AudioFrame]) -> Tuple[bool, List[str]]:
        """Validate frame sequence integrity"""
        errors = []
        
        if not frames:
            return True, []
            
        # Check for gaps between frames
        for i in range(1, len(frames)):
            prev_end = frames[i-1].offset + frames[i-1].size
            curr_start = frames[i].offset
            
            if curr_start != prev_end:
                gap = curr_start - prev_end
                if gap > 0:
                    errors.append(f"Gap of {gap} bytes between frames {i-1} and {i}")
                else:
                    errors.append(f"Overlap of {-gap} bytes between frames {i-1} and {i}")
                    
        # Check for consistent frame sizes (for fixed-size formats)
        if self._detected_format in [AudioFormat.MP3]:
            sizes = [f.size for f in frames]
            if len(set(sizes)) > len(frames) * 0.1:  # More than 10% variation
                errors.append("Inconsistent frame sizes detected")
                
        return len(errors) == 0, errors