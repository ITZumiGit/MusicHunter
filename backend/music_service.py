"""
MusicHunter v4 — полноценный музыкальный поисковик

Источники поиска:
  1. YouTube InnerTube API (прямой доступ, русская локаль, без прокси)
  2. Deezer API (публичный, отличная база русской музыки)
  3. Audius (инди/легальный)

Стриминг:
  1. Piped API (инстансы с автовыбором)
  2. Invidious API (инстансы с автовыбором)
  3. Cobalt API (надёжный YouTube загрузчик)
"""
import json
import re
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

import aiohttp
from aiocache import cached

logger = logging.getLogger("musichunter")


@dataclass
class Track:
    """Модель трека"""
    id: str
    title: str
    artist: str
    duration: int = 0
    url: str = ""
    cover_url: str = ""

    @property
    def duration_str(self) -> str:
        m, s = divmod(self.duration, 60)
        return f"{m}:{s:02d}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "duration_str": self.duration_str,
            "url": self.url,
            "cover_url": self.cover_url,
        }


# ─────────────────────────────────────────────────────────────
# YouTube InnerTube — прямой поиск, без прокси-серверов
# ─────────────────────────────────────────────────────────────

class InnerTubeSource:
    """
    Прямой поиск через YouTube InnerTube API.
    Это тот же API, который использует веб-клиент YouTube.
    - Без прокси, без ключей, без ограничений
    - Полная поддержка русского языка (hl=ru, gl=RU)
    - Огромная база: вся музыка мира, включая русскую
    """

    API_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
    BASE_URL = "https://www.youtube.com/youtubei/v1/search"

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=15),
            )
        return self._session

    async def search(self, query: str, limit: int = 30) -> list[Track]:
        """Поиск через InnerTube — два запроса параллельно: Music + Video"""
        results = await asyncio.gather(
            self._search_music(query, limit),
            self._search_videos(query, limit),
            return_exceptions=True,
        )

        all_tracks: list[Track] = []
        seen: set[str] = set()

        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"[InnerTube] Search error: {result}")
                continue
            for t in result:
                if t.id not in seen:
                    seen.add(t.id)
                    all_tracks.append(t)

        return all_tracks[:limit]

    async def _search_music(self, query: str, limit: int) -> list[Track]:
        """Поиск через YouTube Music клиент (WEB_REMIX)"""
        body = {
            "context": {
                "client": {
                    "clientName": "WEB_REMIX",
                    "clientVersion": "1.20250610.00.00",
                    "hl": "ru",
                    "gl": "RU",
                }
            },
            "query": query,
        }
        return await self._do_search(body, limit, mode="music")

    async def _search_videos(self, query: str, limit: int) -> list[Track]:
        """Поиск через обычный YouTube (WEB) — шире охват"""
        body = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20250610.00.00",
                    "hl": "ru",
                    "gl": "RU",
                }
            },
            "query": query,
        }
        return await self._do_search(body, limit, mode="video")

    async def _do_search(self, body: dict, limit: int, mode: str = "video") -> list[Track]:
        """Выполнить поиск и распарсить результаты"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}?key={self.API_KEY}"

            async with session.post(url, json=body) as resp:
                if resp.status != 200:
                    logger.warning(f"[InnerTube] HTTP {resp.status} for {mode} search")
                    return []

                data = await resp.json()

                if mode == "music":
                    return self._parse_music_results(data, limit)
                else:
                    return self._parse_video_results(data, limit)
        except Exception as e:
            logger.warning(f"[InnerTube] {mode} search error: {e}")
            return []

    def _parse_music_results(self, data: dict, limit: int) -> list[Track]:
        """Парсинг WEB_REMIX ответа (YouTube Music)"""
        tracks = []
        try:
            tabs = (
                data.get("contents", {})
                .get("tabbedSearchResultsRenderer", {})
                .get("tabs", [])
            )
            for tab in tabs:
                sections = (
                    tab.get("tabRenderer", {})
                    .get("content", {})
                    .get("sectionListRenderer", {})
                    .get("contents", [])
                )
                for section in sections:
                    shelf = section.get("musicShelfRenderer")
                    if not shelf:
                        continue

                    for item in shelf.get("contents", []):
                        renderer = item.get("musicResponsiveListItemRenderer")
                        if not renderer:
                            continue

                        track = self._extract_music_track(renderer)
                        if track:
                            tracks.append(track)

                        if len(tracks) >= limit:
                            return tracks
        except Exception as e:
            logger.warning(f"[InnerTube] Music parse error: {e}")

        return tracks

    def _extract_music_track(self, renderer: dict) -> Optional[Track]:
        """Извлечь Track из musicResponsiveListItemRenderer"""
        try:
            # videoId
            video_id = (
                renderer.get("playlistItemData", {})
                .get("videoId", "")
            )
            if not video_id:
                # Альтернативный путь
                overlay = renderer.get("overlay", {})
                nav = overlay.get("musicItemThumbnailOverlayRenderer", {}).get(
                    "content", {}
                ).get("musicPlayButtonRenderer", {}).get(
                    "playNavigationEndpoint", {}
                ).get("watchEndpoint", {})
                video_id = nav.get("videoId", "")

            if not video_id:
                return None

            # Title
            flex_columns = renderer.get("flexColumns", [])
            title = ""
            artist = ""
            duration_str = ""

            if len(flex_columns) >= 1:
                runs = (
                    flex_columns[0]
                    .get("musicResponsiveListItemFlexColumnRenderer", {})
                    .get("text", {})
                    .get("runs", [])
                )
                title = "".join(r.get("text", "") for r in runs)

            if len(flex_columns) >= 2:
                runs = (
                    flex_columns[1]
                    .get("musicResponsiveListItemFlexColumnRenderer", {})
                    .get("text", {})
                    .get("runs", [])
                )
                artist = " ".join(r.get("text", "") for r in runs if r.get("text"))

            if len(flex_columns) >= 3:
                runs = (
                    flex_columns[2]
                    .get("musicResponsiveListItemFlexColumnRenderer", {})
                    .get("text", {})
                    .get("runs", [])
                )
                duration_str = "".join(r.get("text", "") for r in runs)

            # Duration
            duration = self._parse_duration_text(duration_str)

            # Фильтр: отбрасываем слишком длинные (>2ч) или слишком короткие (<15с)
            if duration > 7200 or (0 < duration < 15):
                return None

            # Cover
            cover = ""
            thumbs = (
                renderer.get("thumbnail", {})
                .get("musicThumbnailRenderer", {})
                .get("thumbnail", {})
                .get("thumbnails", [])
            )
            for thumb in thumbs:
                cover = thumb.get("url", cover)
                if "maxres" in thumb.get("url", "") or "hq" in thumb.get("url", ""):
                    cover = thumb["url"]
                    break

            return Track(
                id=f"yt_{video_id}",
                title=self._clean_title(title or "Unknown"),
                artist=artist or "Unknown",
                duration=duration,
                url="",
                cover_url=cover,
            )
        except Exception as e:
            logger.debug(f"[InnerTube] Extract music track error: {e}")
            return None

    def _parse_video_results(self, data: dict, limit: int) -> list[Track]:
        """Парсинг WEB ответа (обычный YouTube)"""
        tracks = []
        try:
            contents = (
                data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
            )
            for section in contents:
                items = section.get("itemSectionRenderer", {}).get("contents", [])
                for item in items:
                    renderer = item.get("videoRenderer")
                    if not renderer:
                        continue

                    track = self._extract_video_track(renderer)
                    if track:
                        tracks.append(track)

                    if len(tracks) >= limit:
                        return tracks
        except Exception as e:
            logger.warning(f"[InnerTube] Video parse error: {e}")

        return tracks

    def _extract_video_track(self, renderer: dict) -> Optional[Track]:
        """Извлечь Track из videoRenderer"""
        try:
            video_id = renderer.get("videoId", "")
            if not video_id:
                return None

            # Title
            title = ""
            title_runs = renderer.get("title", {}).get("runs", [])
            if title_runs:
                title = title_runs[0].get("text", "")

            # Artist (channel name)
            artist = ""
            byline = renderer.get("longBylineText", renderer.get("ownerText", {}))
            byline_runs = byline.get("runs", [])
            if byline_runs:
                artist = byline_runs[0].get("text", "")

            # Duration
            duration_text = renderer.get("lengthText", {}).get("simpleText", "")
            duration = self._parse_duration_text(duration_text)

            # Фильтр: отбрасываем длинные/короткие
            if duration > 7200 or (0 < duration < 15):
                return None

            # Live-стримы отбрасываем
            if renderer.get("badges"):
                for badge in renderer.get("badges", []):
                    label = badge.get("metadataBadgeRenderer", {}).get("label", "")
                    if label.lower() in ("live", "live now", "прямой эфир"):
                        return None

            # Cover
            cover = ""
            thumbnails = renderer.get("thumbnail", {}).get("thumbnails", [])
            for thumb in thumbnails:
                cover = thumb.get("url", cover)
                if thumb.get("width", 0) >= 320:
                    cover = thumb["url"]

            return Track(
                id=f"yt_{video_id}",
                title=self._clean_title(title or "Unknown"),
                artist=artist or "Unknown",
                duration=duration,
                url="",
                cover_url=cover,
            )
        except Exception as e:
            logger.debug(f"[InnerTube] Extract video track error: {e}")
            return None

    def _clean_title(self, title: str) -> str:
        """Убрать мусор из названия"""
        patterns = [
            r'\s*\(Official\s*Video\)', r'\s*\(Official\s*Music\s*Video\)',
            r'\s*\(Lyric\s*Video\)', r'\s*\(Lyrics\)',
            r'\s*\(Audio\)', r'\s*\(Official\s*Audio\)',
            r'\s*\[Official\s*Video\]', r'\s*\[Lyrics\]',
            r'\s*\(HD\)', r'\s*\(HQ\)', r'\s*\(4K\)',
        ]
        for p in patterns:
            title = re.sub(p, '', title, flags=re.IGNORECASE)
        return title.strip()

    def _parse_duration_text(self, text: str) -> int:
        """Парсить '3:45' или '1:23:45' в секунды"""
        if not text:
            return 0
        text = text.strip()
        parts = text.split(":")
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return 0
        except (ValueError, IndexError):
            return 0

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


# ─────────────────────────────────────────────────────────────
# Deezer — публичный API, отличная база русской музыки
# ─────────────────────────────────────────────────────────────

class DeezerSource:
    """
    Поиск через Deezer API.
    - Публичный, без авторизации
    - Отличная база русской и мировой музыки
    - Высококачественные обложки
    - Результаты используются для поиска + отображения,
      стриминг резолвится через YouTube
    """

    SEARCH_URL = "https://api.deezer.com/search"

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36",
                    "Accept": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=10),
            )
        return self._session

    async def search(self, query: str, limit: int = 30) -> list[Track]:
        """Поиск треков на Deezer"""
        try:
            session = await self._get_session()
            params = {
                "q": query,
                "limit": str(limit),
                "output": "json",
            }
            async with session.get(self.SEARCH_URL, params=params) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return self._parse(data, limit)
        except Exception as e:
            logger.warning(f"[Deezer] Search error: {e}")
            return []

    def _parse(self, data: dict, limit: int) -> list[Track]:
        tracks = []
        for item in data.get("data", []):
            try:
                track_id = str(item.get("id", ""))
                title = item.get("title", "Unknown")
                artist = item.get("artist", {}).get("name", "Unknown")
                duration = int(item.get("duration", 0))

                # Лучшая обложка
                album = item.get("album", {})
                cover = (
                    album.get("cover_xl", "")
                    or album.get("cover_big", "")
                    or album.get("cover_medium", "")
                    or album.get("cover_small", "")
                )

                tracks.append(Track(
                    id=f"dz_{track_id}",
                    title=title,
                    artist=artist,
                    duration=duration,
                    url="",
                    cover_url=cover,
                ))

                if len(tracks) >= limit:
                    break
            except Exception:
                continue

        return tracks

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


# ─────────────────────────────────────────────────────────────
# Audius — децентрализованный, легальный
# ─────────────────────────────────────────────────────────────

class AudiusSource:
    """Поиск на Audius (инди/легальная музыка)"""

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._host: Optional[str] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=10),
            )
        return self._session

    async def _get_host(self) -> Optional[str]:
        if self._host:
            return self._host
        try:
            session = await self._get_session()
            async with session.get("https://api.audius.co") as resp:
                data = await resp.json()
                hosts = data.get("data", [])
                if hosts:
                    self._host = hosts[0]
                    return self._host
        except Exception:
            pass
        return None

    async def search(self, query: str, limit: int = 15) -> list[Track]:
        try:
            host = await self._get_host()
            if not host:
                return []
            session = await self._get_session()
            async with session.get(
                f"{host}/v1/tracks/search",
                params={"query": query, "limit": str(limit), "app_name": "MusicHunter"},
            ) as resp:
                data = await resp.json()
                tracks = []
                for r in data.get("data", []):
                    artwork = r.get("artwork", {})
                    cover = ""
                    if artwork:
                        cover = artwork.get("480x480", "") or artwork.get("150x150", "")
                    tracks.append(Track(
                        id=f"au_{r.get('id', '')}",
                        title=r.get("title", "Unknown"),
                        artist=r.get("user", {}).get("name", "Unknown"),
                        duration=int(r.get("duration", 0) or 0),
                        url=f"{host}/v1/tracks/{r.get('id', '')}/stream?app_name=MusicHunter",
                        cover_url=cover,
                    ))
                return tracks
        except Exception as e:
            logger.warning(f"[Audius] Search error: {e}")
            return []

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


# ─────────────────────────────────────────────────────────────
# Stream Resolver — получение прямых URL для воспроизведения
# ─────────────────────────────────────────────────────────────

class StreamResolver:
    """
    Разрешение стрим URL:
    1. yt-dlp (прямой вызов, самый надёжный)
    2. Piped API (фоллбэк)
    3. Invidious API (фоллбэк)
    """

    PIPED_INSTANCES = [
        "https://pipedapi.kavin.rocks",
        "https://pipedapi.adminforge.de",
        "https://pipedapi.r4fo.com",
    ]

    INVIDIOUS_INSTANCES = [
        "https://inv.nadeko.net",
        "https://invidious.nerdvpn.de",
        "https://inv.thepixora.com",
        "https://invidious.tiekoetter.com",
    ]

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._yt_dlp_available: Optional[bool] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36",
                    "Accept": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=15),
            )
        return self._session

    async def _check_yt_dlp(self) -> bool:
        """Проверить доступность yt-dlp"""
        if self._yt_dlp_available is not None:
            return self._yt_dlp_available
        try:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.wait(), timeout=5)
            self._yt_dlp_available = proc.returncode == 0
            if self._yt_dlp_available:
                logger.info("[StreamResolver] yt-dlp available")
        except Exception:
            self._yt_dlp_available = False
            logger.warning("[StreamResolver] yt-dlp not found")
        return self._yt_dlp_available

    async def resolve_youtube(self, video_id: str) -> Optional[str]:
        """Получить аудио URL для YouTube видео"""

        # 1. yt-dlp (самый надёжный)
        if await self._check_yt_dlp():
            url = await self._ytdlp_stream(video_id)
            if url:
                return url

        # 2. Piped
        url = await self._piped_stream(video_id)
        if url:
            return url

        # 3. Invidious
        url = await self._invidious_stream(video_id)
        if url:
            return url

        return None

    async def _ytdlp_stream(self, video_id: str) -> Optional[str]:
        """Получить прямой аудио URL через yt-dlp"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "-f", "bestaudio[ext=webm]/bestaudio/best",
                "--get-url",
                "--no-warnings",
                "--no-check-certificates",
                f"https://www.youtube.com/watch?v={video_id}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)

            if proc.returncode == 0 and stdout:
                url = stdout.decode().strip()
                if url and url.startswith("http"):
                    logger.info(f"[yt-dlp] Got stream URL for {video_id}")
                    return url

            err = stderr.decode().strip() if stderr else ""
            logger.debug(f"[yt-dlp] Failed for {video_id}: {err[:200]}")
        except asyncio.TimeoutError:
            logger.warning(f"[yt-dlp] Timeout for {video_id}")
        except Exception as e:
            logger.warning(f"[yt-dlp] Error: {e}")

        return None

    async def _piped_stream(self, video_id: str) -> Optional[str]:
        """Получить стрим через Piped"""
        session = await self._get_session()
        for instance in self.PIPED_INSTANCES:
            try:
                url = f"{instance}/streams/{video_id}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()

                    audio_streams = data.get("audioStreams", [])
                    if not audio_streams:
                        continue

                    best = None
                    best_bitrate = 0
                    for stream in audio_streams:
                        codec = stream.get("codec", "").lower()
                        bitrate = int(stream.get("bitrate", 0) or 0)
                        stream_url = stream.get("url", "")
                        if not stream_url:
                            continue
                        if "opus" in codec:
                            if bitrate > best_bitrate or not best:
                                best = stream_url
                                best_bitrate = bitrate
                        elif not best and "aac" in codec:
                            best = stream_url

                    if best:
                        return best
                    if audio_streams:
                        return audio_streams[0].get("url")
            except Exception:
                continue
        return None

    async def _invidious_stream(self, video_id: str) -> Optional[str]:
        """Получить стрим через Invidious"""
        session = await self._get_session()
        for instance in self.INVIDIOUS_INSTANCES:
            try:
                url = f"{instance}/latest_version?id={video_id}&itag=251&local=true"
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10),
                    allow_redirects=False,
                ) as resp:
                    if resp.status in (301, 302, 303, 307, 308):
                        redirect_url = resp.headers.get("Location", "")
                        if redirect_url and "googlevideo" in redirect_url:
                            return redirect_url
                    elif resp.status == 200:
                        return str(resp.url)

                url = f"{instance}/latest_version?id={video_id}&itag=140&local=true"
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10),
                    allow_redirects=False,
                ) as resp:
                    if resp.status in (301, 302, 303, 307, 308):
                        redirect_url = resp.headers.get("Location", "")
                        if redirect_url and "googlevideo" in redirect_url:
                            return redirect_url
                    elif resp.status == 200:
                        return str(resp.url)

                url = f"{instance}/api/v1/videos/{video_id}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
                    for fmt in data.get("adaptiveFormats", []):
                        type_ = fmt.get("type", "")
                        if "audio" in type_.lower() and fmt.get("url"):
                            return fmt["url"]
            except Exception:
                continue
        return None

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


# ─────────────────────────────────────────────────────────────
# MusicService — главный сервис
# ─────────────────────────────────────────────────────────────

class MusicService:
    """
    Объединённый музыкальный сервис.
    Поиск: InnerTube (YouTube) + Deezer + Audius
    Стриминг: Piped + Invidious + Cobalt
    """

    def __init__(self):
        self._innertube = InnerTubeSource()
        self._deezer = DeezerSource()
        self._audius = AudiusSource()
        self._resolver = StreamResolver()
        self._yt_search_session: Optional[aiohttp.ClientSession] = None

    async def _get_yt_search_session(self) -> aiohttp.ClientSession:
        """Сессия для поиска YouTube видео (резолв Deezer треков)"""
        if self._yt_search_session is None or self._yt_search_session.closed:
            self._yt_search_session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=10),
            )
        return self._yt_search_session

    @cached(ttl=180)
    async def search(self, query: str, limit: int = 30) -> list[Track]:
        """
        Поиск треков из всех источников параллельно.
        InnerTube + Deezer + Audius → дедупликация → результат
        """
        results = await asyncio.gather(
            self._innertube.search(query, limit),
            self._deezer.search(query, limit),
            self._audius.search(query, min(limit, 15)),
            return_exceptions=True,
        )

        all_tracks: list[Track] = []
        seen_ids: set[str] = set()
        # Для дедупликации Deezer по названию+артисту (у них другие ID)
        seen_title_artist: set[str] = set()

        for result in results:
            if isinstance(result, Exception):
                continue
            for t in result:
                if t.id in seen_ids:
                    continue
                # Дедупликация по title+artist для Deezer
                key = f"{t.title.lower()}|{t.artist.lower()}"
                if t.id.startswith("dz_") and key in seen_title_artist:
                    continue
                seen_ids.add(t.id)
                seen_title_artist.add(key)
                all_tracks.append(t)

        return all_tracks[:limit]

    async def get_stream_url(self, track_id: str) -> Optional[str]:
        """Получить прямой URL для стриминга"""

        # YouTube — прямое разрешение
        if track_id.startswith("yt_"):
            video_id = track_id[3:]
            return await self._resolver.resolve_youtube(video_id)

        # Deezer — находим YouTube видео по artist+title, стримим через него
        if track_id.startswith("dz_"):
            return await self._resolve_deezer_via_youtube(track_id)

        # Audius — прямая ссылка
        if track_id.startswith("au_"):
            audius_id = track_id[3:]
            try:
                session = await self._get_yt_search_session()
                async with session.get("https://api.audius.co") as resp:
                    data = await resp.json()
                    host = data.get("data", ["https://api.audius.co"])[0]
                return f"{host}/v1/tracks/{audius_id}/stream?app_name=MusicHunter"
            except Exception:
                return None

        return None

    async def _resolve_deezer_via_youtube(self, track_id: str) -> Optional[str]:
        """
        Deezer не даёт полный стрим, поэтому:
        ищем трек на YouTube по названию и стримим через YouTube
        """
        try:
            # Получаем инфо о треке из Deezer
            deezer_id = track_id[3:]
            session = await self._get_yt_search_session()
            async with session.get(
                f"https://api.deezer.com/track/{deezer_id}"
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                title = data.get("title", "")
                artist = data.get("artist", {}).get("name", "")

            if not title:
                return None

            # Ищем на YouTube
            query = f"{artist} {title}".strip()
            yt_results = await self._innertube.search(query, limit=5)

            if yt_results:
                video_id = yt_results[0].id.replace("yt_", "")
                return await self._resolver.resolve_youtube(video_id)

        except Exception as e:
            logger.warning(f"[Deezer resolve] Error: {e}")

        return None

    async def close(self):
        await self._innertube.close()
        await self._deezer.close()
        await self._audius.close()
        await self._resolver.close()
        if self._yt_search_session and not self._yt_search_session.closed:
            await self._yt_search_session.close()


# Глобальный инстанс
music = MusicService()
