from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
from PIL import Image
import numpy as np
import torch
import warnings

warnings.filterwarnings("ignore")

# Load model globally (Downloads ~100MB model on first run)
processor = None
model = None

def load_model():
    global processor, model
    if processor is None:
        processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
        model = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        model.eval()

def parse_garments(image: Image.Image):
    """
    Parses an image to isolate garments (Top, Pants, Skirts, Dresses) from the human body.
    Returns:
        garments (dict): A dictionary mapping garment type to an isolated RGBA PIL Image.
        has_human (bool): True if human body parts (face, arms, legs) were detected.
    """
    load_model()
    
    # Ensure image is RGB for the model
    rgb_image = image.convert("RGB")
    
    inputs = processor(images=rgb_image, return_tensors="pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        
    logits = outputs.logits.cpu()

    # Upsample logits to original image size
    upsampled_logits = torch.nn.functional.interpolate(
        logits,
        size=image.size[::-1], # (height, width)
        mode="bilinear",
        align_corners=False,
    )
    
    # Get highest probability class per pixel
    pred_seg = upsampled_logits.argmax(dim=1)[0].numpy()

    # Segformer B2 Clothes Classes:
    # 4: Upper-clothes, 5: Skirt, 6: Pants, 7: Dress
    # 11: Face, 12: Left-leg, 13: Right-leg, 14: Left-arm, 15: Right-arm
    
    garments = {}
    img_arr = np.array(image.convert("RGBA"))
    
    garment_classes = {
        "upper": 4,
        "skirt": 5,
        "pants": 6,
        "dress": 7
    }
    
    for label, class_idx in garment_classes.items():
        # Create a binary mask for this specific class
        mask = (pred_seg == class_idx).astype(np.uint8) * 255
        
        # If the mask has enough pixels (ignore tiny noise)
        if np.sum(mask > 0) > 2000:
            # Create transparent cutout
            cutout = np.zeros_like(img_arr)
            cutout[:, :, :3] = img_arr[:, :, :3]
            cutout[:, :, 3] = mask # Set alpha channel to mask
            
            # Smooth the edges slightly using OpenCV
            import cv2
            smoothed_mask = cv2.GaussianBlur(mask, (5, 5), 0)
            cutout[:, :, 3] = smoothed_mask
            
            # Crop to bounding box
            pil_cutout = Image.fromarray(cutout)
            bbox = pil_cutout.getbbox()
            if bbox:
                garments[label] = pil_cutout.crop(bbox)

    # Detect human presence
    human_classes = [11, 12, 13, 14, 15]
    has_human = any(np.any(pred_seg == c) for c in human_classes)

    return garments, has_human
