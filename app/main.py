# app/main.py
from fastapi import FastAPI
from app.routes import youtube_routes
from app.auth.routes import router as auth_router

app = FastAPI(
    title="Dynamic YouTube Backend",
    description="Fetch YouTube data with secure authenticated access",
    version="2.0"
)

# Include Auth routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Include YouTube routes (all protected)
app.include_router(youtube_routes.router, prefix="/youtube", tags=["YouTube"])

@app.get("/")
def root():
    return {
        "message": "Backend running ",
        "docs": "/docs",
        "auth": "/auth",
        "youtube": "/youtube"
    }