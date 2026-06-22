import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# VK Music (необязателен для MVP — можно искать без авторизации)
VK_LOGIN = os.getenv("VK_LOGIN", "")
VK_PASSWORD = os.getenv("VK_PASSWORD", "")

# Сервер
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://t.me")
