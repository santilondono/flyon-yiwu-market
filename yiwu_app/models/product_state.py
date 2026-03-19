import reflex as rx
from sqlalchemy import select
import os, base64, io
from datetime import datetime
from yiwu_app.models.models import ProductList, Product
from yiwu_app.models.auth_state import AuthState
from yiwu_app.utils.excel import export_to_excel
from yiwu_app.utils.export_zip import export_list_zip
from yiwu_app.utils.image_client import (
    get_image_url, upload_image_to_folder, upload_temp_image,
    delete_image, ensure_folder, rename_images_for_reference,
    IMAGE_SERVER_URL
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "assets/uploads")


def compress_image(data: bytes, max_size: tuple, quality: int) -> tuple:
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(max_size, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        return data, "image/jpeg"


class ProductState(AuthState):
    is_loading_products: bool = True
    current_list_id: int = 0
    current_list_name: str = ""
    current_list_desc: str = ""
    current_list_folder: str = ""
    products: list[dict] = []

    show_product_modal: bool = False
    editing_product_id: int = 0

    pf_store: str = ""
    pf_store_contact: str = ""
    pf_reference: str = ""
    pf_description: str = ""
    pf_measurement: str = ""
    pf_price: str = ""
    pf_qty: str = ""
    pf_cbm: str = ""
    pf_material: str = ""
    pf_notes: str = ""

    # Each item: {"preview_url": "https://...", "filepath": "folder/tmp_xxx.jpg", "is_temp": True}
    pf_images: list[dict] = []

    product_error: str = ""
    is_saving: bool = False
    is_uploading_image: bool = False
    confirm_delete_id: int = 0
    is_exporting_excel: bool = False
    is_exporting_zip: bool = False

    def on_load(self):
        self._load_user_from_token()
        if not self.is_authenticated:
            return rx.redirect("/login")
        list_id = self.router.page.params.get("list_id", "")
        if list_id:
            self._load_list_data(int(list_id))

    def _load_list_data(self, lid: int):
        self.is_loading_products = True
        with rx.session() as session:
            lst = session.get(ProductList, lid)
            if not lst or lst.owner_id != self.user_id:
                return
            self.current_list_id = lst.id
            self.current_list_name = lst.name
            self.current_list_desc = lst.description or ""
            self.current_list_folder = lst.folder_name or ""
            rows = session.execute(
                select(Product).where(Product.list_id == lid).order_by(Product.created_at)
            ).scalars().all()
            self.products = [self._to_dict(p) for p in rows]
        self.is_loading_products = False

    def reload_products(self):
        if self.current_list_id:
            self._load_list_data(self.current_list_id)

    def _parse_image_paths(self, image_paths: str) -> list[str]:
        if not image_paths:
            return []
        return [p.strip() for p in image_paths.split(",") if p.strip()]

    def _to_dict(self, p: Product) -> dict:
        paths = self._parse_image_paths(p.image_paths or "")
        image_urls = [get_image_url(fp) for fp in paths]
        return {
            "id": p.id,
            "store": p.store or "",
            "store_contact": p.store_contact or "",
            "reference": p.reference or "",
            "description": p.description or "",
            "measurement": p.measurement or "",
            "price": str(p.price) if p.price is not None else "",
            "qty": str(p.qty) if p.qty is not None else "",
            "cbm": str(p.cbm) if p.cbm is not None else "",
            "material": p.material or "",
            "notes": p.notes or "",
            "image_paths": p.image_paths or "",
            "image_urls": image_urls,
            "first_image_url": image_urls[0] if image_urls else "",
            "image_count": len(image_urls),
            "created_at": p.created_at.strftime("%d/%m/%Y %H:%M") if p.created_at else "",
        }

    def open_create_product(self):
        self._reset_form()
        self.editing_product_id = 0
        self.show_product_modal = True

    def open_edit_product(self, product_id: int):
        p = next((x for x in self.products if x["id"] == product_id), None)
        if not p:
            return
        self.editing_product_id = product_id
        self.pf_store = p["store"]
        self.pf_store_contact = p["store_contact"]
        self.pf_reference = p["reference"]
        self.pf_description = p["description"]
        self.pf_measurement = p["measurement"]
        self.pf_price = p["price"]
        self.pf_qty = p["qty"]
        self.pf_cbm = p["cbm"]
        self.pf_material = p["material"]
        self.pf_notes = p["notes"]
        paths = self._parse_image_paths(p["image_paths"])
        urls = p["image_urls"]
        # Existing images — already on server with final name, not temp
        self.pf_images = [
            {"preview_url": url, "filepath": fp, "is_temp": False}
            for url, fp in zip(urls, paths)
        ]
        self.product_error = ""
        self.show_product_modal = True

    def close_product_modal(self):
        """Close modal and delete any temp images that weren't saved."""
        self._cleanup_temp_images()
        self.show_product_modal = False

    def _cleanup_temp_images(self):
        """Delete temp images from server if product was not saved."""
        for img in self.pf_images:
            if img.get("is_temp") and img.get("filepath"):
                delete_image(img["filepath"])

    def _reset_form(self):
        self.pf_store = ""
        self.pf_store_contact = ""
        self.pf_reference = ""
        self.pf_description = ""
        self.pf_measurement = ""
        self.pf_price = ""
        self.pf_qty = ""
        self.pf_cbm = ""
        self.pf_material = ""
        self.pf_notes = ""
        self.pf_images = []
        self.product_error = ""

    def set_pf_store(self, v): self.pf_store = v
    def set_pf_store_contact(self, v): self.pf_store_contact = v
    def set_pf_reference(self, v): self.pf_reference = v; self.product_error = ""
    def set_pf_description(self, v): self.pf_description = v
    def set_pf_measurement(self, v): self.pf_measurement = v
    def set_pf_price(self, v): self.pf_price = v
    def set_pf_qty(self, v): self.pf_qty = v
    def set_pf_cbm(self, v): self.pf_cbm = v
    def set_pf_material(self, v): self.pf_material = v
    def set_pf_notes(self, v): self.pf_notes = v

    def remove_image(self, index: int):
        """Remove image from list — delete from server if temp."""
        if 0 <= index < len(self.pf_images):
            img = self.pf_images[index]
            if img.get("is_temp") and img.get("filepath"):
                delete_image(img["filepath"])
            self.pf_images = [x for i, x in enumerate(self.pf_images) if i != index]

    async def handle_image_upload(self, files: list[rx.UploadFile]):
        """
        Upload image immediately to server as tmp_xxx.jpg.
        Preview comes from the server URL — no base64, no latency on preview.
        """
        if not files:
            return
        allowed = {"image/jpeg", "image/png", "image/webp"}
        folder = self.current_list_folder or "default"

        self.is_uploading_image = True
        yield

        for file in files:
            data = await file.read()
            if file.content_type not in allowed:
                self.product_error = f"Skipped {file.filename}: only JPG, PNG, WebP."
                continue
            try:
                # Compress before uploading
                compressed, content_type = compress_image(data, (1600, 1600), 82)
                # Upload as temp file
                filepath = upload_temp_image(
                    folder=folder,
                    file_content=compressed,
                    content_type=content_type,
                    original_filename=file.filename,
                )
                preview_url = get_image_url(filepath)
                self.pf_images = self.pf_images + [{
                    "preview_url": preview_url,
                    "filepath": filepath,
                    "is_temp": True,
                }]
            except Exception as e:
                self.product_error = f"Upload error: {str(e)}"

        self.is_uploading_image = False

    def save_product(self):
        if not self.pf_reference.strip() and not self.pf_description.strip():
            self.product_error = "Reference or description is required."
            return
        self.is_saving = True
        yield

        ref = self.pf_reference.strip() or self.pf_description.strip()[:20]
        folder = self.current_list_folder or "default"

        # Rename temp images to final names based on reference
        final_paths = []
        new_index = 1
        for img in self.pf_images:
            fp = img.get("filepath", "")
            if img.get("is_temp") and fp:
                # Rename tmp_xxx.jpg → REF001.jpg
                final_paths_so_far = rename_images_for_reference(
                    folder=folder,
                    old_ref=fp.split("/")[-1].replace(".jpg", "").replace(".jpeg", "").replace(".png", "").replace(".webp", ""),
                    new_ref=ref,
                    current_paths=[fp],
                )
                # Use upload_image_to_folder naming logic directly
                from yiwu_app.utils.image_client import sanitize_folder_name
                import pathlib
                ext = pathlib.Path(fp).suffix or ".jpg"
                safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in ref) or "product"
                new_filename = f"{safe_ref}{ext}" if new_index == 1 else f"{safe_ref}_{new_index - 1}{ext}"
                new_filepath = f"{folder}/{new_filename}"
                from yiwu_app.utils.image_client import httpx as _httpx, IMAGE_SERVER_URL, _headers
                try:
                    _httpx.post(
                        f"{IMAGE_SERVER_URL}/rename",
                        json={"old_path": fp, "new_path": new_filepath},
                        headers=_headers(),
                        timeout=10,
                    )
                    final_paths.append(new_filepath)
                except Exception:
                    final_paths.append(fp)  # keep original if rename fails
            else:
                final_paths.append(fp)
            new_index += 1

        image_paths_str = ",".join(final_paths)

        def to_float(v):
            try: return float(v) if v and v.strip() else None
            except: return None

        def to_int(v):
            try: return int(v) if v and v.strip() else None
            except: return None

        with rx.session() as session:
            if self.editing_product_id:
                p = session.get(Product, self.editing_product_id)
                if p and p.list_id == self.current_list_id:
                    old_ref = p.reference or ""
                    new_ref = self.pf_reference.strip()
                    if old_ref and new_ref and old_ref != new_ref:
                        # Rename existing (non-temp) final images
                        existing_paths = [
                            img["filepath"] for img in self.pf_images
                            if not img.get("is_temp") and img.get("filepath")
                        ]
                        if existing_paths:
                            renamed = rename_images_for_reference(
                                folder=folder, old_ref=old_ref,
                                new_ref=new_ref, current_paths=existing_paths,
                            )
                            # Rebuild final_paths with renamed existing + new temp-renamed
                            temp_paths = [
                                img["filepath"] for img in self.pf_images
                                if img.get("is_temp")
                            ]
                            image_paths_str = ",".join(renamed + [fp for fp in final_paths if fp not in existing_paths])
                    p.store = self.pf_store.strip()
                    p.store_contact = self.pf_store_contact.strip()
                    p.reference = self.pf_reference.strip()
                    p.description = self.pf_description.strip()
                    p.measurement = self.pf_measurement.strip()
                    p.price = to_float(self.pf_price)
                    p.qty = to_int(self.pf_qty)
                    p.cbm = to_float(self.pf_cbm)
                    p.material = self.pf_material.strip()
                    p.notes = self.pf_notes.strip()
                    p.image_paths = image_paths_str
                    p.updated_at = datetime.utcnow()
            else:
                p = Product(
                    list_id=self.current_list_id,
                    store=self.pf_store.strip(),
                    store_contact=self.pf_store_contact.strip(),
                    reference=self.pf_reference.strip(),
                    description=self.pf_description.strip(),
                    measurement=self.pf_measurement.strip(),
                    price=to_float(self.pf_price),
                    qty=to_int(self.pf_qty),
                    cbm=to_float(self.pf_cbm),
                    material=self.pf_material.strip(),
                    notes=self.pf_notes.strip(),
                    image_paths=image_paths_str,
                )
                session.add(p)
            lst = session.get(ProductList, self.current_list_id)
            if lst:
                lst.updated_at = datetime.utcnow()
            session.commit()

        self.is_saving = False
        self.show_product_modal = False
        self.reload_products()

    def request_delete(self, product_id: int):
        self.confirm_delete_id = product_id

    def cancel_delete(self):
        self.confirm_delete_id = 0

    def confirm_delete(self):
        with rx.session() as session:
            p = session.get(Product, self.confirm_delete_id)
            if p and p.list_id == self.current_list_id:
                for fp in self._parse_image_paths(p.image_paths or ""):
                    delete_image(fp)
                session.delete(p)
                session.commit()
        self.confirm_delete_id = 0
        self.reload_products()

    def export_excel(self):
        self.is_exporting_excel = True
        yield
        with rx.session() as session:
            rows = session.execute(
                select(Product).where(Product.list_id == self.current_list_id).order_by(Product.created_at)
            ).scalars().all()
            products = [
                {
                    "store": p.store or "", "store_contact": p.store_contact or "",
                    "reference": p.reference or "", "description": p.description or "",
                    "measurement": p.measurement or "", "price": p.price,
                    "qty": p.qty, "cbm": p.cbm, "material": p.material or "",
                    "notes": p.notes or "",
                    "image_paths": self._parse_image_paths(p.image_paths or ""),
                }
                for p in rows
            ]
        excel_bytes = export_to_excel(self.current_list_name, self.current_list_desc, products)
        b64 = base64.b64encode(excel_bytes).decode()
        filename = f"{self.current_list_name.replace(' ', '_')}.xlsx"
        self.is_exporting_excel = False
        yield rx.call_script(
            f"const a=document.createElement('a');a.href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}';a.download='{filename}';document.body.appendChild(a);a.click();document.body.removeChild(a);"
        )

    def export_zip(self):
        self.is_exporting_zip = True
        yield
        with rx.session() as session:
            rows = session.execute(
                select(Product).where(Product.list_id == self.current_list_id).order_by(Product.created_at)
            ).scalars().all()
            products = [
                {
                    "store": p.store or "", "store_contact": p.store_contact or "",
                    "reference": p.reference or "", "description": p.description or "",
                    "measurement": p.measurement or "", "price": p.price,
                    "qty": p.qty, "cbm": p.cbm, "material": p.material or "",
                    "notes": p.notes or "",
                    "image_paths": self._parse_image_paths(p.image_paths or ""),
                }
                for p in rows
            ]
        zip_bytes = export_list_zip(self.current_list_name, self.current_list_desc, products)
        b64 = base64.b64encode(zip_bytes).decode()
        filename = f"{self.current_list_name.replace(' ', '_')}_export.zip"
        self.is_exporting_zip = False
        yield rx.call_script(
            f"const a=document.createElement('a');a.href='data:application/zip;base64,{b64}';a.download='{filename}';document.body.appendChild(a);a.click();document.body.removeChild(a);"
        )
