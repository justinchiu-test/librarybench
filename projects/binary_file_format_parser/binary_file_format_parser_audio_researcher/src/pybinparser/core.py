"""Core binary parser functionality"""

from typing import BinaryIO, Dict, List, Optional, Tuple, Union
from enum import Enum
from pathlib import Path
import struct
from pydantic import BaseModel, Field, ConfigDict


class AudioFormat(str, Enum):
    """Supported audio format types"""
    
    MP3 = "mp3"
    AAC = "aac"
    FLAC = "flac"
    OGG = "ogg"
    OPUS = "opus"
    WAV = "wav"
    UNKNOWN = "unknown"


class CodecType(str, Enum):
    """Audio codec types"""
    
    LOSSY = "lossy"
    LOSSLESS = "lossless"
    UNCOMPRESSED = "uncompressed"


class AudioFrame(BaseModel):
    """Represents a single audio frame"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    offset: int = Field(description="Byte offset in file")
    size: int = Field(description="Frame size in bytes")
    header: bytes = Field(description="Frame header data")
    data: bytes = Field(description="Frame audio data")
    timestamp: Optional[float] = Field(None, description="Frame timestamp in seconds")
    

class CodecParameters(BaseModel):
    """Audio codec parameters"""
    
    format: AudioFormat = Field(description="Audio format type")
    codec_type: CodecType = Field(description="Codec type")
    bitrate: Optional[int] = Field(None, description="Bitrate in bits per second")
    sample_rate: Optional[int] = Field(None, description="Sample rate in Hz")
    bit_depth: Optional[int] = Field(None, description="Bit depth")
    channels: Optional[int] = Field(None, description="Number of channels")
    compression_ratio: Optional[float] = Field(None, description="Compression ratio")
    frame_size: Optional[int] = Field(None, description="Frame size in samples")
    custom_params: Dict[str, Union[int, float, str]] = Field(
        default_factory=dict, description="Format-specific parameters"
    )


class BinaryParser:
    """Main binary parser for audio files"""
    
    def __init__(self, file_path: Union[str, Path]):
        """Initialize parser with file path"""
        self.file_path = Path(file_path)
        self._file: Optional[BinaryIO] = None
        self._file_size: int = 0
        
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def open(self) -> None:
        """Open the file for reading"""
        if self._file is None:
            self._file = open(self.file_path, "rb")
            self._file.seek(0, 2)  # Seek to end
            self._file_size = self._file.tell()
            self._file.seek(0)  # Return to start
            
    def close(self) -> None:
        """Close the file"""
        if self._file is not None:
            self._file.close()
            self._file = None
            
    def read(self, size: int = -1) -> bytes:
        """Read bytes from file"""
        if self._file is None:
            raise RuntimeError("File not opened")
        return self._file.read(size)
        
    def seek(self, offset: int, whence: int = 0) -> None:
        """Seek to position in file"""
        if self._file is None:
            raise RuntimeError("File not opened")
        self._file.seek(offset, whence)
        
    def tell(self) -> int:
        """Get current file position"""
        if self._file is None:
            raise RuntimeError("File not opened")
        return self._file.tell()
        
    @property
    def file_size(self) -> int:
        """Get total file size"""
        return self._file_size
        
    def read_uint8(self) -> int:
        """Read unsigned 8-bit integer"""
        data = self.read(1)
        if len(data) < 1:
            raise EOFError("Unexpected end of file")
        return struct.unpack("B", data)[0]
        
    def read_uint16_be(self) -> int:
        """Read unsigned 16-bit integer (big-endian)"""
        data = self.read(2)
        if len(data) < 2:
            raise EOFError("Unexpected end of file")
        return struct.unpack(">H", data)[0]
        
    def read_uint16_le(self) -> int:
        """Read unsigned 16-bit integer (little-endian)"""
        data = self.read(2)
        if len(data) < 2:
            raise EOFError("Unexpected end of file")
        return struct.unpack("<H", data)[0]
        
    def read_uint32_be(self) -> int:
        """Read unsigned 32-bit integer (big-endian)"""
        data = self.read(4)
        if len(data) < 4:
            raise EOFError("Unexpected end of file")
        return struct.unpack(">I", data)[0]
        
    def read_uint32_le(self) -> int:
        """Read unsigned 32-bit integer (little-endian)"""
        data = self.read(4)
        if len(data) < 4:
            raise EOFError("Unexpected end of file")
        return struct.unpack("<I", data)[0]
        
    def find_pattern(self, pattern: bytes, start: int = 0, end: Optional[int] = None) -> int:
        """Find pattern in file, return offset or -1 if not found"""
        if end is None:
            end = self._file_size
            
        self.seek(start)
        chunk_size = 65536  # 64KB chunks
        overlap = len(pattern) - 1
        
        while self.tell() < end:
            chunk = self.read(min(chunk_size, end - self.tell()))
            if not chunk:
                break
                
            pos = chunk.find(pattern)
            if pos != -1:
                return self.tell() - len(chunk) + pos
                
            # Move back to handle pattern at chunk boundary
            if self.tell() < end and len(chunk) == chunk_size:
                self.seek(-overlap, 1)
                
        return -1