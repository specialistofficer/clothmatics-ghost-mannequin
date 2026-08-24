import os
import time
import uuid
import glob
from pathlib import Path
from ..config import settings

class StorageManager:
    def __init__(self):
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def generate_id(self) -> str:
        return str(uuid.uuid4())

    def get_path(self, request_id: str, filename: str) -> str:
        """Get absolute path for a file associated with a request"""
        req_dir = self.temp_dir / request_id
        req_dir.mkdir(exist_ok=True)
        return str(req_dir / filename)
        
    def get_url(self, request_id: str, filename: str) -> str:
        """Get the API URL to access this file"""
        return f"/api/v1/outputs/{request_id}/{filename}"

    def cleanup_old_files(self):
        """Removes files older than the configured cleanup time."""
        cutoff = time.time() - (settings.temp_cleanup_minutes * 60)
        
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                if os.path.getmtime(file_path) < cutoff:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
            
            # Remove empty directories
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except Exception:
                    pass

storage = StorageManager()
