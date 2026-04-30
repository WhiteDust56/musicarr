from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    indexer_url = Column(String, default="")
    indexer_api_key = Column(String, default="")
    sabnzbd_url = Column(String, default="")
    sabnzbd_api_key = Column(String, default="")
    quality = Column(String, default="MP3")
    sync_interval_minutes = Column(Integer, default=60)
    youtube_oauth_token = Column(String, default="")
    download_path = Column(String, default="./downloads") # Path for yt-dlp fallback

class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    sync_enabled = Column(Boolean, default=False)

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)
    playlist_id = Column(String, index=True)
    title = Column(String)
    artist = Column(String)
    status = Column(String, default="pending") # pending, grabbed, downloaded, failed
    sabnzbd_nzo_id = Column(String, nullable=True)
