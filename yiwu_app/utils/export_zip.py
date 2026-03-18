"""
Export a product list as a ZIP containing:
  - products.xlsx
  - images/  (all product photos downloaded from the image server)
"""
import io
import os
import zipfile
import httpx
from yiwu_app.utils.excel import export_to_excel

IMAGE_SERVER_URL = os.getenv("IMAGE_SERVER_URL", "").rstrip("/")
IMAGE_SERVER_API_KEY = os.getenv("IMAGE_SERVER_API_KEY", "")
LOCAL_UPLOAD_DIR = os.getenv("UPLOAD_DIR", "assets/uploads")


def fetch_image(filepath: str) -> bytes | None:
    """Fetch image bytes from remote server or local disk."""
    if not filepath:
        return None
    if IMAGE_SERVER_URL:
        try:
            r = httpx.get(
                f"{IMAGE_SERVER_URL}/images/{filepath}",
                timeout=15,
            )
            if r.status_code == 200:
                return r.content
        except Exception:
            pass
    else:
        import os as _os
        local = _os.path.join(LOCAL_UPLOAD_DIR, filepath)
        if _os.path.exists(local):
            with open(local, "rb") as f:
                return f.read()
    return None


def export_list_zip(
    list_name: str,
    description: str,
    products: list,
) -> bytes:
    """
    Build a ZIP in memory:
      ListName.xlsx
      images/
        REF001.jpg
        REF001_1.jpg
        REF002.jpg
        ...
    Returns the ZIP as bytes.
    """
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. Excel file
        excel_bytes = export_to_excel(list_name, description, products)
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in list_name).strip()
        zf.writestr(f"{safe_name}.xlsx", excel_bytes)

        # 2. Images folder
        added = set()
        for p in products:
            paths = p.get("image_paths", [])
            if isinstance(paths, str):
                paths = [x.strip() for x in paths.split(",") if x.strip()]
            for filepath in paths:
                if filepath in added:
                    continue
                img_bytes = fetch_image(filepath)
                if img_bytes:
                    # Keep only the filename inside images/ folder
                    filename = filepath.split("/")[-1]
                    zf.writestr(f"images/{filename}", img_bytes)
                added.add(filepath)

    buf.seek(0)
    return buf.read()
