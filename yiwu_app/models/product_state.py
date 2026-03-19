import reflex as rx
from sqlalchemy import select
import os, base64, io
from datetime import datetime
from yiwu_app.models.models import ProductList, Product
from yiwu_app.models.auth_state import AuthState
from yiwu_app.utils.excel import export_to_excel
from yiwu_app.utils.export_zip import export_list_zip
from yiwu_app.utils.image_client import (
    get_image_url, upload_image_to_folder, delete_image, ensure_folder, rename_images_for_reference
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "assets/uploads")
MAX_PREVIEW_SIZE = (800, 800)   # max preview dimensions
PREVIEW_QUALITY = 72            # JPEG quality for preview (smaller = faster)
UPLOAD_QUALITY = 85             # JPEG quality for server upload


def compress_image(data: bytes, max_size: tuple, quality: int) -> tuple[bytes, str]:
    """Compress and resize image. Returns (bytes, content_type)."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        # Convert RGBA to RGB if needed
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # Resize maintaining aspect ratio
        img.thumbnail(max_size, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        return data, "image/jpeg"


class ProductState(AuthState):
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
    pf_images: list[dict] = []

    product_error: str = ""
    is_saving: bool = False
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
        self.pf_images = [
            {"preview": url, "b64": "", "content_type": "", "filename": "", "filepath": fp}
            for url, fp in zip(urls, paths)
        ]
        self.product_error = ""
        self.show_product_modal = True

    def close_product_modal(self):
        self.show_product_modal = False

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
        if 0 <= index < len(self.pf_images):
            self.pf_images = [img for i, img in enumerate(self.pf_images) if i != index]

    async def handle_image_upload(self, files: list[rx.UploadFile]):
        """Read and compress images locally, store as b64. Upload on save only."""
        if not files:
            return
        allowed = {"image/jpeg", "image/png", "image/webp"}
        for file in files:
            data = await file.read()
            if file.content_type not in allowed:
                self.product_error = f"Skipped {file.filename}: only JPG, PNG, WebP."
                continue
            # Compress preview small (fast display)
            preview_data, _ = compress_image(data, (600, 600), 65)
            b64_preview = base64.b64encode(preview_data).decode()
            # Compress upload medium quality
            upload_data, _ = compress_image(data, (1600, 1600), 82)
            b64_upload = base64.b64encode(upload_data).decode()
            self.pf_images = self.pf_images + [{
                "preview": f"data:image/jpeg;base64,{b64_preview}",
                "b64": b64_upload,
                "content_type": "image/jpeg",
                "filename": file.filename,
                "filepath": "",
            }]

    def save_product(self):
        if not self.pf_reference.strip() and not self.pf_description.strip():
            self.product_error = "Reference or description is required."
            return
        self.is_saving = True
        yield

        ref = self.pf_reference.strip() or self.pf_description.strip()[:20]
        folder = self.current_list_folder or "default"

        final_images = []
        new_index = 1
        for img in self.pf_images:
            if img["filepath"]:
                final_images.append(img["filepath"])
            else:
                try:
                    filepath = upload_image_to_folder(
                        folder=folder,
                        reference=ref,
                        index=new_index,
                        file_content=base64.b64decode(img["b64"]),
                        content_type=img["content_type"],
                        original_filename=img["filename"],
                    )
                    final_images.append(filepath)
                except Exception as e:
                    self.product_error = f"Upload error: {str(e)}"
                    self.is_saving = False
                    return
            new_index += 1

        image_paths_str = ",".join(final_images)

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
                        final_images = rename_images_for_reference(
                            folder=self.current_list_folder or "default",
                            old_ref=old_ref,
                            new_ref=new_ref,
                            current_paths=final_images,
                        )
                        image_paths_str = ",".join(final_images)
                    p.store = self.pf_store.strip()
                    p.store_contact = self.pf_store_contact.strip()
                    p.reference = new_ref
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
                    "store": p.store or "",
                    "store_contact": p.store_contact or "",
                    "reference": p.reference or "",
                    "description": p.description or "",
                    "measurement": p.measurement or "",
                    "price": p.price,
                    "qty": p.qty,
                    "cbm": p.cbm,
                    "material": p.material or "",
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
                    "store": p.store or "",
                    "store_contact": p.store_contact or "",
                    "reference": p.reference or "",
                    "description": p.description or "",
                    "measurement": p.measurement or "",
                    "price": p.price,
                    "qty": p.qty,
                    "cbm": p.cbm,
                    "material": p.material or "",
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
