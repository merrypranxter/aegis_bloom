"""Reverse dispatcher for steganographic extraction."""
from . import lsb, dct, pixelmod

def extract_fragment(image, bit_count: int, zone, cdi: dict) -> str:
    """Extract fragment using method specified in CDI."""
    method = cdi["method"]
    seed = cdi["seed"]
    
    if method == "LSB_ADAPTIVE":
        return lsb.extract_lsb(image, bit_count, zone, seed)
    elif method == "DCT_LUMINANCE":
        return dct.extract_dct(image, bit_count, zone, seed)
    elif method == "PIXEL_MOD":
        return pixelmod.extract_pixel_mod(image, bit_count, zone, seed)
    else:
        raise ValueError(f"Unknown extraction method: {method}")
