import os
from typing import Final
from urllib import error, parse, request

from fastapi import HTTPException, UploadFile

_DEFAULT_MAX_FILE_SIZE_MB: Final[int] = 10


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    raise HTTPException(
        status_code=500,
        detail=f"Missing required environment variable: {name}",
    )


def _allowed_image_mime_types() -> set[str]:
    configured = os.getenv("ALLOWED_IMAGE_MIME_TYPES", "").strip()
    if configured:
        return {value.strip().lower() for value in configured.split(",") if value.strip()}
    return {"image/jpeg", "image/png", "image/webp", "image/gif"}


def _supabase_service_key() -> str:
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if service_role_key:
        return service_role_key
    return _required_env("SUPABASE_KEY")


def _max_file_size_bytes() -> int:
    max_size_mb = int(os.getenv("MAX_UPLOAD_FILE_SIZE_MB", str(_DEFAULT_MAX_FILE_SIZE_MB)))
    return max_size_mb * 1024 * 1024


def is_supabase_storage_url(public_url: str) -> bool:
    supabase_url = _required_env("SUPABASE_URL").rstrip("/")
    bucket_name = os.getenv("SUPABASE_STORAGE_BUCKET", "uploads").strip() or "uploads"
    parsed_public_url = parse.urlparse(public_url)
    parsed_supabase_url = parse.urlparse(supabase_url)
    public_prefix = f"/storage/v1/object/public/{bucket_name}/"

    return (
        parsed_public_url.scheme == parsed_supabase_url.scheme
        and parsed_public_url.netloc == parsed_supabase_url.netloc
        and parsed_public_url.path.startswith(public_prefix)
    )


def upload_image_to_supabase(
    *,
    data: bytes,
    destination_path: str,
    content_type: str,
) -> str:
    supabase_url = _required_env("SUPABASE_URL").rstrip("/")
    service_role_key = _supabase_service_key()
    bucket_name = os.getenv("SUPABASE_STORAGE_BUCKET", "uploads").strip() or "uploads"
    encoded_path = parse.quote(destination_path, safe="/")
    upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{encoded_path}"

    req = request.Request(
        upload_url,
        data=data,
        method="POST",
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": content_type,
            "x-upsert": "false",
        },
    )
    try:
        with request.urlopen(req):
            pass
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore") or "Failed to upload image"
        raise HTTPException(status_code=502, detail=f"Supabase upload failed: {detail}") from exc
    except error.URLError as exc:
        raise HTTPException(status_code=502, detail="Could not reach Supabase Storage") from exc

    return f"{supabase_url}/storage/v1/object/public/{bucket_name}/{encoded_path}"


def get_supabase_storage_object_path(public_url: str) -> str:
    bucket_name = os.getenv("SUPABASE_STORAGE_BUCKET", "uploads").strip() or "uploads"
    parsed_public_url = parse.urlparse(public_url)

    if not is_supabase_storage_url(public_url):
        raise HTTPException(status_code=400, detail="Invalid storage URL")

    public_prefix = f"/storage/v1/object/public/{bucket_name}/"
    object_path = parse.unquote(parsed_public_url.path[len(public_prefix):]).strip("/")
    if not object_path:
        raise HTTPException(status_code=400, detail="Invalid storage URL")
    return object_path


def delete_image_from_supabase(*, public_url: str) -> bool:
    if not is_supabase_storage_url(public_url):
        return False

    supabase_url = _required_env("SUPABASE_URL").rstrip("/")
    service_role_key = _supabase_service_key()
    bucket_name = os.getenv("SUPABASE_STORAGE_BUCKET", "uploads").strip() or "uploads"
    object_path = get_supabase_storage_object_path(public_url)
    encoded_path = parse.quote(object_path, safe="/")
    delete_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{encoded_path}"

    req = request.Request(
        delete_url,
        method="DELETE",
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
        },
    )
    try:
        with request.urlopen(req):
            pass
    except error.HTTPError as exc:
        if exc.code == 404:
            return True
        detail = exc.read().decode("utf-8", errors="ignore") or "Failed to delete image"
        raise HTTPException(status_code=502, detail=f"Supabase delete failed: {detail}") from exc
    except error.URLError as exc:
        raise HTTPException(status_code=502, detail="Could not reach Supabase Storage") from exc

    return True


async def validate_image_upload(file: UploadFile) -> bytes:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    content_type = (file.content_type or "").lower().strip()
    if content_type not in _allowed_image_mime_types():
        raise HTTPException(status_code=400, detail="Unsupported file type")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(data) > _max_file_size_bytes():
        raise HTTPException(status_code=400, detail="File is too large")

    return data
