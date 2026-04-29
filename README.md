# YT Music to SABnzbd Sync

A full-stack application to synchronize user-created YouTube Music playlists by searching a Newznab indexer for audio tracks, queueing them in SABnzbd, and falling back to a direct YouTube download (`yt-dlp`) if the track is not found.

## Requirements
* Docker & Docker Compose
* A YouTube Music Account
* A Newznab-compatible Indexer (API Key)
* A SABnzbd Instance (API Key)

## Running with Docker Compose

1. Clone this repository.
2. Ensure you have Docker and Docker Compose installed.
3. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```
4. Access the web interface at `http://localhost:8080`.

### Directories
When running via Docker Compose, two local directories will be created to persist data:
* `./data/`: Holds the SQLite database (`app.db`).
* `./downloads/`: Holds the audio files downloaded directly via the `yt-dlp` fallback mechanism.

Make sure the fallback download path in the UI Settings is set to `./downloads` or `/app/downloads`.

## Features
* **OAuth Authentication**: Connect directly to your YouTube Music account securely using the device flow.
* **Auto-Sync**: Background worker (APScheduler) routinely checks selected playlists for new tracks.
* **Smart Fallback**: If an indexer search yields no results for a specific quality, the app seamlessly falls back to `yt-dlp` to fetch the audio directly from YouTube.
* **Realtime Monitoring**: View SABnzbd's download queue and history statuses directly within the dashboard.
