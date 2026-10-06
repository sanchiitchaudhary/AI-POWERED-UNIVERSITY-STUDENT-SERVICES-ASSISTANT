FROM python:3.9-slim

# Install system dependencies & Tesseract OCR (Section J)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY package.json package-lock.json ./
COPY tsconfig*.json vite.config.ts ./
COPY backend ./backend
COPY data ./data
COPY scripts ./scripts
COPY eval ./eval
COPY docs ./docs
COPY src ./src
COPY index.html ./

RUN pip install --no-cache-dir fastapi uvicorn pydantic chromadb pypdf python-docx requests pytest

EXPOSE 8000 5173

CMD ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
