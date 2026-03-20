import reedsolo  # pip install reedsolo

def fragment(payload: bytes, min_frag: int = 128, max_frags: int = 16) -> list[bytes]:
    """Split + Reed-Solomon ECC per fragment."""
    n = min(max(len(payload) // min_frag, 4), max_frags)
    raw_size = len(payload) // n
    frags = []
    for i in range(n):
        chunk = payload[i*raw_size : (i+1)*raw_size] if i < n-1 else payload[i*raw_size:]
        rs = reedsolo.RSCodec(16)  # 16 bytes ECC
        frags.append(rs.encode(chunk))
    return frags  # Each: data + 16 ECC bytes
