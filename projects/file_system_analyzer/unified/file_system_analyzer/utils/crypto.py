"""
Cryptographic utilities for secure logging and evidence integrity.

This module provides cryptographic functions for creating secure hashes,
digital signatures, and verifying the integrity of audit logs and evidence.
"""

# Import from common library
from common.utils.crypto import CryptoProvider as CommonCryptoProvider
from common.utils.crypto import sign_data, verify_signed_data


class CryptoProvider(CommonCryptoProvider):
    """
    Provider of cryptographic functions for secure logging and verification.
    
    This class extends the common CryptoProvider with any security auditor
    specific functionality.
    """
    pass