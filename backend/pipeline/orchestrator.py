from PIL import Image
import time
from . import segmentation, classifier, normalizer, generator, postprocessor
from ..config import settings

def process_pipeline(image: Image.Image, debug: bool = False):
    """
    Orchestrates the entire Ghost Mannequin processing pipeline.
    """
    start_time = time.time()
    intermediates = {}
    warnings = []
    
    # 01. Original
    if debug: intermediates["01_original"] = image.copy()
    
    try:
        # 02 & 03. Segmentation
        mask, cutout = segmentation.segment_garment(image)
        if debug: 
            intermediates["02_mask"] = mask.copy()
            intermediates["03_cutout"] = cutout.copy()
            
        # Garment Classification
        garment_type = classifier.classify(cutout)
        
        # 04. Normalization (Center, Scale)
        normalized = normalizer.normalize(cutout, garment_type, settings.output_max_dimension)
        if debug: intermediates["04_normalized"] = normalized.copy()
        
        # 05. Generation (Ghost Mannequin effect)
        generated = generator.generate(normalized, garment_type, mask)
        if debug: intermediates["05_generated"] = generated.copy()
        
        # 06. Post-process (Format, BG)
        final = postprocessor.process(generated, settings.output_format, settings.output_background)
        if debug: intermediates["06_final"] = final.copy()
        
    except Exception as e:
        warnings.append(f"Pipeline error: {str(e)}")
        # Fallback to returning original if failed
        final = image.convert("RGBA")
        garment_type = "error"
        
    end_time = time.time()
    processing_time_ms = int((end_time - start_time) * 1000)
    
    return final, intermediates, garment_type, processing_time_ms, warnings
