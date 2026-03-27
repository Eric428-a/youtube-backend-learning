# app/auth/service.py
import random
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL

# In-memory OTP store
otp_store = {}

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def store_otp(email: str, otp: str):
    """Store OTP with expiry"""
    otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }

def verify_otp_logic(email: str, otp: str) -> tuple[bool, str]:
    """Verify OTP correctness and expiration"""
    record = otp_store.get(email)
    if not record:
        return False, "No OTP found"

    if datetime.utcnow() > record["expires_at"]:
        otp_store.pop(email)
        return False, "OTP expired"

    if record["otp"] != otp:
        return False, "Invalid OTP"

    otp_store.pop(email)
    return True, "Verified"

def send_email(to_email: str, subject: str, body: str):
    """Send email using SendGrid"""
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"SendGrid status: {response.status_code}")
    except Exception as e:
        print(f"SendGrid error: {e}")
