# dockerfile.prod - Production build for AI Assistant

FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential libssl-dev libffi-dev python3-dev git curl \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy dependency manifests first
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install PyTorch CPU wheels
RUN pip install --no-cache-dir \
    torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (HF Spaces requires 7860)
EXPOSE 7860

# 👇 Environment Variables
ENV PYTHON_ENV=production

# Run FastAPI with Uvicorn (production mode)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "2"]
