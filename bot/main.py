# -*- coding: utf-8 -*-
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
    """Принимает аудиофайлы и сохраняет в backend/music/"""
    music_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'music')
    os.makedirs(music_dir, exist_ok=True)

    # Определяем файл
    if message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or f"audio_{message.message_id}.mp3"
    elif message.voice:
        file_id = message.voice.file_id
        file_name = f"voice_{message.message_id}.ogg"
    elif message.document and message.document.mime_type and message.document.mime_type.startswith("audio"):
        file_id = message.document.file_id
        file_name = message.document.file_name or f"file_{message.message_id}.mp3"
    else:
        return

    # Скачиваем через Telegram API
    try:
        file = await bot.get_file(file_id)
        downloaded = await bot.download_file(file.file_path)

        save_path = os.path.join(music_dir, file_name)
        with open(save_path, "wb") as f:
            f.write(downloaded.read())

        await message.reply(f"✅ <b>{file_name}</b> добавлен в библиотеку!", parse_mode="HTML")
        logger.info(f"Audio saved: {file_name}")
    except Exception as e:
        logger.error(f"Error saving audio: {e}")
        await message.reply("❌ Ошибка при сохранении файла.")


async def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("❌ BOT_TOKEN не задан! Установи переменную окружения.")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("🤖 MusicHunter Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
