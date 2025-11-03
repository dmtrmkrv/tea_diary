# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC

# (опционально) системные пакеты, если вдруг понадобятся колёсам
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# сначала зависимости для кеша слоёв
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# затем — весь код (включая app/, alembic/, alembic.ini и пр.)
COPY . .

# По умолчанию просто стартуем бота; на Timeweb это будет перекрыто Start command-ом
CMD ["bash","-lc","python -m app.main"]
