from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ProxyResolution(str, Enum):
    THUMBNAIL = "thumbnail"  # 320x180
    PREVIEW = "preview"      # 854x480
    EDITORIAL = "editorial"  # 1920x1080


class VideoCodec(str, Enum):
    PRORES_422 = "prores_422"
    PRORES_4444 = "prores_4444"
    DNXHD = "dnxhd"
    H264 = "h264"
    H265 = "h265"


class TapeFormat(str, Enum):
    LTO8 = "lto8"
    LTO9 = "lto9"


class Timecode(BaseModel):
    hours: int = Field(ge=0, lt=24)
    minutes: int = Field(ge=0, lt=60)
    seconds: int = Field(ge=0, lt=60)
    frames: int = Field(ge=0)
    frame_rate: float = Field(gt=0)

    @property
    def total_frames(self) -> int:
        return int(
            (self.hours * 3600 + self.minutes * 60 + self.seconds) * self.frame_rate
            + self.frames
        )

    @classmethod
    def from_string(cls, timecode_str: str, frame_rate: float = 24.0) -> "Timecode":
        parts = timecode_str.split(":")
        if len(parts) != 4:
            raise ValueError("Invalid timecode format. Expected HH:MM:SS:FF")
        
        return cls(
            hours=int(parts[0]),
            minutes=int(parts[1]),
            seconds=int(parts[2]),
            frames=int(parts[3]),
            frame_rate=frame_rate
        )

    def __str__(self) -> str:
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}:{self.frames:02d}"


class MediaFile(BaseModel):
    file_path: Path
    size: int
    codec: VideoCodec
    duration: Optional[Timecode] = None
    frame_rate: float = 24.0
    resolution: tuple[int, int] = (1920, 1080)
    audio_channels: int = 2
    metadata: Dict[str, str] = Field(default_factory=dict)


class ProxyFile(BaseModel):
    original_file: Path
    proxy_path: Path
    resolution: ProxyResolution
    size: int
    codec: VideoCodec = VideoCodec.H264
    bitrate: int


class ArchiveMetadata(BaseModel):
    archive_id: str
    created_at: datetime
    modified_at: datetime
    total_size: int
    file_count: int
    has_proxies: bool = False
    tape_id: Optional[str] = None
    version: str = "1.0"
    parent_archive: Optional[str] = None


class StreamRequest(BaseModel):
    archive_path: Path
    file_path: str
    start_byte: int = 0
    end_byte: Optional[int] = None
    buffer_size: int = 8192


class TimecodeRange(BaseModel):
    start: Timecode
    end: Timecode
    handles: int = 0  # Extra frames before/after

    @property
    def duration_frames(self) -> int:
        return self.end.total_frames - self.start.total_frames + 2 * self.handles


class ArchiveBranch(BaseModel):
    branch_id: str
    parent_id: Optional[str]
    created_at: datetime
    description: str
    changes: List[str] = Field(default_factory=list)


class TapeArchive(BaseModel):
    tape_id: str
    format: TapeFormat
    capacity_bytes: int
    used_bytes: int = 0
    span_sequence: int = 1
    total_spans: int = 1
    catalog_path: Optional[Path] = None
    verification_checksum: Optional[str] = None