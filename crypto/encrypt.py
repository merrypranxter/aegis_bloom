import zlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """AES-256-GCM with Zlib compression."""
    compressed = zlib.compress(plaintext, level=9)
    aesgcm = AESGCM(key)  # key: 32 bytes
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, compressed, None)
    return nonce + ciphertext  # 12 + len(cipher)

# Key derivation: PBKDF2-HMAC-SHA256(password, salt, 100000 iterations, dklen=32)
