"""
MusicHunter Telegram Bot — обёртка для Mini App
"""
import asyncio
import logging
import os
import sys

# Добавляем backend в path для импорта config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from aiogram import Bot, Dispatcher, Router
from aiogram.types import (
    Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

# URL Mini App — берём из env или дефолт
MINI_APP_URL = os.getenv("FRONTEND_URL", "https://musichunter.vercel.app")


@router.message(CommandStart())
async def start_cmd(message: Message):
    """Приветственное сообщение с кнопкой открытия Mini App"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎵 Открыть MusicHunter",
                web_app=WebAppInfo(url=MINI_APP_URL),
            )
        ],
        [
            InlineKeyboardButton(
                text="📢 Канал Завоз Идей",
                url="https://t.me/zavoz_idey",
            )
        ],
    ])

    await message.answer(
        "🎧 <b>MusicHunter</b>\n\n"
        "Музыка без границ — ищи и слушай прямо в Telegram!\n\n"
        "Нажми кнопку ниже, чтобы открыть плеер 👇",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


# ─── Приём аудиофайлов (на будущее) ──────────
@router.message(lambda m: m.audio or m.voice or m.document)
async def handle_audio(message: Message, bot: Bot):
    """Принимает аудиоф�