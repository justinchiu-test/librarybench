"""Codec parameter extraction module"""

from typing import Dict, Optional, Union
import struct
from .core import BinaryParser, CodecParameters, AudioFormat, CodecType


class CodecParameterExtractor:
    """Extracts codec parameters from audio files"""
    
    def __init__(self, parser: BinaryParser):
        """Initialize extractor with binary parser"""
        self.parser = parser
        
    def extract_parameters(self, format_type: AudioFormat) -> CodecParameters:
        """Extract codec parameters based on format type"""
        if format_type == AudioFormat.MP3:
            return self._extract_mp3_parameters()
        elif format_type == AudioFormat.AAC:
            return self._extract_aac_parameters()
        elif format_type == AudioFormat.FLAC:
            return self._extract_flac_parameters()
        elif format_type == AudioFormat.OGG:
            return self._extract_ogg_parameters()
        elif format_type == AudioFormat.OPUS:
            return self._extract_opus_parameters()
        elif format_type == AudioFormat.WAV:
            return self._extract_wav_parameters()
        else:
            return CodecParameters(
                format=AudioFormat.UNKNOWN,
                codec_type=CodecType.LOSSY
            )
            
    def _extract_mp3_parameters(self) -> CodecParameters:
        """Extract MP3 codec parameters"""
        self.parser.seek(0)
        
        # Skip ID3v2 if present
        header = self.parser.read(10)
        self.parser.seek(0)
        
        start_pos = 0
        if header[:3] == b"ID3":
            # Calculate ID3v2 size
            size = ((header[6] & 0x7F) << 21) | \
                   ((header[7] & 0x7F) << 14) | \
                   ((header[8] & 0x7F) << 7) | \
                   (header[9] & 0x7F)
            start_pos = size + 10
            
        # Find first MP3 frame
        self.parser.seek(start_pos)
        
        while self.parser.tell() < self.parser.file_size - 4:
            byte1 = self.parser.read_uint8()
            if byte1 == 0xFF:
                pos = self.parser.tell()
                byte2 = self.parser.read_uint8()
                if (byte2 & 0xE0) == 0xE0:
                    self.parser.seek(pos - 1)
                    break
                self.parser.seek(pos)
                
        # Read MP3 frame header
        frame_header = self.parser.read(4)
        if len(frame_header) < 4:
            return CodecParameters(
                format=AudioFormat.MP3,
                codec_type=CodecType.LOSSY
            )
            
        # Parse header
        version = (frame_header[1] >> 3) & 0x03
        layer = (frame_header[1] >> 1) & 0x03
        bitrate_index = (frame_header[2] >> 4) & 0x0F
        sample_rate_index = (frame_header[2] >> 2) & 0x03
        channel_mode = (frame_header[3] >> 6) & 0x03
        
        # Lookup tables
        bitrate_table = {
            0x03: {  # MPEG1
                0x01: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0],
            },
            0x02: {  # MPEG2
                0x01: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0],
            }
        }
        
        sample_rate_table = {
            0x03: [44100, 48000, 32000, 0],  # MPEG1
            0x02: [22050, 24000, 16000, 0],  # MPEG2
            0x00: [11025, 12000, 8000, 0],   # MPEG2.5
        }
        
        # Get values
        bitrate = 0
        sample_rate = 0
        
        if version in bitrate_table and layer in bitrate_table[version]:
            bitrate = bitrate_table[version][layer][bitrate_index] * 1000
            
        if version in sample_rate_table:
            sample_rate = sample_rate_table[version][sample_rate_index]
            
        # Channel configuration
        channels = 1 if channel_mode == 3 else 2
        
        # Calculate compression ratio (approximate)
        compression_ratio = 1.0
        if bitrate > 0 and sample_rate > 0:
            uncompressed_bitrate = sample_rate * 16 * channels  # Assume 16-bit
            compression_ratio = uncompressed_bitrate / bitrate
            
        return CodecParameters(
            format=AudioFormat.MP3,
            codec_type=CodecType.LOSSY,
            bitrate=bitrate,
            sample_rate=sample_rate,
            bit_depth=16,  # MP3 typically decodes to 16-bit
            channels=channels,
            compression_ratio=compression_ratio,
            frame_size=1152,  # MP3 Layer III frame size
            custom_params={
                "version": ["MPEG2.5", "reserved", "MPEG2", "MPEG1"][version],
                "layer": ["reserved", "Layer3", "Layer2", "Layer1"][layer],
                "channel_mode": ["Stereo", "Joint Stereo", "Dual Channel", "Mono"][channel_mode]
            }
        )
        
    def _extract_aac_parameters(self) -> CodecParameters:
        """Extract AAC ADTS parameters"""
        self.parser.seek(0)
        
        # Find ADTS sync
        sync_found = False
        while self.parser.tell() < self.parser.file_size - 7:
            if self.parser.read(2) == b"\xFF\xF1":
                self.parser.seek(-2, 1)
                sync_found = True
                break
                
        if not sync_found:
            return CodecParameters(
                format=AudioFormat.AAC,
                codec_type=CodecType.LOSSY
            )
            
        # Read ADTS header
        header = self.parser.read(7)
        if len(header) < 7:
            return CodecParameters(
                format=AudioFormat.AAC,
                codec_type=CodecType.LOSSY
            )
            
        # Parse ADTS header
        profile = ((header[2] & 0xC0) >> 6) + 1
        sample_rate_index = (header[2] & 0x3C) >> 2
        channel_config = ((header[2] & 0x01) << 2) | ((header[3] & 0xC0) >> 6)
        
        # Sample rate table
        sample_rates = [96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050, 16000, 12000, 11025, 8000]
        
        sample_rate = sample_rates[sample_rate_index] if sample_rate_index < len(sample_rates) else 44100
        channels = channel_config if channel_config < 8 else 2
        
        # AAC typically uses variable bitrate
        bitrate = sample_rate * channels * 2  # Rough estimate
        
        return CodecParameters(
            format=AudioFormat.AAC,
            codec_type=CodecType.LOSSY,
            bitrate=bitrate,
            sample_rate=sample_rate,
            bit_depth=16,
            channels=channels,
            compression_ratio=8.0,  # Typical AAC compression
            frame_size=1024,  # AAC frame size
            custom_params={
                "profile": ["Main", "LC", "SSR", "LTP"][profile - 1] if profile <= 4 else f"Profile{profile}",
                "adts_buffer_fullness": ((header[5] & 0x1F) << 6) | ((header[6] & 0xFC) >> 2)
            }
        )
        
    def _extract_flac_parameters(self) -> CodecParameters:
        """Extract FLAC parameters"""
        self.parser.seek(0)
        
        # Check FLAC signature
        if self.parser.read(4) != b"fLaC":
            return CodecParameters(
                format=AudioFormat.FLAC,
                codec_type=CodecType.LOSSLESS
            )
            
        # Read metadata blocks
        while True:
            block_header = self.parser.read(4)
            if len(block_header) < 4:
                break
                
            block_type = block_header[0] & 0x7F
            is_last = (block_header[0] & 0x80) != 0
            block_size = struct.unpack(">I", b"\x00" + block_header[1:4])[0]
            
            if block_type == 0:  # STREAMINFO block
                streaminfo = self.parser.read(block_size)
                if len(streaminfo) >= 18:
                    min_block_size = struct.unpack(">H", streaminfo[0:2])[0]
                    max_block_size = struct.unpack(">H", streaminfo[2:4])[0]
                    min_frame_size = struct.unpack(">I", b"\x00" + streaminfo[4:7])[0]
                    max_frame_size = struct.unpack(">I", b"\x00" + streaminfo[7:10])[0]
                    
                    # Sample rate (20 bits) and channels (3 bits) and bits per sample (5 bits)
                    combined = struct.unpack(">I", streaminfo[10:14])[0]
                    sample_rate = combined >> 12
                    channels = ((combined >> 9) & 0x07) + 1
                    bits_per_sample = ((combined >> 4) & 0x1F) + 1
                    
                    # Total samples (36 bits)
                    total_samples = ((combined & 0x0F) << 32) | struct.unpack(">I", streaminfo[14:18])[0]
                    
                    # Calculate bitrate
                    file_size = self.parser.file_size
                    duration = total_samples / sample_rate if sample_rate > 0 else 0
                    bitrate = int(file_size * 8 / duration) if duration > 0 else 0
                    
                    # Compression ratio
                    uncompressed_bitrate = sample_rate * bits_per_sample * channels
                    compression_ratio = uncompressed_bitrate / bitrate if bitrate > 0 else 2.0
                    
                    return CodecParameters(
                        format=AudioFormat.FLAC,
                        codec_type=CodecType.LOSSLESS,
                        bitrate=bitrate,
                        sample_rate=sample_rate,
                        bit_depth=bits_per_sample,
                        channels=channels,
                        compression_ratio=compression_ratio,
                        frame_size=max_block_size,
                        custom_params={
                            "min_block_size": min_block_size,
                            "max_block_size": max_block_size,
                            "min_frame_size": min_frame_size,
                            "max_frame_size": max_frame_size,
                            "total_samples": total_samples
                        }
                    )
            else:
                # Skip other blocks
                self.parser.seek(block_size, 1)
                
            if is_last:
                break
                
        return CodecParameters(
            format=AudioFormat.FLAC,
            codec_type=CodecType.LOSSLESS
        )
        
    def _extract_ogg_parameters(self) -> CodecParameters:
        """Extract Ogg Vorbis parameters"""
        self.parser.seek(0)
        
        # Find first Ogg page
        if self.parser.read(4) != b"OggS":
            return CodecParameters(
                format=AudioFormat.OGG,
                codec_type=CodecType.LOSSY
            )
            
        # Read page header
        self.parser.seek(22, 1)  # Skip to segment count
        segments = self.parser.read_uint8()
        segment_table = self.parser.read(segments)
        
        # Read Vorbis header
        vorbis_header = self.parser.read(7)
        if vorbis_header[1:7] != b"vorbis":
            return CodecParameters(
                format=AudioFormat.OGG,
                codec_type=CodecType.LOSSY
            )
            
        # Read identification header
        version = self.parser.read_uint32_le()
        channels = self.parser.read_uint8()
        sample_rate = self.parser.read_uint32_le()
        bitrate_max = self.parser.read_uint32_le()
        bitrate_nominal = self.parser.read_uint32_le()
        bitrate_min = self.parser.read_uint32_le()
        blocksize = self.parser.read_uint8()
        
        blocksize_0 = 1 << (blocksize & 0x0F)
        blocksize_1 = 1 << ((blocksize & 0xF0) >> 4)
        
        # Use nominal bitrate if available
        bitrate = bitrate_nominal if bitrate_nominal > 0 else bitrate_max
        
        return CodecParameters(
            format=AudioFormat.OGG,
            codec_type=CodecType.LOSSY,
            bitrate=bitrate,
            sample_rate=sample_rate,
            bit_depth=16,  # Vorbis typically decodes to 16-bit
            channels=channels,
            compression_ratio=10.0,  # Typical Vorbis compression
            frame_size=blocksize_1,
            custom_params={
                "version": version,
                "blocksize_0": blocksize_0,
                "blocksize_1": blocksize_1,
                "bitrate_min": bitrate_min,
                "bitrate_max": bitrate_max
            }
        )
        
    def _extract_opus_parameters(self) -> CodecParameters:
        """Extract Opus parameters"""
        self.parser.seek(0)
        
        # Find OpusHead in Ogg container
        found_opus = False
        while self.parser.tell() < self.parser.file_size - 19:
            if self.parser.read(8) == b"OpusHead":
                self.parser.seek(-8, 1)
                found_opus = True
                break
                
        if not found_opus:
            return CodecParameters(
                format=AudioFormat.OPUS,
                codec_type=CodecType.LOSSY
            )
            
        # Read OpusHead
        magic = self.parser.read(8)
        version = self.parser.read_uint8()
        channels = self.parser.read_uint8()
        pre_skip = self.parser.read_uint16_le()
        sample_rate = self.parser.read_uint32_le()
        output_gain = self.parser.read_uint16_le()
        mapping_family = self.parser.read_uint8()
        
        # Opus always decodes at 48kHz internally
        internal_rate = 48000
        
        return CodecParameters(
            format=AudioFormat.OPUS,
            codec_type=CodecType.LOSSY,
            bitrate=128000,  # Typical Opus bitrate
            sample_rate=sample_rate if sample_rate > 0 else internal_rate,
            bit_depth=16,
            channels=channels,
            compression_ratio=6.0,  # Typical Opus compression
            frame_size=960,  # 20ms at 48kHz
            custom_params={
                "version": version,
                "pre_skip": pre_skip,
                "output_gain": output_gain,
                "mapping_family": mapping_family,
                "internal_rate": internal_rate
            }
        )
        
    def _extract_wav_parameters(self) -> CodecParameters:
        """Extract WAV parameters"""
        self.parser.seek(0)
        
        # Read RIFF header
        riff_header = self.parser.read(12)
        if riff_header[:4] != b"RIFF" or riff_header[8:12] != b"WAVE":
            return CodecParameters(
                format=AudioFormat.WAV,
                codec_type=CodecType.UNCOMPRESSED
            )
            
        # Find fmt chunk
        while self.parser.tell() < self.parser.file_size:
            chunk_header = self.parser.read(8)
            if len(chunk_header) < 8:
                break
                
            chunk_id = chunk_header[:4]
            chunk_size = struct.unpack("<I", chunk_header[4:8])[0]
            
            if chunk_id == b"fmt ":
                fmt_data = self.parser.read(min(chunk_size, 16))
                if len(fmt_data) >= 16:
                    audio_format = struct.unpack("<H", fmt_data[0:2])[0]
                    channels = struct.unpack("<H", fmt_data[2:4])[0]
                    sample_rate = struct.unpack("<I", fmt_data[4:8])[0]
                    byte_rate = struct.unpack("<I", fmt_data[8:12])[0]
                    block_align = struct.unpack("<H", fmt_data[12:14])[0]
                    bits_per_sample = struct.unpack("<H", fmt_data[14:16])[0]
                    
                    bitrate = byte_rate * 8
                    
                    codec_type = CodecType.UNCOMPRESSED if audio_format == 1 else CodecType.LOSSY
                    
                    return CodecParameters(
                        format=AudioFormat.WAV,
                        codec_type=codec_type,
                        bitrate=bitrate,
                        sample_rate=sample_rate,
                        bit_depth=bits_per_sample,
                        channels=channels,
                        compression_ratio=1.0 if audio_format == 1 else 4.0,
                        frame_size=block_align,
                        custom_params={
                            "audio_format": audio_format,
                            "format_name": "PCM" if audio_format == 1 else f"Format{audio_format}",
                            "block_align": block_align,
                            "byte_rate": byte_rate
                        }
                    )
                break
            else:
                # Skip chunk
                self.parser.seek(chunk_size, 1)
                
        return CodecParameters(
            format=AudioFormat.WAV,
            codec_type=CodecType.UNCOMPRESSED
        )