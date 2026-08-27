import torch
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image, ImageDraw
import numpy as np
import warnings

warnings.filterwarnings("ignore")

pipe = None

def load_pipeline():
    global pipe
    if pipe is None:
        print("Downloading/Loading Stable Diffusion Inpainting Model...")
        pipe = StableDiffusionInpaintPipeline.from_pretrained(
            "runwayml/stable-diffusion-inpainting",
            torch_dtype=torch.float32
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = pipe.to(device)
        if device == "cpu":
            pipe.enable_attention_slicing()
        print(f"Model Loaded Successfully on {device}!")

def generate(image: Image.Image, g_type: str, mask: Image.Image = None) -> Image.Image:
    """
    Uses Generative AI (Stable Diffusion) to inpaint the realistic back collar AND reconstruct missing fabric (where hands/body were).
    """
    load_pipeline()
    import cv2
    
    img_w, img_h = image.size
    
    # 1. Get original mask
    mask_arr = np.array(image.split()[3])
    y_indices, x_indices = np.where(mask_arr > 128)
    
    if len(y_indices) == 0:
        return image
        
    top_y, bottom_y = np.min(y_indices), np.max(y_indices)
    left_x, right_x = np.min(x_indices), np.max(x_indices)
    height = bottom_y - top_y
    width = right_x - left_x
    
    inpaint_mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(inpaint_mask)
    
    # B. Intelligent Masking based on Garment Type
    if g_type in ["upper", "dress"]:
        # For jackets/shirts: draw the back collar ellipse
        neck_width = int(width * 0.45)
        neck_left = left_x + int(width * 0.275)
        neck_height = int(height * 0.1)
        draw.ellipse([neck_left, top_y - int(neck_height * 0.5), neck_left + neck_width, top_y + neck_height], fill=255)
    elif g_type in ["pants", "skirt"]:
        # For jeans/pants: hands usually cover the waist. We completely inpaint the top 15% waistband area.
        waist_height = int(height * 0.15)
        draw.rectangle([left_x, top_y, right_x, top_y + waist_height], fill=255)
    
    inpaint_mask_arr = np.array(inpaint_mask)
    
    # C. Detect deep holes left by human body parts (hands overlapping clothes)
    kernel = np.ones((25, 25), np.uint8)
    closed_mask = cv2.morphologyEx(mask_arr, cv2.MORPH_CLOSE, kernel)
    holes_mask = cv2.subtract(closed_mask, mask_arr)
    
    # D. Combine Type Mask + Missing Fabric Holes
    combined_mask = np.maximum(inpaint_mask_arr, holes_mask)
    # Dilate significantly so AI has room to blend the new fabric perfectly
    combined_mask = cv2.dilate(combined_mask, np.ones((10,10), np.uint8), iterations=1)
    # Gaussian blur for seamless blending
    combined_mask = cv2.GaussianBlur(combined_mask, (21, 21), 0)
    final_inpaint_mask = Image.fromarray(combined_mask)
    
    # 2. Prepare RGB Image for SD (Paste garment on white background)
    rgb_image = Image.new("RGB", image.size, (255, 255, 255))
    rgb_image.paste(image, (0, 0), image)
    
    # 3. Resize to 512x512
    orig_size = rgb_image.size
    rgb_image_512 = rgb_image.resize((512, 512), Image.Resampling.LANCZOS)
    inpaint_mask_512 = final_inpaint_mask.resize((512, 512), Image.Resampling.LANCZOS)
    
    # 4. Run Stable Diffusion Inpainting with Strong 3D Prompts
    # Adjusted prompt to avoid hallucinations like labels or hangers
    prompt = f"perfect 3D ghost mannequin shot of a {g_type}, invisible mannequin inside, plump fabric, hollow neck and waist, professional fashion photography, studio lighting, highly detailed fabric texture, plain white background"
    negative_prompt = "hanger, hook, label, tag, logo, text, human, person, hands, skin, flat, paper cutout, 2d, watermark, messy, distorted, drawing, illustration"
    
    print(f"Starting Perfect 3D Inpainting for {g_type}...")
    result_512 = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=rgb_image_512,
        mask_image=inpaint_mask_512,
        num_inference_steps=25,
        guidance_scale=8.5
    ).images[0]
    
    # 5. Restore original size and transparency
    result_full = result_512.resize(orig_size, Image.Resampling.LANCZOS)
    
    # Final alpha = Original Mask + Inpainted areas
    final_alpha = np.maximum(mask_arr, combined_mask)
    final_alpha_img = Image.fromarray(final_alpha).convert("L")
    
    result_rgba = result_full.convert("RGBA")
    result_rgba.putalpha(final_alpha_img)
    
    return result_rgba
