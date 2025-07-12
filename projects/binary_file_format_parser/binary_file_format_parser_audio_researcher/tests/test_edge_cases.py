"""Tests for edge cases and boundary conditions"""

import pytest
import struct

from pybinparser import (
    BinaryParser, AudioFormat, FrameDetector, CodecParameterExtractor,
    FormatDetector, MetadataParser, PsychoacousticAnalyzer
)
from pybinparser.core import AudioFrame, CodecParameters, CodecType
from pybinparser.metadata_parser import MetadataTag, TagType


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_small_mp3_frame(self, temp_audio_file):
        """Test handling of very small MP3 frame"""
        # Minimum valid MP3 frame
        mp3_header = b"\xFF\xFB\x10\x00"  # Very low bitrate
        test_file = temp_audio_file(mp3_header + b"\x00" * 10)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            assert format_type == AudioFormat.MP3
            
    def test_maximum_metadata_size(self, temp_audio_file):
        """Test handling of maximum size metadata"""
        # ID3v2 with maximum size
        id3_header = b"ID3\x03\x00\x00"
        # Max synchsafe size (28 bits = 256MB)
        max_size = b"\x7F\x7F\x7F\x7F"
        
        # Just test header parsing, not full tag
        test_file = temp_audio_file(id3_header + max_size + b"\x00" * 100)
        
        with BinaryParser(test_file) as parser:
            metadata_parser = MetadataParser(parser)
            # Should handle large size gracefully
            metadata_parser._parse_id3v2()
            
    def test_unicode_in_all_fields(self, temp_audio_file):
        """Test Unicode handling in all metadata fields"""
        # Create ID3v1 with high ASCII chars
        tag_data = b"TAG"
        tag_data += "Tëst Tïtlé".encode("latin-1")[:30].ljust(30, b"\x00")
        tag_data += "Tëst Ärtïst".encode("latin-1")[:30].ljust(30, b"\x00")
        tag_data += "Tëst Älbüm".encode("latin-1")[:30].ljust(30, b"\x00")
        tag_data += b"2023"
        tag_data += b"\x00" * 30  # Comment
        tag_data += b"\x00"  # Genre
        
        test_file = temp_audio_file(b"\x00" * 128 + tag_data)
        
        with BinaryParser(test_file) as parser:
            metadata_parser = MetadataParser(parser)
            tags = metadata_parser.parse_all_tags(AudioFormat.MP3)
            
            # Should handle extended ASCII
            assert len(tags) > 0
            
    def test_zero_bitrate_codec_params(self, temp_audio_file):
        """Test codec parameter extraction with zero bitrate"""
        # MP3 header with bitrate index 0 (free format)
        mp3_header = b"\xFF\xFB\x00\x00"
        test_file = temp_audio_file(mp3_header + b"\x00" * 100)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.MP3)
            
            assert params.format == AudioFormat.MP3
            assert params.bitrate == 0 or params.bitrate is None
            
    def test_all_genre_indices(self, temp_audio_file):
        """Test all ID3v1 genre indices"""
        for genre_idx in range(80):  # Test first 80 genres
            tag_data = b"TAG" + b"\x00" * 124 + bytes([genre_idx])
            test_file = temp_audio_file(b"\x00" * 128 + tag_data)
            
            with BinaryParser(test_file) as parser:
                metadata_parser = MetadataParser(parser)
                metadata_parser._parse_id3v1()
                
                # Should handle all genre indices
                tags = [t for t in metadata_parser._tags if t.key == "genre"]
                if tags:
                    assert tags[0].value in metadata_parser.ID3V1_GENRES
                    
    def test_fractional_frame_size(self, temp_audio_file):
        """Test handling of fractional frame size calculations"""
        # MP3 header that would result in fractional frame size
        mp3_header = b"\xFF\xFB\x92\x00"  # Specific bitrate/samplerate combo
        test_file = temp_audio_file(mp3_header + b"\x00" * 500)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            frames = detector.find_frames(max_frames=1)
            
            # Frame size should be integer
            if frames:
                assert isinstance(frames[0].size, int)
                
    def test_overlapping_metadata_tags(self, temp_audio_file):
        """Test file with overlapping metadata tags"""
        # File with both ID3v1 and ID3v2
        id3v2 = b"ID3\x03\x00\x00\x00\x00\x00\x20" + b"\x00" * 32
        audio_data = b"\xFF\xFB\x90\x00" + b"\x00" * 413
        id3v1 = b"TAG" + b"\x00" * 125
        
        test_file = temp_audio_file(id3v2 + audio_data + id3v1)
        
        with BinaryParser(test_file) as parser:
            metadata_parser = MetadataParser(parser)
            tags = metadata_parser.parse_all_tags(AudioFormat.MP3)
            
            # Should find both tag types
            assert len(tags) >= 1
            
    def test_recursive_frame_detection(self, temp_audio_file):
        """Test recursive frame patterns"""
        # MP3 sync pattern within frame data
        mp3_header = b"\xFF\xFB\x90\x00"
        frame_data = b"\x00" * 200 + b"\xFF\xFB" + b"\x00" * 213
        
        test_file = temp_audio_file(mp3_header + frame_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            frames = detector.find_frames()
            
            # Should handle embedded sync patterns
            assert len(frames) >= 1
            
    def test_format_detector_with_noise(self, temp_audio_file):
        """Test format detection with random noise"""
        import random
        # Create noise that might look like audio
        noise = bytes([random.randint(100, 156) for _ in range(1000)])
        test_file = temp_audio_file(noise)
        
        with BinaryParser(test_file) as parser:
            detector = FormatDetector(parser)
            result = detector.detect_format_characteristics()
            
            # Should return some result even with noise
            assert "sample_rate" in result
            assert "bit_depth" in result
            
    def test_extreme_compression_ratios(self, temp_audio_file):
        """Test extreme compression ratio calculations"""
        # Create WAV with very high sample rate
        wav_data = b"RIFF" + struct.pack("<I", 44) + b"WAVE"
        wav_data += b"fmt " + struct.pack("<I", 16)
        wav_data += struct.pack("<HHIIHH", 1, 2, 384000, 384000*2*4, 8, 32)
        wav_data += b"data" + struct.pack("<I", 0)
        
        test_file = temp_audio_file(wav_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.WAV)
            
            # Should handle extreme values
            assert params.compression_ratio == 1.0
            
    def test_psychoacoustic_with_invalid_frames(self, temp_audio_file):
        """Test psychoacoustic analysis with invalid frame data"""
        invalid_frames = [
            AudioFrame(offset=0, size=0, header=b"", data=b"", timestamp=0),
            AudioFrame(offset=100, size=10, header=b"XXXX", data=b"invalid", timestamp=1),
        ]
        
        test_file = temp_audio_file(b"dummy")
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            params = analyzer.extract_parameters(AudioFormat.MP3, invalid_frames)
            
            # Should handle invalid frames gracefully
            assert params.model_type == "MPEG Layer III"
            
    def test_all_audio_format_strings(self):
        """Test all audio format string representations"""
        for format_type in AudioFormat:
            assert isinstance(format_type.value, str)
            assert len(format_type.value) > 0
            
    def test_all_codec_type_strings(self):
        """Test all codec type string representations"""
        for codec_type in CodecType:
            assert isinstance(codec_type.value, str)
            assert codec_type.value in ["lossy", "lossless", "uncompressed"]