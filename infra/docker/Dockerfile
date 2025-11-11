# ==========================================================
# Base image
# ==========================================================
FROM python:3.12-slim AS base

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Working directory
WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy all requirements files (needed for -r base.txt references)
COPY requirements/ /app/requirements/

# Install base requirements
RUN pip install --upgrade pip && pip install -r requirements/base.txt

# Copy project files
COPY . /app

# ==========================================================
# Dev stage
# ==========================================================
FROM base AS dev

# Install dev-specific requirements (includes base.txt via -r)
RUN pip install -r requirements/dev.txt

EXPOSE 8000

# ==========================================================
# Test stage
# ==========================================================
FROM base AS test

# Install test-specific requirements (includes base.txt via -r)
RUN pip install -r requirements/test.txt

# ==========================================================
# Production stage
# ==========================================================
FROM base AS prod

# Install prod-specific requirements (includes base.txt via -r)
RUN pip install -r requirements/prod.txt

# Use non-root user for security
RUN useradd -m django294
USER django294

EXPOSE 8000

# Default production command
# Environment variables loaded from .env.prod
CMD ["gunicorn", "app.core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]