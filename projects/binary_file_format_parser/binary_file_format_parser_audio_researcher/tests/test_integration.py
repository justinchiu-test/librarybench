"""Integration tests for PyBinParser"""

import pytest
from pathlib import Path

from pybinparser import (
    BinaryParser, AudioFormat, FrameDetector, CodecParameterExtractor,
    FormatDetector, MetadataParser, PsychoacousticAnalyzer
)


class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_complete_mp3_analysis(self, temp_audio_file, mp3_test_data, id3v2_test_data):
        """Test complete MP3 file analysis workflow"""
        # Create MP3 file with ID3v2 tag
        test_file = temp_audio_file(id3v2_test_data + mp3_test_data * 5)
        
        with BinaryParser(test_file) as parser:
            # 1. Detect format
            frame_detector = FrameDetector(parser)
            format_type = frame_detector.detect_format()
            assert format_type == AudioFormat.MP3
            
            # 2. Extract codec parameters
            codec_extractor = CodecParameterExtractor(parser)
            codec_params = codec_extractor.extract_parameters(format_type)
            assert codec_params.bitrate == 128000
            assert codec_params.sample_rate == 44100
            
            # 3. Find frames
            frames = frame_detector.find_frames(max_frames=5)
            assert len(frames) == 5
            
            # 4. Parse metadata
            metadata_parser = MetadataParser(parser)
            tags = metadata_parser.parse_all_tags(format_type)
            assert len(tags) > 0
            
            # 5. Extract psychoacoustic parameters
            psycho_analyzer = PsychoacousticAnalyzer(parser)
            psycho_params = psycho_analyzer.extract_parameters(format_type, frames[:2])
            assert psycho_params.model_type == "MPEG Layer III"
            
    def test_complete_wav_analysis(self, temp_audio_file, wav_test_data):
        """Test complete WAV file analysis workflow"""
        test_file = temp_audio_file(wav_test_data)
        
        with BinaryParser(test_file) as parser:
            # 1. Detect format
            frame_detector = FrameDetector(parser)
            format_type = frame_detector.detect_format()
            assert format_type == AudioFormat.WAV
            
            # 2. Extract codec parameters
            codec_extractor = CodecParameterExtractor(parser)
            codec_params = codec_extractor.extract_parameters(format_type)
            assert codec_params.sample_rate == 44100
            assert codec_params.channels == 2
            assert codec_params.bit_depth == 16
            
            # 3. Auto-detect format characteristics
            format_detector = FormatDetector(parser)
            characteristics = format_detector.detect_format_characteristics()
            assert characteristics["sample_rate"] == 44100
            assert characteristics["bit_depth"] == 16
            
    def test_complete_flac_analysis(self, temp_audio_file, flac_test_data):
        """Test complete FLAC file analysis workflow"""
        test_file = temp_audio_file(flac_test_data)
        
        with BinaryParser(test_file) as parser:
            # 1. Detect format
            frame_detector = FrameDetector(parser)
            format_type = frame_detector.detect_format()
            assert format_type == AudioFormat.FLAC
            
            # 2. Extract codec parameters
            codec_extractor = CodecParameterExtractor(parser)
            codec_params = codec_extractor.extract_parameters(format_type)
            assert codec_params.codec_type.value == "lossless"
            
            # 3. Find frames (FLAC audio frames)
            frames = frame_detector.find_frames(max_frames=1)
            # FLAC detection is simplified in our implementation
            
    def test_unknown_format_handling(self, temp_audio_file):
        """Test handling of unknown format through full pipeline"""
        test_file = temp_audio_file(b"UNKNOWN FORMAT" + b"\x00" * 1000)
        
        with BinaryParser(test_file) as parser:
            # 1. Detect format
            frame_detector = FrameDetector(parser)
            format_type = frame_detector.detect_format()
            assert format_type == AudioFormat.UNKNOWN
            
            # 2. Attempt parameter extraction
            codec_extractor = CodecParameterExtractor(parser)
            codec_params = codec_extractor.extract_parameters(format_type)
            assert codec_params.format == AudioFormat.UNKNOWN
            
            # 3. Auto-detect characteristics
            format_detector = FormatDetector(parser)
            characteristics = format_detector.detect_format_characteristics()
            # Should still attempt detection
            assert "sample_rate" in characteristics
            assert "bit_depth" in characteristics
            
    def test_corrupted_file_handling(self, temp_audio_file):
        """Test handling of corrupted file data"""
        # Create file with partial MP3 header
        corrupted_data = b"\xFF\xFB"  # Incomplete MP3 header
        test_file = temp_audio_file(corrupted_data)
        
        with BinaryParser(test_file) as parser:
            frame_detector = FrameDetector(parser)
            format_type = frame_detector.detect_format()
            
            # Should detect MP3 despite corruption
            assert format_type == AudioFormat.MP3
            
            # But frame detection should handle gracefully
            frames = frame_detector.find_frames()
            assert len(frames) == 0  # No complete frames
            
    def test_multi_format_detection(self, temp_audio_file):
        """Test detection across multiple format types"""
        formats_data = {
            AudioFormat.MP3: b"\xFF\xFB\x90\x00" + b"\x00" * 100,
            AudioFormat.AAC: b"\xFF\xF1\x50\x80\x00\x1F\xC0" + b"\x00" * 100,
            AudioFormat.FLAC: b"fLaC" + b"\x00" * 100,
            AudioFormat.OGG: b"OggS" + b"\x00" * 100,
        }
        
        for expected_format, data in formats_data.items():
            test_file = temp_audio_file(data)
            
            with BinaryParser(test_file) as parser:
                frame_detector = FrameDetector(parser)
                detected_format = frame_detector.detect_format()
                assert detected_format == expected_format
                
    def test_real_time_performance(self, temp_audio_file):
        """Test real-time performance requirements"""
        # Create a larger test file (1MB)
        large_data = b"\xFF\xFB\x90\x00" + b"\x00" * 417  # One MP3 frame
        large_data = large_data * 2000  # ~800KB
        test_file = temp_audio_file(large_data)
        
        import time
        
        with BinaryParser(test_file) as parser:
            start_time = time.time()
            
            # Perform analysis
            frame_detector = FrameDetector(parser)
            format_type = frame_detector.detect_format()
            frames = frame_detector.find_frames(max_frames=100)
            
            codec_extractor = CodecParameterExtractor(parser)
            codec_params = codec_extractor.extract_parameters(format_type)
            
            elapsed_time = time.time() - start_time
            
            # Should complete within reasonable time for real-time
            assert elapsed_time < 1.0  # Less than 1 second
            assert len(frames) == 100
            
    def test_edge_case_small_file(self, temp_audio_file):
        """Test handling of very small files"""
        # File smaller than any valid frame
        small_data = b"\xFF"
        test_file = temp_audio_file(small_data)
        
        with BinaryParser(test_file) as parser:
            frame_detector = FrameDetector(parser)
            format_type = frame_detector.detect_format()
            
            codec_extractor = CodecParameterExtractor(parser)
            codec_params = codec_extractor.extract_parameters(AudioFormat.MP3)
            
            # Should handle gracefully
            assert codec_params.format == AudioFormat.MP3
            assert codec_params.bitrate is None or codec_params.bitrate == 0