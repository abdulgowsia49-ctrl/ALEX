# syntax=docker/dockerfile:1
# Single service: FastAPI serves the API and the built React dashboard on one origin.
# Verified locally (not via Docker): the API reaches /health in ~16 s and uses ~2.0 GB RAM.
# Needs a host with >= 3 GB RAM (Hugging Face Spaces gives 16 GB free).

FROM node:22-alpine AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# uid 1000 is what Hugging Face Spaces runs containers as.
RUN useradd -m -u 1000 user
COPY requirements-api.txt ./
RUN pip install --upgrade pip && pip install -r requirements-api.txt

COPY backend ./backend
COPY config.yaml ./config.yaml
COPY data/adapters.py data/__init__.py ./data/
# The three cleaned FIRMS CSVs (Git LFS). backend/ingestion.py reads them at start-up.
COPY data/cleaned ./data/cleaned
COPY --from=frontend /app/dist ./frontend/dist

RUN chown -R user:user /app
USER user
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips=*"]
