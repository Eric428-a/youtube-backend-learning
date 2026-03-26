# app/routes/youtube_routes.py
from fastapi import APIRouter, Query, Depends, HTTPException
import httpx
from urllib.parse import urlparse, parse_qs
from app.config import YOUTUBE_API_KEY
from app.dependencies.auth_guard import get_current_user

BASE_URL = "https://www.googleapis.com/youtube/v3"

#  All routes protected
router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

# -----------------------
# Helpers
# -----------------------

def extract_video_id(video_url: str) -> str:
    parsed = urlparse(video_url)
    if parsed.hostname == "youtu.be":
        return parsed.path[1:]

    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        vid = parse_qs(parsed.query).get("v", [None])[0]
        if vid:
            return vid

    raise HTTPException(status_code=400, detail=f"Invalid YouTube URL: {video_url}")

async def safe_get(endpoint: str, params: dict):
    url = f"{BASE_URL}/{endpoint}"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"YouTube API error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

def ensure_items(data: dict):
    items = data.get("items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Resource not found")
    return items

# -----------------------
# Core Endpoints
# -----------------------

@router.get("/channel-id")
async def channel_id(video_url: str = Query(...)):
    video_id = extract_video_id(video_url)
    data = await safe_get("videos", {"part": "snippet", "id": video_id, "key": YOUTUBE_API_KEY})
    items = ensure_items(data)
    return {"channel_id": items[0]["snippet"]["channelId"]}

@router.get("/live-streams")
async def live_streams(channel_id: str):
    data = await safe_get("search", {"part": "snippet", "channelId": channel_id, "eventType": "live", "type": "video", "key": YOUTUBE_API_KEY})
    streams = [{
        "video_id": item["id"]["videoId"],
        "title": item["snippet"]["title"],
        "description": item["snippet"].get("description"),
        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
        "channel_title": item["snippet"]["channelTitle"],
        "video_url": f"https://youtu.be/{item['id']['videoId']}"
    } for item in data.get("items", [])]
    return {"count": len(streams), "streams": streams}

@router.get("/video-details")
async def video_details(video_id: str):
    return await safe_get("videos", {"part": "snippet,statistics,contentDetails", "id": video_id, "key": YOUTUBE_API_KEY})

@router.get("/search")
async def search_videos(query: str, max_results: int = 10):
    return await safe_get("search", {"part": "snippet", "q": query, "type": "video", "maxResults": max_results, "key": YOUTUBE_API_KEY})

@router.get("/channel-videos")
async def channel_videos(channel_id: str, max_results: int = 10):
    return await safe_get("search", {"part": "snippet", "channelId": channel_id, "order": "date", "type": "video", "maxResults": max_results, "key": YOUTUBE_API_KEY})

@router.get("/video-comments")
async def video_comments(video_id: str, max_results: int = 20):
    return await safe_get("commentThreads", {"part": "snippet,replies", "videoId": video_id, "maxResults": max_results, "key": YOUTUBE_API_KEY})

@router.get("/related")
async def related_videos(video_id: str, max_results: int = 10):
    return await safe_get("search", {"part": "snippet", "relatedToVideoId": video_id, "type": "video", "maxResults": max_results, "key": YOUTUBE_API_KEY})

@router.get("/video-stats")
async def video_stats(video_id: str):
    return await safe_get("videos", {"part": "statistics", "id": video_id, "key": YOUTUBE_API_KEY})

@router.get("/channel-details")
async def channel_details(channel_id: str):
    return await safe_get("channels", {"part": "snippet,statistics,contentDetails", "id": channel_id, "key": YOUTUBE_API_KEY})

@router.get("/playlists")
async def channel_playlists(channel_id: str, max_results: int = 10):
    return await safe_get("playlists", {"part": "snippet,contentDetails", "channelId": channel_id, "maxResults": max_results, "key": YOUTUBE_API_KEY})

@router.get("/playlist-items")
async def playlist_items(playlist_id: str, max_results: int = 50):
    return await safe_get("playlistItems", {"part": "snippet,contentDetails", "playlistId": playlist_id, "maxResults": max_results, "key": YOUTUBE_API_KEY})

@router.get("/video-thumbnails")
async def video_thumbnails(video_id: str):
    data = await safe_get("videos", {"part": "snippet", "id": video_id, "key": YOUTUBE_API_KEY})
    items = ensure_items(data)
    return items[0]["snippet"]["thumbnails"]

@router.get("/video-duration")
async def video_duration(video_id: str):
    data = await safe_get("videos", {"part": "contentDetails", "id": video_id, "key": YOUTUBE_API_KEY})
    items = ensure_items(data)
    return {"duration": items[0]["contentDetails"]["duration"]}

@router.get("/channel-subscribers")
async def channel_subscribers(channel_id: str):
    data = await safe_get("channels", {"part": "statistics", "id": channel_id, "key": YOUTUBE_API_KEY})
    items = ensure_items(data)
    return {"subscriberCount": items[0]["statistics"].get("subscriberCount")}

@router.get("/trending")
async def trending(region_code: str = "US", max_results: int = 10):
    return await safe_get("videos", {"part": "snippet,statistics", "chart": "mostPopular", "regionCode": region_code, "maxResults": max_results, "key": YOUTUBE_API_KEY})

@router.get("/categories")
async def video_categories():
    return await safe_get("videoCategories", {"part": "snippet", "regionCode": "US", "key": YOUTUBE_API_KEY})

@router.get("/live-chat")
async def live_chat_messages(live_chat_id: str, max_results: int = 20):
    return await safe_get("liveChat/messages", {"part": "snippet,authorDetails", "liveChatId": live_chat_id, "maxResults": max_results, "key": YOUTUBE_API_KEY})