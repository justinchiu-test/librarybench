"""Vehicle-specific encryption key derivation module."""

from typing import Dict, Optional, Tuple
from enum import Enum
import struct
import hashlib
import binascii


class SecurityAlgorithm(str, Enum):
    """Common automotive security algorithms."""

    FIXED_BYTES = "fixed_bytes"
    XOR_OPERATION = "xor_operation"
    BIT_MANIPULATION = "bit_manipulation"
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    CRC_BASED = "crc_based"
    HASH_BASED = "hash_based"
    MANUFACTURER_A = "manufacturer_a"  # Proprietary algorithms
    MANUFACTURER_B = "manufacturer_b"
    MANUFACTURER_C = "manufacturer_c"


class SecurityLevel(str, Enum):
    """Security access levels."""

    PROGRAMMING = "programming"
    EXTENDED_DIAGNOSTICS = "extended_diagnostics"
    EOL_PROGRAMMING = "eol_programming"
    DEVELOPMENT = "development"


class SecurityKeyDeriver:
    """Derives security access keys using vehicle-specific algorithms."""

    def __init__(self):
        self.algorithms: Dict[str, callable] = {
            SecurityAlgorithm.FIXED_BYTES: self._fixed_bytes_algorithm,
            SecurityAlgorithm.XOR_OPERATION: self._xor_algorithm,
            SecurityAlgorithm.BIT_MANIPULATION: self._bit_manipulation_algorithm,
            SecurityAlgorithm.ADDITION: self._addition_algorithm,
            SecurityAlgorithm.SUBTRACTION: self._subtraction_algorithm,
            SecurityAlgorithm.CRC_BASED: self._crc_algorithm,
            SecurityAlgorithm.HASH_BASED: self._hash_algorithm,
            SecurityAlgorithm.MANUFACTURER_A: self._manufacturer_a_algorithm,
            SecurityAlgorithm.MANUFACTURER_B: self._manufacturer_b_algorithm,
            SecurityAlgorithm.MANUFACTURER_C: self._manufacturer_c_algorithm,
        }

        # Common fixed keys for testing (never use in production!)
        self.test_keys = {
            "default": [0x00, 0x00, 0x00, 0x00],
            "development": [0x12, 0x34, 0x56, 0x78],
            "service": [0xFF, 0xFF, 0xFF, 0xFF],
        }

    def derive_key(
        self,
        seed: bytes,
        algorithm: SecurityAlgorithm,
        level: SecurityLevel = SecurityLevel.EXTENDED_DIAGNOSTICS,
        params: Optional[Dict] = None,
    ) -> bytes:
        """Derive security key from seed using specified algorithm."""
        if algorithm not in self.algorithms:
            raise ValueError(f"Unknown security algorithm: {algorithm}")

        if params is None:
            params = {}

        # Add security level to params
        params["level"] = level

        return self.algorithms[algorithm](seed, params)

    def _fixed_bytes_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """Fixed bytes algorithm - XOR seed with constant."""
        # Common in older ECUs
        if len(seed) == 2:
            constant = params.get("constant", 0x1234)
            seed_val = struct.unpack(">H", seed)[0]
            key_val = seed_val ^ constant
            return struct.pack(">H", key_val)
        elif len(seed) == 4:
            constant = params.get("constant", 0x12345678)
            seed_val = struct.unpack(">I", seed)[0]
            key_val = seed_val ^ constant
            return struct.pack(">I", key_val)
        else:
            # Default: XOR with repeating pattern
            pattern = params.get("pattern", [0x12, 0x34, 0x56, 0x78])
            key = bytearray()
            for i, byte in enumerate(seed):
                key.append(byte ^ pattern[i % len(pattern)])
            return bytes(key)

    def _xor_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """XOR-based algorithm with multiple operations."""
        # Get XOR masks from params
        mask1 = params.get("mask1", 0x87654321)
        mask2 = params.get("mask2", 0x12345678)

        if len(seed) == 4:
            seed_val = struct.unpack(">I", seed)[0]
            # Two-stage XOR
            temp = seed_val ^ mask1
            key_val = temp ^ mask2
            return struct.pack(">I", key_val)
        else:
            # Byte-wise XOR
            key = bytearray()
            for i, byte in enumerate(seed):
                key.append(byte ^ (mask1 >> (8 * (i % 4)) & 0xFF))
            return bytes(key)

    def _bit_manipulation_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """Bit manipulation algorithm - rotate and swap."""
        rotate_bits = params.get("rotate", 3)

        if len(seed) == 4:
            seed_val = struct.unpack(">I", seed)[0]

            # Rotate left
            key_val = (
                (seed_val << rotate_bits) | (seed_val >> (32 - rotate_bits))
            ) & 0xFFFFFFFF

            # Swap bytes
            key_val = (
                ((key_val & 0xFF000000) >> 24)
                | ((key_val & 0x00FF0000) >> 8)
                | ((key_val & 0x0000FF00) << 8)
                | ((key_val & 0x000000FF) << 24)
            )

            return struct.pack(">I", key_val)
        else:
            # Byte-wise manipulation
            key = bytearray()
            for byte in seed:
                # Rotate each byte
                rotated = ((byte << rotate_bits) | (byte >> (8 - rotate_bits))) & 0xFF
                # Invert certain bits
                key.append(rotated ^ 0x55)
            return bytes(key)

    def _addition_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """Addition-based algorithm."""
        addend = params.get("addend", 0x11111111)

        if len(seed) == 4:
            seed_val = struct.unpack(">I", seed)[0]
            key_val = (seed_val + addend) & 0xFFFFFFFF
            return struct.pack(">I", key_val)
        elif len(seed) == 2:
            seed_val = struct.unpack(">H", seed)[0]
            key_val = (seed_val + (addend & 0xFFFF)) & 0xFFFF
            return struct.pack(">H", key_val)
        else:
            # Byte-wise addition with carry
            key = bytearray()
            carry = 0
            for byte in seed:
                result = byte + (addend & 0xFF) + carry
                key.append(result & 0xFF)
                carry = result >> 8
                addend >>= 8
            return bytes(key)

    def _subtraction_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """Subtraction-based algorithm."""
        subtrahend = params.get("subtrahend", 0x87654321)

        if len(seed) == 4:
            seed_val = struct.unpack(">I", seed)[0]
            key_val = (subtrahend - seed_val) & 0xFFFFFFFF
            return struct.pack(">I", key_val)
        else:
            # Inverse of addition
            return self._addition_algorithm(seed, {"addend": -subtrahend & 0xFFFFFFFF})

    def _crc_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """CRC-based key generation."""
        # Combine seed with additional data
        level = params.get("level", SecurityLevel.EXTENDED_DIAGNOSTICS)
        data = seed + level.value.encode()

        # Calculate CRC32
        crc = binascii.crc32(data) & 0xFFFFFFFF

        # Transform CRC based on seed length
        if len(seed) == 2:
            return struct.pack(">H", crc & 0xFFFF)
        elif len(seed) == 4:
            return struct.pack(">I", crc)
        else:
            # Return CRC bytes matching seed length
            crc_bytes = struct.pack(">I", crc)
            return crc_bytes[: len(seed)]

    def _hash_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """Hash-based algorithm using SHA256."""
        # Add salt based on security level
        level = params.get("level", SecurityLevel.EXTENDED_DIAGNOSTICS)
        salt = params.get("salt", b"ECU_SECURITY_2024")

        # Create hash input
        hash_input = seed + salt + level.value.encode()

        # Calculate SHA256
        hash_result = hashlib.sha256(hash_input).digest()

        # Return appropriate length
        return hash_result[: len(seed)]

    def _manufacturer_a_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """Manufacturer A specific algorithm."""
        # Example: Complex bit operations
        if len(seed) != 4:
            raise ValueError("Manufacturer A requires 4-byte seed")

        seed_val = struct.unpack(">I", seed)[0]

        # Step 1: XOR with VIN-based constant
        vin_constant = params.get("vin_constant", 0x5A5A5A5A)
        temp1 = seed_val ^ vin_constant

        # Step 2: Rotate and multiply
        temp2 = ((temp1 << 7) | (temp1 >> 25)) & 0xFFFFFFFF
        temp3 = (temp2 * 0x1337) & 0xFFFFFFFF

        # Step 3: Final XOR
        key_val = temp3 ^ 0xDEADBEEF

        return struct.pack(">I", key_val)

    def _manufacturer_b_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """Manufacturer B specific algorithm."""
        # Example: Table lookup based
        lookup_table = params.get("lookup_table", list(range(256)))

        key = bytearray()
        for i, byte in enumerate(seed):
            # Use seed byte as index into lookup table
            table_index = (byte + i) & 0xFF
            key_byte = lookup_table[table_index]
            # Additional transformation
            key_byte = ((key_byte << 4) | (key_byte >> 4)) & 0xFF
            key.append(key_byte)

        return bytes(key)

    def _manufacturer_c_algorithm(self, seed: bytes, params: Dict) -> bytes:
        """Manufacturer C specific algorithm."""
        # Example: Feistel network
        if len(seed) != 4:
            raise ValueError("Manufacturer C requires 4-byte seed")

        left = struct.unpack(">H", seed[:2])[0]
        right = struct.unpack(">H", seed[2:])[0]

        # Multiple rounds
        rounds = params.get("rounds", 4)
        for round_num in range(rounds):
            # Round function
            f_result = ((right * 0x9E37) + round_num) & 0xFFFF
            new_right = left ^ f_result
            left = right
            right = new_right

        return struct.pack(">HH", left, right)

    def brute_force_algorithm(
        self, seed: bytes, expected_key: bytes, max_attempts: int = 1000000
    ) -> Optional[Tuple[SecurityAlgorithm, Dict]]:
        """Attempt to determine algorithm by brute force (for research only)."""
        # Try common algorithms with common parameters
        test_params = [
            {"constant": const}
            for const in [0x0000, 0x1234, 0x5678, 0xABCD, 0xFFFF, 0x1111, 0x2222]
        ]

        for algorithm in SecurityAlgorithm:
            for params in test_params:
                try:
                    key = self.derive_key(seed, algorithm, params=params)
                    if key == expected_key:
                        return algorithm, params
                except Exception:
                    continue

        return None

    def validate_seed_key_pair(
        self,
        seed: bytes,
        key: bytes,
        algorithm: SecurityAlgorithm,
        params: Optional[Dict] = None,
    ) -> bool:
        """Validate a seed-key pair against an algorithm."""
        try:
            calculated_key = self.derive_key(seed, algorithm, params=params)
            return calculated_key == key
        except Exception:
            return False
