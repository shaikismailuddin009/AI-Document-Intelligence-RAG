FROM python:3.14-slim

WORKDIR /app

# System deps needed by some ML wheels (torch/onnxruntime) at import time,
# plus curl for the container HEALTHCHECK below
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Persistent data lives outside the image, mounted as a volume in compose
RUN mkdir -p app/data/uploads app/data/chroma

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Pre-downloading the embedding model into the image is left to the user —
# see README "Docker" section — so first container start may take longer
# while sentence-transformers fetches all-MiniLM-L6-v2.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
