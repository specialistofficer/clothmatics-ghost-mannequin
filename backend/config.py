from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    cors_origins: str = "http://localhost:3000,http://localhost:5500,http://127.0.0.1:3000,http://127.0.0.1:5500"
    
    max_upload_size_mb: int = 20
    output_format: str = "png"
    output_background: str = "transparent"
    output_max_dimension: int = 1024
    
    temp_dir: str = "./tmp"
    temp_cleanup_minutes: int = 60
    
    pipeline_version: str = "GM-0.1.0"
    enable_debug_endpoint: bool = True
    enable_gpu: str = "auto"
    rate_limit: str = "10/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

settings = Settings()

# Ensure temp directory exists
os.makedirs(settings.temp_dir, exist_ok=True)
