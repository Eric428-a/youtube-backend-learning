# YouTube Backend

## Project Overview

`youtube_backend` is a FastAPI-powered backend for fetching dynamic YouTube data with secure authentication. It supports:

* Channel ID retrieval from video URLs
* Live streams, trending videos, video details, playlists, comments, and related content
* User authentication via JWT and email verification
* Background email notifications

The backend is designed for both local development and production deployment, with robust error handling and scalable architecture.

## Folder Structure

```
youtube_backend/
├── app/
│   ├── main.py                     # FastAPI entrypoint
│   ├── config.py                   # Environment & config variables
│
│   ├── core/
│   │   ├── security.py             # Hashing, JWT functions
│   │   └── database.py             # MongoDB connection
│
│   ├── auth/
│   │   ├── routes.py               # Register/Login/Verify endpoints
│   │   ├── schemas.py              # Pydantic schemas for auth
│   │   ├── service.py              # OTP & email logic
│   │   └── utils.py                # Helper utilities
│
│   ├── dependencies/
│   │   └── auth_guard.py           # Protect endpoints, JWT validation
│
│   ├── routes/
│   │   └── youtube_routes.py       # YouTube API endpoints
│
│   └── services/
│       └── youtube_service.py      # YouTube API call logic
├── .env                            # Environment variables
├── requirements.txt                # Dependencies
└── README.md                        # Project overview and usage
```

## Environment Variables (.env)

* `YOUTUBE_API_KEY` : Your YouTube Data API key
* `MONGO_URI` : MongoDB connection string
* `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXP_MINUTES` : JWT authentication settings
* `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` : SendGrid email settings
* `FRONTEND_DOMAIN` : Frontend application URL (for OTP links or redirects)

## Installation

```bash
# Clone the repository
git clone <repo_url>
cd youtube_backend

# Install dependencies
pip install -r requirements.txt
```

## Running Locally

```bash
# Ensure .env is configured
uvicorn app.main:app --reload
```

* API docs available at `http://localhost:8000/docs`
* Auth and YouTube endpoints are protected and require JWT tokens after registration and login

## Endpoints Overview

### Auth

* `POST /auth/register` : Register user (triggers OTP email)
* `POST /auth/verify-otp` : Verify OTP to activate account
* `POST /auth/login` : Login user and receive JWT token

### YouTube (All Protected)

* `GET /youtube/channel-id?video_url=<url>` : Get channel ID from video URL
* `GET /youtube/live-streams?channel_id=<id>` : List live streams for a channel
* `GET /youtube/video-details?video_id=<id>` : Fetch video metadata
* `GET /youtube/video-comments?video_id=<id>&max_results=20` : Fetch comments for a video
* `GET /youtube/related?video_id=<id>&max_results=10` : Fetch related videos
* `GET /youtube/trending?region_code=US&max_results=10` : Fetch trending videos
* `GET /youtube/channel-videos?channel_id=<id>&max_results=10` : Fetch latest videos of a channel
* `GET /youtube/channel-details?channel_id=<id>` : Fetch channel metadata and statistics
* `GET /youtube/playlists?channel_id=<id>&max_results=10` : Fetch playlists of a channel
* `GET /youtube/playlist-items?playlist_id=<id>&max_results=50` : Fetch items of a playlist
* `GET /youtube/video-thumbnails?video_id=<id>` : Fetch all video thumbnails
* `GET /youtube/video-duration?video_id=<id>` : Get video duration in ISO 8601 format
* `GET /youtube/channel-subscribers?channel_id=<id>` : Get subscriber count of channel
* `GET /youtube/video-stats?video_id=<id>` : Get video statistics (views, likes, etc.)
* `GET /youtube/categories` : Fetch video categories
* `GET /youtube/live-chat?live_chat_id=<id>&max_results=20` : Fetch live chat messages

## Notes

* Designed for **easy extension**. Add new YouTube endpoints in `youtube_routes.py` and their logic in `youtube_service.py`.
* Emails are sent asynchronously via `BackgroundTasks` using SendGrid.
* Auth guards protect YouTube endpoints with JWT.
* Robust error handling for YouTube API failures.
* `.env` variables must be set before running.

## License

MIT License
