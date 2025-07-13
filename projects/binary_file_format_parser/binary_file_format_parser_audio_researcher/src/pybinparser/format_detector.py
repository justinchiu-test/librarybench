"""Format detection module for automatic sample rate and bit depth detection"""

from typing import Dict, List, Optional, Tuple
import struct
import numpy as np
from .core import BinaryParser, AudioFormat


class FormatDetector:
    """Auto-detects audio format characteristics"""
    
    # Common sample rates to test
    COMMON_SAMPLE_RATES = [
        8000, 11025, 12000, 16000, 22050, 24000,
        32000, 44100, 48000, 88200, 96000, 176400, 192000
    ]
    
    # Common bit depths
    COMMON_BIT_DEPTHS = [8, 16, 24, 32]
    
    def __init__(self, parser: BinaryParser):
        """Initialize format detector"""
        self.parser = parser
        
    def detect_format_characteristics(self, data: Optional[bytes] = None) -> Dict[str, Optional[int]]:
        """Auto-detect sample rate and bit depth from raw audio data"""
        if data is None:
            # Read a chunk of data for analysis
            self.parser.seek(0)
            data = self.parser.read(min(1048576, self.parser.file_size))  # 1MB max
            
        results = {
            "sample_rate": None,
            "bit_depth": None,
            "channels": None,
            "byte_order": None  # "little" or "big"
        }
        
        # Handle empty data
        if not data:
            return results
            
        # Try to detect from header first
        header_result = self._detect_from_header(data)
        if header_result["sample_rate"] is not None:
            return header_result
            
        # Fall back to heuristic detection
        results["bit_depth"] = self._detect_bit_depth(data)
        results["channels"] = self._detect_channels(data, results["bit_depth"])
        results["sample_rate"] = self._detect_sample_rate(data, results["bit_depth"], results["channels"])
        results["byte_order"] = self._detect_byte_order(data)
        
        return results
        
    def _detect_from_header(self, data: bytes) -> Dict[str, Optional[int]]:
        """Try to detect from known header formats"""
        result = {
            "sample_rate": None,
            "bit_depth": None,
            "channels": None,
            "byte_order": None
        }
        
        # Check for WAV header
        if len(data) > 44 and data[:4] == b"RIFF" and data[8:12] == b"WAVE":
            # Find fmt chunk
            offset = 12
            while offset < len(data) - 8:
                chunk_id = data[offset:offset+4]
                chunk_size = struct.unpack("<I", data[offset+4:offset+8])[0]
                
                if chunk_id == b"fmt " and offset + 8 + chunk_size <= len(data):
                    fmt_data = data[offset+8:offset+8+chunk_size]
                    if len(fmt_data) >= 16:
                        result["channels"] = struct.unpack("<H", fmt_data[2:4])[0]
                        result["sample_rate"] = struct.unpack("<I", fmt_data[4:8])[0]
                        result["bit_depth"] = struct.unpack("<H", fmt_data[14:16])[0]
                        result["byte_order"] = "little"
                        return result
                        
                offset += 8 + chunk_size
                
        # Check for AIFF header
        if len(data) > 54 and data[:4] == b"FORM" and data[8:12] == b"AIFF":
            # Find COMM chunk
            offset = 12
            while offset < len(data) - 8:
                chunk_id = data[offset:offset+4]
                chunk_size = struct.unpack(">I", data[offset+4:offset+8])[0]
                
                if chunk_id == b"COMM" and offset + 8 + chunk_size <= len(data):
                    comm_data = data[offset+8:offset+8+chunk_size]
                    if len(comm_data) >= 18:
                        result["channels"] = struct.unpack(">H", comm_data[0:2])[0]
                        result["bit_depth"] = struct.unpack(">H", comm_data[6:8])[0]
                        # Sample rate is stored as 80-bit IEEE extended precision
                        # For simplicity, we'll extract the integer part
                        exponent = struct.unpack(">H", comm_data[8:10])[0]
                        mantissa = struct.unpack(">Q", comm_data[10:18])[0]
                        if exponent >= 0x400E:  # Expected exponent for 44100 Hz
                            # Approximate calculation for common sample rates
                            if exponent == 0x400E and mantissa >> 56 == 0xAC:
                                result["sample_rate"] = 44100
                            else:
                                result["sample_rate"] = int(mantissa >> (16446 - exponent)) if exponent < 16446 else 44100
                        result["byte_order"] = "big"
                        return result
                        
                offset += 8 + chunk_size
                
        return result
        
    def _detect_bit_depth(self, data: bytes) -> int:
        """Detect bit depth by analyzing data patterns"""
        if len(data) < 1024:
            return 16  # Default
            
        # Check for 8-bit data (all values in 0-255 range)
        all_8bit = all(b < 256 for b in data[:1024])
        if all_8bit:
            # Check if centered around 128 (unsigned 8-bit)
            avg = sum(data[:1024]) / 1024
            if 118 < avg < 138:  # Tighter range around 128
                return 8
                
        # Check for 24-bit patterns (every 3rd byte often 0x00 or 0xFF)
        zero_count_24 = sum(1 for i in range(2, min(len(data), 3000), 3) if data[i] in [0x00, 0xFF])
        if zero_count_24 > 900:  # More than 90% of 3rd bytes are 0x00 or 0xFF
            return 24
            
        # Check for 32-bit patterns (every 4th byte often 0x00)
        zero_count_32 = sum(1 for i in range(3, min(len(data), 4000), 4) if data[i] == 0x00)
        if zero_count_32 > 700:  # More than 70% of 4th bytes are 0x00
            return 32
            
        # Default to 16-bit
        return 16
        
    def _detect_channels(self, data: bytes, bit_depth: int) -> int:
        """Detect number of channels by analyzing data patterns"""
        if bit_depth == 0 or len(data) < 1024:
            return 2  # Default to stereo
            
        bytes_per_sample = bit_depth // 8
        
        # For stereo, left and right channels often have similar patterns
        # Check correlation between alternating samples
        if len(data) >= bytes_per_sample * 200:
            # Extract alternating samples
            samples1 = []
            samples2 = []
            
            for i in range(0, 200 * bytes_per_sample * 2, bytes_per_sample * 2):
                if i + bytes_per_sample * 2 <= len(data):
                    if bit_depth == 16:
                        samples1.append(struct.unpack("<h", data[i:i+2])[0])
                        samples2.append(struct.unpack("<h", data[i+2:i+4])[0])
                    elif bit_depth == 8:
                        samples1.append(data[i] - 128)
                        samples2.append(data[i+1] - 128)
                        
            if len(samples1) > 50 and len(samples2) > 50:
                # Calculate correlation
                # Handle case where all samples are the same (avoid divide by zero)
                if np.std(samples1[:50]) > 0 and np.std(samples2[:50]) > 0:
                    corr = np.corrcoef(samples1[:50], samples2[:50])[0, 1]
                    
                    # High correlation suggests stereo
                    if abs(corr) > 0.7:
                        return 2
                else:
                    # If no variation, likely mono
                    return 1
                    
        # Check for silence patterns that might indicate mono
        silence_threshold = 10 if bit_depth == 16 else 5
        silence_count = 0
        
        for i in range(0, min(len(data), 1000), bytes_per_sample):
            if i + bytes_per_sample <= len(data):
                if bit_depth == 16:
                    sample = abs(struct.unpack("<h", data[i:i+2])[0])
                elif bit_depth == 8:
                    sample = abs(data[i] - 128)
                else:
                    sample = 1000  # Non-zero
                    
                if sample < silence_threshold:
                    silence_count += 1
                    
        # If mostly silence, might be mono
        if silence_count > 800:
            return 1
            
        return 2  # Default to stereo
        
    def _detect_sample_rate(self, data: bytes, bit_depth: int, channels: int) -> int:
        """Detect sample rate using FFT analysis"""
        if bit_depth == 0 or channels == 0 or len(data) < 4096:
            return 44100  # Default
            
        bytes_per_sample = bit_depth // 8
        bytes_per_frame = bytes_per_sample * channels
        
        # Extract samples for FFT
        samples = []
        for i in range(0, min(len(data), 8192), bytes_per_frame):
            if i + bytes_per_sample <= len(data):
                if bit_depth == 16:
                    sample = struct.unpack("<h", data[i:i+2])[0] / 32768.0
                elif bit_depth == 8:
                    sample = (data[i] - 128) / 128.0
                elif bit_depth == 24:
                    if i + 3 <= len(data):
                        # 24-bit little-endian
                        sample_bytes = data[i:i+3] + (b'\x00' if data[i+2] < 128 else b'\xFF')
                        sample = struct.unpack("<i", sample_bytes)[0] / 8388608.0
                    else:
                        continue
                else:  # 32-bit
                    if i + 4 <= len(data):
                        sample = struct.unpack("<i", data[i:i+4])[0] / 2147483648.0
                    else:
                        continue
                        
                samples.append(sample)
                
        if len(samples) < 1024:
            return 44100  # Default
            
        # Perform FFT
        samples = samples[:1024]  # Use power of 2
        fft_result = np.fft.fft(samples)
        magnitudes = np.abs(fft_result[:512])  # Only positive frequencies
        
        # Find dominant frequency
        peak_idx = np.argmax(magnitudes[1:]) + 1  # Skip DC component
        
        # For a 1kHz test signal, we expect peak at specific bins depending on sample rate
        # At 44100 Hz: bin ~23, at 48000 Hz: bin ~21, at 22050 Hz: bin ~46
        if 20 <= peak_idx <= 25:
            return 44100
        elif 19 <= peak_idx <= 22:
            return 48000  
        elif 44 <= peak_idx <= 48:
            return 22050
        elif 30 <= peak_idx <= 34:
            return 32000
        else:
            # Fall back to frequency analysis
            best_rate = 44100
            best_score = 0
            
            for rate in self.COMMON_SAMPLE_RATES:
                freq = peak_idx * rate / 1024
                
                # Score based on common audio frequencies
                score = 0
                if 900 <= freq <= 1100:  # Near 1kHz test signal
                    score += 20
                if 80 <= freq <= 4000:  # Human voice range
                    score += 10
                if 440 <= freq <= 880:  # Musical note A
                    score += 5
                    
                if score > best_score:
                    best_score = score
                    best_rate = rate
                    
            return best_rate
        
    def _detect_byte_order(self, data: bytes) -> str:
        """Detect byte order (endianness)"""
        if len(data) < 1000:
            return "little"  # Default
            
        # Count zero bytes in even vs odd positions
        even_zeros = sum(1 for i in range(0, min(len(data), 1000), 2) if data[i] == 0)
        odd_zeros = sum(1 for i in range(1, min(len(data), 1000), 2) if data[i] == 0)
        
        # In little-endian 16-bit audio, high byte (odd position) is more likely to be zero
        if odd_zeros > even_zeros * 1.5:
            return "little"
        elif even_zeros > odd_zeros * 1.5:
            return "big"
            
        return "little"  # Default
        
    def analyze_data_patterns(self, data: bytes) -> Dict[str, any]:
        """Analyze data patterns for format detection"""
        analysis = {
            "min_value": None,
            "max_value": None,
            "mean_value": None,
            "zero_crossings": 0,
            "dynamic_range": None,
            "likely_signed": None,
            "histogram": {}
        }
        
        if len(data) < 100:
            return analysis
            
        # Basic statistics
        values = list(data[:10000])  # Analyze first 10KB
        analysis["min_value"] = min(values)
        analysis["max_value"] = max(values)
        analysis["mean_value"] = sum(values) / len(values)
        
        # Check if likely signed or unsigned
        if analysis["mean_value"] > 100 and analysis["mean_value"] < 156:
            analysis["likely_signed"] = False  # Unsigned 8-bit
        elif analysis["min_value"] < 20 and analysis["max_value"] > 236:
            analysis["likely_signed"] = False  # Full range unsigned
        else:
            analysis["likely_signed"] = True
            
        # Count zero crossings (for 8-bit)
        prev_val = values[0]
        zero_line = 128 if not analysis["likely_signed"] else 0
        
        for val in values[1:]:
            if (prev_val < zero_line and val >= zero_line) or \
               (prev_val > zero_line and val <= zero_line):
                analysis["zero_crossings"] += 1
            prev_val = val
            
        # Dynamic range
        analysis["dynamic_range"] = analysis["max_value"] - analysis["min_value"]
        
        # Simple histogram (10 bins)
        bin_size = (analysis["max_value"] - analysis["min_value"] + 1) // 10
        if bin_size > 0:
            for val in values:
                bin_idx = min((val - analysis["min_value"]) // bin_size, 9)
                analysis["histogram"][bin_idx] = analysis["histogram"].get(bin_idx, 0) + 1
                
        return analysis