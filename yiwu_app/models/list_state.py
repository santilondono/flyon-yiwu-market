import reflex as rx
from sqlalchemy import select, func, delete
from typing import Optional
from yiwu_app.models.models import ProductList, Product
from yiwu_app.models.auth_state import AuthState
from yiwu_app.utils.image_client import sanitize_folder_name, ensure_folder
from datetime import datetime


class ListState(AuthState):
    lists: list[dict] = []
    is_loading_lists: bool = False
    show_list_modal: bool = False
    editing_list_id: int = 0
    list_form_name: str = ""
    list_form_desc: str = ""
    list_error: str = ""
    is_loading: bool = False

    def load_lists(self):
        self._load_user_from_token()
        if not self.is_authenticated:
            return rx.redirect("/login")
        self.is_loading_lists = True
        yield
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
                    "product_count": session.execute(
                        select(func.count(Product.id)).where(Product.list_id == r.id)
                    ).scalar(),
                    "updated_at": r.updated_at.strftime("%d/%m/%Y %H:%M") if r.updated_at else "",
                }
                for r in rows
            ]
        self.is_loading_lists = False
        self.is_loading_lists = False

    def open_create_modal(self):
        self.editing_list_id = 0
        self.list_form_name = ""
        self.list_form_desc = ""
        self.list_error = ""
        self.show_list_modal = True

    def open_edit_modal(self, list_id: int, name: str, desc: str):
        self.editing_list_id = list_id
        self.list_form_name = name
        self.list_form_desc = desc
        self.list_error = ""
        self.show_list_modal = True

    def close_list_modal(self):
        self.show_list_modal = False

    def set_list_name(self, v: str):
        self.list_form_name = v
        self.list_error = ""

    def set_list_desc(self, v: str):
        self.list_form_desc = v

    def save_list(self):
        if not self.list_form_name.strip():
            self.list_error = "List name is required."
            return
        name = self.list_form_name.strip()
        with rx.session() as session:
            if self.editing_list_id:
                # Check duplicate name (excluding current list)
                dup = session.execute(
                    select(ProductList).where(
                        ProductList.owner_id == self.user_id,
                        ProductList.name == name,
                        ProductList.id != self.editing_list_id,
                    )
                ).scalar_one_or_none()
                if dup:
                    self.list_error = f'A list named "{name}" already exists.'
                    return
                lst = session.get(ProductList, self.editing_list_id)
                if lst and lst.owner_id == self.user_id:
                    lst.name = name
                    lst.description = self.list_form_desc.strip()
                    lst.updated_at = datetime.utcnow()
            else:
                # Check duplicate name
                dup = session.execute(
                    select(ProductList).where(
                        ProductList.owner_id == self.user_id,
                        ProductList.name == name,
                    )
                ).scalar_one_or_none()
                if dup:
                    self.list_error = f'A list named "{name}" already exists.'
                    return
                folder = sanitize_folder_name(name)
                lst = ProductList(
                    name=name,
                    description=self.list_form_desc.strip(),
                    owner_id=self.user_id,
                    folder_name=folder,
                )
                session.add(lst)
                session.commit()
                ensure_folder(folder)
            session.commit()
        self.show_list_modal = False
        self.load_lists()

    def delete_list(self, list_id: int):
        with rx.session() as session:
            session.execute(delete(Product).where(Product.list_id == list_id))
            session.execute(
                delete(ProductList).where(
                    ProductList.id == list_id,
                    ProductList.owner_id == self.user_id,
                )
            )
            session.commit()
        self.load_lists()

    def go_to_list(self, list_id: int):
        return rx.redirect(f"/list/{list_id}")
