# app/auth/utils.py
from datetime import datetime

def is_valid_email(email: str) -> bool:
    """Basic check for email structure."""
    return "@" in email and "." in email

def format_response(message: str, data: dict = None) -> dict:
    """Standard response format for API."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "message": message,
        "data": data or {}
    }