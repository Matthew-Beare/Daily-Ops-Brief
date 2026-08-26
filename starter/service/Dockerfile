FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MIRROR_DATA_DIR=/data \
    MIRROR_AUTH_MODE=required \
    MIRROR_EVIDENCE_PROVIDER=auto \
    MIRROR_CORS_ORIGINS=http://localhost:8765,http://127.0.0.1:8765,http://tauri.localhost,https://tauri.localhost,tauri://localhost,https://appassets.androidplatform.net,null

WORKDIR /app
COPY starter/service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY starter/service/app.py /app/app.py
COPY starter/service/provider_extensions.py /app/provider_extensions.py
COPY starter/service/platform_foundations.py /app/platform_foundations.py
COPY starter/service/product_v1.py /app/product_v1.py
COPY starter/service/experience_v3.py /app/experience_v3.py
COPY starter/service/inventory_hierarchy.py /app/inventory_hierarchy.py
COPY starter/service/enrichment.py /app/enrichment.py
COPY starter/service/receipts.py /app/receipts.py
COPY starter/service/receipt_processing.py /app/receipt_processing.py
COPY starter/service/reconciliation.py /app/reconciliation.py
COPY starter/service/merchants.py /app/merchants.py
COPY starter/service/integrations.py /app/integrations.py
COPY starter/service/media.py /app/media.py
COPY starter/service/maintenance.py /app/maintenance.py
COPY starter/service/migration_apply.py /app/migration_apply.py
COPY starter/service/backup_scheduler.py /app/backup_scheduler.py
COPY starter/service/device_auth.py /app/device_auth.py
COPY starter/service/oauth_hardening.py /app/oauth_hardening.py
COPY starter/service/idempotency.py /app/idempotency.py
COPY starter/service/release_guard.py /app/release_guard.py
COPY starter/service/signed_media.py /app/signed_media.py
COPY starter/service/run.py /app/run.py
COPY starter/integration-catalog.json /app/integration-catalog.json
COPY starter/backup-policy.json /app/backup-policy.json
COPY starter/deployment-modes.json /app/deployment-modes.json
COPY starter/clients/release.json /app/release.json
COPY starter/clients/pwa /app/ui
RUN mkdir -p /data/evidence/receipts /data/backups && useradd --system --uid 10001 --home /nonexistent --shell /usr/sbin/nologin mirror && chown -R mirror:mirror /data /app

USER mirror
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/v1/health', timeout=3).read()"

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8765", "--proxy-headers", "--forwarded-allow-ips", "*"]
