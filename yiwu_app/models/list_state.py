import reflex as rx
from sqlalchemy import select, func, delete
from typing import Optional
from yiwu_app.models.models import ProductList, Product, User
from yiwu_app.models.auth_state import AuthState
from yiwu_app.utils.image_client import sanitize_folder_name, ensure_folder
from datetime import datetime


class ListState(AuthState):
    lists: list[dict] = []
    is_loading_lists: bool = True
    show_list_modal: bool = False
    editing_list_id: int = 0
    list_form_name: str = ""
    list_form_desc: str = ""
    list_error: str = ""
    is_loading: bool = False
    active_tab: str = "mis_listas"
    new_list_client: str = ""
    new_list_date: str = ""

    @rx.var
    def new_list_name_preview(self) -> str:
        client = self.new_list_client.strip().upper()
        date = self.new_list_date.strip()
        try:
            d = datetime.strptime(date, "%d/%m/%Y")
            date_fmt = d.strftime("%Y%m%d")
        except Exception:
            return f"{client}_FECHA_INVALIDA" if client else ""
        return f"{client}_{date_fmt}" if client else ""

    def _do_load_lists(self):
        with rx.session() as session:
            rows = session.execute(
                select(ProductList)
                .where(ProductList.owner_id == self.user_id)
                .order_by(ProductList.updated_at.desc())
            ).scalars().all()
            self.lists = [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description or "",
                    "folder_name": r.folder_name or "",
                    "owner_name": "",
                    "product_count": session.execute(
                        select(func.count(Product.id)).where(Product.list_id == r.id)
                    ).scalar(),
                    "updated_at": r.updated_at.strftime("%d/%m/%Y %H:%M") if r.updated_at else "",
                }
                for r in rows
            ]
        self.is_loading_lists = False

    def _do_load_all_lists(self):
        with rx.session() as session:
            stmt = (
                select(ProductList, User)
                .join(User, ProductList.owner_id == User.id)
                .order_by(ProductList.updated_at.desc())
            )
            # El admin ve todas las listas (incluidas las suyas). El resto de
            # usuarios no ven las listas cuyo owner sea admin, ni las propias.
            if not self.is_admin:
                stmt = stmt.where(
                    ProductList.owner_id != self.user_id,
                    User.is_admin == False,  # noqa: E712
                )
            rows = session.execute(stmt).all()
            self.lists = [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description or "",
                    "folder_name": r.folder_name or "",
                    "owner_name": u.name,
                    "product_count": session.execute(
                        select(func.count(Product.id)).where(Product.list_id == r.id)
                    ).scalar(),
                    "updated_at": r.updated_at.strftime("%d/%m/%Y %H:%M") if r.updated_at else "",
                }
                for r, u in rows
            ]
        self.is_loading_lists = False

    def load_lists(self):
        self._load_user_from_token()
        if not self.is_authenticated:
            return rx.redirect("/login")
        self.is_loading_lists = True
        yield
        if self.active_tab == "todas":
            self._do_load_all_lists()
        else:
            self._do_load_lists()

    def set_tab(self, tab: str):
        self.active_tab = tab
        self.is_loading_lists = True
        yield
        if tab == "todas":
            self._do_load_all_lists()
        else:
            self._do_load_lists()

    def open_create_modal(self):
        self.editing_list_id = 0
        self.list_form_name = ""
        self.list_form_desc = ""
        self.list_error = ""
        self.new_list_client = ""
        self.new_list_date = datetime.now().strftime("%d/%m/%Y")
        self.show_list_modal = True

    def open_edit_modal(self, list_id: int, name: str, desc: str):
        self.editing_list_id = list_id
        self.list_form_name = name
        self.list_form_desc = desc
        self.list_error = ""
        self.show_list_modal = True

    def close_list_modal(self):
        self.show_list_modal = False
        self.new_list_client = ""
        self.new_list_date = datetime.now().strftime("%d/%m/%Y")

    def set_list_name(self, v: str):
        self.list_form_name = v
        self.list_error = ""

    def set_list_desc(self, v: str):
        self.list_form_desc = v

    def set_new_list_client(self, v: str):
        self.new_list_client = v
        self.list_error = ""

    def set_new_list_date(self, v: str):
        self.new_list_date = v
        self.list_error = ""

    def uppercase_client(self):
        self.new_list_client = self.new_list_client.strip().upper()

    def save_list(self):
        if self.editing_list_id:
            if not self.list_form_name.strip():
                self.list_error = "El nombre de la lista es obligatorio."
                return
            name = self.list_form_name.strip()
        else:
            if not self.new_list_client.strip():
                self.list_error = "El cliente es obligatorio."
                return
            if "FECHA_INVALIDA" in self.new_list_name_preview:
                self.list_error = "La fecha no es válida. Usa el formato DD/MM/YYYY."
                return
            name = self.new_list_name_preview

        new_folder: Optional[str] = None
        with rx.session() as session:
            if self.editing_list_id:
                dup = session.execute(
                    select(ProductList).where(
                        ProductList.owner_id == self.user_id,
                        ProductList.name == name,
                        ProductList.id != self.editing_list_id,
                    )
                ).scalar_one_or_none()
                if dup:
                    self.list_error = f'Ya existe una lista con el nombre "{name}".'
                    return
                lst = session.get(ProductList, self.editing_list_id)
                if lst and lst.owner_id == self.user_id:
                    lst.name = name
                    lst.description = self.list_form_desc.strip()
                    lst.updated_at = datetime.utcnow()
            else:
                dup = session.execute(
                    select(ProductList).where(
                        ProductList.owner_id == self.user_id,
                        ProductList.name == name,
                    )
                ).scalar_one_or_none()
                if dup:
                    self.list_error = f'Ya existe una lista con el nombre "{name}".'
                    return
                new_folder = sanitize_folder_name(name)
                lst = ProductList(
                    name=name,
                    description=self.list_form_desc.strip(),
                    owner_id=self.user_id,
                    folder_name=new_folder,
                )
                session.add(lst)
            session.commit()
        self.show_list_modal = False
        self.new_list_client = ""
        self.new_list_date = datetime.now().strftime("%d/%m/%Y")
        self.is_loading_lists = True
        yield
        if new_folder:
            ensure_folder(new_folder)
        self._do_load_lists()

    def delete_list(self, list_id: int):
        if not self.is_admin:
            return
        with rx.session() as session:
            session.execute(delete(Product).where(Product.list_id == list_id))
            session.execute(delete(ProductList).where(ProductList.id == list_id))
            session.commit()
        self.is_loading_lists = True
        yield
        self._do_load_lists()

    def go_to_list(self, list_id: int):
        return rx.redirect(f"/list/{list_id}")
