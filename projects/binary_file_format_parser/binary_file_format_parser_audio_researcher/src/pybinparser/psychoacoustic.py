"""Psychoacoustic model parameter extraction module"""

from typing import Dict, List, Optional, Tuple
import struct
import numpy as np
from pydantic import BaseModel, Field
from .core import BinaryParser, AudioFormat, AudioFrame


class MaskingThreshold(BaseModel):
    """Represents masking threshold data"""
    
    frequency: float = Field(description="Frequency in Hz")
    threshold: float = Field(description="Masking threshold in dB")
    masker_type: str = Field(description="Type of masker (tonal/noise)")


class FrequencyBand(BaseModel):
    """Represents a frequency band allocation"""
    
    start_freq: float = Field(description="Start frequency in Hz")
    end_freq: float = Field(description="End frequency in Hz")
    scale_factor: int = Field(description="Scale factor for this band")
    bits_allocated: int = Field(description="Bits allocated to this band")
    quantization_step: float = Field(description="Quantization step size")


class PsychoacousticParameters(BaseModel):
    """Psychoacoustic model parameters"""
    
    model_type: str = Field(description="Psychoacoustic model type")
    masking_thresholds: List[MaskingThreshold] = Field(
        default_factory=list, description="Masking threshold data"
    )
    frequency_bands: List[FrequencyBand] = Field(
        default_factory=list, description="Frequency band allocations"
    )
    temporal_masking: Dict[str, float] = Field(
        default_factory=dict, description="Temporal masking parameters"
    )
    perceptual_entropy: Optional[float] = Field(
        None, description="Perceptual entropy value"
    )
    sme_ratio: Optional[float] = Field(
        None, description="Signal-to-mask energy ratio"
    )
    window_type: Optional[str] = Field(
        None, description="Analysis window type"
    )
    block_switching: Optional[bool] = Field(
        None, description="Whether block switching is used"
    )


class PsychoacousticAnalyzer:
    """Analyzes psychoacoustic model parameters from audio codecs"""
    
    # Critical bands for MP3 (simplified)
    MP3_CRITICAL_BANDS = [
        (0, 100), (100, 200), (200, 300), (300, 400), (400, 510),
        (510, 630), (630, 770), (770, 920), (920, 1080), (1080, 1270),
        (1270, 1480), (1480, 1720), (1720, 2000), (2000, 2320), (2320, 2700),
        (2700, 3150), (3150, 3700), (3700, 4400), (4400, 5300), (5300, 6400),
        (6400, 7700), (7700, 9500), (9500, 12000), (12000, 15500), (15500, 20000)
    ]
    
    def __init__(self, parser: BinaryParser):
        """Initialize psychoacoustic analyzer"""
        self.parser = parser
        
    def extract_parameters(self, format_type: AudioFormat, frames: List[AudioFrame]) -> PsychoacousticParameters:
        """Extract psychoacoustic parameters based on format"""
        if format_type == AudioFormat.MP3:
            return self._extract_mp3_psychoacoustic(frames)
        elif format_type == AudioFormat.AAC:
            return self._extract_aac_psychoacoustic(frames)
        elif format_type == AudioFormat.OGG:
            return self._extract_vorbis_psychoacoustic(frames)
        elif format_type == AudioFormat.OPUS:
            return self._extract_opus_psychoacoustic(frames)
        else:
            return PsychoacousticParameters(model_type="unknown")
            
    def _extract_mp3_psychoacoustic(self, frames: List[AudioFrame]) -> PsychoacousticParameters:
        """Extract MP3 psychoacoustic model parameters"""
        params = PsychoacousticParameters(model_type="MPEG Layer III")
        
        if not frames:
            return params
            
        # Analyze first few frames
        for frame_idx, frame in enumerate(frames[:10]):
            if len(frame.header) < 4:
                continue
                
            # Parse MP3 header
            header_bits = struct.unpack(">I", frame.header)[0]
            
            # Extract header fields
            version = (header_bits >> 19) & 0x03
            layer = (header_bits >> 17) & 0x03
            protection = (header_bits >> 16) & 0x01
            bitrate_index = (header_bits >> 12) & 0x0F
            sample_rate_index = (header_bits >> 10) & 0x03
            padding = (header_bits >> 9) & 0x01
            private = (header_bits >> 8) & 0x01
            mode = (header_bits >> 6) & 0x03
            mode_extension = (header_bits >> 4) & 0x03
            
            # Check for side information (after header and CRC if present)
            side_info_start = 2 if protection == 0 else 0  # side info is in frame.data, not including header
            
            if side_info_start + 32 <= len(frame.data):
                # Extract side information
                side_info = frame.data[side_info_start:side_info_start+32]
                
                # Parse main_data_begin (9 bits)
                main_data_begin = (side_info[0] << 1) | (side_info[1] >> 7)
                
                # Parse private bits and scale factor selection info
                scfsi = []
                if mode != 3:  # Not mono
                    for ch in range(2):
                        scfsi.append([
                            (side_info[2 + ch] >> 3) & 0x01,
                            (side_info[2 + ch] >> 2) & 0x01,
                            (side_info[2 + ch] >> 1) & 0x01,
                            (side_info[2 + ch]) & 0x01
                        ])
                        
                # Extract granule information
                offset = 4 if mode == 3 else 6
                
                for gr in range(2):  # MP3 has 2 granules per frame
                    for ch in range(1 if mode == 3 else 2):
                        if offset + 59 > len(side_info):
                            break
                            
                        # Parse granule data
                        part2_3_length = (side_info[offset] << 4) | (side_info[offset+1] >> 4)
                        big_values = ((side_info[offset+1] & 0x0F) << 5) | (side_info[offset+2] >> 3)
                        global_gain = ((side_info[offset+2] & 0x07) << 5) | (side_info[offset+3] >> 3)
                        scalefac_compress = (side_info[offset+3] & 0x07) << 1 | (side_info[offset+4] >> 7)
                        window_switching = (side_info[offset+4] >> 6) & 0x01
                        
                        # Window switching indicates transient detection
                        if window_switching:
                            params.block_switching = True
                            
                            if frame_idx == 0:
                                block_type = (side_info[offset+4] >> 4) & 0x03
                                mixed_block = (side_info[offset+4] >> 3) & 0x01
                                
                                if block_type == 2:
                                    params.window_type = "short"
                                elif block_type == 0:
                                    params.window_type = "stop"
                                elif block_type == 1:
                                    params.window_type = "start"
                                else:
                                    params.window_type = "normal"
                                
                        # Extract scale factor information
                        if frame_idx == 0 and len(params.frequency_bands) == 0:
                            # Simplified frequency band creation based on scale factor compress
                            num_bands = min(len(self.MP3_CRITICAL_BANDS), 21)
                            for i in range(num_bands):
                                band_start, band_end = self.MP3_CRITICAL_BANDS[i]
                                
                                # Estimate bits allocated based on scale factor compress
                                bits = max(0, 16 - scalefac_compress // 2)
                                
                                params.frequency_bands.append(FrequencyBand(
                                    start_freq=float(band_start),
                                    end_freq=float(band_end),
                                    scale_factor=scalefac_compress,
                                    bits_allocated=bits,
                                    quantization_step=2.0 ** (scalefac_compress / 4.0)
                                ))
                                
                        offset += 59  # Size of granule info
                        
        # If no frequency bands were created from side info, create default ones
        if len(params.frequency_bands) == 0:
            # Create default frequency bands for MP3
            for i in range(min(len(self.MP3_CRITICAL_BANDS), 21)):
                band_start, band_end = self.MP3_CRITICAL_BANDS[i]
                params.frequency_bands.append(FrequencyBand(
                    start_freq=float(band_start),
                    end_freq=float(band_end),
                    scale_factor=8,  # Default scale factor
                    bits_allocated=12,  # Default bits
                    quantization_step=2.0
                ))
                        
        # Add masking thresholds based on critical bands
        for i, (start, end) in enumerate(self.MP3_CRITICAL_BANDS[:10]):
            center_freq = (start + end) / 2.0
            
            # Simplified masking threshold calculation
            # Real implementation would analyze actual spectral content
            threshold = -20.0 - (i * 2.0)  # Decreasing threshold with frequency
            
            params.masking_thresholds.append(MaskingThreshold(
                frequency=center_freq,
                threshold=threshold,
                masker_type="tonal" if i < 5 else "noise"
            ))
            
        # Temporal masking parameters
        params.temporal_masking = {
            "pre_masking": 5.0,  # ms
            "post_masking": 100.0,  # ms
            "masking_decay": 10.0  # dB/ms
        }
        
        # Estimate perceptual entropy (simplified)
        if params.frequency_bands:
            avg_bits = sum(b.bits_allocated for b in params.frequency_bands) / len(params.frequency_bands)
            params.perceptual_entropy = avg_bits / 16.0  # Normalized
            
        return params
        
    def _extract_aac_psychoacoustic(self, frames: List[AudioFrame]) -> PsychoacousticParameters:
        """Extract AAC psychoacoustic model parameters"""
        params = PsychoacousticParameters(model_type="AAC")
        
        if not frames:
            return params
            
        # AAC uses more sophisticated psychoacoustic model
        params.window_type = "KBD"  # Kaiser-Bessel Derived window
        
        # AAC frequency bands (simplified)
        aac_bands = [
            (0, 200), (200, 400), (400, 600), (600, 800), (800, 1000),
            (1000, 1200), (1200, 1600), (1600, 2000), (2000, 2400),
            (2400, 3200), (3200, 4000), (4000, 4800), (4800, 6400),
            (6400, 8000), (8000, 12000), (12000, 16000), (16000, 20000)
        ]
        
        for i, (start, end) in enumerate(aac_bands):
            params.frequency_bands.append(FrequencyBand(
                start_freq=float(start),
                end_freq=float(end),
                scale_factor=0,
                bits_allocated=16 - i // 2,  # Decreasing bits with frequency
                quantization_step=1.0 + (i * 0.5)
            ))
            
        # AAC masking model
        for i in range(0, 20000, 1000):
            freq = float(i)
            # Simplified masking curve
            threshold = -24.0 - (freq / 1000.0) * 1.5
            
            params.masking_thresholds.append(MaskingThreshold(
                frequency=freq,
                threshold=threshold,
                masker_type="combined"
            ))
            
        # AAC temporal parameters
        params.temporal_masking = {
            "pre_masking": 2.0,
            "post_masking": 50.0,
            "transient_detection": "energy_based"
        }
        
        params.block_switching = True
        params.sme_ratio = 20.0  # Typical SMR for AAC
        
        return params
        
    def _extract_vorbis_psychoacoustic(self, frames: List[AudioFrame]) -> PsychoacousticParameters:
        """Extract Vorbis psychoacoustic model parameters"""
        params = PsychoacousticParameters(model_type="Vorbis")
        
        # Vorbis uses a unique approach with floor curves
        params.window_type = "Vorbis"
        
        # Vorbis frequency resolution (simplified)
        for i in range(25):
            start_freq = i * 800.0
            end_freq = (i + 1) * 800.0
            
            params.frequency_bands.append(FrequencyBand(
                start_freq=start_freq,
                end_freq=end_freq,
                scale_factor=0,
                bits_allocated=24 - i // 2,
                quantization_step=0.5 + (i * 0.2)
            ))
            
        # Vorbis masking (simplified floor curve)
        for freq in [100, 200, 400, 800, 1600, 3200, 6400, 12800]:
            threshold = -30.0 + np.log10(freq / 100.0) * 10.0
            
            params.masking_thresholds.append(MaskingThreshold(
                frequency=float(freq),
                threshold=threshold,
                masker_type="floor"
            ))
            
        params.temporal_masking = {
            "lapping": "50%",
            "window_function": "Vorbis window"
        }
        
        return params
        
    def _extract_opus_psychoacoustic(self, frames: List[AudioFrame]) -> PsychoacousticParameters:
        """Extract Opus psychoacoustic model parameters"""
        params = PsychoacousticParameters(model_type="Opus/CELT")
        
        # Opus uses hybrid approach
        params.window_type = "MDCT with multiple sizes"
        
        # Opus bands (CELT bands)
        opus_bands = [
            (0, 200), (200, 400), (400, 600), (600, 800),
            (800, 1000), (1000, 1200), (1200, 1400), (1400, 1600),
            (1600, 2000), (2000, 2400), (2400, 2800), (2800, 3200),
            (3200, 4000), (4000, 4800), (4800, 5600), (5600, 6800),
            (6800, 8000), (8000, 9600), (9600, 12000), (12000, 15600),
            (15600, 20000)
        ]
        
        for i, (start, end) in enumerate(opus_bands):
            params.frequency_bands.append(FrequencyBand(
                start_freq=float(start),
                end_freq=float(end),
                scale_factor=0,
                bits_allocated=32 - i,  # High bit allocation
                quantization_step=0.25 + (i * 0.1)
            ))
            
        # Opus perceptual model
        for i, freq in enumerate(np.logspace(2, 4.3, 20)):  # Log scale from 100Hz to 20kHz
            threshold = -40.0 + i * 1.5
            
            params.masking_thresholds.append(MaskingThreshold(
                frequency=float(freq),
                threshold=threshold,
                masker_type="adaptive"
            ))
            
        params.temporal_masking = {
            "frame_size": "variable",
            "complexity": "0-10",
            "prediction": "LPC-based"
        }
        
        params.block_switching = True
        params.perceptual_entropy = 0.85  # High efficiency
        
        return params
        
    def analyze_spectral_content(self, frame_data: bytes, sample_rate: int = 44100) -> Dict[str, any]:
        """Analyze spectral content of audio frame"""
        # Convert bytes to samples
        samples = []
        for i in range(0, len(frame_data) - 1, 2):
            sample = struct.unpack("<h", frame_data[i:i+2])[0] / 32768.0
            samples.append(sample)
            
        if len(samples) < 512:
            return {}
            
        # Perform FFT
        samples = samples[:512]
        fft_result = np.fft.fft(samples)
        magnitudes = np.abs(fft_result[:256])
        frequencies = np.fft.fftfreq(512, 1/sample_rate)[:256]
        
        # Find spectral peaks
        peaks = []
        for i in range(1, len(magnitudes) - 1):
            if magnitudes[i] > magnitudes[i-1] and magnitudes[i] > magnitudes[i+1]:
                if magnitudes[i] > np.mean(magnitudes) * 2:
                    peaks.append({
                        "frequency": frequencies[i],
                        "magnitude": magnitudes[i],
                        "bin": i
                    })
                    
        # Calculate spectral features
        spectral_centroid = np.sum(frequencies * magnitudes) / np.sum(magnitudes)
        spectral_spread = np.sqrt(np.sum(((frequencies - spectral_centroid) ** 2) * magnitudes) / np.sum(magnitudes))
        
        return {
            "peaks": peaks[:10],  # Top 10 peaks
            "spectral_centroid": spectral_centroid,
            "spectral_spread": spectral_spread,
            "total_energy": np.sum(magnitudes ** 2)
        }