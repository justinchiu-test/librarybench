"""Tests for frame detection functionality"""

import pytest
from pathlib import Path

from pybinparser.core import BinaryParser, AudioFormat
from pybinparser.frame_detector import FrameDetector, FrameInfo


class TestFrameDetector:
    """Test FrameDetector class"""
    
    def test_format_detection_mp3(self, temp_audio_file, mp3_test_data):
        """Test MP3 format detection"""
        test_file = temp_audio_file(mp3_test_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            
            assert format_type == AudioFormat.MP3
            
    def test_format_detection_mp3_with_id3(self, temp_audio_file, id3v2_test_data, mp3_test_data):
        """Test MP3 format detection with ID3v2 tag"""
        test_file = temp_audio_file(id3v2_test_data + mp3_test_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            
            assert format_type == AudioFormat.MP3
            
    def test_format_detection_wav(self, temp_audio_file, wav_test_data):
        """Test WAV format detection"""
        test_file = temp_audio_file(wav_test_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            
            assert format_type == AudioFormat.WAV
            
    def test_format_detection_flac(self, temp_audio_file, flac_test_data):
        """Test FLAC format detection"""
        test_file = temp_audio_file(flac_test_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            
            assert format_type == AudioFormat.FLAC
            
    def test_format_detection_unknown(self, temp_audio_file):
        """Test unknown format detection"""
        test_file = temp_audio_file(b"UNKNOWN FORMAT DATA")
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            
            assert format_type == AudioFormat.UNKNOWN
            
    def test_mp3_frame_detection(self, temp_audio_file, mp3_test_data):
        """Test MP3 frame detection"""
        # Create multiple MP3 frames
        data = mp3_test_data * 3
        test_file = temp_audio_file(data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            frames = detector.find_frames(max_frames=3)
            
            assert len(frames) == 3
            assert all(frame.header[:2] == b"\xFF\xFB" for frame in frames)
            assert all(frame.size == 417 for frame in frames)  # Correct frame size for 128kbps
            
    def test_wav_frame_detection(self, temp_audio_file, wav_test_data):
        """Test WAV data chunk detection"""
        test_file = temp_audio_file(wav_test_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            frames = detector.find_frames()
            
            assert len(frames) == 1  # WAV has one data chunk
            assert frames[0].header[:4] == b"data"
            
    def test_id3v2_size_calculation(self, temp_audio_file, id3v2_test_data):
        """Test ID3v2 tag size calculation"""
        test_file = temp_audio_file(id3v2_test_data)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            parser.seek(0)
            header = parser.read(10)
            size = detector._get_id3v2_size(header)
            
            assert size == 110  # 100 + 10 header
            
    def test_mp3_frame_size_calculation(self, temp_audio_file):
        """Test MP3 frame size calculation"""
        test_file = temp_audio_file(b"dummy")
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            
            # MPEG1 Layer3, 128kbps, 44.1kHz
            header = b"\xFF\xFB\x90\x00"
            frame_size = detector._calculate_mp3_frame_size(header)
            
            assert frame_size == 417  # Expected size for these parameters
            
    def test_frame_validation(self, temp_audio_file, mp3_test_data):
        """Test frame sequence validation"""
        # Create frames with gap
        frame1 = mp3_test_data
        gap = b"\x00" * 100
        frame2 = mp3_test_data
        
        test_file = temp_audio_file(frame1 + gap + frame2)
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            detector._detected_format = AudioFormat.MP3
            
            # Manually create frames with gap
            from pybinparser.core import AudioFrame
            frames = [
                AudioFrame(offset=0, size=len(frame1), header=frame1[:4], data=frame1[4:]),
                AudioFrame(offset=len(frame1) + len(gap), size=len(frame2), header=frame2[:4], data=frame2[4:])
            ]
            
            valid, errors = detector.validate_frame_sequence(frames)
            
            assert not valid
            assert len(errors) > 0
            assert "Gap" in errors[0]
            
    def test_empty_file_handling(self, temp_audio_file):
        """Test handling of empty file"""
        test_file = temp_audio_file(b"")
        
        with BinaryParser(test_file) as parser:
            detector = FrameDetector(parser)
            format_type = detector.detect_format()
            frames = detector.find_frames()
            
            assert format_type == AudioFormat.UNKNOWN
            assert frames == []
            
    def test_aac_sync_pattern(self):
        """Test AAC sync pattern constant"""
        assert FrameDetector.SYNC_PATTERNS[AudioFormat.AAC] == b"\xFF\xF1"
        
    def test_ogg_sync_pattern(self):
        """Test Ogg sync pattern constant"""
        assert FrameDetector.SYNC_PATTERNS[AudioFormat.OGG] == b"OggS"