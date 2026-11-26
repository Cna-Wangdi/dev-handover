FROM node:22-bookworm-slim AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1
WORKDIR /app/backend
COPY backend/requirements.txt backend/requirements-render.txt ./
RUN pip install --no-cache-dir -r requirements-render.txt
COPY backend/ ./
COPY --from=frontend /app/dist /app/frontend/dist
ENV DJANGO_SETTINGS_MODULE=config.render_settings
CMD ["sh", "start-render.sh"]
