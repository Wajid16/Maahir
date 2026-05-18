FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if required (e.g., for cryptography or networking)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables for Vertex AI and Cloud Run
ENV GOOGLE_GENAI_USE_VERTEXAI="TRUE"
ENV PYTHONUNBUFFERED=1

# Expose port 8080 (Cloud Run's default expected port)
EXPOSE 8080

# Command to run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
