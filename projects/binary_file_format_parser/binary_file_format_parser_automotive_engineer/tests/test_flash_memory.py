"""Tests for ECU flash memory layout analysis."""

import pytest
from pybinparser.flash_memory import FlashMemoryAnalyzer, MemoryRegion, MemoryRegionType
import struct


class TestMemoryRegion:
    """Test MemoryRegion functionality."""

    def test_region_creation(self):
        """Test creating a memory region."""
        region = MemoryRegion(
            name="Bootloader",
            start_address=0x08000000,
            end_address=0x08010000,
            size=0x10000,
            region_type=MemoryRegionType.BOOTLOADER,
            executable=True,
        )
        assert region.name == "Bootloader"
        assert region.start_address == 0x08000000
        assert region.size == 0x10000
        assert region.executable is True

    def test_region_validation(self):
        """Test region address validation."""
        # End address must be greater than start
        with pytest.raises(ValueError):
            MemoryRegion(
                name="Invalid",
                start_address=0x1000,
                end_address=0x1000,
                size=0,
                region_type=MemoryRegionType.DATA,
            )

    def test_region_size_calculation(self):
        """Test automatic size calculation."""
        region = MemoryRegion(
            name="Test",
            start_address=0x1000,
            end_address=0x2000,
            size=0,  # Should be calculated
            region_type=MemoryRegionType.DATA,
        )
        assert region.size == 0x1000

    def test_contains_address(self):
        """Test address containment check."""
        region = MemoryRegion(
            name="Test",
            start_address=0x1000,
            end_address=0x2000,
            size=0x1000,
            region_type=MemoryRegionType.DATA,
        )

        assert region.contains_address(0x1000) is True
        assert region.contains_address(0x1500) is True
        assert region.contains_address(0x1FFF) is True
        assert region.contains_address(0x2000) is False  # End is exclusive
        assert region.contains_address(0x0FFF) is False

    def test_get_offset(self):
        """Test getting offset within region."""
        region = MemoryRegion(
            name="Test",
            start_address=0x1000,
            end_address=0x2000,
            size=0x1000,
            region_type=MemoryRegionType.DATA,
        )

        assert region.get_offset(0x1000) == 0
        assert region.get_offset(0x1500) == 0x500

        with pytest.raises(ValueError):
            region.get_offset(0x3000)


class TestFlashMemoryAnalyzer:
    """Test FlashMemoryAnalyzer functionality."""

    def test_analyzer_creation(self):
        """Test creating flash memory analyzer."""
        analyzer = FlashMemoryAnalyzer()
        assert len(analyzer.regions) == 0
        assert analyzer.memory_data is None
        assert analyzer.base_address == 0

    def test_add_region(self):
        """Test adding memory regions."""
        analyzer = FlashMemoryAnalyzer()

        region1 = MemoryRegion(
            name="Region1",
            start_address=0x0000,
            end_address=0x1000,
            size=0x1000,
            region_type=MemoryRegionType.BOOTLOADER,
        )
        analyzer.add_region(region1)
        assert len(analyzer.regions) == 1

        # Add non-overlapping region
        region2 = MemoryRegion(
            name="Region2",
            start_address=0x1000,
            end_address=0x2000,
            size=0x1000,
            region_type=MemoryRegionType.APPLICATION,
        )
        analyzer.add_region(region2)
        assert len(analyzer.regions) == 2

        # Regions should be sorted by start address
        assert analyzer.regions[0].name == "Region1"
        assert analyzer.regions[1].name == "Region2"

    def test_add_overlapping_region(self):
        """Test that overlapping regions are rejected."""
        analyzer = FlashMemoryAnalyzer()

        region1 = MemoryRegion(
            name="Region1",
            start_address=0x1000,
            end_address=0x2000,
            size=0x1000,
            region_type=MemoryRegionType.DATA,
        )
        analyzer.add_region(region1)

        # Try to add overlapping region
        region2 = MemoryRegion(
            name="Region2",
            start_address=0x1500,
            end_address=0x2500,
            size=0x1000,
            region_type=MemoryRegionType.DATA,
        )

        with pytest.raises(ValueError):
            analyzer.add_region(region2)

    def test_analyze_memory_dump_bootloader(self):
        """Test identifying bootloader region."""
        analyzer = FlashMemoryAnalyzer()

        # Create memory with bootloader signature
        memory = b"BOOT" + b"\x00" * 0x1000

        regions = analyzer.analyze_memory_dump(memory, base_address=0x08000000)

        # Should find at least one bootloader region
        bootloader_regions = [
            r for r in regions if r.region_type == MemoryRegionType.BOOTLOADER
        ]
        assert len(bootloader_regions) > 0
        assert bootloader_regions[0].executable is True

    def test_analyze_memory_dump_arm_vectors(self):
        """Test identifying ARM interrupt vectors."""
        analyzer = FlashMemoryAnalyzer()

        # Create ARM Cortex-M vector table
        # Initial SP in RAM range, reset handler in flash range
        sp = 0x20010000  # RAM address
        reset = 0x08000400  # Flash address

        vectors = struct.pack("<II", sp, reset)
        memory = vectors + b"\x00" * 0x1000

        regions = analyzer.analyze_memory_dump(memory, base_address=0x08000000)

        # Should identify interrupt vector table
        vector_regions = [
            r
            for r in regions
            if "interrupt" in r.name.lower()
            or r.region_type == MemoryRegionType.BOOTLOADER
        ]
        assert len(vector_regions) > 0

    def test_analyze_memory_dump_multiple_regions(self):
        """Test identifying multiple region types."""
        analyzer = FlashMemoryAnalyzer()

        # Create memory with multiple regions
        memory = (
            b"BOOT"
            + b"\x00" * 0x100  # Bootloader
            + b"APP\x00"
            + b"\x00" * 0x100  # Application
            + b"CAL\x00"
            + b"\x00" * 0x100  # Calibration
            + b"CRC32"
            + b"\x00" * 0x100  # Checksum
        )

        regions = analyzer.analyze_memory_dump(memory)

        # Should find different region types
        region_types = {r.region_type for r in regions}
        assert MemoryRegionType.BOOTLOADER in region_types
        assert MemoryRegionType.APPLICATION in region_types
        assert MemoryRegionType.CALIBRATION in region_types
        assert MemoryRegionType.CHECKSUM in region_types

    def test_calculate_checksum_crc32(self):
        """Test CRC32 checksum calculation."""
        analyzer = FlashMemoryAnalyzer()

        # Set up memory and region
        test_data = b"Hello, World!"
        analyzer.memory_data = test_data
        analyzer.base_address = 0

        region = MemoryRegion(
            name="TestRegion",
            start_address=0,
            end_address=len(test_data),
            size=len(test_data),
            region_type=MemoryRegionType.DATA,
        )
        analyzer.add_region(region)

        # Calculate checksum
        checksum = analyzer.calculate_checksum(region, algorithm="crc32")

        # Verify it's a valid CRC32
        assert isinstance(checksum, int)
        assert 0 <= checksum <= 0xFFFFFFFF

    def test_calculate_checksum_sum32(self):
        """Test 32-bit sum checksum calculation."""
        analyzer = FlashMemoryAnalyzer()

        # Set up memory with known data
        data = struct.pack("<IIII", 0x12345678, 0x9ABCDEF0, 0x11111111, 0x22222222)
        analyzer.memory_data = data
        analyzer.base_address = 0

        region = MemoryRegion(
            name="Test",
            start_address=0,
            end_address=len(data),
            size=len(data),
            region_type=MemoryRegionType.DATA,
        )
        analyzer.add_region(region)

        checksum = analyzer.calculate_checksum(region, algorithm="sum32")
        expected = (0x12345678 + 0x9ABCDEF0 + 0x11111111 + 0x22222222) & 0xFFFFFFFF
        assert checksum == expected

    def test_calculate_checksum_xor32(self):
        """Test 32-bit XOR checksum calculation."""
        analyzer = FlashMemoryAnalyzer()

        # Set up memory
        data = struct.pack("<II", 0x12345678, 0x87654321)
        analyzer.memory_data = data
        analyzer.base_address = 0

        region = MemoryRegion(
            name="Test",
            start_address=0,
            end_address=len(data),
            size=len(data),
            region_type=MemoryRegionType.DATA,
        )
        analyzer.add_region(region)

        checksum = analyzer.calculate_checksum(region, algorithm="xor32")
        expected = 0x12345678 ^ 0x87654321
        assert checksum == expected

    def test_verify_checksums(self):
        """Test verifying checksum regions."""
        analyzer = FlashMemoryAnalyzer()

        # Create memory with data and checksum
        data = b"TEST_DATA_1234"
        # Calculate expected CRC32
        import binascii

        expected_crc = binascii.crc32(data) & 0xFFFFFFFF
        checksum_bytes = struct.pack("<I", expected_crc)

        memory = data + checksum_bytes
        analyzer.memory_data = memory
        analyzer.base_address = 0

        # Add data region
        data_region = MemoryRegion(
            name="Data",
            start_address=0,
            end_address=len(data),
            size=len(data),
            region_type=MemoryRegionType.DATA,
        )
        analyzer.add_region(data_region)

        # Add checksum region
        checksum_region = MemoryRegion(
            name="Checksum",
            start_address=len(data),
            end_address=len(memory),
            size=4,
            region_type=MemoryRegionType.CHECKSUM,
        )
        analyzer.add_region(checksum_region)

        # Verify checksums
        results = analyzer.verify_checksums()
        assert "Checksum" in results
        assert results["Checksum"] is True

    def test_find_region_by_address(self):
        """Test finding region by address."""
        analyzer = FlashMemoryAnalyzer()

        # Add multiple regions
        regions = [
            MemoryRegion(
                name="Region1",
                start_address=0x0000,
                end_address=0x1000,
                size=0x1000,
                region_type=MemoryRegionType.BOOTLOADER,
            ),
            MemoryRegion(
                name="Region2",
                start_address=0x1000,
                end_address=0x2000,
                size=0x1000,
                region_type=MemoryRegionType.APPLICATION,
            ),
            MemoryRegion(
                name="Region3",
                start_address=0x2000,
                end_address=0x3000,
                size=0x1000,
                region_type=MemoryRegionType.DATA,
            ),
        ]

        for region in regions:
            analyzer.add_region(region)

        # Test finding regions
        assert analyzer.find_region_by_address(0x0500).name == "Region1"
        assert analyzer.find_region_by_address(0x1500).name == "Region2"
        assert analyzer.find_region_by_address(0x2500).name == "Region3"
        assert analyzer.find_region_by_address(0x3500) is None

    def test_export_memory_map(self):
        """Test exporting memory map."""
        analyzer = FlashMemoryAnalyzer()
        analyzer.base_address = 0x08000000

        # Add some regions
        analyzer.add_region(
            MemoryRegion(
                name="Bootloader",
                start_address=0x08000000,
                end_address=0x08010000,
                size=0x10000,
                region_type=MemoryRegionType.BOOTLOADER,
                executable=True,
            )
        )

        analyzer.add_region(
            MemoryRegion(
                name="Application",
                start_address=0x08010000,
                end_address=0x08080000,
                size=0x70000,
                region_type=MemoryRegionType.APPLICATION,
                executable=True,
                writable=False,
            )
        )

        analyzer.add_region(
            MemoryRegion(
                name="Calibration",
                start_address=0x08080000,
                end_address=0x08090000,
                size=0x10000,
                region_type=MemoryRegionType.CALIBRATION,
                writable=True,
            )
        )

        # Export map
        memory_map = analyzer.export_memory_map()

        # Verify output contains expected information
        assert "ECU Memory Map" in memory_map
        assert "Base Address: 0x08000000" in memory_map
        assert "Total Regions: 3" in memory_map
        assert "Bootloader" in memory_map
        assert "Application" in memory_map
        assert "Calibration" in memory_map
        assert "X" in memory_map  # Executable flag
        assert "W" in memory_map  # Writable flag
