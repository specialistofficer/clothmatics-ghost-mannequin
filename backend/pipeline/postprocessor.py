from PIL import Image

def process(generated: Image.Image, output_format: str = "png", output_bg: str = "transparent") -> Image.Image:
    """
    Final formatting. Applies requested background and format.
    """
    if output_bg == "white" or output_format.lower() == "jpeg":
        # Must have a solid background for JPEG or if requested
        bg = Image.new("RGBA", generated.size, (255, 255, 255, 255))
        final = Image.alpha_composite(bg, generated)
        if output_format.lower() == "jpeg":
            final = final.convert("RGB")
        return final
        
    # Default is transparent PNG
    return generated
