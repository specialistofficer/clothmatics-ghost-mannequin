import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from .api.routes import router
from .config import settings
from .utils.storage import storage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Cleanup old temp files
    storage.cleanup_old_files()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Ghost Mannequin API",
    version=settings.pipeline_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Mount the temp directory to serve output images statically
app.mount("/api/v1/outputs", StaticFiles(directory=settings.temp_dir), name="outputs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host=settings.api_host, port=settings.api_port, reload=settings.api_debug)
