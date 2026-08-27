#!/bin/bash
# Oracle Cloud 1-Click Deployment Script

echo "Fetching latest updates from GitHub..."
git pull origin main

echo "Building Docker Container for Ghost Mannequin API..."
# This will download the python environment and install all packages
sudo docker build -t clothmatics-api .

echo "Stopping old API if running..."
sudo docker stop ghost-api || true
sudo docker rm ghost-api || true

echo "Starting new API on port 8000..."
# We map the local 'tmp' folder to the container's 'tmp' folder so generated images persist
sudo docker run -d --name ghost-api --restart unless-stopped -p 8000:8000 -v $(pwd)/tmp:/app/tmp clothmatics-api

echo "========================================="
echo "Deployment Successful!"
echo "API is now running in the background."
echo "You can check logs using: sudo docker logs -f ghost-api"
echo "========================================="
