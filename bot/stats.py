# -*- coding: utf-8 -*-
"""
MusicHunter Bot — статистика использования
Хранит данные в stats.db (SQLite)
"""
import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "stats.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_stats_db():
    """Создаёт таблицы статистики если их нет"""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            first_seen TEXT,
            last_seen TEXT,
            files_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS bot_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            tg_id INTEGER,
            details TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def record_user_visit(tg_id: int, username: str = None, first_name: str = None):
    """Записывает визит пользователя (при /start)"""
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_conn()
    existing = conn.execute("SELECT tg_id FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
    if existing:
        conn.execute(
            "UPDATE users SET username=?, first_name=?, last_seen=? WHERE tg_id=?",
            (username, first_name, now, tg_id)
        )
    else:
        conn.execute(
            "INSERT INTO users (tg_id, username, first_name, first_seen, last_seen) VALUES (?, ?, ?, ?, ?)",
            (tg_id, username, first_name, now, now)
        )
    conn.commit()
    conn.close()


def record_file_upload(tg_id: int, filename: str, is_group: bool = False):
    """Записывает загрузку файла"""
    conn = _get_conn()
    # Увеличиваем счётчик файлов
    conn.execute("UPDATE users SET files_count = files_count + 1 WHERE tg_id = ?", (tg_id,))
    # Записываем событие
    event_type = "file_group" if is_group else "file_personal"
    conn.execute(
        "INSERT INTO bot_events (event_type, tg_id, details) VALUES (?, ?, ?)",
        (event_type, tg_id, filename)
    )
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Возвращает полную статистику для админа"""
    conn = _get_conn()

    # Всего пользователей
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    # Активные за последние 7 дней
    week_ago = datetime.now(timezone.utc).isoformat()
    # Считаем по строке (ISO формат сортируется как строка)
    from datetime import timedelta
    week_ago_str = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_week = conn.execute(
        "SELECT COUNT(*) FROM users WHERE last_seen >= ?", (week_ago_str,)
    ).fetchone()[0]

    # Активные за последние 24 часа
    day_ago_str = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    active_day = conn.execute(
        "SELECT COUNT(*) FROM users WHERE last_seen >= ?", (day_ago_str,)
    ).fetchone()[0]

    # Всего загруженных файлов
    total_files_result = conn.execute("SELECT SUM(files_count) FROM users").fetchone()[0]
    total_files = total_files_result or 0

    # Пользователи, которые загружали файлы
    uploaders_count = conn.execute("SELECT COUNT(*) FROM users WHERE files_count > 0").fetchone()[0]

    # Последние 10 пользователей
    recent_users = conn.execute(
        "SELECT tg_id, username, first_name, first_seen, last_seen, files_count FROM users ORDER BY last_seen DESC LIMIT 10"
    ).fetchall()

    # Последние 10 загрузок
    recent_uploads = conn.execute(
        "SELECT event_type, tg_id, details, created_at FROM bot_events WHERE event_type LIKE 'file%' ORDER BY created_at DESC LIMIT 10"
    ).fetchall()

    # Топ пользователей по загруженным файлам
    top_uploaders = conn.execute(
        "SELECT tg_id, username, first_name, files_count FROM users WHERE files_count > 0 ORDER BY files_count DESC LIMIT 10"
    ).fetchall()

    conn.close()

    return {
        "total_users": total_users,
        "active_day": active_day,
        "active_week": active_week,
        "total_files": total_files,
        "uploaders_count": uploaders_count,
        "recent_users": [dict(u) for u in recent_users],
        "recent_uploads": [dict(u) for u in recent_uploads],
        "top_uploaders": [dict(u) for u in top_uploaders],
    }


def format_stats_text(stats: dict) -> str:
    """Форматирует статистику в читаемый текст для Telegram"""
    lines = []
    lines.append("📊 <b>Статистика MusicHunter</b>")
    lines.append("")
    lines.append(f"👥 Всего пользователей: <b>{stats['total_users']}</b>")
    lines.append(f"📅 Активных за 24ч: <b>{stats['active_day']}</b>")
    lines.append(f"📆 Активных за 7 дней: <b>{stats['active_week']}</b>")
    lines.append("")
    lines.append(f"🎵 Всего файлов загружено: <b>{stats['total_files']}</b>")
    lines.append(f"📤 Загрузили хотя бы 1 файл: <b>{stats['uploaders_count']}</b>")

    # Топ загрузчиков
    if stats["top_uploaders"]:
        lines.append("")
        lines.append("🏆 <b>Топ загрузчиков:</b>")
        for i, u in enumerate(stats["top_uploaders"], 1):
            name = u.get("username") or u.get("first_name") or str(u["tg_id"])
            lines.append(f"  {i}. {name} — {u['files_count']} файл(ов)")

    # Последние пользователи
    if stats["recent_users"]:
        lines.append("")
        lines.append("👤 <b>Последние пользователи:</b>")
        for u in stats["recent_users"][:5]:
            name = u.get("username") or u.get("first_name") or str(u["tg_id"])
            files = f" ({u['files_count']}🎵)" if u["files_count"] > 0 else ""
            lines.append(f"  • {name}{files}")

    # Последние загрузки
    if stats["recent_uploads"]:
        lines.append("")
        lines.append("📥 <b>Последние загрузки:</b>")
        for u in stats["recent_uploads"][:5]:
            name = u.get("details", "unknown")
            lines.append(f"  • {name}")

    return "\n".join(lines)
