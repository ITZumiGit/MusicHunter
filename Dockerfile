FROM python:3.12-slim

WORKDIR /app

# Бэкенд
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Бот
COPY bot/requirements.txt ./bot/requirements.txt
RUN pip install --no-cache-dir -r bot/requirements.txt

COPY backend/ ./backend/
COPY bot/ ./bot/

# Создаём папку для музыки
RUN mkdir -p /app/backend/music

WORKDIR /app/backend
EXPOSE 8000

# Запускаем и бэкенд и бота через supervisord
RUN apt-get update && apt-get install -y --no-install-recommends supervisor && rm -rf /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisor/conf.d/musichunter.conf

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
