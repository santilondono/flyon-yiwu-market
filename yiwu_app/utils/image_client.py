"""
Client for the Flyon Image Server at images.flyon-yiwu-market.com
- Uploads images organized by list folder
- Names images by product reference
- Supports multiple images per product (ref_1.jpg, ref_2.jpg, ...)
"""
import os
import httpx
from pathlib import Path

IMAGE_SERVER_URL = os.getenv("IMAGE_SERVER_URL", "https://images.flyon-yiwu-market.com").rstrip("/")
IMAGE_SERVER_API_KEY = os.getenv("IMAGE_SERVER_API_KEY", "")
LOCAL_UPLOAD_DIR = os.getenv("UPLOAD_DIR", "assets/uploads")


def get_image_url(filepath: str) -> str:
    """filepath is like 'list_folder/ref_1.jpg'"""
    if not filepath:
        return ""
    if IMAGE_SERVER_URL:
        return f"{IMAGE_SERVER_URL}/images/{filepath}"
    return f"/uploads/{filepath}"


def _headers():
    return {"x-api-key": IMAGE_SERVER_API_KEY}


def ensure_folder(folder_name: str) -> bool:
    """Create a folder on the image server."""
    try:
        r = httpx.post(
            f"{IMAGE_SERVER_URL}/folder",
            json={"folder": folder_name},
            headers=_headers(),
            timeout=10,
        )
        return r.status_code in (200, 201, 409)  # 409 = already exists
    except Exception:
        return False


def upload_image_to_folder(
    folder: str,
    reference: str,
    index: int,
    file_content: bytes,
    content_type: str,
    original_filename: str,
) -> str:
    """
    Upload one image. Returns the filepath stored.
    index = 1-based position of this image for the product.
    - index 1 → REF001.jpg       (no suffix)
    - index 2 → REF001_1.jpg
    - index 3 → REF001_2.jpg
    """
    ext = Path(original_filename).suffix.lower() or ".jpg"
    safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in reference) or "product"
    if index == 1:
        filename = f"{safe_ref}{ext}"
    else:
        filename = f"{safe_ref}_{index - 1}{ext}"
    filepath = f"{folder}/{filename}"

    try:
        r = httpx.post(
            f"{IMAGE_SERVER_URL}/upload",
            files={"file": (filename, file_content, content_type)},
            data={"folder": folder},
            headers=_headers(),
            timeout=30,
        )
        r.raise_for_status()
        return filepath
    except Exception as e:
        # Fallback: local save
        local_dir = Path(LOCAL_UPLOAD_DIR) / folder
        local_dir.mkdir(parents=True, exist_ok=True)
        with open(local_dir / filename, "wb") as f:
            f.write(file_content)
        return filepath


def delete_image(filepath: str):
    """Delete image from server. filepath = 'folder/filename.jpg'"""
    if not filepath:
        return
    try:
        httpx.delete(
            f"{IMAGE_SERVER_URL}/delete/{filepath}",
            headers=_headers(),
            timeout=10,
        )
    except Exception:
        pass


def sanitize_folder_name(name: str) -> str:
    """Convert list name to a safe folder name."""
    safe = "".join(c if c.isalnum() or c in "-_ " else "" for c in name)
    return safe.strip().replace(" ", "_")[:60] or "list"

def rename_images_for_reference(
    folder: str,
    old_ref: str,
    new_ref: str,
    current_paths: list[str],
) -> list[str]:
    """
    Rename server files when reference changes.
    Returns the updated list of filepaths.
    """
    if old_ref == new_ref or not current_paths:
        return current_paths

    safe_old = "".join(c if c.isalnum() or c in "-_" else "_" for c in old_ref) or "product"
    safe_new = "".join(c if c.isalnum() or c in "-_" else "_" for c in new_ref) or "product"

    new_paths = []
    for i, old_filepath in enumerate(current_paths):
        index = i + 1  # 1-based
        # Build expected new filename using same logic as upload_image_to_folder
        ext = Path(old_filepath).suffix.lower() or ".jpg"
        if index == 1:
            new_filename = f"{safe_new}{ext}"
        else:
            new_filename = f"{safe_new}_{index - 1}{ext}"
        new_filepath = f"{folder}/{new_filename}"

        if old_filepath != new_filepath:
            try:
                r = httpx.post(
                    f"{IMAGE_SERVER_URL}/rename",
                    json={"old_path": old_filepath, "new_path": new_filepath},
                    headers=_headers(),
                    timeout=10,
                )
                if r.status_code == 200:
                    new_paths.append(new_filepath)
                else:
                    new_paths.append(old_filepath)  # keep old if rename failed
            except Exception:
                new_paths.append(old_filepath)
        else:
            new_paths.append(old_filepath)

    return new_paths
def upload_temp_image(
    folder: str,
    file_content: bytes,
    content_type: str,
    original_filename: str,
) -> str:
    """
    Upload image immediately with a temporary name: tmp_xxxxxxxx.jpg
    Returns the full filepath (folder/tmp_xxx.jpg).
    """
    import uuid
    ext = Path(original_filename).suffix.lower() or ".jpg"
    temp_name = f"tmp_{uuid.uuid4().hex[:12]}{ext}"
    filepath = f"{folder}/{temp_name}"
    try:
        r = httpx.post(
            f"{IMAGE_SERVER_URL}/upload",
            files={"file": (temp_name, file_content, content_type)},
            data={"folder": folder},
            headers=_headers(),
            timeout=30,
        )
        r.raise_for_status()
        return filepath
    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")
def upload_export(filename: str, file_bytes: bytes, content_type: str) -> str:
    """
    Upload an export file (Excel/ZIP) to the image server.
    Returns the direct download URL.
    """
    try:
        r = httpx.post(
            f"{IMAGE_SERVER_URL}/save-export",
            files={"file": (filename, file_bytes, content_type)},
            data={"filename": filename},
            headers=_headers(),
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        safe_name = data["filename"]
        return f"{IMAGE_SERVER_URL}/exports/{safe_name}"
    except Exception as e:
        raise Exception(f"Export upload failed: {str(e)}")

