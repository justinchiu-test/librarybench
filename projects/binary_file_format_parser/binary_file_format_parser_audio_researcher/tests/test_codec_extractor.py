"""Tests for codec parameter extraction"""

import pytest
import struct

from pybinparser.core import BinaryParser, AudioFormat, CodecType
from pybinparser.codec_extractor import CodecParameterExtractor


class TestCodecParameterExtractor:
    """Test CodecParameterExtractor class"""
    
    def test_mp3_parameter_extraction(self, temp_audio_file, mp3_test_data):
        """Test MP3 codec parameter extraction"""
        test_file = temp_audio_file(mp3_test_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.MP3)
            
            assert params.format == AudioFormat.MP3
            assert params.codec_type == CodecType.LOSSY
            assert params.bitrate == 128000
            assert params.sample_rate == 44100
            assert params.channels == 2
            assert params.frame_size == 1152
            assert params.bit_depth == 16
            
    def test_wav_parameter_extraction(self, temp_audio_file, wav_test_data):
        """Test WAV parameter extraction"""
        test_file = temp_audio_file(wav_test_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.WAV)
            
            assert params.format == AudioFormat.WAV
            assert params.codec_type == CodecType.UNCOMPRESSED
            assert params.sample_rate == 44100
            assert params.channels == 2
            assert params.bit_depth == 16
            assert params.compression_ratio == 1.0
            
    def test_flac_parameter_extraction(self, temp_audio_file, flac_test_data):
        """Test FLAC parameter extraction"""
        test_file = temp_audio_file(flac_test_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.FLAC)
            
            assert params.format == AudioFormat.FLAC
            assert params.codec_type == CodecType.LOSSLESS
            assert params.sample_rate == 44100
            assert params.channels == 2
            assert params.bit_depth == 16
            
    def test_aac_parameter_extraction(self, temp_audio_file):
        """Test AAC parameter extraction"""
        # Create AAC ADTS header
        # FF F1 (sync) | 50 (profile, freq, channel) | 80 (config) | 00 1F C0 (frame length)
        aac_header = b"\xFF\xF1\x50\x80\x00\x1F\xC0"
        aac_data = aac_header + b"\x00" * 100
        
        test_file = temp_audio_file(aac_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.AAC)
            
            assert params.format == AudioFormat.AAC
            assert params.codec_type == CodecType.LOSSY
            assert params.sample_rate in [44100, 48000]  # Common rates
            assert params.channels in [1, 2]
            assert params.frame_size == 1024
            
    def test_unknown_format_extraction(self, temp_audio_file):
        """Test unknown format parameter extraction"""
        test_file = temp_audio_file(b"UNKNOWN DATA")
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.UNKNOWN)
            
            assert params.format == AudioFormat.UNKNOWN
            assert params.codec_type == CodecType.LOSSY
            
    def test_mp3_with_id3_extraction(self, temp_audio_file, id3v2_test_data, mp3_test_data):
        """Test MP3 parameter extraction with ID3v2 tag"""
        test_file = temp_audio_file(id3v2_test_data + mp3_test_data)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.MP3)
            
            assert params.format == AudioFormat.MP3
            assert params.sample_rate == 44100
            
    def test_mp3_version_detection(self, temp_audio_file):
        """Test MP3 version detection"""
        # Create different MP3 headers
        # MPEG2 Layer3 header
        mpeg2_header = b"\xFF\xF3\x90\x00"
        test_file = temp_audio_file(mpeg2_header + b"\x00" * 200)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.MP3)
            
            assert params.custom_params.get("version") == "MPEG2"
            
    def test_ogg_vorbis_extraction(self, temp_audio_file):
        """Test Ogg Vorbis parameter extraction"""
        # Create simple Ogg page with Vorbis header
        ogg_page = b"OggS"  # Capture pattern
        ogg_page += b"\x00"  # Version
        ogg_page += b"\x02"  # Header type (first page)
        ogg_page += b"\x00" * 8  # Granule position
        ogg_page += b"\x00" * 4  # Serial number
        ogg_page += b"\x00" * 4  # Page sequence
        ogg_page += b"\x00" * 4  # Checksum
        ogg_page += b"\x01"  # Page segments
        ogg_page += b"\x1E"  # Segment table (30 bytes)
        
        # Vorbis header
        vorbis_header = b"\x01vorbis"  # Packet type + signature
        vorbis_header += struct.pack("<I", 0)  # Version
        vorbis_header += struct.pack("B", 2)  # Channels
        vorbis_header += struct.pack("<I", 44100)  # Sample rate
        vorbis_header += struct.pack("<I", 0)  # Bitrate max
        vorbis_header += struct.pack("<I", 128000)  # Bitrate nominal
        vorbis_header += struct.pack("<I", 0)  # Bitrate min
        vorbis_header += b"\x0B"  # Blocksize
        vorbis_header += b"\x01"  # Framing
        
        test_file = temp_audio_file(ogg_page + vorbis_header)
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            params = extractor.extract_parameters(AudioFormat.OGG)
            
            assert params.format == AudioFormat.OGG
            assert params.codec_type == CodecType.LOSSY
            assert params.sample_rate == 44100
            assert params.channels == 2
            assert params.bitrate == 128000
            
    def test_empty_file_handling(self, temp_audio_file):
        """Test handling of empty file"""
        test_file = temp_audio_file(b"")
        
        with BinaryParser(test_file) as parser:
            extractor = CodecParameterExtractor(parser)
            
            for format_type in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.FLAC]:
                params = extractor.extract_parameters(format_type)
                assert params.format == format_type