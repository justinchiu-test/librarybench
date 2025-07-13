"""PyBinParser - Audio Codec Analysis Tool"""

from .core import BinaryParser, AudioFormat
from .frame_detector import FrameDetector
from .codec_extractor import CodecParameterExtractor
from .format_detector import FormatDetector
from .metadata_parser import MetadataParser
from .psychoacoustic import PsychoacousticAnalyzer

__version__ = "0.1.0"
__all__ = [
    "BinaryParser",
    "AudioFormat",
    "FrameDetector",
    "CodecParameterExtractor",
    "FormatDetector",
    "MetadataParser",
    "PsychoacousticAnalyzer",
]