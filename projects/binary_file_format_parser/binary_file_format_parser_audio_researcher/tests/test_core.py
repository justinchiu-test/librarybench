"""Tests for core binary parser functionality"""

import pytest
from pathlib import Path
import struct

from pybinparser.core import BinaryParser, AudioFormat, CodecType, AudioFrame, CodecParameters


class TestBinaryParser:
    """Test BinaryParser class"""
    
    def test_initialization(self, temp_audio_file):
        """Test parser initialization"""
        test_file = temp_audio_file(b"test data")
        parser = BinaryParser(test_file)
        assert parser.file_path == test_file
        assert parser._file is None
        
    def test_context_manager(self, temp_audio_file):
        """Test context manager functionality"""
        test_file = temp_audio_file(b"test data")
        
        with BinaryParser(test_file) as parser:
            assert parser._file is not None
            assert parser.file_size == 9
            
        assert parser._file is None
        
    def test_read_operations(self, temp_audio_file):
        """Test various read operations"""
        data = b"Hello World!"
        test_file = temp_audio_file(data)
        
        with BinaryParser(test_file) as parser:
            # Test basic read
            assert parser.read(5) == b"Hello"
            assert parser.tell() == 5
            
            # Test seek
            parser.seek(0)
            assert parser.tell() == 0
            
            # Test read all
            assert parser.read() == data
            
    def test_integer_reading(self, temp_audio_file):
        """Test integer reading methods"""
        data = struct.pack("B", 255)  # uint8
        data += struct.pack(">H", 65535)  # uint16 BE
        data += struct.pack("<H", 65535)  # uint16 LE
        data += struct.pack(">I", 4294967295)  # uint32 BE
        data += struct.pack("<I", 4294967295)  # uint32 LE
        
        test_file = temp_audio_file(data)
        
        with BinaryParser(test_file) as parser:
            assert parser.read_uint8() == 255
            assert parser.read_uint16_be() == 65535
            assert parser.read_uint16_le() == 65535
            assert parser.read_uint32_be() == 4294967295
            assert parser.read_uint32_le() == 4294967295
            
    def test_pattern_finding(self, temp_audio_file):
        """Test pattern finding functionality"""
        data = b"0123456789ABCDEF" * 10
        pattern = b"ABC"
        test_file = temp_audio_file(data)
        
        with BinaryParser(test_file) as parser:
            # Find first occurrence
            pos = parser.find_pattern(pattern)
            assert pos == 10
            
            # Find with start offset
            pos = parser.find_pattern(pattern, start=15)
            assert pos == 26
            
            # Pattern not found
            pos = parser.find_pattern(b"XYZ")
            assert pos == -1
            
    def test_eof_handling(self, temp_audio_file):
        """Test EOF error handling"""
        test_file = temp_audio_file(b"12")
        
        with BinaryParser(test_file) as parser:
            parser.read_uint8()
            parser.read_uint8()
            
            # Should raise EOFError
            with pytest.raises(EOFError):
                parser.read_uint8()
                
            with pytest.raises(EOFError):
                parser.read_uint16_be()


class TestAudioFormat:
    """Test AudioFormat enum"""
    
    def test_format_values(self):
        """Test audio format enum values"""
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.AAC.value == "aac"
        assert AudioFormat.FLAC.value == "flac"
        assert AudioFormat.OGG.value == "ogg"
        assert AudioFormat.OPUS.value == "opus"
        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.UNKNOWN.value == "unknown"


class TestCodecType:
    """Test CodecType enum"""
    
    def test_codec_type_values(self):
        """Test codec type enum values"""
        assert CodecType.LOSSY.value == "lossy"
        assert CodecType.LOSSLESS.value == "lossless"
        assert CodecType.UNCOMPRESSED.value == "uncompressed"


class TestAudioFrame:
    """Test AudioFrame model"""
    
    def test_audio_frame_creation(self):
        """Test AudioFrame creation"""
        frame = AudioFrame(
            offset=100,
            size=200,
            header=b"\xFF\xFB",
            data=b"\x00" * 198,
            timestamp=1.5
        )
        
        assert frame.offset == 100
        assert frame.size == 200
        assert frame.header == b"\xFF\xFB"
        assert len(frame.data) == 198
        assert frame.timestamp == 1.5
        
    def test_audio_frame_optional_timestamp(self):
        """Test AudioFrame with optional timestamp"""
        frame = AudioFrame(
            offset=0,
            size=100,
            header=b"HEAD",
            data=b"DATA"
        )
        
        assert frame.timestamp is None


class TestCodecParameters:
    """Test CodecParameters model"""
    
    def test_codec_parameters_creation(self):
        """Test CodecParameters creation"""
        params = CodecParameters(
            format=AudioFormat.MP3,
            codec_type=CodecType.LOSSY,
            bitrate=128000,
            sample_rate=44100,
            bit_depth=16,
            channels=2,
            compression_ratio=11.0,
            frame_size=1152,
            custom_params={"version": "MPEG1", "layer": "Layer3"}
        )
        
        assert params.format == AudioFormat.MP3
        assert params.codec_type == CodecType.LOSSY
        assert params.bitrate == 128000
        assert params.sample_rate == 44100
        assert params.bit_depth == 16
        assert params.channels == 2
        assert params.compression_ratio == 11.0
        assert params.frame_size == 1152
        assert params.custom_params["version"] == "MPEG1"
        
    def test_codec_parameters_minimal(self):
        """Test CodecParameters with minimal data"""
        params = CodecParameters(
            format=AudioFormat.UNKNOWN,
            codec_type=CodecType.LOSSY
        )
        
        assert params.format == AudioFormat.UNKNOWN
        assert params.codec_type == CodecType.LOSSY
        assert params.bitrate is None
        assert params.sample_rate is None
        assert params.custom_params == {}