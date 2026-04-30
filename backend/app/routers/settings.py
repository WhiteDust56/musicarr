from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
from app.database import get_db
from app.models import Settings
from app.schemas import Settings as SettingsSchema, SettingsUpdate, TestIntegrationRequest

router = APIRouter(prefix="/api/settings", tags=["settings"])

def get_or_create_settings(db: Session) -> Settings:
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.get("/", response_model=SettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    return get_or_create_settings(db)

@router.put("/", response_model=SettingsSchema)
def update_settings(settings_update: SettingsUpdate, db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)

    settings.indexer_url = settings_update.indexer_url
    settings.indexer_api_key = settings_update.indexer_api_key
    settings.sabnzbd_url = settings_update.sabnzbd_url
    settings.sabnzbd_api_key = settings_update.sabnzbd_api_key
    settings.quality = settings_update.quality
    settings.download_path = settings_update.download_path

    interval_changed = settings.sync_interval_minutes != settings_update.sync_interval_minutes
    settings.sync_interval_minutes = settings_update.sync_interval_minutes

    if settings_update.youtube_oauth_token is not None:
        settings.youtube_oauth_token = settings_update.youtube_oauth_token

    db.commit()
    db.refresh(settings)

    if interval_changed:
        from app.main import scheduler
        from app.scheduler import sync_job
        scheduler.reschedule_job('sync_job', trigger='interval', minutes=settings.sync_interval_minutes)

    return settings

@router.post("/test-indexer")
async def test_indexer(request: TestIntegrationRequest):
    if not request.indexer_url or not request.indexer_api_key:
        raise HTTPException(status_code=400, detail="Indexer URL and API Key are required")
    url = request.indexer_url.rstrip('/')
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url}/api",
                params={"t": "caps", "apikey": request.indexer_api_key, "o": "json"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                 return {"success": False, "message": f"Indexer error: {data['error'].get('description', 'Unknown error')}"}
            return {"success": True, "message": "Successfully connected to indexer"}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}

@router.post("/test-sabnzbd")
async def test_sabnzbd(request: TestIntegrationRequest):
    if not request.sabnzbd_url or not request.sabnzbd_api_key:
        raise HTTPException(status_code=400, detail="SABnzbd URL and API Key are required")
    url = request.sabnzbd_url.rstrip('/')
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url}/api",
                params={"mode": "version", "apikey": request.sabnzbd_api_key, "output": "json"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            if "version" in data:
                return {"success": True, "message": f"Successfully connected to SABnzbd (v{data['version']})"}
            else:
                return {"success": False, "message": "Invalid response from SABnzbd"}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}
