import io
import rembg
from PIL import Image
import numpy as np

# Initialize the rembg session (downloads model on first run if needed)
# Using u2net for optimal quality. u2netp is faster but less accurate.
session = rembg.new_session("u2net")

def segment_garment(image: Image.Image) -> tuple[Image.Image, Image.Image]:
    """
    Takes a PIL Image of a garment.
    Returns a tuple of (mask, cutout) where:
      - mask is a grayscale PIL Image (L mode) representing the alpha channel.
      - cutout is an RGBA PIL Image with the background removed.
    """
    # Use rembg to remove the background
    # post_process=True applies morphological operations to smooth edges
    cutout = rembg.remove(image, session=session, post_process=True)
    
    # Extract the mask from the alpha channel
    mask = cutout.split()[3]
    
    return mask, cutout

def cleanup_edges(mask: Image.Image, amount: int = 2) -> Image.Image:
    """
    Optional helper to further refine the mask edges if rembg leaves artifacts.
    Not strictly needed if post_process=True is working well.
    """
    import cv2
    from ..utils.image_utils import pil_to_cv2, cv2_to_pil
    
    cv_mask = pil_to_cv2(mask)
    if len(cv_mask.shape) == 3:
        cv_mask = cv2.cvtColor(cv_mask, cv2.COLOR_BGR2GRAY)
        
    kernel = np.ones((amount, amount), np.uint8)
    eroded = cv2.erode(cv_mask, kernel, iterations=1)
    smoothed = cv2.GaussianBlur(eroded, (3, 3), 0)
    
    return cv2_to_pil(smoothed).convert("L")
