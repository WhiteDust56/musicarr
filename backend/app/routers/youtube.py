from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import json
from ytmusicapi import YTMusic
from app.database import get_db
from app.models import Playlist
from app.routers.settings import get_or_create_settings
from pydantic import BaseModel

router = APIRouter(prefix="/api/youtube", tags=["youtube"])

class SyncToggleRequest(BaseModel):
    sync_enabled: bool

oauth_state = {}

def get_ytmusic(db: Session):
    settings = get_or_create_settings(db)
    if not settings.youtube_oauth_token:
        return None
    try:
        token_dict = json.loads(settings.youtube_oauth_token)
        return YTMusic(auth=token_dict)
    except Exception as e:
        return None

@router.get("/auth/status")
def get_auth_status(db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    return {"authenticated": bool(settings.youtube_oauth_token)}

@router.get("/auth/start")
def start_oauth():
    try:
        import requests
        from ytmusicapi.auth.oauth import OAuthCredentials

        # ytmusicapi v1.9+ removed the hardcoded client secrets from constants.py.
        # We must supply the standard YouTube TV client credentials to use the device flow.
        CLIENT_ID = "861556708454-d6dlm3lh05idd8npek18k6be8ba3oc68.apps.googleusercontent.com"
        CLIENT_SECRET = "SboVhoG9s0rNafixCSGGKXAT"

        session = requests.Session()
        oauth = OAuthCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, session=session)
        code = oauth.get_code()

        oauth_state['flow'] = oauth
        oauth_state['device_code'] = code['device_code']
        oauth_state['session'] = session
        return {"success": True, "url": code["verification_url"], "code": code["user_code"]}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.post("/auth/complete")
def complete_oauth(db: Session = Depends(get_db)):
    if 'flow' not in oauth_state or 'device_code' not in oauth_state:
        raise HTTPException(status_code=400, detail="No active OAuth flow")
    oauth = oauth_state['flow']
    device_code = oauth_state['device_code']
    try:
        token = oauth.token_from_code(device_code)
        settings = get_or_create_settings(db)
        settings.youtube_oauth_token = json.dumps(token)
        db.commit()
        del oauth_state['flow']
        del oauth_state['device_code']
        if 'session' in oauth_state:
            del oauth_state['session']
        return {"success": True, "message": "Successfully authenticated"}
    except Exception as e:
        return {"success": False, "message": f"Authentication failed: {str(e)}"}

@router.post("/auth/logout")
def logout(db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    settings.youtube_oauth_token = ""
    db.commit()
    return {"success": True}

@router.get("/playlists")
def get_playlists(db: Session = Depends(get_db)):
    yt = get_ytmusic(db)
    if not yt:
        raise HTTPException(status_code=401, detail="Not authenticated with YouTube Music")
    try:
        yt_playlists = yt.get_library_playlists(limit=100)
        db_playlists = {p.id: p for p in db.query(Playlist).all()}
        result = []
        for p in yt_playlists:
            if 'playlistId' not in p:
                continue
            pid = p['playlistId']
            is_synced = False
            if pid in db_playlists:
                is_synced = db_playlists[pid].sync_enabled
            else:
                new_p = Playlist(id=pid, title=p.get('title', 'Unknown'), sync_enabled=False)
                db.add(new_p)
                db.commit()
            result.append({
                "id": pid,
                "title": p.get('title', 'Unknown'),
                "count": p.get('count', 0),
                "sync_enabled": is_synced
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch playlists: {str(e)}")

@router.put("/playlists/{playlist_id}/sync")
def toggle_playlist_sync(playlist_id: str, req: SyncToggleRequest, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        playlist = Playlist(id=playlist_id, title="Unknown", sync_enabled=req.sync_enabled)
        db.add(playlist)
    else:
        playlist.sync_enabled = req.sync_enabled
    db.commit()
    return {"success": True, "sync_enabled": playlist.sync_enabled}
