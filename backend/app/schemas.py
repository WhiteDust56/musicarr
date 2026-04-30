from pydantic import BaseModel
from typing import Optional

class SettingsBase(BaseModel):
    indexer_url: str = ""
    indexer_api_key: str = ""
    sabnzbd_url: str = ""
    sabnzbd_api_key: str = ""
    quality: str = "MP3"
    sync_interval_minutes: int = 60
    youtube_oauth_token: str = ""
    download_path: str = "./downloads"

class SettingsUpdate(SettingsBase):
    pass

class Settings(SettingsBase):
    id: int
    class Config:
        from_attributes = True

class TestIntegrationRequest(BaseModel):
    indexer_url: str = ""
    indexer_api_key: str = ""
    sabnzbd_url: str = ""
    sabnzbd_api_key: str = ""

class PlaylistBase(BaseModel):
    id: str
    title: str
    sync_enabled: bool = False

class Playlist(PlaylistBase):
    class Config:
        from_attributes = True

class TrackBase(BaseModel):
    id: int
    video_id: str
    playlist_id: str
    title: str
    artist: str
    status: str
    sabnzbd_nzo_id: Optional[str] = None

class Track(TrackBase):
    class Config:
        from_attributes = True
