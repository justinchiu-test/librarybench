"""Metadata tag parsing module"""

from typing import Dict, List, Optional, Union, Tuple
import struct
from enum import Enum
from pydantic import BaseModel, Field
from .core import BinaryParser, AudioFormat


class TagType(str, Enum):
    """Metadata tag types"""
    
    ID3V1 = "id3v1"
    ID3V2 = "id3v2"
    VORBIS_COMMENT = "vorbis_comment"
    APE = "ape"
    FLAC = "flac"
    MP4 = "mp4"
    CUSTOM = "custom"


class MetadataTag(BaseModel):
    """Represents a metadata tag"""
    
    tag_type: TagType = Field(description="Type of metadata tag")
    key: str = Field(description="Tag key/name")
    value: Union[str, bytes, int] = Field(description="Tag value")
    language: Optional[str] = Field(None, description="Language code if applicable")
    description: Optional[str] = Field(None, description="Tag description")


class ArtworkInfo(BaseModel):
    """Embedded artwork information"""
    
    mime_type: str = Field(description="MIME type of the image")
    picture_type: str = Field(description="Picture type (cover, artist, etc.)")
    description: str = Field(default="", description="Picture description")
    data: bytes = Field(description="Image data")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")


class MetadataParser:
    """Parses metadata tags from audio files"""
    
    # ID3v1 genres
    ID3V1_GENRES = [
        "Blues", "Classic Rock", "Country", "Dance", "Disco", "Funk", "Grunge",
        "Hip-Hop", "Jazz", "Metal", "New Age", "Oldies", "Other", "Pop", "R&B",
        "Rap", "Reggae", "Rock", "Techno", "Industrial", "Alternative", "Ska",
        "Death Metal", "Pranks", "Soundtrack", "Euro-Techno", "Ambient",
        "Trip-Hop", "Vocal", "Jazz+Funk", "Fusion", "Trance", "Classical",
        "Instrumental", "Acid", "House", "Game", "Sound Clip", "Gospel",
        "Noise", "AlternRock", "Bass", "Soul", "Punk", "Space", "Meditative",
        "Instrumental Pop", "Instrumental Rock", "Ethnic", "Gothic", "Darkwave",
        "Techno-Industrial", "Electronic", "Pop-Folk", "Eurodance", "Dream",
        "Southern Rock", "Comedy", "Cult", "Gangsta", "Top 40", "Christian Rap",
        "Pop/Funk", "Jungle", "Native American", "Cabaret", "New Wave",
        "Psychadelic", "Rave", "Showtunes", "Trailer", "Lo-Fi", "Tribal",
        "Acid Punk", "Acid Jazz", "Polka", "Retro", "Musical", "Rock & Roll",
        "Hard Rock"
    ]
    
    def __init__(self, parser: BinaryParser):
        """Initialize metadata parser"""
        self.parser = parser
        self._tags: List[MetadataTag] = []
        self._artwork: List[ArtworkInfo] = []
        
    def parse_all_tags(self, format_type: AudioFormat) -> Dict[str, List[MetadataTag]]:
        """Parse all metadata tags from file"""
        self._tags = []
        self._artwork = []
        
        # Parse based on format
        if format_type == AudioFormat.MP3:
            self._parse_id3v1()
            self._parse_id3v2()
            self._parse_ape_tags()
        elif format_type == AudioFormat.FLAC:
            self._parse_flac_metadata()
        elif format_type == AudioFormat.OGG or format_type == AudioFormat.OPUS:
            self._parse_vorbis_comments()
        elif format_type == AudioFormat.MP4 or format_type == AudioFormat.AAC:
            self._parse_mp4_metadata()
            
        # Organize tags by type
        tags_by_type: Dict[str, List[MetadataTag]] = {}
        for tag in self._tags:
            tag_type = tag.tag_type.value
            if tag_type not in tags_by_type:
                tags_by_type[tag_type] = []
            tags_by_type[tag_type].append(tag)
            
        return tags_by_type
        
    def get_artwork(self) -> List[ArtworkInfo]:
        """Get all embedded artwork"""
        return self._artwork
        
    def _parse_id3v1(self) -> None:
        """Parse ID3v1 tags from end of file"""
        # ID3v1 is always at the last 128 bytes
        if self.parser.file_size < 128:
            return
            
        self.parser.seek(-128, 2)  # Seek from end
        tag_data = self.parser.read(128)
        
        if tag_data[:3] != b"TAG":
            return
            
        # Parse ID3v1 fields
        title = tag_data[3:33].rstrip(b"\x00").decode("latin-1", errors="ignore")
        artist = tag_data[33:63].rstrip(b"\x00").decode("latin-1", errors="ignore")
        album = tag_data[63:93].rstrip(b"\x00").decode("latin-1", errors="ignore")
        year = tag_data[93:97].rstrip(b"\x00").decode("latin-1", errors="ignore")
        comment = tag_data[97:127].rstrip(b"\x00").decode("latin-1", errors="ignore")
        genre_idx = tag_data[127]
        
        # Add tags
        if title:
            self._tags.append(MetadataTag(tag_type=TagType.ID3V1, key="title", value=title))
        if artist:
            self._tags.append(MetadataTag(tag_type=TagType.ID3V1, key="artist", value=artist))
        if album:
            self._tags.append(MetadataTag(tag_type=TagType.ID3V1, key="album", value=album))
        if year:
            self._tags.append(MetadataTag(tag_type=TagType.ID3V1, key="year", value=year))
        if comment:
            # Check for track number in comment (ID3v1.1)
            # Check if comment field has track number in last two bytes
            comment_raw = tag_data[97:127]
            if len(comment_raw) >= 2 and comment_raw[-2] == 0 and comment_raw[-1] != 0:
                track = comment_raw[-1]
                comment = comment_raw[:-2].rstrip(b"\x00").decode("latin-1", errors="ignore")
                self._tags.append(MetadataTag(tag_type=TagType.ID3V1, key="track", value=str(track)))
            if comment:
                self._tags.append(MetadataTag(tag_type=TagType.ID3V1, key="comment", value=comment))
        if genre_idx < len(self.ID3V1_GENRES):
            self._tags.append(MetadataTag(tag_type=TagType.ID3V1, key="genre", value=self.ID3V1_GENRES[genre_idx]))
            
    def _parse_id3v2(self) -> None:
        """Parse ID3v2 tags from beginning of file"""
        self.parser.seek(0)
        header = self.parser.read(10)
        
        if header[:3] != b"ID3":
            return
            
        # Parse header
        version = (header[3], header[4])
        flags = header[5]
        size = ((header[6] & 0x7F) << 21) | ((header[7] & 0x7F) << 14) | \
               ((header[8] & 0x7F) << 7) | (header[9] & 0x7F)
               
        # Read tag data
        tag_data = self.parser.read(size)
        offset = 0
        
        while offset < len(tag_data) - 10:
            if version[0] == 3 or version[0] == 4:  # ID3v2.3 or ID3v2.4
                # Frame header
                frame_id = tag_data[offset:offset+4].decode("ascii", errors="ignore")
                if frame_id == "\x00\x00\x00\x00":
                    break
                    
                frame_size = struct.unpack(">I", tag_data[offset+4:offset+8])[0]
                if version[0] == 4:  # Synchsafe in v2.4
                    frame_size = ((frame_size & 0x7F000000) >> 3) | \
                                ((frame_size & 0x007F0000) >> 2) | \
                                ((frame_size & 0x00007F00) >> 1) | \
                                (frame_size & 0x0000007F)
                                
                frame_flags = struct.unpack(">H", tag_data[offset+8:offset+10])[0]
                
                if offset + 10 + frame_size > len(tag_data):
                    break
                    
                frame_data = tag_data[offset+10:offset+10+frame_size]
                offset += 10 + frame_size
                
                # Parse frame content
                self._parse_id3v2_frame(frame_id, frame_data, version)
                
            elif version[0] == 2:  # ID3v2.2
                # Frame header (smaller)
                frame_id = tag_data[offset:offset+3].decode("ascii", errors="ignore")
                if frame_id == "\x00\x00\x00":
                    break
                    
                frame_size = struct.unpack(">I", b"\x00" + tag_data[offset+3:offset+6])[0]
                
                if offset + 6 + frame_size > len(tag_data):
                    break
                    
                frame_data = tag_data[offset+6:offset+6+frame_size]
                offset += 6 + frame_size
                
                # Convert v2.2 frame IDs to v2.3/v2.4 equivalents
                frame_id_map = {
                    "TT2": "TIT2", "TP1": "TPE1", "TAL": "TALB",
                    "TYE": "TYER", "TCO": "TCON", "TRK": "TRCK",
                    "PIC": "APIC", "COM": "COMM"
                }
                frame_id = frame_id_map.get(frame_id, frame_id)
                
                self._parse_id3v2_frame(frame_id, frame_data, version)
            else:
                break
                
    def _parse_id3v2_frame(self, frame_id: str, frame_data: bytes, version: Tuple[int, int]) -> None:
        """Parse individual ID3v2 frame"""
        if not frame_data:
            return
            
        # Text frames
        if frame_id.startswith("T") and frame_id != "TXXX":
            encoding = frame_data[0] if frame_data else 0
            text = self._decode_id3_string(frame_data[1:], encoding)
            
            # Map frame IDs to tag keys
            key_map = {
                "TIT2": "title", "TPE1": "artist", "TALB": "album",
                "TYER": "year", "TDRC": "year", "TCON": "genre",
                "TRCK": "track", "TPE2": "albumartist", "TPOS": "disc",
                "TIT1": "grouping", "TIT3": "subtitle", "TPE3": "conductor",
                "TPE4": "remixer", "TCOM": "composer", "TEXT": "lyricist",
                "TLAN": "language", "TMOO": "mood", "TBPM": "bpm",
                "TCOP": "copyright", "TPUB": "publisher", "TENC": "encoder",
                "TSSE": "encoding_settings", "TSRC": "isrc"
            }
            
            key = key_map.get(frame_id, frame_id.lower())
            if text:
                self._tags.append(MetadataTag(tag_type=TagType.ID3V2, key=key, value=text))
                
        # Comment frame
        elif frame_id == "COMM":
            if len(frame_data) >= 4:
                encoding = frame_data[0]
                language = frame_data[1:4].decode("ascii", errors="ignore")
                
                # Find null terminator for description
                desc_end = frame_data.find(b"\x00\x00" if encoding in [1, 2] else b"\x00", 4)
                if desc_end == -1:
                    desc_end = len(frame_data)
                    
                description = self._decode_id3_string(frame_data[4:desc_end], encoding)
                text = self._decode_id3_string(frame_data[desc_end+1:], encoding)
                
                if text:
                    self._tags.append(MetadataTag(
                        tag_type=TagType.ID3V2,
                        key="comment",
                        value=text,
                        language=language,
                        description=description
                    ))
                    
        # Picture frame
        elif frame_id == "APIC":
            self._parse_apic_frame(frame_data)
            
        # User-defined text frame
        elif frame_id == "TXXX":
            if len(frame_data) >= 1:
                encoding = frame_data[0]
                # Find null terminator for description
                desc_end = frame_data.find(b"\x00\x00" if encoding in [1, 2] else b"\x00", 1)
                if desc_end == -1:
                    desc_end = len(frame_data)
                    
                description = self._decode_id3_string(frame_data[1:desc_end], encoding)
                value = self._decode_id3_string(frame_data[desc_end+1:], encoding)
                
                if description and value:
                    self._tags.append(MetadataTag(
                        tag_type=TagType.ID3V2,
                        key=f"txxx:{description}",
                        value=value
                    ))
                    
    def _parse_apic_frame(self, frame_data: bytes) -> None:
        """Parse APIC (attached picture) frame"""
        if len(frame_data) < 4:
            return
            
        encoding = frame_data[0]
        offset = 1
        
        # MIME type
        mime_end = frame_data.find(b"\x00", offset)
        if mime_end == -1:
            return
            
        mime_type = frame_data[offset:mime_end].decode("latin-1", errors="ignore")
        offset = mime_end + 1
        
        # Picture type
        if offset >= len(frame_data):
            return
        picture_type_byte = frame_data[offset]
        offset += 1
        
        # Description
        desc_terminator = b"\x00\x00" if encoding in [1, 2] else b"\x00"
        desc_end = frame_data.find(desc_terminator, offset)
        if desc_end == -1:
            desc_end = len(frame_data)
            
        description = self._decode_id3_string(frame_data[offset:desc_end], encoding)
        offset = desc_end + len(desc_terminator)
        
        # Picture data
        if offset < len(frame_data):
            picture_data = frame_data[offset:]
            
            # Picture type names
            picture_types = [
                "Other", "File icon", "Other file icon", "Cover (front)",
                "Cover (back)", "Leaflet page", "Media", "Lead artist",
                "Artist", "Conductor", "Band", "Composer", "Lyricist",
                "Recording location", "During recording", "During performance",
                "Movie screen capture", "A bright colored fish", "Illustration",
                "Band logotype", "Publisher logotype"
            ]
            
            picture_type_name = picture_types[picture_type_byte] if picture_type_byte < len(picture_types) else "Other"
            
            self._artwork.append(ArtworkInfo(
                mime_type=mime_type,
                picture_type=picture_type_name,
                description=description,
                data=picture_data
            ))
            
    def _decode_id3_string(self, data: bytes, encoding: int) -> str:
        """Decode ID3 string based on encoding"""
        if not data:
            return ""
            
        # Remove null terminators
        if encoding == 0:  # ISO-8859-1
            data = data.rstrip(b"\x00")
            return data.decode("latin-1", errors="ignore")
        elif encoding == 1:  # UTF-16 with BOM
            data = data.rstrip(b"\x00\x00")
            return data.decode("utf-16", errors="ignore")
        elif encoding == 2:  # UTF-16BE
            data = data.rstrip(b"\x00\x00")
            return data.decode("utf-16be", errors="ignore")
        elif encoding == 3:  # UTF-8
            data = data.rstrip(b"\x00")
            return data.decode("utf-8", errors="ignore")
        else:
            return data.decode("latin-1", errors="ignore")
            
    def _parse_vorbis_comments(self) -> None:
        """Parse Vorbis comments from Ogg/FLAC files"""
        # This is simplified - in reality, we'd need to find the comment header
        # within the Ogg stream or FLAC metadata blocks
        pass
        
    def _parse_flac_metadata(self) -> None:
        """Parse FLAC metadata blocks"""
        self.parser.seek(0)
        
        # Check FLAC signature
        if self.parser.read(4) != b"fLaC":
            return
            
        # Read metadata blocks
        while True:
            block_header = self.parser.read(4)
            if len(block_header) < 4:
                break
                
            block_type = block_header[0] & 0x7F
            is_last = (block_header[0] & 0x80) != 0
            block_size = struct.unpack(">I", b"\x00" + block_header[1:4])[0]
            
            block_data = self.parser.read(block_size)
            
            if block_type == 4:  # VORBIS_COMMENT
                self._parse_vorbis_comment_block(block_data)
            elif block_type == 6:  # PICTURE
                self._parse_flac_picture_block(block_data)
                
            if is_last:
                break
                
    def _parse_vorbis_comment_block(self, data: bytes) -> None:
        """Parse Vorbis comment block"""
        offset = 0
        
        # Vendor string length
        if offset + 4 > len(data):
            return
        vendor_length = struct.unpack("<I", data[offset:offset+4])[0]
        offset += 4
        
        # Skip vendor string
        offset += vendor_length
        
        # Number of comments
        if offset + 4 > len(data):
            return
        num_comments = struct.unpack("<I", data[offset:offset+4])[0]
        offset += 4
        
        # Parse comments
        for _ in range(num_comments):
            if offset + 4 > len(data):
                break
                
            comment_length = struct.unpack("<I", data[offset:offset+4])[0]
            offset += 4
            
            if offset + comment_length > len(data):
                break
                
            comment = data[offset:offset+comment_length].decode("utf-8", errors="ignore")
            offset += comment_length
            
            # Split key=value
            if "=" in comment:
                key, value = comment.split("=", 1)
                self._tags.append(MetadataTag(
                    tag_type=TagType.VORBIS_COMMENT,
                    key=key.lower(),
                    value=value
                ))
                
    def _parse_flac_picture_block(self, data: bytes) -> None:
        """Parse FLAC picture block"""
        offset = 0
        
        # Picture type
        if offset + 4 > len(data):
            return
        picture_type = struct.unpack(">I", data[offset:offset+4])[0]
        offset += 4
        
        # MIME type length and string
        if offset + 4 > len(data):
            return
        mime_length = struct.unpack(">I", data[offset:offset+4])[0]
        offset += 4
        
        if offset + mime_length > len(data):
            return
        mime_type = data[offset:offset+mime_length].decode("ascii", errors="ignore")
        offset += mime_length
        
        # Description length and string
        if offset + 4 > len(data):
            return
        desc_length = struct.unpack(">I", data[offset:offset+4])[0]
        offset += 4
        
        if offset + desc_length > len(data):
            return
        description = data[offset:offset+desc_length].decode("utf-8", errors="ignore")
        offset += desc_length
        
        # Image dimensions
        if offset + 16 > len(data):
            return
        width = struct.unpack(">I", data[offset:offset+4])[0]
        height = struct.unpack(">I", data[offset+4:offset+8])[0]
        offset += 16  # Skip color depth and colors used
        
        # Picture data length and data
        if offset + 4 > len(data):
            return
        pic_length = struct.unpack(">I", data[offset:offset+4])[0]
        offset += 4
        
        if offset + pic_length > len(data):
            return
        picture_data = data[offset:offset+pic_length]
        
        # Picture type names (same as ID3v2)
        picture_types = [
            "Other", "File icon", "Other file icon", "Cover (front)",
            "Cover (back)", "Leaflet page", "Media", "Lead artist"
        ]
        
        picture_type_name = picture_types[picture_type] if picture_type < len(picture_types) else "Other"
        
        self._artwork.append(ArtworkInfo(
            mime_type=mime_type,
            picture_type=picture_type_name,
            description=description,
            data=picture_data,
            width=width,
            height=height
        ))
        
    def _parse_ape_tags(self) -> None:
        """Parse APE tags (often found in MP3 files)"""
        # APE tags can be at the end of the file
        if self.parser.file_size < 32:
            return
            
        self.parser.seek(-32, 2)  # Seek from end
        footer = self.parser.read(32)
        
        if footer[:8] != b"APETAGEX":
            return
            
        # Parse APE tag footer
        version = struct.unpack("<I", footer[8:12])[0]
        tag_size = struct.unpack("<I", footer[12:16])[0]
        item_count = struct.unpack("<I", footer[16:20])[0]
        
        # Read tag data
        self.parser.seek(-(tag_size + 32), 2)
        tag_data = self.parser.read(tag_size)
        
        offset = 0
        for _ in range(item_count):
            if offset + 8 > len(tag_data):
                break
                
            # Item header
            value_size = struct.unpack("<I", tag_data[offset:offset+4])[0]
            flags = struct.unpack("<I", tag_data[offset+4:offset+8])[0]
            offset += 8
            
            # Key (null-terminated)
            key_end = tag_data.find(b"\x00", offset)
            if key_end == -1:
                break
                
            key = tag_data[offset:key_end].decode("utf-8", errors="ignore")
            offset = key_end + 1
            
            # Value
            if offset + value_size > len(tag_data):
                break
                
            value = tag_data[offset:offset+value_size].decode("utf-8", errors="ignore")
            offset += value_size
            
            if key and value:
                self._tags.append(MetadataTag(
                    tag_type=TagType.APE,
                    key=key.lower(),
                    value=value
                ))
                
    def _parse_mp4_metadata(self) -> None:
        """Parse MP4/M4A metadata atoms"""
        # This is a simplified implementation
        # Full MP4 parsing would require navigating the atom structure
        pass
        
    def extract_custom_tags(self, patterns: List[Tuple[bytes, str]]) -> List[MetadataTag]:
        """Extract custom tags based on byte patterns"""
        custom_tags = []
        
        for pattern, tag_name in patterns:
            offset = 0
            while True:
                pos = self.parser.find_pattern(pattern, offset)
                if pos == -1:
                    break
                    
                # Read some context around the pattern
                self.parser.seek(max(0, pos - 16))
                context = self.parser.read(len(pattern) + 32)
                
                custom_tags.append(MetadataTag(
                    tag_type=TagType.CUSTOM,
                    key=tag_name,
                    value=context.hex()
                ))
                
                offset = pos + len(pattern)
                
        return custom_tags