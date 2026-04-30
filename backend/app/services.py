import httpx
import logging
from app.models import Settings
import yt_dlp
import os

logger = logging.getLogger(__name__)

async def search_indexer(settings: Settings, artist: str, title: str):
    if not settings.indexer_url or not settings.indexer_api_key:
        return None

    category = "3000"
    if settings.quality == "MP3":
        category = "3010"
    elif settings.quality == "FLAC":
        category = "3040"

    query = f"{artist} {title}"
    url = settings.indexer_url.rstrip('/')

    params = {
        "t": "search",
        "q": query,
        "cat": category,
        "apikey": settings.indexer_api_key,
        "o": "json"
    }

    try:
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}) as client:
            response = await client.get(f"{url}/api", params=params, timeout=15.0)
            response.raise_for_status()

            data = response.json()
            if "channel" not in data or "item" not in data["channel"]:
                return None

            items = data["channel"]["item"]
            if not items:
                return None

            if isinstance(items, dict):
                items = [items]

            first_result = items[0]
            if "link" in first_result:
                 return {
                     "title": first_result.get("title"),
                     "link": first_result["link"]
                 }
            return None
    except Exception as e:
        return None

async def send_to_sabnzbd(settings: Settings, nzb_url: str, name: str):
    if not settings.sabnzbd_url or not settings.sabnzbd_api_key:
        return None

    url = settings.sabnzbd_url.rstrip('/')
    params = {
        "mode": "addurl",
        "name": nzb_url,
        "nzbname": name,
        "apikey": settings.sabnzbd_api_key,
        "output": "json"
    }

    try:
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}) as client:
            response = await client.post(f"{url}/api", data=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            if data.get("status") and "nzo_ids" in data:
                return data["nzo_ids"][0]
            return None
    except Exception:
        return None

async def get_sabnzbd_queue(settings: Settings):
    if not settings.sabnzbd_url or not settings.sabnzbd_api_key:
        return None
    url = settings.sabnzbd_url.rstrip('/')
    params = {
        "mode": "queue",
        "apikey": settings.sabnzbd_api_key,
        "output": "json"
    }
    try:
         async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}) as client:
            response = await client.get(f"{url}/api", params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception:
        return None

async def get_sabnzbd_history(settings: Settings):
    if not settings.sabnzbd_url or not settings.sabnzbd_api_key:
        return None
    url = settings.sabnzbd_url.rstrip('/')
    params = {
        "mode": "history",
        "apikey": settings.sabnzbd_api_key,
        "output": "json",
        "limit": 100
    }
    try:
         async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}) as client:
            response = await client.get(f"{url}/api", params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception:
        return None

def download_youtube_audio(video_id: str, settings: Settings):
    try:
        download_path = settings.download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        url = f"https://music.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3' if settings.quality == 'MP3' else 'flac',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(download_path, '%(artist)s - %(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return True
    except Exception as e:
        logger.error(f"yt-dlp failed for {video_id}: {e}")
        return False
