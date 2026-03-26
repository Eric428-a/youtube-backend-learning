# app/services/youtube_service.py
import httpx
from app.config import YOUTUBE_API_KEY
from urllib.parse import urlparse, parse_qs
from fastapi import HTTPException

BASE_URL = "https://www.googleapis.com/youtube/v3"

async def get_channel_id_from_video(video_url: str) -> str:
    """
    Convert a YouTube video URL to its channel ID.
    """
    parsed = urlparse(video_url)
    video_id = None

    if parsed.hostname == "youtu.be":
        video_id = parsed.path[1:]
    elif parsed.hostname in ["www.youtube.com", "youtube.com"]:
        qs = parse_qs(parsed.query)
        video_id = qs.get("v", [None])[0]

    if not video_id:
        raise HTTPException(status_code=400, detail=f"Invalid YouTube URL: {video_url}")

    url = f"{BASE_URL}/videos"
    params = {"part": "snippet", "id": video_id, "key": YOUTUBE_API_KEY}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items")
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            return items[0]["snippet"]["channelId"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"YouTube API error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

async def get_live_streams(channel_id: str):
    """
    Fetch active live streams for a given channel ID.
    """
    url = f"{BASE_URL}/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "eventType": "live",
        "type": "video",
        "key": YOUTUBE_API_KEY
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            streams = []
            for item in data.get("items", []):
                streams.append({
                    "video_id": item["id"]["videoId"],
                    "video_url": f"https://youtu.be/{item['id']['videoId']}",
                    "title": item["snippet"]["title"],
                    "description": item["snippet"].get("description"),
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    "channel_title": item["snippet"]["channelTitle"]
                })
            return streams
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"YouTube API error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")