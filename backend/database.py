"""
MusicHunter — база данных (SQLite + SQLAlchemy)
Лайки, плейлисты, история прослушивания
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Пользователь TG Mini App"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    likes = relationship("LikedTrack", back_populates="user", cascade="all, delete-orphan")
    playlists = relationship("Playlist", back_populates="user", cascade="all, delete-orphan")
    history = relationship("ListenHistory", back_populates="user", cascade="all, delete-orphan")


class LikedTrack(Base):
    """Лайкнутый трек"""
    __tablename__ = "liked_tracks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    track_id = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    artist = Column(String(500), nullable=False)
    duration = Column(Integer, default=0)
    url = Column(Text, nullable=True)
    cover_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="likes")

    class Config:
        unique_together = ("user_id", "track_id")


class Playlist(Base):
    """Плейлист"""
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    cover_url = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="playlists")
    tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistTrack(Base):
    """Трек в плейлисте"""
    __tablename__ = "playlist_tracks"

    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False, index=True)
    track_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    artist = Column(String(500), nullable=False)
    duration = Column(Integer, default=0)
    url = Column(Text, nullable=True)
    cover_url = Column(Text, nullable=True)
    position = Column(Integer, default=0)
    added_at = Column(DateTime, default=datetime.utcnow)

    playlist = relationship("Playlist", back_populates="tracks")


class ListenHistory(Base):
    """История прослушивания"""
    __tablename__ = "listen_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    track_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    artist = Column(String(500), nullable=False)
    duration = Column(Integer, default=0)
    url = Column(Text, nullable=True)
    cover_url = Column(Text, nullable=True)
    listened_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="history")
