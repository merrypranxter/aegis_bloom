"""Receiver CLI/API entry point."""
from crypto import decrypt
from fragment import reassemble
from ai import zone_mapper, cdi as cdi_module
from stego import extract

def receive(stego, key: bytes) -> str:
    """Extract and decrypt message from stego-image."""
    # 1. Extract Master CDIs (scan alpha, DCT watermark, metadata)
    master = None
    for attempt in ["alpha_lsb", "dct_watermark", "exif"]:
        try:
            master = cdi_module.extract_master(stego, method=attempt)
            if master:
                break
        except:
            continue
    
    if not master:
        raise ValueError("No Master CDI found")
    
    # 2. Extract fragment CDIs
    cdis = []
    for i in range(len(master["perm"]["order"])):
        cdi = cdi_module.extract_cdi(stego, master["locator"], index=i)
        cdis.append(cdi)
    
    # 3. Extract fragments
    frags = []
    for cdi in cdis:
        zone = zone_mapper.find_zone(stego, cdi["zone"])  # Re-detect
        bits = extract.extract_fragment(stego, cdi["bits"]//8, zone, cdi)
        frag = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
        frags.append(frag)
    
    # 4. Reassemble
    payload = reassemble.reassemble(frags, master["perm"]["order"])
    
    # 5. Decrypt
    plaintext = decrypt.decrypt(payload, key)
    return plaintext.decode()

if __name__ == "__main__":
    import sys
    import cv2
    
    if len(sys.argv) != 3:
        print("Usage: receiver.py <stego_image> <key_file>")
        sys.exit(1)
    
    stego = cv2.imread(sys.argv[1], cv2.IMREAD_UNCHANGED)
    with open(sys.argv[2], "rb") as f:
        key = f.read()
    
    result = receive(stego, key)
    print(f"Extracted message: {result}")
