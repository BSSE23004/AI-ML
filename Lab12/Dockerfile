# ──────────────────────────────────────────────────────────────
# Dockerfile — Lab 12: Flask ML Deployment
# ──────────────────────────────────────────────────────────────

# Use a slim official Python image as the base
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency manifest first (layer-cache optimization:
# dependencies only reinstall when requirements.txt changes)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and templates
COPY app.py .
COPY templates/ templates/

# Copy the serialized model produced by Lab 11's run_pipeline()
# Make sure model.joblib exists in the build context before running
# docker build, or remove this line and mount it at runtime.
COPY model.joblib .

# Expose the port Flask will listen on
EXPOSE 5000

# Run the Flask application
# host=0.0.0.0 makes the server reachable from outside the container
CMD ["python", "app.py"]
