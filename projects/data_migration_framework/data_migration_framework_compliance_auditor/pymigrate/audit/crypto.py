"""Cryptographic utilities for audit logging."""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
)


class CryptoManager:
    """Manages cryptographic operations for audit logging."""

    def __init__(self, key_size: int = 2048):
        """Initialize the crypto manager.

        Args:
            key_size: Size of RSA keys to generate (default: 2048)
        """
        self.key_size = key_size
        self._private_key: Optional[rsa.RSAPrivateKey] = None
        self._public_key: Optional[rsa.RSAPublicKey] = None

    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """Generate a new RSA key pair.

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        self._private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=self.key_size, backend=default_backend()
        )
        self._public_key = self._private_key.public_key()

        private_pem = self._private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = self._public_key.public_bytes(
            encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    def load_private_key(self, private_key_pem: bytes) -> None:
        """Load a private key from PEM format.

        Args:
            private_key_pem: Private key in PEM format
        """
        self._private_key = serialization.load_pem_private_key(
            private_key_pem, password=None, backend=default_backend()
        )
        self._public_key = self._private_key.public_key()

    def load_public_key(self, public_key_pem: bytes) -> None:
        """Load a public key from PEM format.

        Args:
            public_key_pem: Public key in PEM format
        """
        self._public_key = serialization.load_pem_public_key(
            public_key_pem, backend=default_backend()
        )

    def sign_data(self, data: bytes) -> bytes:
        """Sign data using the private key.

        Args:
            data: Data to sign

        Returns:
            Digital signature

        Raises:
            ValueError: If no private key is loaded
        """
        if not self._private_key:
            raise ValueError("No private key loaded")

        signature = self._private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return signature

    def verify_signature(self, data: bytes, signature: bytes) -> bool:
        """Verify a signature using the public key.

        Args:
            data: Original data
            signature: Signature to verify

        Returns:
            True if signature is valid, False otherwise

        Raises:
            ValueError: If no public key is loaded
        """
        if not self._public_key:
            raise ValueError("No public key loaded")

        try:
            self._public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    @staticmethod
    def compute_hash(data: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of data.

        Args:
            data: Data to hash

        Returns:
            Hex-encoded hash
        """
        # Sort keys for consistent hashing
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    @staticmethod
    def compute_chain_hash(current_data: Dict[str, Any], previous_hash: str) -> str:
        """Compute hash for blockchain-style chaining.

        Args:
            current_data: Current event data
            previous_hash: Hash of previous event

        Returns:
            Hex-encoded hash
        """
        # Include previous hash in computation
        data_with_prev = {**current_data, "previous_hash": previous_hash}
        return CryptoManager.compute_hash(data_with_prev)

    @staticmethod
    def generate_timestamp_proof(timestamp: datetime) -> str:
        """Generate a cryptographic proof of timestamp.

        Args:
            timestamp: Timestamp to prove

        Returns:
            Hex-encoded proof
        """
        # In production, this would integrate with a timestamp authority
        # For now, we'll create a simple hash-based proof
        proof_data = {
            "timestamp": timestamp.isoformat(),
            "unix_time": timestamp.timestamp(),
            "nonce": hashlib.sha256(timestamp.isoformat().encode()).hexdigest()[:16],
        }
        return CryptoManager.compute_hash(proof_data)
