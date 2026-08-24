from PIL import Image

def classify(cutout: Image.Image) -> str:
    """
    Classifies the garment type based on aspect ratio and basic heuristics.
    Phase 1: Extremely simple rule-based approach.
    Phase 2: Could be replaced by a lightweight MobileNetV3.
    """
    width, height = cutout.size
    
    # If the image is empty or invalid
    if width == 0 or height == 0:
        return "unknown"
        
    aspect_ratio = height / width
    
    # Simple aspect ratio heuristics for typical folded/flat garments
    # Tall and narrow -> pants/dresses (for future)
    # Boxy -> t-shirt / shirt
    # Very wide -> might be arms spread out
    
    # For MVP, we default to t-shirt unless it's exceptionally tall/wide.
    # In a real scenario, you'd analyze contours for lapels (jacket) or collars (shirt).
    
    if aspect_ratio > 1.8:
        return "dress_or_pants" # Out of scope for current MVP
    elif 1.1 <= aspect_ratio <= 1.8:
        return "shirt" # general top
    else:
        return "tshirt"

