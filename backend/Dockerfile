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
# Use curl (reliable, retries, no partial file on failure) instead of Python urllib.
RUN mkdir -p /root/.deepface/weights && \
    curl -fL --retry 5 --retry-delay 10 --retry-max-time 300 --connect-timeout 30 \
    -o /root/.deepface/weights/facenet512_weights.h5 \
    "https://github.com/serengil/deepface_models/releases/download/v1.0/facenet512_weights.h5" && \
    echo "Facenet512 weights size: $(du -sh /root/.deepface/weights/facenet512_weights.h5)"

# Copy application
COPY . .

EXPOSE 8080

# Health check - allow enough start-period for TF model loading
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Run with gunicorn. Cloud Run injects PORT (default 8080), so bind to it.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --worker-class gthread --timeout 120 --access-logfile - --error-logfile - app:app"]
