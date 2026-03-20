import zlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """AES-256-GCM decrypt + Zlib decompress."""
    nonce = ciphertext[:12]
    encrypted = ciphertext[12:]
    aesgcm = AESGCM(key)
    compressed = aesgcm.decrypt(nonce, encrypted, None)
    return zlib.decompress(compressed)
