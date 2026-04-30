import asyncio
import logging
from app.database import SessionLocal
from app.models import Settings, Playlist, Track
from app.services import search_indexer, send_to_sabnzbd, get_sabnzbd_history, download_youtube_audio
from ytmusicapi import YTMusic
import json
import os

logger = logging.getLogger(__name__)

async def sync_job():
    db = SessionLocal()
    try:
        settings = db.query(Settings).first()
        if not settings or not settings.youtube_oauth_token:
            return

        try:
            token_dict = json.loads(settings.youtube_oauth_token)
            yt = YTMusic(auth=token_dict)
        except Exception as e:
            return

        synced_playlists = db.query(Playlist).filter(Playlist.sync_enabled == True).all()
        for playlist in synced_playlists:
            try:
                yt_playlist = yt.get_playlist(playlist.id, limit=200)
                if 'tracks' not in yt_playlist:
                    continue

                # Pre-fetch existing tracks to prevent N+1 query problem
                existing_tracks = {
                    track.video_id: track
                    for track in db.query(Track).filter(Track.playlist_id == playlist.id).all()
                }

                for track_data in yt_playlist['tracks']:
                    video_id = track_data.get('videoId')
                    if not video_id:
                        continue

                    track = existing_tracks.get(video_id)

                    if not track:
                        title = track_data.get('title', 'Unknown Title')
                        artists = track_data.get('artists', [{'name': 'Unknown Artist'}])
                        artist_name = artists[0]['name'] if artists else 'Unknown Artist'

                        track = Track(
                            video_id=video_id,
                            playlist_id=playlist.id,
                            title=title,
                            artist=artist_name,
                            status="pending"
                        )
                        db.add(track)
                        db.commit()

                    # Process pending tracks
                    if track.status == "pending":
                        result = await search_indexer(settings, track.artist, track.title)
                        if result:
                            nzo_id = await send_to_sabnzbd(settings, result['link'], f"{track.artist} - {track.title}")
                            if nzo_id:
                                track.status = "grabbed"
                                track.sabnzbd_nzo_id = nzo_id
                                db.commit()
                            else:
                                track.status = "failed"
                                db.commit()
                        else:
                            # YT-DLP Fallback: Track not found on indexer
                            success = await asyncio.to_thread(download_youtube_audio, video_id, settings)
                            if success:
                                track.status = "downloaded" # Completed by fallback
                            else:
                                track.status = "failed"
                            db.commit()

            except Exception as e:
                db.rollback()
                logger.error(f"Error syncing playlist {playlist.id}: {e}")

        # Check SABnzbd status for grabbed tracks
        grabbed_tracks = db.query(Track).filter(Track.status == "grabbed").all()
        if grabbed_tracks:
            history = await get_sabnzbd_history(settings)
            if history and "history" in history and "slots" in history["history"]:
                completed_nzo_ids = {slot["nzo_id"] for slot in history["history"]["slots"] if slot["status"] == "Completed"}
                failed_nzo_ids = {slot["nzo_id"] for slot in history["history"]["slots"] if slot["status"] == "Failed"}

                for track in grabbed_tracks:
                    if track.sabnzbd_nzo_id in completed_nzo_ids:
                        track.status = "downloaded"
                        db.commit()
                    elif track.sabnzbd_nzo_id in failed_nzo_ids:
                        track.status = "failed"
                        db.commit()

    except Exception as e:
        logger.error(f"Error in sync job: {e}")
    finally:
        db.close()
