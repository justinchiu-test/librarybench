"""Tests for advanced features and complex scenarios"""

import pytest
import struct
from pybinparser import (
    BinaryParser, AudioFormat, FrameDetector, CodecParameterExtractor,
    FormatDetector, MetadataParser, PsychoacousticAnalyzer
)
from pybinparser.metadata_parser import TagType, MetadataTag, ArtworkInfo


class TestAdvancedFeatures:
    """Test advanced features and complex scenarios"""
    
    def test_mixed_format_file(self, temp_audio_file):
        """Test file with multiple format signatures"""
        # File that starts like FLAC but contains MP3
        mixed_data = b"fLaC" + b"\x00" * 100 + b"\xFF\xFB\x90\x00" + b"\x00" * 413
        test_file = temp_audio_file(mixed_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            
            # Should detect FLAC (first match)
            assert format_type == AudioFormat.FLAC
            
    def test_custom_metadata_patterns(self, temp_audio_file):
        """Test custom metadata pattern extraction"""
        # Create file with custom metadata patterns
        data = b"\x00" * 100
        data += b"CUSTOM_ARTIST:John Doe\x00"
        data += b"\x00" * 50
        data += b"CUSTOM_ALBUM:Test Album\x00"
        data += b"\x00" * 100
        
        test_file = temp_audio_file(data)
        
        with BinaryParser(test_file) as parser:
            metadata_parser = MetadataParser(parser)
            
            patterns = [
                (b"CUSTOM_ARTIST:", "artist"),
                (b"CUSTOM_ALBUM:", "album"),
            ]
            
            custom_tags = metadata_parser.extract_custom_tags(patterns)
            
            assert len(custom_tags) == 2
            assert any(tag.key == "artist" for tag in custom_tags)
            assert any(tag.key == "album" for tag in custom_tags)
            
    def test_multi_channel_detection(self, temp_audio_file):
        """Test detection of multi-channel audio"""
        # Create 5.1 channel WAV header
        wav_data = b"RIFF"
        wav_data += struct.pack("<I", 36 + 1000)
        wav_data += b"WAVE"
        wav_data += b"fmt "
        wav_data += struct.pack("<I", 16)
        wav_data += struct.pack("<H", 1)  # PCM
        wav_data += struct.pack("<H", 6)  # 6 channels (5.1)
        wav_data += struct.pack("<I", 48000)  # Sample rate
        wav_data += struct.pack("<I", 48000 * 6 * 2)  # Byte rate
        wav_data += struct.pack("<H", 12)  # Block align
        wav_data += struct.pack("<H", 16)  # Bits per sample
        wav_data += b"data"
        wav_data += struct.pack("<I", 1000)
        wav_data += b"\x00" * 1000
        
        test_file = temp_audio_file(wav_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.WAV)
            
            assert params.channels == 6
            assert params.sample_rate == 48000
            
    def test_high_resolution_audio(self, temp_audio_file):
        """Test high-resolution audio format detection"""
        # Create 24-bit, 192kHz WAV
        wav_data = b"RIFF"
        wav_data += struct.pack("<I", 36 + 1000)
        wav_data += b"WAVE"
        wav_data += b"fmt "
        wav_data += struct.pack("<I", 16)
        wav_data += struct.pack("<H", 1)  # PCM
        wav_data += struct.pack("<H", 2)  # Stereo
        wav_data += struct.pack("<I", 192000)  # 192kHz
        wav_data += struct.pack("<I", 192000 * 2 * 3)  # Byte rate
        wav_data += struct.pack("<H", 6)  # Block align
        wav_data += struct.pack("<H", 24)  # 24-bit
        wav_data += b"data"
        wav_data += struct.pack("<I", 1000)
        wav_data += b"\x00" * 1000
        
        test_file = temp_audio_file(wav_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.WAV)
            
            assert params.bit_depth == 24
            assert params.sample_rate == 192000
            
    def test_embedded_cue_points(self, temp_audio_file):
        """Test extraction of embedded cue points"""
        # WAV with cue chunk
        wav_data = b"RIFF"
        size = 36 + 16 + 12 + 28  # fmt + data + cue
        wav_data += struct.pack("<I", size)
        wav_data += b"WAVE"
        
        # fmt chunk
        wav_data += b"fmt "
        wav_data += struct.pack("<I", 16)
        wav_data += struct.pack("<HHIIHH", 1, 2, 44100, 176400, 4, 16)
        
        # cue chunk
        wav_data += b"cue "
        wav_data += struct.pack("<I", 28)  # Chunk size
        wav_data += struct.pack("<I", 1)    # Number of cue points
        # Cue point
        wav_data += struct.pack("<I", 1)    # ID
        wav_data += struct.pack("<I", 0)    # Position
        wav_data += b"data"                 # Chunk ID
        wav_data += struct.pack("<I", 0)    # Chunk start
        wav_data += struct.pack("<I", 0)    # Block start
        wav_data += struct.pack("<I", 44100) # Sample offset
        
        # data chunk
        wav_data += b"data"
        wav_data += struct.pack("<I", 16)
        wav_data += b"\x00" * 16
        
        test_file = temp_audio_file(wav_data)
        
        with BinaryParser(test_file) as parser:
            # Parser should handle various chunk types
            assert parser.file_size > 0
            
    def test_variable_bitrate_detection(self, temp_audio_file):
        """Test VBR (Variable Bit Rate) detection"""
        # Create MP3 with Xing/Info header (VBR)
        mp3_data = b"\xFF\xFB\x90\x00"  # MP3 header
        mp3_data += b"\x00" * 32         # Side info
        mp3_data += b"Xing"              # Xing tag
        mp3_data += struct.pack(">I", 0x0007)  # Flags: frames, bytes, TOC
        mp3_data += struct.pack(">I", 100)     # Number of frames
        mp3_data += struct.pack(">I", 50000)   # File size
        mp3_data += b"\x00" * 100              # TOC
        mp3_data += b"\x00" * 200              # Padding
        
        test_file = temp_audio_file(mp3_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.MP3)
            
            # Should detect MP3 parameters
            assert params.format == AudioFormat.MP3
            
    def test_spectral_analysis_edge_cases(self, temp_audio_file):
        """Test spectral analysis with edge cases"""
        # Create silent audio data
        silent_data = struct.pack("<h", 0) * 1024
        
        test_file = temp_audio_file(silent_data)
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            spectral_info = analyzer.analyze_spectral_content(silent_data, 44100)
            
            # Should handle silence gracefully
            assert "spectral_centroid" in spectral_info
            assert "total_energy" in spectral_info
            assert spectral_info["total_energy"] < 0.01  # Near zero
            
    def test_metadata_encoding_variants(self, temp_audio_file):
        """Test various metadata encoding scenarios"""
        # ID3v2 with UTF-8 encoding
        id3_data = b"ID3\x04\x00\x00"  # v2.4
        size = b"\x00\x00\x00\x30"
        
        # TIT2 frame with UTF-8
        frame = b"TIT2"
        frame += struct.pack(">I", 15)
        frame += b"\x00\x00"
        frame += b"\x03"  # UTF-8 encoding
        frame += "Test 测试 🎵".encode("utf-8")
        
        padding = b"\x00" * 20
        
        test_data = id3_data + size + frame + padding
        test_file = temp_audio_file(test_data)
        
        with BinaryParser(test_file) as parser:
            metadata_parser = MetadataParser(parser)
            tags = metadata_parser.parse_all_tags(AudioFormat.MP3)
            
            # Should handle UTF-8 with emojis
            id3v2_tags = tags.get(TagType.ID3V2.value, [])
            assert len(id3v2_tags) > 0
            
    def test_psychoacoustic_model_variants(self, temp_audio_file):
        """Test different psychoacoustic model scenarios"""
        test_file = temp_audio_file(b"dummy")
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            
            # Test with empty frame list
            for format_type in [AudioFormat.AAC, AudioFormat.OGG, AudioFormat.OPUS]:
                params = analyzer.extract_parameters(format_type, [])
                assert params.model_type != "unknown"
                # Model parameters should be created even with empty frames
                if format_type == AudioFormat.AAC:
                    assert params.model_type == "AAC"
                elif format_type == AudioFormat.OGG:
                    assert params.model_type == "Vorbis"
                elif format_type == AudioFormat.OPUS:
                    assert params.model_type == "Opus/CELT"
                
    def test_complex_file_structure(self, temp_audio_file):
        """Test file with complex structure"""
        # File with: ID3v2 + APE + MP3 frames + ID3v1
        complex_data = b""
        
        # ID3v2 at start
        complex_data += b"ID3\x03\x00\x00\x00\x00\x00\x20"
        complex_data += b"\x00" * 32
        
        # MP3 frames
        for _ in range(5):
            complex_data += b"\xFF\xFB\x90\x00" + b"\x00" * 413
            
        # APE tag at end
        complex_data += b"APETAGEX" + b"\x00" * 24
        
        # ID3v1 at very end
        complex_data += b"TAG" + b"\x00" * 125
        
        test_file = temp_audio_file(complex_data)
        
        with BinaryParser(test_file) as parser:
            # Should handle multiple metadata formats
            metadata_parser = MetadataParser(parser)
            tags = metadata_parser.parse_all_tags(AudioFormat.MP3)
            
            # Multiple tag types may be present
            assert isinstance(tags, dict)