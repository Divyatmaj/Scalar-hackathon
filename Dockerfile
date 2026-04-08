# OpenEnv-compliant Dockerfile for AI Interview Prep RL Environment
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# HuggingFace Spaces uses port 7860, fallback to 8000 for local Docker
ENV PORT=7860
EXPOSE 7860

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1
ENV API_BASE_URL=https://router.huggingface.co/v1
ENV MODEL_NAME=Qwen/Qwen3-Coder-Next:novita

# Run FastAPI server — uses $PORT so it works on HF Spaces (7860) and local (override with -e PORT=8000)
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
