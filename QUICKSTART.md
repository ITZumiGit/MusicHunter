# MusicHunter — Быстрый старт

## 1. Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API запустится на `http://localhost:8000`

Проверка: открой `http://localhost:8000/search?q=eminem&limit=5`

## 2. Frontend (Vue 3)

```bash
cd frontend
npm install
npm run dev
```

Фронт запустится на `http://localhost:3000`

## 3. Telegram Bot

```bash
cd bot
pip install -r requirements.txt

# Установи токен бота
set BOT_TOKEN=твой_токен_от_BotFather

python main.py
```

## Деплой

### Frontend → Vercel
```bash
cd frontend
npm run build
# Залить на Vercel через CLI или GitHub
```

### Backend → Render
- Создать Web Service на render.com
- Указать `backend` как root директорию
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Bot → Railway
- Создать сервис на railway.app
- Установить BOT_TOKEN как переменную окружения
- Start: `python bot/main.py`
