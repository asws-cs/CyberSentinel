# --- Build Stage ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    # Add other build-time dependencies here
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# --- Final Stage ---
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (like external tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    sslscan \
    gobuster \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info \
    # dirsearch requires python3-pip which is already there
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dirsearch separately
RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/maurosoria/dirsearch.git /opt/dirsearch && \
    ln -s /opt/dirsearch/dirsearch.py /usr/local/bin/dirsearch

# Copy installed Python packages from builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/* && rm -rf /wheels

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Set the command to run the application
CMD ["python", "-m", "backend.main", "run-api"]
