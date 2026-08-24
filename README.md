# Ghost Mannequin MVP

An experimental AI pipeline for creating professional ghost mannequin/invisible mannequin product images from ordinary garment photos.

## Requirements
- Python 3.11+
- CPU is supported for Phase 1. 
- GPU is recommended for future Phase 2.

## Setup
1. Clone this repository.
2. Setup virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Copy `.env.example` to `.env`

## Running Locally

1. **Start the API Backend**:
   ```bash
   python -m backend.app
   ```
   The API will be available at `http://localhost:8000`.

2. **Start the Frontend UI**:
   Use any simple HTTP server to serve the frontend folder. For example:
   ```bash
   npx serve frontend
   # or
   python -m http.server 3000 --directory frontend
   ```

3. Open `http://localhost:3000` in your browser.

## API Documentation
The main endpoint is `POST /api/v1/ghost-mannequin`. Send `multipart/form-data` with an `image` key.
For intermediate pipeline visualizations, use `POST /api/v1/ghost-mannequin/debug`.

## Note on Commercial Use
This project uses only commercially-viable open source models (`rembg` with U2-Net, MIT License).
