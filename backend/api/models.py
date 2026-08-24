from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GhostMannequinResponse(BaseModel):
    success: bool
    request_id: str
    garment_type: str
    processing_time_ms: int
    fidelity_score: Optional[float] = None
    warnings: List[str] = []
    output_url: str
    pipeline_version: str

class DebugResponse(BaseModel):
    success: bool
    request_id: str
    garment_type: str
    processing_time_ms: int
    stages: Dict[str, str]  # Map of stage name to image URL
    warnings: List[str] = []
    pipeline_version: str
