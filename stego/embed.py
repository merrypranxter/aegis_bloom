"""Master dispatcher for steganographic embedding."""
from . import lsb, dct, pixelmod

def embed_fragment(image, bits: str, zone, cdi: dict) -> np.ndarray:
    """Embed fragment using method specified in CDI."""
    method = cdi["method"]
    seed = cdi["seed"]
    
    if method == "LSB_ADAPTIVE":
        return lsb.embed_lsb(image, bits, zone, seed)
    elif method == "DCT_LUMINANCE":
        return dct.embed_dct(image, bits, zone, seed)
    elif method == "PIXEL_MOD":
        return pixelmod.embed_pixel_mod(image, bits, zone, seed)
    else:
        raise ValueError(f"Unknown embedding method: {method}")
