# ── Base ────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Prevents Python from writing .pyc files & enables unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5002

# System deps (keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates tzdata \
 && rm -rf /var/lib/apt/lists/*

# ── App setup ───────────────────────────────────────────────────────────────────
WORKDIR /app

# Install Python deps first (better Docker layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy the rest of the source
COPY . /app

# Make sure the container listens on 5002 (CapRover maps to this)
EXPOSE 5002

# Optional: a lightweight healthcheck (expects 200 from /)
HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
  CMD curl -fsS http://localhost:${PORT}/ || exit 1

# ── Start ───────────────────────────────────────────────────────────────────────
# IMPORTANT: your Flask app module must expose `app = Flask(__name__)`
# (your app.py already does). If the file/module name differs, change "app:app".
CMD ["gunicorn", "-w", "2", "-k", "gthread", "-t", "120", "-b", "0.0.0.0:5002", "app:app"]
