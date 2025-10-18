# Use the official Python 3.13 slim image from Docker Hub with uv pre-installed
FROM ghcr.io/astral-sh/uv:0.5.22-python3.13-bookworm

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Cache dir for UV
ENV UV_CACHE_DIR=.cache/uv

# Install system dependencies, Java, ffmpeg, and Python packages
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy application
COPY . /app

# Installing separately from its dependencies allows optimal layer caching
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Expose port 8000
EXPOSE 8000

# Command to run the app using Gunicorn with Uvicorn workers
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]