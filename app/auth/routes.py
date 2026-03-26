# app/auth/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.auth.schemas import UserCreate, UserLogin, VerifyOTP
from app.core.database import users_collection
from app.core.security import hash_password, verify_password, create_access_token
from app.auth.service import generate_otp, store_otp, verify_otp_logic, send_email
from app.auth.utils import is_valid_email, format_response

router = APIRouter()

# -------------------------
# Register
# -------------------------
@router.post("/register")
def register(user: UserCreate, background_tasks: BackgroundTasks):
    if not is_valid_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User exists")

    users_collection.insert_one({
        "email": user.email,
        "password": hash_password(user.password),
        "is_verified": False
    })

    otp = generate_otp()
    store_otp(user.email, otp)

    background_tasks.add_task(
        send_email,
        user.email,
        "Verify your account",
        f"Your OTP is {otp}"
    )

    return format_response("Registered. Check email for OTP")

# -------------------------
# Verify OTP
# -------------------------
@router.post("/verify-otp")
def verify_otp(data: VerifyOTP):
    valid, msg = verify_otp_logic(data.email, data.otp)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    users_collection.update_one(
        {"email": data.email},
        {"$set": {"is_verified": True}}
    )

    return format_response("Verified")

# -------------------------
# Login
# -------------------------
@router.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not db_user.get("is_verified"):
        raise HTTPException(status_code=400, detail="Verify email first")

    token = create_access_token({"sub": user.email})
    return format_response("Login successful", {"access_token": token})
