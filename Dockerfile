# ---------------------------------------------------------------------------
# Base image
# ---------------------------------------------------------------------------
# Use a slim Python image to keep the final image size small.
FROM python:3.11-slim

# ---------------------------------------------------------------------------
# Working directory
# ---------------------------------------------------------------------------
# All subsequent commands will run relative to this directory inside the container.
WORKDIR /app

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
# Copy requirements first to leverage Docker layer caching.
# As long as requirements.txt does not change, this layer is reused on rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Application code
# ---------------------------------------------------------------------------
COPY app.py .
COPY fetch_characters.py .

# ---------------------------------------------------------------------------
# Runtime configuration
# ---------------------------------------------------------------------------
# Expose the port Flask listens on.
EXPOSE 5000

# Start the Flask application.
CMD ["python", "app.py"]