import numpy as np

def embed_lsb(image: np.ndarray, bits: str, zone, seed: int, order: int = 1) -> np.ndarray:
    """Adaptive LSB: higher order in noisy zones."""
    np.random.seed(seed)
    x, y, w, h = zone.bbox
    
    # Adaptive: use 2nd/3rd LSB in high-density zones
    lsb_order = 2 if zone.params.get("density", 0) > 0.6 else 1
    mask = 0xFF ^ (1 << (lsb_order - 1))
    
    flat = image[y:y+h, x:x+w].flatten()
    indices = np.random.choice(len(flat), len(bits), replace=False)
    
    for i, bit in enumerate(bits):
        flat[indices[i]] = (flat[indices[i]] & mask) | (int(bit) << (lsb_order - 1))
    
    image[y:y+h, x:x+w] = flat.reshape(h, w, -1)
    return image

def extract_lsb(image: np.ndarray, bit_count: int, zone, seed: int) -> str:
    """Reverse with same seed and zone detection."""
    np.random.seed(seed)
    x, y, w, h = zone.bbox
    lsb_order = 2 if zone.params.get("density", 0) > 0.6 else 1
    
    flat = image[y:y+h, x:x+w].flatten()
    indices = np.random.choice(len(flat), bit_count, replace=False)
    indices.sort()  # Deterministic extraction
    
    bits = [(flat[i] >> (lsb_order - 1)) & 1 for i in indices]
    return ''.join(str(b) for b in bits)
