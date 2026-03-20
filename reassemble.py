import reedsolo

def reassemble(frags: list[bytes], order: list[int]) -> bytes:
    """Reassemble fragments with ECC correction."""
    rs = reedsolo.RSCodec(16)
    decoded = []
    for idx in order:
        try:
            data = rs.decode(frags[idx])[0]
            decoded.append(data)
        except reedsolo.ReedSolomonError:
            # ECC recovery failed
            pass
    return b''.join(decoded)
