# 🎵 MusicHunter — Telegram Mini App

Нецензурированная музыка без ограничений. Прямо в Telegram.

## 🎯 Возможности

- 🔍 **Поиск** — находи любую музыку (без цензуры)
- ❤️ **Лайки** — сохраняй любимые треки
- 📁 **Плейлисты** — создавай и управляй своими подборками
- 🕐 **История** — что слушал, всегда под рукой
- 🎧 **Полный плеер** — мини + расширенный режим
- 📱 **TG Mini App** — работает внутри Telegram, без установки

## 🛠️ Стек

### Backend (FastAPI + SQLite)
```
backend/
├── main.py           # API сервер (FastAPI)
├── music_service.py  # Парсинг источников + поиск
├── database.py       # Модели БД (SQLAlchemy)
├── config.py         # Конфигурация
└── requirements.txt
```

**API Endpoints:**

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/search?q=...` | Поиск треков |
| GET | `/stream/{track_id}` | Получить URL стрима |
| POST | `/likes/{tg_id}` | Лайк/дизлайк (toggle) |
| GET | `/likes/{tg_id}` | Список лайков |
| DELETE | `/likes/{tg_id}/{track_id}` | Убрать лайк |
| POST | `/playlists/{tg_id}` | Создать плейлист |
| GET | `/playlists/{tg_id}` | Список плейлистов |
| GET | `/playlists/{tg_id}/{id}` | Треки плейлиста |
| PUT | `/playlists/{tg_id}/{id}` | Обновить плейлист |
| DELETE | `/playlists/{tg_id}/{id}` | Удалить плейлист |
| POST | `/playlists/{tg_id}/{id}/tracks` | Добавить трек |
| DELETE | `/playlists/{tg_id}/{id}/tracks/{track_id}` | Убрать трек |
| POST | `/history/{tg_id}` | Записать прослушивание |
| GET | `/history/{tg_id}` | История (последние 100) |
| DELETE | `/history/{tg_id}` | Очистить историю |
| GET | `/stats/{tg_id}` | Статистика |

### Frontend (Vue 3 + TypeScript)
```
frontend/
├── src/
│   ├── App.vue              # Главное приложение + навигация
│   ├── components/
│   │   ├── SearchBar.vue    # Строка поиска
│   │   ├── TrackCard.vue    # Карточка трека + лайк
│   │   └── Player.vue       # Мини + полный плеер
│   ├── composables/
│   │   ├── usePlayer.ts     # Логика плеера + лайки + история
│   │   └── useTelegram.ts   # TG SDK интеграция
│   └── services/
│       └── api.ts           # API клиент v2
├── index.html
├── vite.config.ts
└── package.json
```

### Bot (aiogram 3)
```
bot/
├── main.py       # Запуск бота
└── requirements.txt
```

## 🚀 Запуск

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
# → http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Bot
```bash
cd bot
pip install -r requirements.txt
BOT_TOKEN=your_token python main.py
```

## 📦 Деплой

| Компонент | Платформа | URL |
|-----------|-----------|-----|
| Frontend | Vercel | `https://musichunter.vercel.app` |
| Backend | Render | `https://musichunter-api.onrender.com` |
| Bot | Railway | — |

## ⚠️ Источники музыки

Приоритет поиска:
1. **Пиратские сайты** (полные mp3, без цензуры) — ChiaSeNhac, Zaycev и др.
2. **Audius** (легальный fallback, децентрализованный стриминг)

На прод-сервере доступны дополнительные источники через yt-dlp.
