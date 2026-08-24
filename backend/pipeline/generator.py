from PIL import Image, ImageFilter, ImageDraw
import numpy as np

def get_dominant_color(image: Image.Image, mask: Image.Image) -> tuple:
    """
    Extracts the dominant color of the garment by sampling the non-transparent pixels.
    Returns an RGB tuple.
    """
    # Resize for faster processing
    small_img = image.resize((50, 50))
    small_mask = mask.resize((50, 50))
    
    img_array = np.array(small_img)
    mask_array = np.array(small_mask)
    
    # Extract RGB values where mask is not transparent (alpha > 128)
    valid_pixels = img_array[mask_array > 128]
    
    if len(valid_pixels) == 0:
        return (100, 100, 100) # Fallback gray
        
    # Calculate median color to avoid outliers (like bright white logos)
    median_color = np.median(valid_pixels[:, :3], axis=0).astype(int)
    return tuple(median_color)

def darken_color(color: tuple, factor: float = 0.6) -> tuple:
    """
    Darkens an RGB color by a given factor to simulate shadow/interior.
    """
    return tuple(int(c * factor) for c in color)

def generate_inner_collar(bbox: tuple, img_size: tuple, color: tuple) -> Image.Image:
    """
    Draws a generic synthetic inner collar/back panel.
    Placed at the top-center of the garment bounding box.
    """
    canvas = Image.new("RGBA", img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    left, top, right, bottom = bbox
    width = right - left
    
    # Estimate neck width and position
    neck_width = width * 0.45
    neck_height = width * 0.25
    center_x = left + (width / 2)
    
    # Ellipse coordinates for the back of the neck opening
    e_left = center_x - (neck_width / 2)
    e_right = center_x + (neck_width / 2)
    e_top = top - (neck_height * 0.2) # Slight protrusion above the front line
    e_bottom = top + neck_height
    
    # Draw the inner collar using the darkened dominant color
    draw.ellipse([e_left, e_top, e_right, e_bottom], fill=color + (255,))
    
    return canvas

def generate(normalized: Image.Image, garment_type: str, original_mask: Image.Image) -> Image.Image:
    """
    Phase 2 CPU Ghost Mannequin generator.
    Simulates a 3D inner neck using OpenCV/PIL geometrical compositing,
    avoiding the need for a GPU diffusion model.
    """
    # 1. Find the garment bounding box in the normalized image
    alpha = normalized.split()[3]
    bbox = alpha.getbbox()
    
    if not bbox:
        return normalized

    # 2. Extract dominant color and calculate the interior shadow color
    dominant_rgb = get_dominant_color(normalized, alpha)
    interior_color = darken_color(dominant_rgb, factor=0.45) # Darken significantly for depth
    
    # 3. Generate the synthetic inner collar layer
    inner_collar_layer = generate_inner_collar(bbox, normalized.size, interior_color)
    
    # 4. Create a subtle drop shadow for the main garment layer
    shadow = alpha.copy().filter(ImageFilter.GaussianBlur(radius=8))
    from PIL import ImageEnhance
    shadow = ImageEnhance.Brightness(shadow).enhance(0.5)
    
    shadow_layer = Image.new("RGBA", normalized.size, (0, 0, 0, 0))
    shadow_layer.paste((0, 0, 0), (0, 10), mask=shadow) # Shift shadow down
    
    # 5. Composite everything together (Back to Front)
    # Background -> Inner Collar -> Drop Shadow -> Front Garment
    result = Image.new("RGBA", normalized.size, (0, 0, 0, 0))
    
    # Add the inner collar (this sits behind the garment)
    result = Image.alpha_composite(result, inner_collar_layer)
    
    # Add the garment's drop shadow (falls onto the inner collar and background)
    result = Image.alpha_composite(result, shadow_layer)
    
    # Add the actual front garment
    result = Image.alpha_composite(result, normalized)
    
    return result
