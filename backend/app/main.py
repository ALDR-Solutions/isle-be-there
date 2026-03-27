from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
import shutil
from dotenv import load_dotenv
load_dotenv()

from app.api.routes import favourites, reviews
from app.api.routes import ai, auth, bookings, businesses, interests, listings, profile

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
UPLOAD_DIR = BASE_DIR.parent / "uploads"

app = FastAPI(
    title="Isle Be There API",
    description="Travel platform API with AI recommendations",
    version="1.0.0",
)


def get_allowed_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
    if configured_origins.strip():
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]


# CORS
app.add_middleware(
    CORSMiddleware,
    # Explicit origins keep credentialed requests compatible across browsers.
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(bookings.router)
app.include_router(reviews.router)
app.include_router(ai.router)
app.include_router(profile.router)
app.include_router(favourites.router)
app.include_router(interests.router)
app.include_router(businesses.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "url": f"/uploads/{file.filename}"}

# Root route - serve Vue app
@app.get("/")
async def root():
    if FRONTEND_DIST.exists():
        return FileResponse(str(FRONTEND_DIST / "index.html"))
    return {"message": "Isle Be There API"}

# Catch-all for Vue Router SPA
@app.get("/{path:path}")
async def serve_spa(path: str):
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")

    if FRONTEND_DIST.exists():
        return FileResponse(str(FRONTEND_DIST / "index.html"))
    return {"message": "Isle Be There API"}
