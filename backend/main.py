from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import shutil

from app.api import auth, listings, bookings, reviews, ai, profile, favorites, interests, businesses

# Paths
BASE_DIR = Path(__file__).parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
UPLOAD_DIR = BASE_DIR / "uploads"

app = FastAPI(
    title="Isle Be There API",
    description="Travel platform API with AI recommendations",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(favorites.router)
app.include_router(interests.router)
app.include_router(businesses.router)

# Root route - serve Vue app
@app.get("/")
async def root():
    if FRONTEND_DIST.exists():
        return FileResponse(str(FRONTEND_DIST / "index.html"))
    return {"message": "Isle Be There API"}

# Catch-all for Vue Router SPA
@app.get("/{path:path}")
async def serve_spa(path: str):
    if FRONTEND_DIST.exists():
        return FileResponse(str(FRONTEND_DIST / "index.html"))
    return {"message": "Isle Be There API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "url": f"/uploads/{file.filename}"}
