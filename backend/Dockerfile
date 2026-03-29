FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download Facenet512 weights during image build so runtime embedding
# extraction never depends on outbound network. Use the same gdown transport as
# DeepFace itself, then validate the HDF5 file before finishing the build.
RUN python - <<'PY'
import os
import time
from pathlib import Path

import gdown
import h5py

url = "https://github.com/serengil/deepface_models/releases/download/v1.0/facenet512_weights.h5"
target = Path("/root/.deepface/weights/facenet512_weights.h5")
target.parent.mkdir(parents=True, exist_ok=True)

last_error = None
for attempt in range(1, 6):
    if target.exists():
        target.unlink()

    print(f"Downloading Facenet512 weights (attempt {attempt}/5)...")
    gdown.download(url, str(target), quiet=False)

    try:
        with h5py.File(target, "r"):
            pass
        print(f"Facenet512 weights verified successfully: {target.stat().st_size} bytes")
        break
    except Exception as err:
        last_error = err
        print(f"Validation failed on attempt {attempt}: {err}")
        if target.exists():
            target.unlink()
        if attempt < 5:
            time.sleep(5 * attempt)
else:
    raise RuntimeError(f"Failed to download valid Facenet512 weights: {last_error}")
PY

# Copy application
COPY . .

EXPOSE 8080

# Health check - allow enough start-period for TF model loading
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Run with gunicorn. Cloud Run injects PORT (default 8080), so bind to it.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --worker-class gthread --timeout 120 --access-logfile - --error-logfile - app:app"]
