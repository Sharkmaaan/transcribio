# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.9
FROM python:${PYTHON_VERSION}-slim as base

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
    
# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies including ffmpeg for moviepy
RUN apt-get update && \
    apt-get install -y \
    libpq-dev \
    gcc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Create media directories with proper permissions BEFORE switching user
RUN mkdir -p /app/media/videos && \
    chmod -R 777 /app/media

# Download dependencies as a separate step to take advantage of Docker's caching.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY --chown=appuser:appuser . .

# Switch to the non-privileged user to run the application.
USER appuser

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD gunicorn 'transcripio.wsgi:application' --bind=0.0.0.0:8000