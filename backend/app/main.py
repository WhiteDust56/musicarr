from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="YT Music to SABnzbd Sync")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import settings, youtube, dashboard
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler import sync_job
from app.database import SessionLocal
from app.models import Settings

app.include_router(settings.router)
app.include_router(youtube.router)
app.include_router(dashboard.router)

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    settings = db.query(Settings).first()
    interval = settings.sync_interval_minutes if settings else 60
    db.close()

    scheduler.add_job(sync_job, 'interval', minutes=interval, id='sync_job', replace_existing=True)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.get("/")
def read_root():
    return {"message": "YT Music Sync API is running"}
