FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app
COPY server/requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock && useradd --uid 10001 --create-home storeloop
COPY server ./server
COPY packages ./packages
COPY scripts/seed ./scripts/seed
COPY deploy/container_init.py ./deploy/container_init.py
RUN mkdir -p /app/.local/media && chown -R storeloop:storeloop /app/.local
USER storeloop
CMD ["python", "-m", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8102", "--no-access-log"]
