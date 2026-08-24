from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from PIL import Image
import io
import time
from typing import Optional

from .models import GhostMannequinResponse, DebugResponse
from ..pipeline.orchestrator import process_pipeline
from ..utils.storage import storage
from ..config import settings

router = APIRouter(prefix="/api/v1")

def _validate_image(file: UploadFile) -> Image.Image:
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Invalid file type. Must be an image.")
    try:
        contents = file.file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGBA")
        return image
    except Exception as e:
        raise HTTPException(400, f"Failed to read image: {str(e)}")

def _save_image(img: Image.Image, request_id: str, name: str) -> str:
    path = storage.get_path(request_id, name)
    img.save(path, format="PNG")
    return storage.get_url(request_id, name)

@router.post("/ghost-mannequin", response_model=GhostMannequinResponse)
async def process_standard(
    image: UploadFile = File(...),
    garmentType: Optional[str] = Form("auto")
):
    request_id = storage.generate_id()
    
    try:
        pil_img = _validate_image(image)
        final, intermediates, detected_type, proc_time, warnings = process_pipeline(pil_img, debug=False)
        
        # Override detected type if user specified one
        g_type = detected_type if garmentType == "auto" else garmentType
        
        # Save final output
        out_url = _save_image(final, request_id, "final.png")
        
        return GhostMannequinResponse(
            success=True,
            request_id=request_id,
            garment_type=g_type,
            processing_time_ms=proc_time,
            warnings=warnings,
            output_url=out_url,
            pipeline_version=settings.pipeline_version
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Internal error: {str(e)}")


@router.post("/ghost-mannequin/debug", response_model=DebugResponse)
async def process_debug(
    image: UploadFile = File(...),
    garmentType: Optional[str] = Form("auto")
):
    if not settings.enable_debug_endpoint:
        raise HTTPException(403, "Debug endpoint is disabled in configuration.")
        
    request_id = storage.generate_id()
    
    try:
        pil_img = _validate_image(image)
        final, intermediates, detected_type, proc_time, warnings = process_pipeline(pil_img, debug=True)
        
        g_type = detected_type if garmentType == "auto" else garmentType
        
        stages = {}
        for stage_name, stage_img in intermediates.items():
            stages[stage_name] = _save_image(stage_img, request_id, f"{stage_name}.png")
            
        return DebugResponse(
            success=True,
            request_id=request_id,
            garment_type=g_type,
            processing_time_ms=proc_time,
            stages=stages,
            warnings=warnings,
            pipeline_version=settings.pipeline_version
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Internal error: {str(e)}")

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "pipeline_version": settings.pipeline_version,
        "gpu_enabled": settings.enable_gpu
    }
