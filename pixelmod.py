import numpy as np

def embed_pixel_mod(image: np.ndarray, bits: str, zone, seed: int) -> np.ndarray:
    """Statistical pixel value modulation for spread spectrum."""
    np.random.seed(seed)
    x, y, w, h = zone.bbox
    
    roi = image[y:y+h, x:x+w].copy()
    flat = roi.reshape(-1, roi.shape[-1] if len(roi.shape) > 2 else 1)
    
    # Select pixels pseudorandomly
    indices = np.random.choice(len(flat), len(bits), replace=False)
    
    for idx, bit in zip(indices, bits):
        # Modulate pixel value statistically
        # Even/odd modulation with dithering
        channel = idx % flat.shape[1] if len(flat.shape) > 1 else 0
        pixel_idx = idx // flat.shape[1] if len(flat.shape) > 1 else idx
        
        current = flat[pixel_idx, channel]
        desired_parity = int(bit)
        actual_parity = current % 2
        
        if actual_parity != desired_parity:
            # Adjust with minimal visual impact
            adjustment = 1 if current < 128 else -1
            flat[pixel_idx, channel] = np.clip(current + adjustment, 0, 255)
    
    image[y:y+h, x:x+w] = flat.reshape(roi.shape)
    return image

def extract_pixel_mod(image: np.ndarray, bit_count: int, zone, seed: int) -> str:
    """Extract statistically modulated bits."""
    np.random.seed(seed)
    x, y, w, h = zone.bbox
    
    roi = image[y:y+h, x:x+w]
    flat = roi.reshape(-1, roi.shape[-1] if len(roi.shape) > 2 else 1)
    
    indices = np.random.choice(len(flat), bit_count, replace=False)
    indices.sort()
    
    bits = []
    for idx in indices:
        channel = idx % flat.shape[1] if len(flat.shape) > 1 else 0
        pixel_idx = idx // flat.shape[1] if len(flat.shape) > 1 else idx
        bits.append(str(flat[pixel_idx, channel] % 2))
    
    return ''.join(bits)
