import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.modules.auth.router import router as auth_router
from app.modules.bookings.router import router as bookings_router
from app.modules.businesses.router import router as businesses_router
from app.modules.favourites.router import router as favourites_router
from app.modules.interests.router import router as interests_router
from app.modules.listings.router import router as listings_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.reviews.router import router as reviews_router
from app.modules.users.router import router as profile_router
from app.modules.employees.router import router as employees_router

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
app.include_router(auth_router)
app.include_router(listings_router)
app.include_router(bookings_router)
app.include_router(reviews_router)
app.include_router(recommendations_router)
app.include_router(profile_router)
app.include_router(favourites_router)
app.include_router(interests_router)
app.include_router(businesses_router)
app.include_router(employees_router)
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
