from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Track
from app.routers.settings import get_or_create_settings
from app.services import get_sabnzbd_queue, get_sabnzbd_history

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/tracks")
def get_tracks(db: Session = Depends(get_db)):
    tracks = db.query(Track).order_by(Track.id.desc()).limit(100).all()
    return tracks

@router.get("/sabnzbd/progress")
async def get_sabnzbd_progress(db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    queue = await get_sabnzbd_queue(settings)
    history = await get_sabnzbd_history(settings)

    return {
        "queue": queue,
        "history": history
    }
