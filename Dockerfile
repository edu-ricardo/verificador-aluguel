# Stage 1: Build do Frontend React
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build

# Stage 2: Runtime unificado Python FastAPI + Frontend Estático
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite+aiosqlite:////app/data/aluguel.db

RUN mkdir -p /app/data /app/static

COPY backend/requirements.txt .
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    --prefer-binary \
    -r requirements.txt

COPY backend/ /app/
COPY --from=frontend-builder /app/dist /app/static

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
