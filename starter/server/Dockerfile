FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY starter/server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY starter/server/mirror_service /app/mirror_service
COPY starter/clients/pwa /app/pwa

RUN useradd --create-home --uid 10001 mirror && \
    mkdir -p /data && chown -R mirror:mirror /data /app
USER mirror

ENV MIRROR_META_DB=/data/mirror-meta.sqlite3 \
    MIRROR_FILE_STORE=/data/evidence \
    MIRROR_WEB_ROOT=/app/pwa \
    MIRROR_PORT=8080

EXPOSE 8080
CMD ["sh", "-c", "uvicorn mirror_service.app:app --host 0.0.0.0 --port ${MIRROR_PORT:-8080}"]
