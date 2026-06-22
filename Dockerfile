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
RUN apt-get update && apt-get install -y --no-install-recommends supervisor ffmpeg curl && rm -rf /var/lib/apt/lists/* && curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp && chmod a+rx /usr/local/bin/yt-dlp

COPY supervisord.conf /etc/supervisor/conf.d/musichunter.conf

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
