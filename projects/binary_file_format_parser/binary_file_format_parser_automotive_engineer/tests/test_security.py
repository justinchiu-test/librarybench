"""Tests for vehicle-specific encryption key derivation."""

import pytest
from pybinparser.security import SecurityKeyDeriver, SecurityAlgorithm, SecurityLevel
import struct


class TestSecurityKeyDeriver:
    """Test SecurityKeyDeriver functionality."""

    def test_deriver_creation(self):
        """Test creating security key deriver."""
        deriver = SecurityKeyDeriver()
        assert len(deriver.algorithms) > 0
        assert SecurityAlgorithm.FIXED_BYTES in deriver.algorithms
        assert len(deriver.test_keys) > 0

    def test_fixed_bytes_algorithm_2byte(self):
        """Test fixed bytes algorithm with 2-byte seed."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">H", 0x1234)
        params = {"constant": 0x5678}

        key = deriver.derive_key(seed, SecurityAlgorithm.FIXED_BYTES, params=params)

        # Key should be seed XOR constant
        expected = struct.pack(">H", 0x1234 ^ 0x5678)
        assert key == expected

    def test_fixed_bytes_algorithm_4byte(self):
        """Test fixed bytes algorithm with 4-byte seed."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">I", 0x12345678)
        params = {"constant": 0x87654321}

        key = deriver.derive_key(seed, SecurityAlgorithm.FIXED_BYTES, params=params)

        expected = struct.pack(">I", 0x12345678 ^ 0x87654321)
        assert key == expected

    def test_fixed_bytes_algorithm_variable(self):
        """Test fixed bytes algorithm with variable length seed."""
        deriver = SecurityKeyDeriver()

        seed = bytes([0x11, 0x22, 0x33, 0x44, 0x55])
        params = {"pattern": [0xAA, 0xBB]}

        key = deriver.derive_key(seed, SecurityAlgorithm.FIXED_BYTES, params=params)

        expected = bytes(
            [
                0x11 ^ 0xAA,  # 0xBB
                0x22 ^ 0xBB,  # 0x99
                0x33 ^ 0xAA,  # 0x99
                0x44 ^ 0xBB,  # 0xFF
                0x55 ^ 0xAA,  # 0xFF
            ]
        )
        assert key == expected

    def test_xor_algorithm(self):
        """Test XOR-based algorithm."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">I", 0x12345678)
        params = {"mask1": 0x11111111, "mask2": 0x22222222}

        key = deriver.derive_key(seed, SecurityAlgorithm.XOR_OPERATION, params=params)

        # Two-stage XOR
        temp = 0x12345678 ^ 0x11111111
        expected_val = temp ^ 0x22222222
        expected = struct.pack(">I", expected_val)
        assert key == expected

    def test_bit_manipulation_algorithm(self):
        """Test bit manipulation algorithm."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">I", 0x12345678)
        params = {"rotate": 4}

        key = deriver.derive_key(
            seed, SecurityAlgorithm.BIT_MANIPULATION, params=params
        )

        # Rotate left by 4 bits
        rotated = ((0x12345678 << 4) | (0x12345678 >> 28)) & 0xFFFFFFFF
        # Swap bytes
        swapped = (
            ((rotated & 0xFF000000) >> 24)
            | ((rotated & 0x00FF0000) >> 8)
            | ((rotated & 0x0000FF00) << 8)
            | ((rotated & 0x000000FF) << 24)
        )

        expected = struct.pack(">I", swapped)
        assert key == expected

    def test_addition_algorithm(self):
        """Test addition-based algorithm."""
        deriver = SecurityKeyDeriver()

        # Test 4-byte seed
        seed = struct.pack(">I", 0xFFFFFF00)
        params = {"addend": 0x00000200}

        key = deriver.derive_key(seed, SecurityAlgorithm.ADDITION, params=params)

        expected = struct.pack(">I", 0x00000100)  # Wraps around
        assert key == expected

        # Test 2-byte seed
        seed = struct.pack(">H", 0x1000)
        params = {"addend": 0x0500}

        key = deriver.derive_key(seed, SecurityAlgorithm.ADDITION, params=params)

        expected = struct.pack(">H", 0x1500)
        assert key == expected

    def test_subtraction_algorithm(self):
        """Test subtraction-based algorithm."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">I", 0x12345678)
        params = {"subtrahend": 0x87654321}

        key = deriver.derive_key(seed, SecurityAlgorithm.SUBTRACTION, params=params)

        expected_val = (0x87654321 - 0x12345678) & 0xFFFFFFFF
        expected = struct.pack(">I", expected_val)
        assert key == expected

    def test_crc_algorithm(self):
        """Test CRC-based algorithm."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">I", 0x12345678)

        key = deriver.derive_key(
            seed, SecurityAlgorithm.CRC_BASED, SecurityLevel.PROGRAMMING
        )

        # Should return 4 bytes for 4-byte seed
        assert len(key) == 4

        # Test with 2-byte seed
        seed = struct.pack(">H", 0x1234)
        key = deriver.derive_key(seed, SecurityAlgorithm.CRC_BASED)
        assert len(key) == 2

    def test_hash_algorithm(self):
        """Test hash-based algorithm."""
        deriver = SecurityKeyDeriver()

        seed = bytes([0x01, 0x02, 0x03, 0x04])
        params = {"salt": b"TEST_SALT"}

        key = deriver.derive_key(
            seed, SecurityAlgorithm.HASH_BASED, SecurityLevel.DEVELOPMENT, params=params
        )

        # Should return same length as seed
        assert len(key) == len(seed)

        # Should be deterministic
        key2 = deriver.derive_key(
            seed, SecurityAlgorithm.HASH_BASED, SecurityLevel.DEVELOPMENT, params=params
        )
        assert key == key2

    def test_manufacturer_a_algorithm(self):
        """Test manufacturer A specific algorithm."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">I", 0x12345678)
        params = {"vin_constant": 0xABCDEF00}

        key = deriver.derive_key(seed, SecurityAlgorithm.MANUFACTURER_A, params=params)

        assert len(key) == 4

        # Should fail with wrong seed length
        with pytest.raises(ValueError):
            deriver.derive_key(bytes([0x01, 0x02]), SecurityAlgorithm.MANUFACTURER_A)

    def test_manufacturer_b_algorithm(self):
        """Test manufacturer B specific algorithm."""
        deriver = SecurityKeyDeriver()

        seed = bytes([0x10, 0x20, 0x30, 0x40])
        # Create a simple lookup table
        lookup_table = list(range(256))
        lookup_table[0x10] = 0xA0
        lookup_table[0x21] = 0xB1
        lookup_table[0x32] = 0xC2
        lookup_table[0x43] = 0xD3

        params = {"lookup_table": lookup_table}

        key = deriver.derive_key(seed, SecurityAlgorithm.MANUFACTURER_B, params=params)

        assert len(key) == len(seed)
        # Check transformations were applied
        assert key[0] == ((0xA0 << 4) | (0xA0 >> 4)) & 0xFF

    def test_manufacturer_c_algorithm(self):
        """Test manufacturer C specific algorithm."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">HH", 0x1234, 0x5678)
        params = {"rounds": 2}

        key = deriver.derive_key(seed, SecurityAlgorithm.MANUFACTURER_C, params=params)

        assert len(key) == 4

        # Should fail with wrong seed length
        with pytest.raises(ValueError):
            deriver.derive_key(bytes([0x01]), SecurityAlgorithm.MANUFACTURER_C)

    def test_validate_seed_key_pair(self):
        """Test validating seed-key pairs."""
        deriver = SecurityKeyDeriver()

        seed = struct.pack(">I", 0x12345678)
        params = {"constant": 0xABCDEF00}

        # Generate valid key
        valid_key = deriver.derive_key(
            seed, SecurityAlgorithm.FIXED_BYTES, params=params
        )

        # Should validate correctly
        assert (
            deriver.validate_seed_key_pair(
                seed, valid_key, SecurityAlgorithm.FIXED_BYTES, params=params
            )
            is True
        )

        # Should fail with wrong key
        wrong_key = struct.pack(">I", 0x00000000)
        assert (
            deriver.validate_seed_key_pair(
                seed, wrong_key, SecurityAlgorithm.FIXED_BYTES, params=params
            )
            is False
        )

        # Should fail with wrong algorithm
        assert (
            deriver.validate_seed_key_pair(
                seed, valid_key, SecurityAlgorithm.XOR_OPERATION, params=params
            )
            is False
        )

    def test_security_levels(self):
        """Test different security levels."""
        deriver = SecurityKeyDeriver()

        seed = bytes([0x11, 0x22, 0x33, 0x44])

        # Different levels should produce different keys
        key_prog = deriver.derive_key(
            seed, SecurityAlgorithm.HASH_BASED, SecurityLevel.PROGRAMMING
        )

        key_diag = deriver.derive_key(
            seed, SecurityAlgorithm.HASH_BASED, SecurityLevel.EXTENDED_DIAGNOSTICS
        )

        key_dev = deriver.derive_key(
            seed, SecurityAlgorithm.HASH_BASED, SecurityLevel.DEVELOPMENT
        )

        # All keys should be different
        assert key_prog != key_diag
        assert key_prog != key_dev
        assert key_diag != key_dev

    def test_unknown_algorithm(self):
        """Test handling unknown algorithm."""
        deriver = SecurityKeyDeriver()

        # Create an invalid algorithm
        with pytest.raises(ValueError):
            deriver.derive_key(
                bytes([0x01, 0x02]),
                "UNKNOWN_ALGORITHM",  # type: ignore
            )
