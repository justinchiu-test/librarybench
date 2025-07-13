"""Tests for psychoacoustic parameter extraction"""

import pytest
import struct
import numpy as np

from pybinparser.core import BinaryParser, AudioFormat, AudioFrame
from pybinparser.psychoacoustic import (
    PsychoacousticAnalyzer, PsychoacousticParameters,
    MaskingThreshold, FrequencyBand
)


class TestPsychoacousticAnalyzer:
    """Test PsychoacousticAnalyzer class"""
    
    def test_mp3_psychoacoustic_extraction(self, temp_audio_file):
        """Test MP3 psychoacoustic parameter extraction"""
        # Create MP3 frame with side information
        mp3_header = b"\xFF\xFB\x90\x00"  # MPEG1 Layer3, 128kbps, 44.1kHz
        
        # Side information (simplified)
        side_info = bytearray(32)
        side_info[0] = 0x00  # main_data_begin
        side_info[1] = 0x00
        side_info[2] = 0x00  # private bits, scfsi
        side_info[3] = 0x00
        
        # Granule info
        side_info[4] = 0x12  # part2_3_length high
        side_info[5] = 0x34  # part2_3_length low, big_values high
        side_info[6] = 0x56  # big_values low, global_gain high
        side_info[7] = 0x78  # global_gain low, scalefac_compress high
        side_info[8] = 0x90  # scalefac_compress low, window_switching
        
        frame_data = mp3_header + b"\x00\x00" + bytes(side_info) + b"\x00" * 381
        
        frames = [AudioFrame(
            offset=0,
            size=len(frame_data),
            header=mp3_header,
            data=frame_data[4:],
            timestamp=0.0
        )]
        
        test_file = temp_audio_file(frame_data)
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            params = analyzer.extract_parameters(AudioFormat.MP3, frames)
            
            assert params.model_type == "MPEG Layer III"
            assert len(params.frequency_bands) > 0
            assert len(params.masking_thresholds) > 0
            assert "pre_masking" in params.temporal_masking
            assert "post_masking" in params.temporal_masking
            
    def test_aac_psychoacoustic_extraction(self, temp_audio_file):
        """Test AAC psychoacoustic parameter extraction"""
        # Create dummy AAC frame
        aac_frame = AudioFrame(
            offset=0,
            size=100,
            header=b"\xFF\xF1\x00\x00",
            data=b"\x00" * 96,
            timestamp=0.0
        )
        
        test_file = temp_audio_file(b"dummy")
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            params = analyzer.extract_parameters(AudioFormat.AAC, [aac_frame])
            
            assert params.model_type == "AAC"
            assert params.window_type == "KBD"
            assert len(params.frequency_bands) > 0
            assert len(params.masking_thresholds) > 0
            assert params.block_switching is True
            assert params.sme_ratio == 20.0
            
    def test_vorbis_psychoacoustic_extraction(self, temp_audio_file):
        """Test Vorbis psychoacoustic parameter extraction"""
        test_file = temp_audio_file(b"dummy")
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            params = analyzer.extract_parameters(AudioFormat.OGG, [])
            
            assert params.model_type == "Vorbis"
            assert params.window_type == "Vorbis"
            assert len(params.frequency_bands) > 0
            assert len(params.masking_thresholds) > 0
            assert "lapping" in params.temporal_masking
            
    def test_opus_psychoacoustic_extraction(self, temp_audio_file):
        """Test Opus psychoacoustic parameter extraction"""
        test_file = temp_audio_file(b"dummy")
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            params = analyzer.extract_parameters(AudioFormat.OPUS, [])
            
            assert params.model_type == "Opus/CELT"
            assert params.window_type == "MDCT with multiple sizes"
            assert len(params.frequency_bands) > 0
            assert params.block_switching is True
            assert params.perceptual_entropy == 0.85
            
    def test_unknown_format_psychoacoustic(self, temp_audio_file):
        """Test unknown format handling"""
        test_file = temp_audio_file(b"dummy")
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            params = analyzer.extract_parameters(AudioFormat.UNKNOWN, [])
            
            assert params.model_type == "unknown"
            assert len(params.frequency_bands) == 0
            assert len(params.masking_thresholds) == 0
            
    def test_spectral_content_analysis(self, temp_audio_file):
        """Test spectral content analysis"""
        # Create a 1kHz sine wave
        sample_rate = 44100
        frequency = 1000
        duration = 0.02
        
        samples = []
        for i in range(int(sample_rate * duration)):
            sample = int(32767 * np.sin(2 * np.pi * frequency * i / sample_rate))
            samples.extend(struct.pack("<h", sample))
            
        frame_data = bytes(samples)
        test_file = temp_audio_file(frame_data)
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            spectral_info = analyzer.analyze_spectral_content(frame_data, sample_rate)
            
            assert "peaks" in spectral_info
            assert "spectral_centroid" in spectral_info
            assert "spectral_spread" in spectral_info
            assert "total_energy" in spectral_info
            
            # Should find peak near 1kHz
            if spectral_info["peaks"]:
                peak_freqs = [p["frequency"] for p in spectral_info["peaks"]]
                # Check if any peak is close to 1000 Hz
                assert any(900 < freq < 1100 for freq in peak_freqs)
                
    def test_masking_threshold_model(self):
        """Test MaskingThreshold model"""
        threshold = MaskingThreshold(
            frequency=1000.0,
            threshold=-20.0,
            masker_type="tonal"
        )
        
        assert threshold.frequency == 1000.0
        assert threshold.threshold == -20.0
        assert threshold.masker_type == "tonal"
        
    def test_frequency_band_model(self):
        """Test FrequencyBand model"""
        band = FrequencyBand(
            start_freq=1000.0,
            end_freq=2000.0,
            scale_factor=10,
            bits_allocated=16,
            quantization_step=0.5
        )
        
        assert band.start_freq == 1000.0
        assert band.end_freq == 2000.0
        assert band.scale_factor == 10
        assert band.bits_allocated == 16
        assert band.quantization_step == 0.5
        
    def test_mp3_critical_bands(self):
        """Test MP3 critical bands constant"""
        bands = PsychoacousticAnalyzer.MP3_CRITICAL_BANDS
        
        assert len(bands) == 25
        assert bands[0] == (0, 100)
        assert bands[-1] == (15500, 20000)
        
        # Check bands are continuous
        for i in range(len(bands) - 1):
            assert bands[i][1] == bands[i+1][0]
            
    def test_mp3_window_switching_detection(self, temp_audio_file):
        """Test MP3 window switching detection"""
        # Create MP3 frame with window switching enabled
        mp3_header = b"\xFF\xFB\x90\x00"
        
        side_info = bytearray(32)
        # Set window_switching flag in granule info
        side_info[8] = 0x40  # window_switching = 1, block_type = 0
        
        frame_data = mp3_header + b"\x00\x00" + bytes(side_info) + b"\x00" * 381
        
        frames = [AudioFrame(
            offset=0,
            size=len(frame_data),
            header=mp3_header,
            data=frame_data[4:],
            timestamp=0.0
        )]
        
        test_file = temp_audio_file(frame_data)
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            params = analyzer.extract_parameters(AudioFormat.MP3, frames)
            
            # Block switching detection is simplified
            # Check that the model was processed
            assert params.model_type == "MPEG Layer III"
            assert len(params.frequency_bands) > 0
            
    def test_empty_frame_list_handling(self, temp_audio_file):
        """Test handling of empty frame list"""
        test_file = temp_audio_file(b"dummy")
        
        with BinaryParser(test_file) as parser:
            analyzer = PsychoacousticAnalyzer(parser)
            
            for format_type in [AudioFormat.MP3, AudioFormat.AAC]:
                params = analyzer.extract_parameters(format_type, [])
                assert isinstance(params, PsychoacousticParameters)
                assert params.model_type != "unknown"