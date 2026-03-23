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
    upload_export, IMAGE_SERVER_URL
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
    # Measurement: 3 dimensions with units
    pf_m1: str = ""
    pf_u1: str = "cm"
    pf_m2: str = ""
    pf_u2: str = "cm"
    pf_m3: str = ""
    pf_u3: str = "cm"
    pf_price: str = ""
    pf_qty: str = ""
    pf_cbm: str = ""
    pf_material: str = ""
    pf_material_selected: list[str] = []
    pf_notes: str = ""

    # Each item: {"preview_url": "https://...", "filepath": "folder/tmp_xxx.jpg", "is_temp": True}
    # Parallel lists for images (avoids dict field access issues in Reflex foreach)
    pf_image_urls: list[str] = []      # preview URLs
    pf_image_paths: list[str] = []     # server filepaths
    pf_image_temps: list[bool] = []    # is_temp flags

    product_error: str = ""
    is_saving: bool = False
    is_uploading_image: bool = False
    confirm_delete_id: int = 0
    # Pagination
    page: int = 0
    page_size: int = 50

    # Export mode
    show_export_view: bool = False
    export_cancelled: bool = False

    # Selection for export
    selected_ids: list[str] = []
    select_all: bool = False

    is_exporting_excel: bool = False
    is_exporting_zip: bool = False
    export_progress: int = 0       # 0-100
    export_current: str = ""       # current item label

    def on_load(self):
        self._load_user_from_token()
        if not self.is_authenticated:
            return rx.redirect("/login")
        list_id = self.router.page.params.get("list_id", "")
        try:
            if list_id:
                self._load_list_data(int(list_id))
        except (ValueError, TypeError):
            pass

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
        self.page = 0
        self.selected_ids = []
        self.select_all = False
        self._refresh_page()

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
        self.is_saving = False
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
        dims = self._parse_measurement(p["measurement"])
        self.pf_m1, self.pf_u1 = dims[0]
        self.pf_m2, self.pf_u2 = dims[1]
        self.pf_m3, self.pf_u3 = dims[2]
        self.pf_price = p["price"]
        self.pf_qty = p["qty"]
        self.pf_cbm = p["cbm"]
        self.pf_material = p["material"]
        self.pf_material_selected = [m.strip() for m in p["material"].split(",") if m.strip()]
        self.pf_material_selected = [m.strip() for m in p["material"].split(",") if m.strip()]
        self.pf_notes = p["notes"]
        paths = self._parse_image_paths(p["image_paths"])
        urls = p["image_urls"]
        self.pf_image_urls = list(urls)
        self.pf_image_paths = list(paths)
        self.pf_image_temps = [False] * len(paths)
        self.product_error = ""
        self.is_saving = False
        self.show_product_modal = True

    def close_product_modal(self):
        """Close modal and delete any temp images that weren't saved."""
        self._cleanup_temp_images()
        self.show_product_modal = False

    def _cleanup_temp_images(self):
        """Delete temp images from server if product was not saved."""
        for fp, is_temp in zip(self.pf_image_paths, self.pf_image_temps):
            if is_temp and fp:
                delete_image(fp)

    def _reset_form(self):
        self.pf_store = ""
        self.pf_store_contact = ""
        self.pf_reference = ""
        self.pf_description = ""
        self.pf_price = ""
        self.pf_qty = ""
        self.pf_cbm = ""
        self.pf_material = ""
        self.pf_material_selected = []
        self.pf_notes = ""
        self.pf_m1 = ""; self.pf_u1 = "cm"
        self.pf_m2 = ""; self.pf_u2 = "cm"
        self.pf_m3 = ""; self.pf_u3 = "cm"
        self.pf_image_urls = []
        self.pf_image_paths = []
        self.pf_image_temps = []
        self.product_error = ""

    def set_pf_store(self, v): self.pf_store = v.upper() if v else v
    def set_pf_store_contact(self, v): self.pf_store_contact = v.upper() if v else v
    def set_pf_reference(self, v): self.pf_reference = v.upper() if v else v; self.product_error = ""
    def set_pf_description(self, v): self.pf_description = v.upper() if v else v
    def set_pf_price(self, v): self.pf_price = v
    def set_pf_qty(self, v): self.pf_qty = v
    def set_pf_cbm(self, v): self.pf_cbm = v
    def set_pf_material(self, v): self.pf_material = v.upper() if v else v
    def toggle_material(self, mat: str):
        if mat in self.pf_material_selected:
            self.pf_material_selected = [m for m in self.pf_material_selected if m != mat]
        else:
            self.pf_material_selected = [*self.pf_material_selected, mat]
        # Sync to pf_material string
        self.pf_material = ", ".join(self.pf_material_selected)
    def set_pf_notes(self, v): self.pf_notes = v.upper() if v else v
    def set_pf_m1(self, v): self.pf_m1 = v
    def set_pf_u1(self, v): self.pf_u1 = v
    def set_pf_m2(self, v): self.pf_m2 = v
    def set_pf_u2(self, v): self.pf_u2 = v
    def set_pf_m3(self, v): self.pf_m3 = v
    def set_pf_u3(self, v): self.pf_u3 = v

    def _measurement_to_str(self) -> str:
        """Build measurement string: e.g. '3m*15mm' or '10cm*5cm' """
        parts = []
        for val, unit in [(self.pf_m1, self.pf_u1), (self.pf_m2, self.pf_u2), (self.pf_m3, self.pf_u3)]:
            if val and str(val).strip():
                parts.append(f"{val.strip()}{unit}")
        return "*".join(parts)

    def _parse_measurement(self, m: str):
        """Parse '3m*15mm*2cm' back into 3 value+unit pairs."""
        units = ["mm", "cm", "inch", "ft", "m"]
        parts = m.split("*") if m else []
        result = []
        for part in parts[:3]:
            part = part.strip()
            matched_unit = "cm"
            matched_val = part
            for u in sorted(units, key=len, reverse=True):
                if part.lower().endswith(u):
                    matched_unit = u
                    matched_val = part[:-len(u)]
                    break
            result.append((matched_val, matched_unit))
        while len(result) < 3:
            result.append(("", "cm"))
        return result

    def duplicate_product(self, product_id: int):
        """Open create modal pre-filled with product data (minus reference)."""
        p = next((x for x in self.products if x["id"] == product_id), None)
        if not p:
            return
        self._reset_form()
        self.editing_product_id = 0
        self.pf_store = p["store"]
        self.pf_store_contact = p["store_contact"]
        self.pf_reference = ""  # intentionally empty
        self.pf_description = p["description"]
        self.pf_price = p["price"]
        self.pf_qty = p["qty"]
        self.pf_cbm = p["cbm"]
        self.pf_material = p["material"]
        self.pf_material_selected = [m.strip() for m in p["material"].split(",") if m.strip()]
        self.pf_notes = p["notes"]
        # Parse measurement
        dims = self._parse_measurement(p["measurement"])
        self.pf_m1, self.pf_u1 = dims[0]
        self.pf_m2, self.pf_u2 = dims[1]
        self.pf_m3, self.pf_u3 = dims[2]
        self.is_saving = False
        self.show_product_modal = True

    # ── Pagination ────────────────────────────────────────
    def next_page(self):
        if (self.page + 1) * self.page_size < len(self.products):
            self.page += 1
            self._refresh_page()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._refresh_page()

    def go_to_page(self, p: int):
        self.page = p
        self._refresh_page()

    # paged_products is a plain state var updated by _refresh_page()
    paged_products: list[dict] = []
    total_pages: int = 1
    page_start: int = 1
    page_end: int = 0

    @rx.var
    def selected_ids_csv(self) -> str:
        """Comma-separated selected IDs for reliable JS comparison."""
        return "," + ",".join(str(s) for s in self.selected_ids) + ","

    def _refresh_page(self):
        """Recompute paged_products from current page."""
        start = self.page * self.page_size
        end = start + self.page_size
        self.paged_products = self.products[start:end]
        total = len(self.products)
        self.total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        self.page_start = start + 1
        self.page_end = min(end, total)

    # ── Selection ─────────────────────────────────────────
    def toggle_select(self, product_id: int):
        sid = str(int(product_id))
        if sid in self.selected_ids:
            self.selected_ids = [i for i in self.selected_ids if i != sid]
        else:
            self.selected_ids = [*self.selected_ids, sid]
        self.select_all = len(self.selected_ids) == len(self.products)

    def toggle_select_all(self):
        if self.select_all:
            self.selected_ids = []
            self.select_all = False
        else:
            self.selected_ids = [str(p["id"]) for p in self.products]
            self.select_all = True

    def clear_selection(self):
        self.selected_ids = []
        self.select_all = False

    def open_export_view(self):
        self.selected_ids = []
        self.select_all = False
        self.show_export_view = True

    def close_export_view(self):
        self.show_export_view = False
        self.selected_ids = []
        self.select_all = False

    def cancel_export(self):
        self.export_cancelled = True

    def remove_image(self, index: int):
        """Remove image from list — delete from server if temp."""
        if 0 <= index < len(self.pf_image_paths):
            if index < len(self.pf_image_temps) and self.pf_image_temps[index]:
                delete_image(self.pf_image_paths[index])
            self.pf_image_urls = [v for i, v in enumerate(self.pf_image_urls) if i != index]
            self.pf_image_paths = [v for i, v in enumerate(self.pf_image_paths) if i != index]
            self.pf_image_temps = [v for i, v in enumerate(self.pf_image_temps) if i != index]


    def receive_uploaded_image(self, value: str):
        """Receives filepath|||preview_url from JS via input on_change."""
        if not value or "|||" not in value:
            return
        parts = value.split("|||", 1)
        if len(parts) != 2:
            return
        filepath, preview_url = parts
        if not filepath or not preview_url:
            return
        self.pf_image_urls = [*self.pf_image_urls, preview_url]
        self.pf_image_paths = [*self.pf_image_paths, filepath]
        self.pf_image_temps = [*self.pf_image_temps, True]

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
                compressed, content_type = compress_image(data, (1000, 1000), 65)
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
        yield rx.call_script("document.getElementById('upload-spinner').style.display='none';")

    def save_product(self):
        if not self.pf_reference.strip() and not self.pf_description.strip():
            self.product_error = "Reference or description is required."
            return
        self.is_saving = True
        self.product_error = ""
        yield

        import pathlib
        from yiwu_app.utils.image_client import httpx as _httpx, IMAGE_SERVER_URL, _headers

        ref = self.pf_reference.strip() or self.pf_description.strip()[:20]

        # Validate unique reference within this list
        if self.pf_reference.strip():
            with rx.session() as _s:
                from sqlalchemy import select as _sel
                existing = _s.execute(
                    _sel(Product).where(
                        Product.list_id == self.current_list_id,
                        Product.reference == self.pf_reference.strip(),
                        Product.id != self.editing_product_id,
                    )
                ).scalar_one_or_none()
                if existing:
                    self.product_error = f"Reference {self.pf_reference.strip()} already exists in this list."
                    self.is_saving = False
                    return
        folder = self.current_list_folder or "default"
        safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in ref) or "product"

        # Rename temp images to final names
        final_paths = []
        new_index = 1
        for fp, is_temp in zip(self.pf_image_paths, self.pf_image_temps):
            fp = str(fp)
            is_temp = bool(is_temp)
            if not fp:
                new_index += 1
                continue
            if is_temp:
                ext = pathlib.Path(fp).suffix or ".jpg"
                new_filename = f"{safe_ref}{ext}" if new_index == 1 else f"{safe_ref}_{new_index - 1}{ext}"
                new_filepath = f"{folder}/{new_filename}"
                try:
                    _httpx.post(
                        f"{IMAGE_SERVER_URL}/rename",
                        json={"old_path": fp, "new_path": new_filepath},
                        headers=_headers(),
                        timeout=10,
                    )
                    final_paths.append(new_filepath)
                except Exception:
                    final_paths.append(fp)
            else:
                final_paths.append(fp)
            new_index += 1

        image_paths_str = ",".join(final_paths)

        def to_float(v):
            try: return float(v) if v and str(v).strip() else None
            except: return None

        def to_int(v):
            try: return int(v) if v and str(v).strip() else None
            except: return None

        try:
            with rx.session() as session:
                if self.editing_product_id:
                    p = session.get(Product, self.editing_product_id)
                    if p and p.list_id == self.current_list_id:
                        old_ref = p.reference or ""
                        new_ref = self.pf_reference.strip()
                        if old_ref and new_ref and old_ref != new_ref:
                            existing_paths = [
                                fp for fp, is_temp in zip(self.pf_image_paths, self.pf_image_temps)
                                if not is_temp and fp
                            ]
                            if existing_paths:
                                renamed = rename_images_for_reference(
                                    folder=folder, old_ref=old_ref,
                                    new_ref=new_ref, current_paths=existing_paths,
                                )
                                image_paths_str = ",".join(
                                    renamed + [fp for fp in final_paths if fp not in existing_paths]
                                )
                        p.store = self.pf_store.strip()
                        p.store_contact = self.pf_store_contact.strip()
                        p.reference = self.pf_reference.strip()
                        p.description = self.pf_description.strip()
                        p.measurement = self._measurement_to_str()
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
                        measurement=self._measurement_to_str(),
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
            self.show_product_modal = False
            self.reload_products()
        except Exception as e:
            self.product_error = f"Error saving: {str(e)}"
        finally:
            self.is_saving = False


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
        self.export_cancelled = False
        self.export_progress = 0
        self.export_current = "Loading products..."
        yield
        with rx.session() as session:
            rows = session.execute(
                select(Product).where(Product.list_id == self.current_list_id).order_by(Product.created_at)
            ).scalars().all()
            rows = list(rows)
        # Filter by selection if any
        if self.selected_ids:
            rows = [r for r in rows if str(r.id) in self.selected_ids]
        total = len(rows)
        products = []
        for i, p in enumerate(rows):
            ref = p.reference or p.description or f"Product {i+1}"
            self.export_current = ref[:30]
            self.export_progress = int((i / max(total, 1)) * 90)
            yield
            products.append({
                "store": p.store or "", "store_contact": p.store_contact or "",
                "reference": p.reference or "", "description": p.description or "",
                "measurement": p.measurement or "", "price": p.price,
                "qty": p.qty, "cbm": p.cbm, "material": p.material or "",
                "notes": p.notes or "",
                "image_paths": self._parse_image_paths(p.image_paths or ""),
            })
        if self.export_cancelled:
            self.is_exporting_excel = False; self.export_cancelled = False; return
        self.export_current = "Building Excel file..."
        self.export_progress = 92
        yield
        excel_bytes = export_to_excel(self.current_list_name, self.current_list_desc, products)
        self.export_progress = 95
        self.export_current = "Uploading to server..."
        yield
        filename = f"{self.current_list_name.replace(' ', '_')}.xlsx"
        url = upload_export(filename, excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.is_exporting_excel = False
        self.export_progress = 100
        yield rx.call_script(f"window.open('{url}', '_blank') || (window.location.href='{url}')")

    def export_zip(self):
        self.is_exporting_zip = True
        self.export_cancelled = False
        self.export_progress = 0
        self.export_current = "Loading products..."
        yield
        with rx.session() as session:
            rows = session.execute(
                select(Product).where(Product.list_id == self.current_list_id).order_by(Product.created_at)
            ).scalars().all()
            rows = list(rows)
        # Filter by selection if any
        if self.selected_ids:
            rows = [r for r in rows if str(r.id) in self.selected_ids]
        total = len(rows)
        products = []
        for i, p in enumerate(rows):
            ref = p.reference or p.description or f"Product {i+1}"
            self.export_current = f"Downloading {ref[:25]}..."
            self.export_progress = int((i / max(total, 1)) * 85)
            yield
            products.append({
                "store": p.store or "", "store_contact": p.store_contact or "",
                "reference": p.reference or "", "description": p.description or "",
                "measurement": p.measurement or "", "price": p.price,
                "qty": p.qty, "cbm": p.cbm, "material": p.material or "",
                "notes": p.notes or "",
                "image_paths": self._parse_image_paths(p.image_paths or ""),
            })
        if self.export_cancelled:
            self.is_exporting_zip = False; self.export_cancelled = False; return
        self.export_current = "Building Excel..."
        self.export_progress = 87
        yield
        self.export_current = "Packing ZIP..."
        self.export_progress = 93
        yield
        zip_bytes = export_list_zip(self.current_list_name, self.current_list_desc, products)
        self.export_progress = 95
        self.export_current = "Uploading to server..."
        yield
        filename = f"{self.current_list_name.replace(' ', '_')}_export.zip"
        url = upload_export(filename, zip_bytes, "application/zip")
        self.is_exporting_zip = False
        self.export_progress = 100
        yield rx.call_script(f"window.open('{url}', '_blank') || (window.location.href='{url}')")
