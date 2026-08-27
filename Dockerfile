# Use official lightweight Python image (Works perfectly on Oracle ARM Ampere CPUs too)
FROM python:3.10-slim

# Install system libraries required by OpenCV and Rembg
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
# Note: We use the cpu-only index for torch to save space and memory
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy the entire project into the container
COPY . .

# Create the temp directory for outputs
RUN mkdir -p tmp

# Expose the API port
EXPOSE 8000

# Start the FastAPI server
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
