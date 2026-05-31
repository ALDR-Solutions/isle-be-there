from urllib import error, parse, request

from fastapi import HTTPException, UploadFile

from app.core.config import settings


def is_supabase_storage_url(public_url: str) -> bool:
    try:
        supabase_url = settings.require_supabase_url()
    except RuntimeError:
        return False

    bucket_name = settings.supabase_storage_bucket
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
    try:
        supabase_url = settings.require_supabase_url()
        service_role_key = settings.require_supabase_service_role_key()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    bucket_name = settings.supabase_storage_bucket
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
    bucket_name = settings.supabase_storage_bucket
    parsed_public_url = parse.urlparse(public_url)

    if not is_supabase_storage_url(public_url):
        raise HTTPException(status_code=400, detail="Invalid storage URL")

    public_prefix = f"/storage/v1/object/public/{bucket_name}/"
    object_path = parse.unquote(parsed_public_url.path[len(public_prefix) :]).strip("/")
    if not object_path:
        raise HTTPException(status_code=400, detail="Invalid storage URL")
    return object_path


def delete_image_from_supabase(*, public_url: str) -> bool:
    if not is_supabase_storage_url(public_url):
        return False

    try:
        supabase_url = settings.require_supabase_url()
        service_role_key = settings.require_supabase_service_role_key()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    bucket_name = settings.supabase_storage_bucket
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
    if content_type not in settings.allowed_image_mime_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(data) > settings.max_upload_file_size_bytes:
        raise HTTPException(status_code=400, detail="File is too large")

    return data
