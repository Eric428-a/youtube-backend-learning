# app/core/database.py
from pymongo import MongoClient
from app.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["youtube_auth"]
users_collection = db["users"]