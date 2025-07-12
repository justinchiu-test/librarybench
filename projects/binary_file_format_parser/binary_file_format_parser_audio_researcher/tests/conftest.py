"""Pytest configuration and fixtures"""

import pytest
import tempfile
import struct
from pathlib import Path
from typing import BinaryIO


@pytest.fixture
def temp_audio_file():
    """Create a temporary audio file for testing"""
    def _create_file(content: bytes) -> Path:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(content)
            return Path(f.name)
    return _create_file


@pytest.fixture
def mp3_test_data():
    """Create test MP3 data with valid header"""
    # MP3 header: FF FB 90 00 (MPEG1 Layer3, 128kbps, 44.1kHz, stereo)
    header = b"\xFF\xFB\x90\x00"
    # Add some frame data - correct frame size calculation
    # Frame size = 144 * bitrate / sample_rate + padding
    # = 144 * 128000 / 44100 + 0 = 417.95... = 417
    frame_data = b"\x00" * 413  # 417 - 4 (header) = 413
    return header + frame_data


@pytest.fixture
def wav_test_data():
    """Create test WAV data"""
    # RIFF header
    riff = b"RIFF"
    file_size = struct.pack("<I", 36 + 1000)  # Header + data
    wave = b"WAVE"
    
    # fmt chunk
    fmt_chunk = b"fmt "
    fmt_size = struct.pack("<I", 16)
    audio_format = struct.pack("<H", 1)  # PCM
    channels = struct.pack("<H", 2)  # Stereo
    sample_rate = struct.pack("<I", 44100)
    byte_rate = struct.pack("<I", 44100 * 2 * 2)  # SR * channels * bytes per sample
    block_align = struct.pack("<H", 4)  # Channels * bytes per sample
    bits_per_sample = struct.pack("<H", 16)
    
    # data chunk
    data_chunk = b"data"
    data_size = struct.pack("<I", 1000)
    data = b"\x00" * 1000
    
    return (riff + file_size + wave + fmt_chunk + fmt_size + audio_format +
            channels + sample_rate + byte_rate + block_align + bits_per_sample +
            data_chunk + data_size + data)


@pytest.fixture
def flac_test_data():
    """Create test FLAC data"""
    # FLAC signature
    signature = b"fLaC"
    
    # STREAMINFO block (mandatory)
    block_header = b"\x00"  # Not last block, type 0 (STREAMINFO)
    block_size = struct.pack(">I", 34)[1:]  # 24-bit size
    
    # STREAMINFO data
    min_block = struct.pack(">H", 4096)
    max_block = struct.pack(">H", 4096)
    min_frame = b"\x00\x00\x00"  # 24-bit
    max_frame = b"\xFF\xFF\xFF"  # 24-bit
    
    # Sample rate (20 bits), channels (3 bits), bits per sample (5 bits)
    # 44100 Hz, 2 channels, 16 bits
    combined = (44100 << 12) | (1 << 9) | (15 << 4)
    sample_info = struct.pack(">I", combined)
    
    # Total samples (36 bits) - split across 2 fields
    total_samples = b"\x00\x00\x00\x00\x00"
    
    # MD5 signature (16 bytes)
    md5 = b"\x00" * 16
    
    streaminfo = (min_block + max_block + min_frame + max_frame + 
                  sample_info + total_samples + md5)
    
    # Add a last metadata block
    last_block_header = b"\x84"  # Last block, type 4 (VORBIS_COMMENT)
    last_block_size = b"\x00\x00\x00"  # Empty
    
    return signature + block_header + block_size + streaminfo + last_block_header + last_block_size


@pytest.fixture
def id3v2_test_data():
    """Create test ID3v2 tag data"""
    # ID3v2 header
    header = b"ID3"
    version = b"\x03\x00"  # v2.3
    flags = b"\x00"
    
    # Size (synchsafe integer)
    tag_size = 100
    size = struct.pack("BBBB", 
                      (tag_size >> 21) & 0x7F,
                      (tag_size >> 14) & 0x7F,
                      (tag_size >> 7) & 0x7F,
                      tag_size & 0x7F)
    
    # TIT2 frame (title)
    frame_id = b"TIT2"
    frame_size = struct.pack(">I", 11)
    frame_flags = b"\x00\x00"
    frame_data = b"\x00Test Title"  # Encoding + text
    
    # Padding
    padding = b"\x00" * (tag_size - len(frame_id) - len(frame_size) - 
                        len(frame_flags) - len(frame_data))
    
    return (header + version + flags + size + frame_id + frame_size + 
            frame_flags + frame_data + padding)