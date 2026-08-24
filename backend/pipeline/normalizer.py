from PIL import Image
import numpy as np

def normalize(cutout: Image.Image, garment_type: str, max_dim: int = 1024) -> Image.Image:
    """
    Centers, scales, and prepares the cutout for the canonical representation.
    """
    # 1. Find bounding box of the non-transparent content
    bbox = cutout.getbbox()
    if not bbox:
        return cutout # Empty image
        
    # Crop to just the garment
    cropped = cutout.crop(bbox)
    
    # 2. Scale up/down so the longest side fits inside max_dim with some padding
    padding = int(max_dim * 0.1) # 10% padding on each side
    target_size = max_dim - (padding * 2)
    
    width, height = cropped.size
    aspect_ratio = width / height
    
    if width > height:
        new_width = target_size
        new_height = int(target_size / aspect_ratio)
    else:
        new_height = target_size
        new_width = int(target_size * aspect_ratio)
        
    scaled = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 3. Paste into a new max_dim x max_dim transparent canvas (centering it)
    canvas = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
    paste_x = (max_dim - new_width) // 2
    paste_y = (max_dim - new_height) // 2
    
    canvas.paste(scaled, (paste_x, paste_y))
    
    return canvas
