import modal
import os

# Define the environment with all our requirements
image = (
    modal.Image.debian_slim()
    .pip_install(
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pillow",
        "rembg[cli]",
        "diffusers",
        "transformers",
        "accelerate",
        "torch",
        "torchvision",
        "opencv-python-headless"
    )
)

app = modal.App("clothmatics-ghost-mannequin-api")

# We request a T4 GPU. This will run our entire pipeline (SegFormer + rembg + Stable Diffusion) in seconds.
@app.function(image=image, gpu="T4")
@modal.asgi_app()
def fastapi_app():
    # Set an environment variable so our config knows we are in production/Modal
    os.environ["ENVIRONMENT"] = "production"
    
    # Import the FastAPI app from our backend folder
    from backend.app import app as web_app
    return web_app
