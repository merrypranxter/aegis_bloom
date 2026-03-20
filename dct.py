import cv2
import numpy as np

def embed_dct(image: np.ndarray, bits: str, zone, seed: int) -> np.ndarray:
    """Embed in DCT luminance, mid-frequency coefficients."""
    x, y, w, h = zone.bbox
    
    # Ensure 8x8 blocks
    w, h = (w // 8) * 8, (h // 8) * 8
    roi = cv2.cvtColor(image[y:y+h, x:x+w], cv2.COLOR_BGR2YCrCb)[:, :, 0]  # Luminance
    
    blocks = []
    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = roi[i:i+8, j:j+8].astype(np.float32) - 128
            dct = cv2.dct(block)
            blocks.append((i, j, dct))
    
    # Select mid-freq coefficients (2 <= u+v <= 6, skip DC)
    candidates = []
    for bi, (i, j, dct) in enumerate(blocks):
        for u in range(8):
            for v in range(8):
                if 2 <= u+v <= 6 and (u, v) != (0, 0):
                    candidates.append((bi, u, v, dct[u, v]))
    
    # Pseudorandom selection via seed
    np.random.seed(seed)
    selected = np.random.choice(len(candidates), len(bits), replace=False)
    
    for idx, bit in zip(selected, bits):
        bi, u, v, val = candidates[idx]
        # Quantize: even/odd for 0/1
        if int(bit) != (int(round(val)) % 2):
            blocks[bi][2][u, v] += 1 if val >= 0 else -1
    
    # Reconstruct
    for i, j, dct in blocks:
        block = cv2.idct(dct) + 128
        roi[i:i+8, j:j+8] = np.clip(block, 0, 255)
    
    image[y:y+h, x:x+w, 0] = roi  # Back to Y channel
    return cv2.cvtColor(image, cv2.COLOR_YCrCb2BGR)

def extract_dct(image: np.ndarray, bit_count: int, zone, seed: int) -> str:
    """Extract bits from DCT coefficients."""
    # Implementation similar to embed but read-only
    pass
