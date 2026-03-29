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
# extraction never depends on outbound network. DeepFace's original GitHub
# release asset is no longer available, so use a live mirror and validate the
# downloaded HDF5 file before finishing the build.
RUN mkdir -p /root/.deepface/weights && \
    curl -fL --retry 5 --retry-delay 10 --retry-max-time 300 --connect-timeout 30 \
    -o /root/.deepface/weights/facenet512_weights.h5 \
    "https://huggingface.co/WePrompt/deepface-weights/resolve/main/facenet512_weights.h5" && \
    python - <<'PY'
from pathlib import Path
import h5py

target = Path('/root/.deepface/weights/facenet512_weights.h5')
with h5py.File(target, 'r'):
    pass
print(f"Facenet512 weights verified successfully: {target.stat().st_size} bytes")
PY

# Copy application
COPY . .

EXPOSE 8080

# Health check - allow enough start-period for TF model loading
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Run with gunicorn. Cloud Run injects PORT (default 8080), so bind to it.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --worker-class gthread --timeout 120 --access-logfile - --error-logfile - app:app"]
