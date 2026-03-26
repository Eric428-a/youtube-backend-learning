# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# YouTube API
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# SendGrid Email
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

# JWT Settings
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", 60))

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")