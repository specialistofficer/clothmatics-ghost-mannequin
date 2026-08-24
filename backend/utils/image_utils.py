import cv2
import numpy as np
from PIL import Image
import io

def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV format (BGR or BGRA)."""
    numpy_image = np.array(pil_img)
    if len(numpy_image.shape) == 3 and numpy_image.shape[2] == 3:
        # RGB to BGR
        return cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    elif len(numpy_image.shape) == 3 and numpy_image.shape[2] == 4:
        # RGBA to BGRA
        return cv2.cvtColor(numpy_image, cv2.COLOR_RGBA2BGRA)
    return numpy_image

def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """Convert OpenCV Image to PIL format."""
    if len(cv2_img.shape) == 3 and cv2_img.shape[2] == 3:
        # BGR to RGB
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    elif len(cv2_img.shape) == 3 and cv2_img.shape[2] == 4:
        # BGRA to RGBA
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGRA2RGBA)
    return Image.fromarray(cv2_img)

def save_cv2_image(cv2_img: np.ndarray, path: str):
    """Save an OpenCV image to disk safely."""
    cv2.imwrite(path, cv2_img)

def load_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Load image from bytes directly to OpenCV."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
