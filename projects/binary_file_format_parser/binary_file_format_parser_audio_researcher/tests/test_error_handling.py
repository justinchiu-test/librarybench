"""Tests for error handling and edge cases"""

import pytest
from pathlib import Path
import tempfile

from pybinparser import (
    BinaryParser, AudioFormat, FrameDetector, CodecParameterExtractor,
    FormatDetector, MetadataParser, PsychoacousticAnalyzer
)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_nonexistent_file(self):
        """Test handling of non-existent file"""
        with pytest.raises(FileNotFoundError):
            with BinaryParser("/path/to/nonexistent/file.mp3") as parser:
                pass
                
    def test_empty_file_parser(self, temp_audio_file):
        """Test parsing empty file"""
        test_file = temp_audio_file(b"")
        
        with BinaryParser(test_file) as parser:
            assert parser.file_size == 0
            assert parser.read() == b""
            
            # Test EOF on reads
            with pytest.raises(EOFError):
                parser.read_uint8()
                
    def test_corrupted_mp3_header(self, temp_audio_file):
        """Test handling of corrupted MP3 header"""
        # Invalid MP3 header
        corrupted_data = b"\xFF\xFF\xFF\xFF" + b"\x00" * 100
        test_file = temp_audio_file(corrupted_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            frames = detector.find_frames()
            
            # Should still try to detect but find no valid frames
            assert len(frames) == 0
            
    def test_truncated_file(self, temp_audio_file):
        """Test handling of truncated file"""
        # Start of MP3 frame but truncated
        truncated_data = b"\xFF\xFB\x90"  # Missing last byte of header
        test_file = temp_audio_file(truncated_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.MP3)
            
            # Should return default parameters
            assert params.format == AudioFormat.MP3
            assert params.bitrate is None or params.bitrate == 0
            
    def test_invalid_metadata(self, temp_audio_file):
        """Test handling of invalid metadata"""
        # Invalid ID3v2 header
        invalid_id3 = b"ID3\xFF\xFF\xFF\xFF\xFF\xFF\xFF"
        test_file = temp_audio_file(invalid_id3 + b"\x00" * 100)
        
        with BinaryParser(test_file) as parser:
            metadata_parser = MetadataParser(parser)
            tags = metadata_parser.parse_all_tags(AudioFormat.MP3)
            
            # Should handle gracefully
            assert isinstance(tags, dict)
            
    def test_seek_beyond_file(self, temp_audio_file):
        """Test seeking beyond file boundaries"""
        test_file = temp_audio_file(b"test data")
        
        with BinaryParser(test_file) as parser:
            # Seek beyond file
            parser.seek(1000)
            assert parser.tell() == 1000
            
            # Read should return empty
            assert parser.read() == b""
            
    def test_pattern_not_found(self, temp_audio_file):
        """Test pattern search when pattern doesn't exist"""
        test_file = temp_audio_file(b"some test data without pattern")
        
        with BinaryParser(test_file) as parser:
            pos = parser.find_pattern(b"NOTFOUND")
            assert pos == -1
            
    def test_invalid_format_detection(self, temp_audio_file):
        """Test format detection with random data"""
        import random
        random_data = bytes(random.randint(0, 255) for _ in range(1000))
        test_file = temp_audio_file(random_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            
            # Should return UNKNOWN for random data
            assert format_type == AudioFormat.UNKNOWN
            
    def test_zero_size_frames(self, temp_audio_file):
        """Test handling of zero-size frame calculation"""
        # MP3 header with bitrate index 0 (invalid)
        invalid_mp3 = b"\xFF\xFB\x00\x00" + b"\x00" * 100
        test_file = temp_audio_file(invalid_mp3)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            frames = detector.find_frames()
            
            # Should handle zero-size frames gracefully
            assert len(frames) == 0
            
    def test_large_file_handling(self, temp_audio_file):
        """Test handling of large file simulation"""
        # Create a file with repeating pattern
        pattern = b"\xFF\xFB\x90\x00" + b"\x00" * 413
        large_data = pattern * 1000  # ~417KB
        test_file = temp_audio_file(large_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            # Limit frames to test performance
            frames = detector.find_frames(max_frames=10)
            
            assert len(frames) == 10
            assert all(f.size == 417 for f in frames)