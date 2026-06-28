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

from stats import init_stats_db, record_user_visit, record_file_upload, get_stats, format_stats_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

# URL Mini App — берём из env или дефолт
MINI_APP_URL = os.getenv("FRONTEND_URL", "https://music-hunter-llart.vercel.app")

# Админ — только этот ID может смотреть статистику
ADMIN_ID = 907830810


@router.message(CommandStart())
async def start_cmd(message: Message):
    """Приветственное сообщение с кнопкой открытия Mini App"""
    # Записываем пользователя в статистику
    record_user_visit(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

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
                url="https://t.me/zavozide",
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


# ─── Приём аудиофайлов ──────────────────────
@router.message(lambda m: m.audio or m.voice or m.document)
async def handle_audio(message: Message, bot: Bot):
    """Принимает аудиофайлы и сохраняет в music/{tg_id}/ (личка) или music/chat_{chat_id}/ (группа)"""
    music_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'music')

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

    # Личная переписка → music/{tg_id}/, группа → music/chat_{chat_id}/
    chat_id = message.chat.id
    is_group = message.chat.type in ("group", "supergroup")
    if is_group:
        save_dir = os.path.join(music_dir, f"chat_{chat_id}")
    else:
        save_dir = os.path.join(music_dir, str(message.from_user.id))

    os.makedirs(save_dir, exist_ok=True)

    # Скачиваем через Telegram API
    try:
        file = await bot.get_file(file_id)
        downloaded = await bot.download_file(file.file_path)

        save_path = os.path.join(save_dir, file_name)
        with open(save_path, "wb") as f:
            f.write(downloaded.read())

        await message.reply(f"✅ <b>{file_name}</b> добавлен в библиотеку!", parse_mode="HTML")
        logger.info(f"Audio saved: {save_path}")

        # Записываем в статистику
        uploader_id = message.from_user.id
        record_file_upload(tg_id=uploader_id, filename=file_name, is_group=is_group)

    except Exception as e:
        logger.error(f"Error saving audio: {e}")
        await message.reply("❌ Ошибка при сохранении файла.")


# ─── Статистика для админа ─────────────────
from aiogram.filters import Command

@router.message(Command("stats"))
async def stats_cmd(message: Message):
    """Команда /stats — доступна только админу"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔️ У вас нет доступа к этой команде.")
        return

    stats = get_stats()
    text = format_stats_text(stats)
    await message.answer(text, parse_mode="HTML")


async def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("❌ BOT_TOKEN не задан! Установи переменную окружения.")
        return

    # Инициализируем базу статистики
    init_stats_db()

    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("🤖 MusicHunter Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
