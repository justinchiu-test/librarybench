"""Tests for cryptographic utilities."""

import pytest
import base64
from datetime import datetime, timedelta
import pytz

from pymigrate.audit.crypto import CryptoManager


class TestCryptoManager:
    """Extended tests for CryptoManager."""

    def test_key_sizes(self):
        """Test generating keys with different sizes."""
        # Test 2048-bit keys (default)
        crypto1 = CryptoManager(key_size=2048)
        private1, public1 = crypto1.generate_key_pair()
        assert b"BEGIN" in private1
        assert b"BEGIN PUBLIC KEY" in public1

        # Test 4096-bit keys
        crypto2 = CryptoManager(key_size=4096)
        private2, public2 = crypto2.generate_key_pair()
        assert b"BEGIN" in private2
        assert b"BEGIN PUBLIC KEY" in public2

        # 4096-bit keys should be longer
        assert len(private2) > len(private1)
        assert len(public2) > len(public1)

    def test_load_keys(self):
        """Test loading keys from PEM format."""
        crypto1 = CryptoManager()
        private_pem, public_pem = crypto1.generate_key_pair()

        # Load into new instance
        crypto2 = CryptoManager()
        crypto2.load_private_key(private_pem)

        # Should be able to sign with loaded key
        data = b"test data"
        signature = crypto2.sign_data(data)
        assert crypto2.verify_signature(data, signature)

        # Load only public key
        crypto3 = CryptoManager()
        crypto3.load_public_key(public_pem)

        # Should be able to verify but not sign
        assert crypto3.verify_signature(data, signature)
        with pytest.raises(ValueError, match="No private key loaded"):
            crypto3.sign_data(data)

    def test_sign_verify_edge_cases(self):
        """Test edge cases in signing and verification."""
        crypto = CryptoManager()
        crypto.generate_key_pair()

        # Empty data
        empty_sig = crypto.sign_data(b"")
        assert crypto.verify_signature(b"", empty_sig)

        # Large data
        large_data = b"x" * 10000
        large_sig = crypto.sign_data(large_data)
        assert crypto.verify_signature(large_data, large_sig)

        # Binary data
        binary_data = bytes(range(256))
        binary_sig = crypto.sign_data(binary_data)
        assert crypto.verify_signature(binary_data, binary_sig)

    def test_signature_tampering(self):
        """Test that tampered signatures are detected."""
        crypto = CryptoManager()
        crypto.generate_key_pair()

        data = b"original data"
        signature = crypto.sign_data(data)

        # Tamper with signature
        sig_bytes = bytearray(signature)
        sig_bytes[0] ^= 0xFF  # Flip bits
        tampered_sig = bytes(sig_bytes)

        assert not crypto.verify_signature(data, tampered_sig)

        # Truncated signature
        truncated_sig = signature[:-10]
        assert not crypto.verify_signature(data, truncated_sig)

    def test_hash_consistency(self):
        """Test hash computation consistency."""
        data1 = {"key": "value", "number": 42, "list": [1, 2, 3]}
        data2 = {"number": 42, "key": "value", "list": [1, 2, 3]}  # Different order

        # Should produce same hash regardless of key order
        hash1 = CryptoManager.compute_hash(data1)
        hash2 = CryptoManager.compute_hash(data2)
        assert hash1 == hash2

        # Different data should produce different hash
        data3 = {"key": "value", "number": 43, "list": [1, 2, 3]}
        hash3 = CryptoManager.compute_hash(data3)
        assert hash3 != hash1

    def test_hash_data_types(self):
        """Test hashing different data types."""
        # String values
        assert CryptoManager.compute_hash({"str": "hello"})

        # Numeric values
        assert CryptoManager.compute_hash({"int": 42, "float": 3.14})

        # Boolean values
        assert CryptoManager.compute_hash({"bool": True})

        # None values
        assert CryptoManager.compute_hash({"none": None})

        # Nested structures
        assert CryptoManager.compute_hash({"nested": {"deep": {"value": "test"}}})

        # Lists
        assert CryptoManager.compute_hash({"list": [1, "two", 3.0, None]})

    def test_chain_hash_properties(self):
        """Test properties of chain hashing."""
        data = {"event": "test", "value": 123}

        # Chain with no previous hash
        hash1 = CryptoManager.compute_chain_hash(data, "")
        assert hash1

        # Chain with previous hash
        hash2 = CryptoManager.compute_chain_hash(data, hash1)
        assert hash2 != hash1  # Should be different

        # Same data with same previous hash should produce same result
        hash3 = CryptoManager.compute_chain_hash(data, hash1)
        assert hash3 == hash2

        # Different previous hash should produce different result
        hash4 = CryptoManager.compute_chain_hash(data, "different_prev")
        assert hash4 != hash2

    def test_timestamp_proof_properties(self):
        """Test timestamp proof generation properties."""
        now = datetime.now(pytz.UTC)

        # Same timestamp should produce same proof
        proof1 = CryptoManager.generate_timestamp_proof(now)
        proof2 = CryptoManager.generate_timestamp_proof(now)
        assert proof1 == proof2

        # Different timestamps should produce different proofs
        later = now + timedelta(seconds=1)
        proof3 = CryptoManager.generate_timestamp_proof(later)
        assert proof3 != proof1

        # Microsecond differences should matter
        micro_later = now + timedelta(microseconds=1)
        proof4 = CryptoManager.generate_timestamp_proof(micro_later)
        assert proof4 != proof1

    def test_error_handling(self):
        """Test error handling in crypto operations."""
        crypto = CryptoManager()

        # Try to sign without keys
        with pytest.raises(ValueError, match="No private key loaded"):
            crypto.sign_data(b"data")

        # Try to verify without keys
        with pytest.raises(ValueError, match="No public key loaded"):
            crypto.verify_signature(b"data", b"signature")

        # Invalid signature format
        crypto.generate_key_pair()
        assert not crypto.verify_signature(b"data", b"invalid_signature")

    def test_key_serialization(self):
        """Test that keys can be serialized and deserialized correctly."""
        crypto1 = CryptoManager()
        private_pem, public_pem = crypto1.generate_key_pair()

        # Keys should be in PEM format
        assert private_pem.startswith(b"-----BEGIN")
        assert private_pem.endswith(b"-----\n")
        assert public_pem.startswith(b"-----BEGIN PUBLIC KEY-----")
        assert public_pem.endswith(b"-----\n")

        # Should be able to decode base64 content
        lines = public_pem.decode().split("\n")
        content_lines = [l for l in lines if l and not l.startswith("-----")]
        content = "".join(content_lines)
        base64.b64decode(content)  # Should not raise
