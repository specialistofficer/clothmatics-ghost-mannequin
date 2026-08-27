from PIL import Image
import time
from . import segmentation, classifier, normalizer, ai_generator, postprocessor, human_parsing
from ..config import settings

def process_pipeline(image: Image.Image, debug: bool = False):
    """
    Orchestrates the Ghost Mannequin processing pipeline.
    Now supports Human Parsing & Multi-Garment Extraction.
    """
    start_time = time.time()
    intermediates = {}
    warnings = []
    final_outputs = {}
    
    if debug: intermediates["01_original"] = image.copy()
    
    try:
        # Step 1: Attempt Human Garment Parsing First
        parsed_garments, has_human = human_parsing.parse_garments(image)
        
        garments_to_process = {}
        
        if parsed_garments and has_human:
            # Multi-garment human image detected
            warnings.append(f"Human detected. Extracted garments: {', '.join(parsed_garments.keys())}")
            garments_to_process = parsed_garments
            detected_type = list(parsed_garments.keys())[0] # Use first one as primary type
        else:
            # Fallback to standard rembg flat-lay processing
            warnings.append("No human detected. Running standard flat-lay background removal.")
            mask, cutout = segmentation.segment_garment(image)
            if debug: 
                intermediates["02_flatlay_mask"] = mask.copy()
                intermediates["03_flatlay_cutout"] = cutout.copy()
            detected_type = classifier.classify(cutout)
            garments_to_process = {"main": cutout}
            
        # Step 2: Process each extracted garment
        for label, cutout in garments_to_process.items():
            # Classify specifically for this piece if it's the main fallback, else use label
            g_type = detected_type if label == "main" else label
            
            # Normalize (Center, Scale)
            normalized = normalizer.normalize(cutout, g_type, settings.output_max_dimension)
            if debug: intermediates[f"04_{label}_normalized"] = normalized.copy()
            
            # Generate Ghost Mannequin (Using Generative AI Inpainting)
            generated = ai_generator.generate(normalized, g_type)
            if debug: intermediates[f"05_{label}_generated"] = generated.copy()
            
            # Post-process
            final = postprocessor.process(generated, settings.output_format, settings.output_background)
            final_outputs[label] = final
            
            if debug: intermediates[f"06_{label}_final"] = final.copy()
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        warnings.append(f"Pipeline error: {str(e)}")
        final_outputs["error"] = image.convert("RGBA")
        detected_type = "error"
        
    end_time = time.time()
    processing_time_ms = int((end_time - start_time) * 1000)
    
    return final_outputs, intermediates, detected_type, processing_time_ms, warnings
