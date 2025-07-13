"""ECU flash memory layout analysis module."""

from typing import Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
import struct
import binascii


class MemoryRegionType(str, Enum):
    """Types of memory regions in ECU flash."""

    BOOTLOADER = "bootloader"
    APPLICATION = "application"
    CALIBRATION = "calibration"
    DATA = "data"
    RESERVED = "reserved"
    CHECKSUM = "checksum"
    SECURITY = "security"
    DIAGNOSTICS = "diagnostics"


class MemoryRegion(BaseModel):
    """Represents a region in ECU flash memory."""

    name: str
    start_address: int = Field(ge=0)
    end_address: int = Field(ge=0)
    size: int = Field(ge=0)
    region_type: MemoryRegionType
    checksum: Optional[str] = None
    version: Optional[str] = None
    writable: bool = False
    executable: bool = False
    description: Optional[str] = None

    @field_validator("end_address")
    @classmethod
    def validate_addresses(cls, v, info):
        if (
            info.data.get("start_address") is not None
            and v <= info.data["start_address"]
        ):
            raise ValueError("End address must be greater than start address")
        return v

    @model_validator(mode="after")
    def validate_size(self):
        if self.start_address is not None and self.end_address is not None:
            expected_size = self.end_address - self.start_address
            if self.size != expected_size:
                self.size = expected_size
        return self

    def contains_address(self, address: int) -> bool:
        """Check if address falls within this region."""
        return self.start_address <= address < self.end_address

    def get_offset(self, address: int) -> int:
        """Get offset of address within region."""
        if not self.contains_address(address):
            raise ValueError(f"Address 0x{address:X} not in region {self.name}")
        return address - self.start_address


class FlashMemoryAnalyzer:
    """Analyzer for ECU firmware structure and memory layout."""

    def __init__(self):
        self.regions: List[MemoryRegion] = []
        self.memory_data: Optional[bytes] = None
        self.base_address: int = 0

    def add_region(self, region: MemoryRegion, allow_overlap: bool = False) -> None:
        """Add a memory region to the layout."""
        if not allow_overlap:
            # Check for overlaps
            for existing in self.regions:
                if (
                    region.start_address < existing.end_address
                    and region.end_address > existing.start_address
                ):
                    raise ValueError(
                        f"Region {region.name} overlaps with {existing.name}"
                    )

        self.regions.append(region)
        self.regions.sort(key=lambda r: r.start_address)

    def analyze_memory_dump(
        self, data: bytes, base_address: int = 0
    ) -> List[MemoryRegion]:
        """Analyze memory dump and identify regions."""
        self.memory_data = data
        self.base_address = base_address
        identified_regions = []

        # Common patterns for different regions
        patterns = {
            "bootloader": [
                b"\x7c\x08\x02\xa6",  # PowerPC bootloader signature
                b"\x48\x8b\x05",  # x86_64 common start
                b"\x13\x00\x00\xea",  # ARM reset vector
                b"BOOT",  # ASCII marker
            ],
            "application": [
                b"APP\x00",
                b"APP",  # Without null terminator
                b"\xff\xff\xff\xff",  # Common app start marker
                b"MAIN",
            ],
            "calibration": [
                b"CAL\x00",
                b"CAL",  # Without null terminator
                b"CALB",
                b"\xca\x1b",  # Calibration magic number
            ],
            "checksum": [
                b"CRC32",
                b"CHK\x00",
                b"\xcc\xcc\xcc\xcc",  # Checksum placeholder
            ],
        }

        # Scan for known patterns
        for region_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                offset = 0
                while True:
                    pos = data.find(pattern, offset)
                    if pos == -1:
                        break

                    # Try to determine region boundaries
                    start = pos
                    end = self._find_region_end(data, pos, region_type)

                    if end > start:
                        region = MemoryRegion(
                            name=f"{region_type}_{pos:X}",
                            start_address=base_address + start,
                            end_address=base_address + end,
                            size=end - start,
                            region_type=MemoryRegionType(region_type),
                            executable=(region_type in ["bootloader", "application"]),
                            writable=(region_type in ["calibration", "data"]),
                        )
                        identified_regions.append(region)

                    offset = pos + 1

        # Analyze structure-based regions
        self._analyze_structured_regions(data, base_address, identified_regions)

        # Sort and merge overlapping regions
        identified_regions.sort(key=lambda r: r.start_address)
        merged_regions = self._merge_overlapping_regions(identified_regions)

        for region in merged_regions:
            try:
                self.add_region(region, allow_overlap=True)
            except ValueError:
                # Skip overlapping regions
                pass

        return self.regions

    def _find_region_end(self, data: bytes, start: int, region_type: str) -> int:
        """Find the end of a memory region."""
        # Simple heuristic: look for padding or next region marker
        pos = start + 4  # Skip marker
        max_size = {
            "bootloader": 0x10000,  # 64KB typical bootloader
            "application": 0x100000,  # 1MB typical application
            "calibration": 0x20000,  # 128KB typical calibration
            "checksum": 0x100,  # 256B checksum area
        }

        max_end = min(len(data), start + max_size.get(region_type, 0x10000))

        # Look for padding (continuous 0xFF or 0x00)
        padding_count = 0
        for i in range(pos, max_end):
            if data[i] in [0xFF, 0x00]:
                padding_count += 1
                if padding_count > 256:  # Found significant padding
                    return i - 256
            else:
                padding_count = 0

        return max_end

    def _analyze_structured_regions(
        self, data: bytes, base_address: int, regions: List[MemoryRegion]
    ) -> None:
        """Analyze structured regions like interrupt vectors."""
        # Check for interrupt vector table (ARM Cortex-M)
        if len(data) >= 8:
            # First word is initial stack pointer, should be RAM address
            sp = struct.unpack("<I", data[0:4])[0]
            # Second word is reset handler, should be in flash
            reset = struct.unpack("<I", data[4:8])[0]

            if 0x20000000 <= sp <= 0x20100000 and 0x08000000 <= reset <= 0x08100000:
                # Likely ARM Cortex-M vector table
                vector_size = 0x400  # 1KB typical vector table
                region = MemoryRegion(
                    name="interrupt_vectors",
                    start_address=base_address,
                    end_address=base_address + vector_size,
                    size=vector_size,
                    region_type=MemoryRegionType.BOOTLOADER,
                    executable=True,
                    description="ARM Cortex-M interrupt vector table",
                )
                regions.append(region)

    def _merge_overlapping_regions(
        self, regions: List[MemoryRegion]
    ) -> List[MemoryRegion]:
        """Merge overlapping regions."""
        if not regions:
            return []

        merged = []
        for region in regions:
            # Only merge if regions are of same type
            should_merge = False
            for existing in merged:
                if (
                    region.start_address <= existing.end_address
                    and region.end_address >= existing.start_address
                    and region.region_type == existing.region_type
                ):
                    # Extend existing region
                    existing.start_address = min(
                        existing.start_address, region.start_address
                    )
                    existing.end_address = max(existing.end_address, region.end_address)
                    existing.size = existing.end_address - existing.start_address
                    should_merge = True
                    break

            if not should_merge:
                merged.append(region)

        return merged

    def calculate_checksum(
        self, region: Union[MemoryRegion, str], algorithm: str = "crc32"
    ) -> Optional[int]:
        """Calculate checksum for a memory region."""
        if not self.memory_data:
            return None

        if isinstance(region, str):
            # Find region by name
            region_obj = None
            for r in self.regions:
                if r.name == region:
                    region_obj = r
                    break
            if not region_obj:
                raise ValueError(f"Region {region} not found")
            region = region_obj

        # Get region data
        start_offset = region.start_address - self.base_address
        end_offset = region.end_address - self.base_address

        if start_offset < 0 or end_offset > len(self.memory_data):
            raise ValueError("Region outside of loaded memory")

        region_data = self.memory_data[start_offset:end_offset]

        # Calculate checksum
        if algorithm == "crc32":
            return binascii.crc32(region_data) & 0xFFFFFFFF
        elif algorithm == "sum32":
            checksum = 0
            for i in range(0, len(region_data), 4):
                if i + 4 <= len(region_data):
                    checksum += struct.unpack("<I", region_data[i : i + 4])[0]
                    checksum &= 0xFFFFFFFF
            return checksum
        elif algorithm == "xor32":
            checksum = 0
            for i in range(0, len(region_data), 4):
                if i + 4 <= len(region_data):
                    checksum ^= struct.unpack("<I", region_data[i : i + 4])[0]
            return checksum
        else:
            raise ValueError(f"Unknown checksum algorithm: {algorithm}")

    def verify_checksums(self) -> Dict[str, bool]:
        """Verify all checksum regions."""
        results = {}

        for region in self.regions:
            if region.region_type == MemoryRegionType.CHECKSUM:
                # Find the region this checksum protects
                # (Usually the previous region)
                protected_region = None
                for i, r in enumerate(self.regions):
                    if r == region and i > 0:
                        protected_region = self.regions[i - 1]
                        break

                if protected_region:
                    try:
                        calc_checksum = self.calculate_checksum(protected_region)
                        # Read stored checksum
                        offset = region.start_address - self.base_address
                        stored_checksum = struct.unpack(
                            "<I", self.memory_data[offset : offset + 4]
                        )[0]
                        results[region.name] = calc_checksum == stored_checksum
                    except Exception:
                        results[region.name] = False

        return results

    def find_region_by_address(self, address: int) -> Optional[MemoryRegion]:
        """Find which region contains the given address."""
        for region in self.regions:
            if region.contains_address(address):
                return region
        return None

    def export_memory_map(self) -> str:
        """Export memory map as formatted string."""
        lines = ["ECU Memory Map", "=" * 80]
        lines.append(f"Base Address: 0x{self.base_address:08X}")
        lines.append(f"Total Regions: {len(self.regions)}")
        lines.append("")
        lines.append(
            f"{'Region Name':<20} {'Start':<12} {'End':<12} {'Size':<10} {'Type':<15} {'Flags'}"
        )
        lines.append("-" * 80)

        for region in self.regions:
            flags = []
            if region.writable:
                flags.append("W")
            if region.executable:
                flags.append("X")
            flags_str = "/".join(flags) if flags else "-"

            lines.append(
                f"{region.name:<20} "
                f"0x{region.start_address:08X}  "
                f"0x{region.end_address:08X}  "
                f"{region.size:8}  "
                f"{region.region_type.value:<15} "
                f"{flags_str}"
            )

        return "\n".join(lines)
