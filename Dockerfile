# Stage 1: Build SvelteKit dashboard
FROM oven/bun:1 AS frontend
WORKDIR /frontend
COPY dashboard-app/package.json dashboard-app/bun.lock* ./
RUN bun install --frozen-lockfile || bun install
COPY dashboard-app/ ./
RUN bun run build

# Stage 2: Python backend
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY static/ static/

# Copy SvelteKit build from stage 1
COPY --from=frontend /frontend/build/ dashboard-app/build/

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
