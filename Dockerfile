# ── Stage 1: Choose a base image ──────────────────────────────────────────────
# We start from an official Python 3.12 image on Debian Slim (small size).
# "slim" variants are minimal, reducing image size and attack surface.
FROM python:3.12-slim

# ── Stage 2: Set up the environment ───────────────────────────────────────────
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc cache files
# PYTHONUNBUFFERED: Prevents Python from buffering stdout/stderr (logs show immediately)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ── Stage 3: Set working directory ────────────────────────────────────────────
# This is the folder inside the container where our code will live.
# All subsequent commands run from this folder.
WORKDIR /app

# ── Stage 4: Install system dependencies ──────────────────────────────────────
# psycopg2 (our postgres driver) requires libpq-dev at build time.
# We clean up apt cache afterwards to keep the image small.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Stage 5: Install Python dependencies ──────────────────────────────────────
# We copy requirements.txt FIRST (before the rest of the code).
# Docker caches each step. If requirements.txt hasn't changed, this
# layer is cached and won't re-run — making rebuilds much faster.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 6: Copy the source code ─────────────────────────────────────────────
# Now we copy everything else. Changes to source code won't invalidate
# the pip install cache layer above.
COPY . .

# ── Stage 7: Expose the port ──────────────────────────────────────────────────
# This documents which port the container listens on (doesn't actually open it).
EXPOSE 8000

# ── Stage 8: Default start command ────────────────────────────────────────────
# What runs when the container starts. We use gunicorn for production.
CMD ["gunicorn", "takhtit.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
