# Stage 1: Build
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install

COPY requirements.txt .

# Pre-install CPU-only PyTorch (~150MB instead of 3GB+ GPU/CUDA binaries) and dependencies
RUN pip install --no-cache-dir --prefix=/install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --prefix=/install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Stage 2: Production Runtime
FROM python:3.11-slim

# Install runtime dependencies (libmagic for python-magic)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    openssl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Generate RS256 JWT Keys if they don't exist
RUN mkdir -p /app/keys

EXPOSE 8000

# Default CMD (can be overridden by docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
