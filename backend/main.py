# -*- coding: utf-8 -*-
"""
MusicHunter API — полная музыкальная платформа
Поиск, стриминг, лайки, плейлисты, история
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, delete, func, desc, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database import Base, User, LikedTrack, Playlist, PlaylistTrack, ListenHistory
from music_service import music

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./musichunter.db")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ─────────────────────────────────────────────
# DB Init
# ─────────────────────────────────────────────
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session() as session:
        yield session


# ─────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────
class TrackResponse(BaseModel):
    id: str
    title: str
    artist: str
    duration: int
    duration_str: str = ""
    url: str = ""
    cover_url: str = ""


class SearchResponse(BaseModel):
    query: str
    count: int
    tracks: list[TrackResponse]


class LikeRequest(BaseModel):
    track_id: str
    title: str
    artist: str
    duration: int = 0
    url: str = ""
    cover_url: str = ""


class PlaylistCreate(BaseModel):
    name: str
    description: str = ""
    cover_url: str = ""
    is_public: bool = True


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    is_public: Optional[bool] = None


class PlaylistTrackAdd(BaseModel):
    track_id: str
    title: str
    artist: str
    duration: int = 0
    url: str = ""
    cover_url: str = ""


class HistoryRequest(BaseModel):
    track_id: str
    title: str
    artist: str
    duration: int = 0
    url: str = ""
    cover_url: str = ""


# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("🎵 MusicHunter API started")
    yield
    await music.close()
    await engine.dispose()


app = FastAPI(
    title="MusicHunter API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Helper: получить или создать пользователя
# ─────────────────────────────────────────────
async def get_or_create_user(db: AsyncSession, tg_id: int, username: str = None, first_name: str = None) -> User:
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(tg_id=tg_id, username=username, first_name=first_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


def track_to_response(t) -> TrackResponse:
    """Convert Track object or dict to TrackResponse"""
    if isinstance(t, dict):
        return TrackResponse(
            id=t["id"],
            title=t["title"],
            artist=t["artist"],
            duration=t.get("duration", 0),
            duration_str=t.get("duration_str", f"{t.get('duration',0)//60}:{t.get('duration',0)%60:02d}"),
            url=t.get("url", ""),
            cover_url=t.get("cover_url", ""),
        )
    # SQLAlchemy model
    return TrackResponse(
        id=t.track_id if hasattr(t, "track_id") else t.id,
        title=t.title,
        artist=t.artist,
        duration=t.duration,
        duration_str=f"{t.duration//60}:{t.duration%60:02d}" if t.duration else "0:00",
        url=t.url or "",
        cover_url=t.cover_url or "",
    )


# ═════════════════════════════════════════════
# ENDPOINTS
# ═════════════════════════════════════════════

# ─── Base ────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ok", "service": "MusicHunter", "version": "2.0.0"}


# ─── Search ──────────────────────────────────
@app.get("/search", response_model=SearchResponse)
async def search_tracks(q: str = Query(..., min_length=1), limit: int = Query(30, ge=1, le=100)):
    tracks = await music.search(q, limit)
    return SearchResponse(
        query=q,
        count=len(tracks),
        tracks=[track_to_response(t.to_dict()) for t in tracks],
    )


# ─── Stream (proxy audio through backend with WebM→MP3 conversion) ───
@app.api_route("/stream/{track_id:path}", methods=["GET", "HEAD"])
async def get_stream(track_id: str, request: Request):
    """Проксируем аудио через бэкенд с конвертацией WebM → MP3"""
    url = await music.get_stream_url(track_id)
    if not url:
        raise HTTPException(404, "Stream URL not found")
    
    import httpx
    import asyncio
    import tempfile
    import os
    
    client = httpx.AsyncClient(follow_redirects=True, timeout=httpx.Timeout(60.0, connect=10.0, read=30.0))
    
    try:
        # Для HEAD запроса — просто проверяем доступность
        if request.method == "HEAD":
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
            }
            req = client.build_request("HEAD", url, headers=headers)
            resp = await client.send(req)
            await resp.aclose()
            await client.aclose()
            
            from fastapi.responses import Response
            return Response(
                status_code=200,
                headers={
                    "Content-Type": "audio/mpeg",
                    "Accept-Ranges": "bytes",
                }
            )
        
        # Для GET запроса — скачиваем WebM и конвертируем в MP3
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
        }
        # Игнорируем Range header от клиента — всегда загружаем полный файл для конвертации
        req = client.build_request("GET", url, headers=headers)
        resp = await client.send(req, stream=True)
        
        if resp.status_code not in [200, 206]:
            await resp.aclose()
            await client.aclose()
            raise HTTPException(502, f"Upstream returned {resp.status_code}")
        
        # Создаём временный файл для WebM
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_webm:
            webm_path = tmp_webm.name
            mp3_path = webm_path.replace('.webm', '.mp3')
            
            # Скачиваем WebM
            async for chunk in resp.aiter_bytes(chunk_size=65536):
                tmp_webm.write(chunk)
        
        await resp.aclose()
        await client.aclose()
        
        # Конвертируем WebM → MP3 через ffmpeg
        process = await asyncio.create_subprocess_exec(
            'ffmpeg',
            '-i', webm_path,
            '-vn',  # без видео
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            '-ar', '44100',
            '-y',  # перезаписать выходной файл
            mp3_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            os.unlink(webm_path)
            raise HTTPException(500, f"FFmpeg conversion failed: {stderr.decode()}")
        
        # Читаем конвертированный MP3
        with open(mp3_path, 'rb') as f:
            mp3_data = f.read()
        
        # Удаляем временные файлы
        os.unlink(webm_path)
        os.unlink(mp3_path)
        
        from fastapi.responses import Response
        return Response(
            content=mp3_data,
            media_type="audio/mpeg",
            headers={
                "Content-Length": str(len(mp3_data)),
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await client.aclose()
        raise HTTPException(502, f"Stream proxy error: {str(e)}")


@app.get("/stream-url/{track_id:path}")
async def get_stream_url_endpoint(track_id: str):
    """Вернуть прямой URL (для отладки)"""
    url = await music.get_stream_url(track_id)
    if not url:
        raise HTTPException(404, "Stream URL not found")
    return {"url": url}


@app.get("/download/{track_id:path}")
async def download_track(track_id: str):
    """Проксируем аудио для скачивания"""
    url = await music.get_stream_url(track_id)
    if not url:
        raise HTTPException(404, "Stream URL not found")
    
    import httpx
    client = httpx.AsyncClient(follow_redirects=True, timeout=httpx.Timeout(120.0, connect=10.0, read=60.0))
    try:
        req = client.build_request("GET", url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
        })
        resp = await client.send(req, stream=True)
        if resp.status_code != 200:
            await resp.aclose()
            await client.aclose()
            raise HTTPException(502, f"Upstream returned {resp.status_code}")
        
        content_type = resp.headers.get("content-type", "audio/webm")
        
        async def audio_generator():
            try:
                async for chunk in resp.aiter_bytes(chunk_size=32768):
                    yield chunk
            finally:
                await resp.aclose()
                await client.aclose()
        
        return StreamingResponse(
            audio_generator(),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{track_id}.webm"',
                "Cache-Control": "no-cache",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        await client.aclose()
        raise HTTPException(502, f"Download proxy error: {str(e)}")


# ─── Cover proxy (i.ytimg.com заблокирован в РФ) ──
@app.get("/cover")
async def proxy_cover(url: str = Query(..., max_length=500)):
    """Прокси обложек через бэкенд"""
    import httpx
    client = httpx.AsyncClient(follow_redirects=True, timeout=httpx.Timeout(15.0))
    try:
        resp = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        if resp.status_code != 200:
            raise HTTPException(502, f"Upstream {resp.status_code}")
        content_type = resp.headers.get("content-type", "image/jpeg")
        body = resp.content
        await client.aclose()
        return StreamingResponse(
            iter([body]),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400",
                "Content-Length": str(len(body)),
            },
        )
    except HTTPException:
        await client.aclose()
        raise
    except Exception as e:
        await client.aclose()
        raise HTTPException(502, f"Cover proxy error: {str(e)}")


# ─── Local Music Files ───────────────────────
LOCAL_MUSIC_DIR = os.getenv("LOCAL_MUSIC_DIR", "./music")


def _scan_music_dir(dir_path: str, prefix: str = "") -> list:
    """Сканирует папку с аудиофайлами, возвращает список TrackResponse"""
    import hashlib
    supported = (".mp3", ".opus", ".ogg", ".m4a", ".wav", ".flac", ".webm")
    tracks = []
    if not os.path.isdir(dir_path):
        return tracks
    for fname in sorted(os.listdir(dir_path)):
        if not fname.lower().endswith(supported):
            continue
        file_id = hashlib.md5(f"{prefix}/{fname}".encode()).hexdigest()[:12]
        name = os.path.splitext(fname)[0]
        if " - " in name:
            artist, title = name.split(" - ", 1)
        else:
            artist, title = "Unknown", name
        tracks.append(TrackResponse(
            id=f"local_{file_id}",
            title=title.strip(),
            artist=artist.strip(),
            duration=0,
            duration_str="",
            url=f"/local/{file_id}",
            cover_url="",
        ))
    return tracks


@app.get("/local")
async def list_local_tracks(tg_id: int = Query(0)):
    """Список аудиофайлов пользователя: личные + из чатов"""
    if not tg_id:
        return {"count": 0, "tracks": []}
    if not os.path.isdir(LOCAL_MUSIC_DIR):
        return {"count": 0, "tracks": []}

    tracks = []
    # Личные файлы пользователя: music/{tg_id}/
    personal_dir = os.path.join(LOCAL_MUSIC_DIR, str(tg_id))
    tracks.extend(_scan_music_dir(personal_dir, prefix=str(tg_id)))

    # Файлы из групповых чатов: music/chat_{chat_id}/
    # Показываем все групповые папки — доступ к боту в группе = право слушать
    for entry in sorted(os.listdir(LOCAL_MUSIC_DIR)):
        entry_path = os.path.join(LOCAL_MUSIC_DIR, entry)
        if os.path.isdir(entry_path) and entry.startswith("chat_"):
            tracks.extend(_scan_music_dir(entry_path, prefix=entry))

    return {"count": len(tracks), "tracks": tracks}


@app.get("/local/{file_id}")
async def stream_local_track(file_id: str, request: Request):
    """Стрим локального аудиофайла с поддержкой Range-запросов"""
    if not os.path.isdir(LOCAL_MUSIC_DIR):
        raise HTTPException(404, "Music directory not found")

    import hashlib
    supported = (".mp3", ".opus", ".ogg", ".m4a", ".wav", ".flac", ".webm")
    content_types = {
        ".mp3": "audio/mpeg", ".opus": "audio/opus", ".ogg": "audio/ogg",
        ".m4a": "audio/mp4", ".wav": "audio/wav", ".flac": "audio/flac",
        ".webm": "audio/webm",
    }

    # Рекурсивный поиск: music/ и music/{subdir}/
    search_dirs = [LOCAL_MUSIC_DIR]
    if os.path.isdir(LOCAL_MUSIC_DIR):
        for entry in os.listdir(LOCAL_MUSIC_DIR):
            entry_path = os.path.join(LOCAL_MUSIC_DIR, entry)
            if os.path.isdir(entry_path):
                search_dirs.append(entry_path)

    for search_dir in search_dirs:
        prefix = os.path.basename(search_dir) if search_dir != LOCAL_MUSIC_DIR else ""
        for fname in os.listdir(search_dir):
            if not fname.lower().endswith(supported):
                continue
            fid = hashlib.md5(f"{prefix}/{fname}".encode()).hexdigest()[:12]
            if fid == file_id:
                filepath = os.path.join(search_dir, fname)
                ext = os.path.splitext(fname)[1].lower()
                ct = content_types.get(ext, "audio/mpeg")
                file_size = os.path.getsize(filepath)

                # Parse Range header
                range_header = request.headers.get("range")
                if range_header:
                    # Format: "bytes=start-end"
                    range_match = range_header.replace("bytes=", "")
                    parts = range_match.split("-")
                    start = int(parts[0]) if parts[0] else 0
                    end = int(parts[1]) if parts[1] else file_size - 1
                    end = min(end, file_size - 1)
                    content_length = end - start + 1

                    def range_generator():
                        with open(filepath, "rb") as f:
                            f.seek(start)
                            remaining = content_length
                            while remaining > 0:
                                chunk = f.read(min(65536, remaining))
                                if not chunk:
                                    break
                                remaining -= len(chunk)
                                yield chunk

                    return StreamingResponse(
                        range_generator(),
                        status_code=206,
                        media_type=ct,
                        headers={
                            "Content-Range": f"bytes {start}-{end}/{file_size}",
                            "Content-Length": str(content_length),
                            "Accept-Ranges": "bytes",
                            "Cache-Control": "public, max-age=86400",
                        },
                    )

                # No Range — return full file
                return StreamingResponse(
                    open(filepath, "rb"),
                    media_type=ct,
                    headers={
                        "Content-Length": str(file_size),
                        "Accept-Ranges": "bytes",
                        "Cache-Control": "public, max-age=86400",
                    },
                )

    raise HTTPException(404, "File not found")


# ─── Likes ───────────────────────────────────
@app.post("/likes/{tg_id}")
async def like_track(tg_id: int, req: LikeRequest, db: AsyncSession = Depends(get_db)):
    await get_or_create_user(db, tg_id)
    # Проверка дубликата
    result = await db.execute(
        select(LikedTrack).where(and_(LikedTrack.user_id == tg_id, LikedTrack.track_id == req.track_id))
    )
    existing = result.scalar_one_or_none()
    if existing:
        # Убираем лайк (toggle)
        await db.delete(existing)
        await db.commit()
        return {"action": "unliked", "track_id": req.track_id}

    like = LikedTrack(
        user_id=tg_id,
        track_id=req.track_id,
        title=req.title,
        artist=req.artist,
        duration=req.duration,
        url=req.url,
        cover_url=req.cover_url,
    )
    db.add(like)
    await db.commit()
    return {"action": "liked", "track_id": req.track_id}


@app.get("/likes/{tg_id}")
async def get_likes(tg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LikedTrack)
        .where(LikedTrack.user_id == tg_id)
        .order_by(desc(LikedTrack.created_at))
    )
    tracks = result.scalars().all()
    return {"count": len(tracks), "tracks": [track_to_response(t) for t in tracks]}


@app.delete("/likes/{tg_id}/{track_id}")
async def unlike_track(tg_id: int, track_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LikedTrack).where(and_(LikedTrack.user_id == tg_id, LikedTrack.track_id == track_id))
    )
    like = result.scalar_one_or_none()
    if not like:
        raise HTTPException(404, "Like not found")
    await db.delete(like)
    await db.commit()
    return {"action": "unliked", "track_id": track_id}


# ─── Playlists ───────────────────────────────
@app.post("/playlists/{tg_id}")
async def create_playlist(tg_id: int, req: PlaylistCreate, db: AsyncSession = Depends(get_db)):
    await get_or_create_user(db, tg_id)
    playlist = Playlist(
        user_id=tg_id,
        name=req.name,
        description=req.description,
        cover_url=req.cover_url,
        is_public=req.is_public,
    )
    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)
    return {
        "id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "is_public": playlist.is_public,
        "track_count": 0,
        "created_at": playlist.created_at.isoformat(),
    }


@app.get("/playlists/{tg_id}")
async def get_playlists(tg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Playlist).where(Playlist.user_id == tg_id).order_by(desc(Playlist.updated_at))
    )
    playlists = result.scalars().all()

    out = []
    for p in playlists:
        count_result = await db.execute(
            select(func.count()).where(PlaylistTrack.playlist_id == p.id)
        )
        track_count = count_result.scalar() or 0
        out.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "cover_url": p.cover_url,
            "is_public": p.is_public,
            "track_count": track_count,
            "created_at": p.created_at.isoformat(),
        })
    return {"count": len(out), "playlists": out}


@app.get("/playlists/{tg_id}/{playlist_id}")
async def get_playlist(tg_id: int, playlist_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(404, "Playlist not found")

    tracks_result = await db.execute(
        select(PlaylistTrack)
        .where(PlaylistTrack.playlist_id == playlist_id)
        .order_by(PlaylistTrack.position)
    )
    tracks = tracks_result.scalars().all()

    return {
        "id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "cover_url": playlist.cover_url,
        "is_public": playlist.is_public,
        "tracks": [track_to_response(t) for t in tracks],
        "track_count": len(tracks),
        "created_at": playlist.created_at.isoformat(),
    }


@app.put("/playlists/{tg_id}/{playlist_id}")
async def update_playlist(tg_id: int, playlist_id: int, req: PlaylistUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(404, "Playlist not found")

    if req.name is not None:
        playlist.name = req.name
    if req.description is not None:
        playlist.description = req.description
    if req.cover_url is not None:
        playlist.cover_url = req.cover_url
    if req.is_public is not None:
        playlist.is_public = req.is_public
    playlist.updated_at = datetime.utcnow()

    await db.commit()
    return {"status": "updated", "id": playlist_id}


@app.delete("/playlists/{tg_id}/{playlist_id}")
async def delete_playlist(tg_id: int, playlist_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(404, "Playlist not found")
    await db.delete(playlist)
    await db.commit()
    return {"status": "deleted", "id": playlist_id}


# ─── Playlist Tracks ─────────────────────────
@app.post("/playlists/{tg_id}/{playlist_id}/tracks")
async def add_track_to_playlist(
    tg_id: int, playlist_id: int, req: PlaylistTrackAdd, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Playlist not found")

    # Get max position
    pos_result = await db.execute(
        select(func.max(PlaylistTrack.position)).where(PlaylistTrack.playlist_id == playlist_id)
    )
    max_pos = pos_result.scalar() or 0

    pt = PlaylistTrack(
        playlist_id=playlist_id,
        track_id=req.track_id,
        title=req.title,
        artist=req.artist,
        duration=req.duration,
        url=req.url,
        cover_url=req.cover_url,
        position=max_pos + 1,
    )
    db.add(pt)
    await db.commit()
    return {"status": "added", "track_id": req.track_id}


@app.delete("/playlists/{tg_id}/{playlist_id}/tracks/{track_id}")
async def remove_track_from_playlist(
    tg_id: int, playlist_id: int, track_id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PlaylistTrack).where(
            and_(PlaylistTrack.playlist_id == playlist_id, PlaylistTrack.track_id == track_id)
        )
    )
    pt = result.scalar_one_or_none()
    if not pt:
        raise HTTPException(404, "Track not in playlist")
    await db.delete(pt)
    await db.commit()
    return {"status": "removed", "track_id": track_id}


# ─── Listen History ──────────────────────────
@app.post("/history/{tg_id}")
async def add_to_history(tg_id: int, req: HistoryRequest, db: AsyncSession = Depends(get_db)):
    await get_or_create_user(db, tg_id)
    entry = ListenHistory(
        user_id=tg_id,
        track_id=req.track_id,
        title=req.title,
        artist=req.artist,
        duration=req.duration,
        url=req.url,
        cover_url=req.cover_url,
    )
    db.add(entry)
    await db.commit()

    # Чистим историю — храним последние 100 треков
    count_result = await db.execute(
        select(func.count()).where(ListenHistory.user_id == tg_id)
    )
    count = count_result.scalar()
    if count > 100:
        # Удаляем самые старые
        old = await db.execute(
            select(ListenHistory)
            .where(ListenHistory.user_id == tg_id)
            .order_by(ListenHistory.listened_at)
            .limit(count - 100)
        )
        for entry in old.scalars().all():
            await db.delete(entry)
        await db.commit()

    return {"status": "recorded"}


@app.get("/history/{tg_id}")
async def get_history(tg_id: int, limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ListenHistory)
        .where(ListenHistory.user_id == tg_id)
        .order_by(desc(ListenHistory.listened_at))
        .limit(limit)
    )
    tracks = result.scalars().all()
    return {"count": len(tracks), "tracks": [track_to_response(t) for t in tracks]}


@app.delete("/history/{tg_id}")
async def clear_history(tg_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ListenHistory).where(ListenHistory.user_id == tg_id))
    await db.commit()
    return {"status": "cleared"}


# ─── Stats ───────────────────────────────────
@app.get("/stats/{tg_id}")
async def get_stats(tg_id: int, db: AsyncSession = Depends(get_db)):
    likes_count = (await db.execute(
        select(func.count()).where(LikedTrack.user_id == tg_id)
    )).scalar() or 0

    playlists_count = (await db.execute(
        select(func.count()).where(Playlist.user_id == tg_id)
    )).scalar() or 0

    history_count = (await db.execute(
        select(func.count()).where(ListenHistory.user_id == tg_id)
    )).scalar() or 0

    # Топ артисты
    top_artists = (await db.execute(
        select(ListenHistory.artist, func.count().label("count"))
        .where(ListenHistory.user_id == tg_id)
        .group_by(ListenHistory.artist)
        .order_by(desc("count"))
        .limit(5)
    )).all()

    return {
        "likes": likes_count,
        "playlists": playlists_count,
        "listened": history_count,
        "top_artists": [{"name": a, "count": c} for a, c in top_artists],
    }


# ─── Run ─────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
