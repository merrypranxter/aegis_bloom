"""Sender CLI/API entry point."""
import cv2
import numpy as np
from crypto import encrypt
from fragment import split
from ai import zone_mapper, cdi as cdi_module
from stego import embed

def send(plaintext: str, cover_path: str, key: bytes) -> np.ndarray:
    """Embed message into cover image."""
    image = cv2.imread(cover_path, cv2.IMREAD_UNCHANGED)
    
    # 1. Encrypt
    encrypted = encrypt.encrypt(plaintext.encode(), key)
    
    # 2. Fragment
    frags = split.fragment(encrypted)
    
    # 3. Map zones
    zones = zone_mapper.map_zones(image)
    if len(zones) < len(frags):
        raise ValueError(f"Need {len(frags)} zones, found {len(zones)}")
    
    # 4. Generate CDIs
    cdis = []
    methods = ["LSB_ADAPTIVE", "DCT_LUMINANCE"] * (len(frags)//2 + 1)
    for i, (frag, zone) in enumerate(zip(frags, zones)):
        method = methods[i % len(methods)]
        cdi = cdi_module.generate_cdi(i, zone, method, len(frag), image)
        cdis.append(cdi)
    
    # 5. Master CDIs
    perm_key = {"order": list(range(len(frags))), "types": ["R"]*len(frags)}
    master = {
        "perm": perm_key,
        "locator": {"method": "LSB_ADAPTIVE", "region": "alpha_channel", "start": 0},
        "redundancy": 3
    }
    
    # 6. Embed (Master CDIs first, 3x redundant)
    stego = image.copy()
    for _ in range(3):
        stego = cdi_module.embed_cdi(master, stego, master["locator"])
    for cdi in cdis:
        stego = cdi_module.embed_cdi(cdi, stego, master["locator"])
    
    # 7. Embed fragments
    for cdi, frag in zip(cdis, frags):
        bits = ''.join(format(b, '08b') for b in frag)
        stego = embed.embed_fragment(stego, bits, cdi["zone"], cdi)
    
    return stego

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: sender.py <plaintext> <cover_image> <key_file>")
        sys.exit(1)
    
    with open(sys.argv[3], "rb") as f:
        key = f.read()
    
    result = send(sys.argv[1], sys.argv[2], key)
    cv2.imwrite("stego.png", result)
    print("Stego image saved to stego.png")
