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

# Pre-download MTCNN and Facenet512 model weights during image build so they
# never need network access at runtime (critical for Cloud Run containers).
RUN python -c "import numpy as np; from mtcnn import MTCNN; from deepface import DeepFace; print('Downloading MTCNN...'); MTCNN(); print('Downloading Facenet512...'); DeepFace.represent(np.zeros((160,160,3),dtype='uint8'),model_name='Facenet512',detector_backend='skip',enforce_detection=False); print('All model weights ready')"

# Copy application
COPY . .

EXPOSE 8080

# Health check - allow enough start-period for TF model loading
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Run with gunicorn. Cloud Run injects PORT (default 8080), so bind to it.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --worker-class gthread --timeout 120 --access-logfile - --error-logfile - app:app"]
