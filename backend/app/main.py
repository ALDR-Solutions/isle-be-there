import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

from app.infrastructure.storage import (
    delete_image_from_supabase,
    get_supabase_storage_object_path,
    is_supabase_storage_url,
    upload_image_to_supabase,
    validate_image_upload,
)
from app.modules.auth.router import router as auth_router
from app.modules.bookings.router import router as bookings_router
from app.modules.businesses.router import router as businesses_router
from app.modules.users.models import User
from app.modules.favourites.router import router as favourites_router
from app.modules.interests.router import router as interests_router
from app.modules.listings.router import router as listings_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.reviews.router import router as reviews_router
from app.modules.users.router import router as profile_router
from app.modules.employees.router import router as employees_router
from app.modules.services.router import router as services_router
from app.shared.dependencies.permissions import get_current_user

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

app = FastAPI(
    title="Isle Be There API",
    description="Travel platform API with AI recommendations",
    version="1.0.0",
)


class UploadCleanupRequest(BaseModel):
    urls: list[str]


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
app.include_router(services_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Form(default="misc"),
    current_user: User = Depends(get_current_user),
):
    safe_folder = "".join(ch for ch in folder.lower() if ch.isalnum() or ch in {"-", "_"})
    folder_name = safe_folder or "misc"
    extension = Path(file.filename).suffix.lower()
    file_bytes = await validate_image_upload(file)
    object_path = f"{folder_name}/{current_user.id}/{uuid4().hex}{extension}"

    public_url = upload_image_to_supabase(
        data=file_bytes,
        destination_path=object_path,
        content_type=(file.content_type or "application/octet-stream"),
    )
    return {"filename": file.filename, "url": public_url}


@app.delete("/api/upload")
async def delete_uploaded_images(
    payload: UploadCleanupRequest = Body(...),
    current_user: User = Depends(get_current_user),
):
    user_id = str(current_user.id)

    for url in payload.urls:
        if not is_supabase_storage_url(url):
            continue
        object_path = get_supabase_storage_object_path(url)
        path_parts = object_path.split("/")
        if len(path_parts) < 2 or path_parts[1] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this image")

    for url in payload.urls:
        delete_image_from_supabase(public_url=url)

    return {"detail": "Deleted"}

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
