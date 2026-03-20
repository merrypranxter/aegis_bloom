import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class Zone:
    type: str  # EDGE, TEXTURE, OBJECT, COLOR
    bbox: tuple  # (x, y, w, h)
    params: dict

def map_zones(image: np.ndarray) -> list[Zone]:
    """Return cognitive zones ranked by embeddability."""
    zones = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Edge zones
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours[:8]:
        x, y, w, h = cv2.boundingRect(cnt)
        density = cv2.contourArea(cnt) / (w*h) if w*h > 0 else 0
        if density > 0.3:
            zones.append(Zone("EDGE", (x, y, w, h), {"density": density}))
    
    # Texture zones (Gabor filter response)
    gabor = cv2.getGaborKernel((21, 21), 5, 0, 10, 0.5, 0, ktype=cv2.CV_32F)
    filtered = cv2.filter2D(gray, cv2.CV_8UC3, gabor)
    # ... threshold to regions
    
    # Color variance zones
    # ... HSV analysis
    
    return sorted(zones, key=lambda z: z.params.get("density", 0), reverse=True)
