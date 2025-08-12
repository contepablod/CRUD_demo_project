# ---------- builder ----------
FROM python:3.12-slim AS builder

# System build deps (needed to compile some wheels like asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /wheels
COPY requirements.txt ./

# Build wheels for all deps (offline-install later)
RUN pip install --upgrade pip wheel && \
    pip wheel --no-cache-dir -r requirements.txt -w /wheels

# ---------- runtime ----------
FROM python:3.12-slim AS runtime

# Minimal runtime libs (libpq for Postgres at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy app code
COPY app ./app
COPY requirements.txt ./

# Copy prebuilt wheels and install (no network)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host","0.0.0.0","--port","8000"]