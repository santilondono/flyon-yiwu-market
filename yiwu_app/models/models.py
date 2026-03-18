import reflex as rx
from sqlmodel import Field, Column
from typing import Optional
from datetime import datetime
import sqlalchemy as sa


class User(rx.Model, table=True):
    __tablename__ = "users"
    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=datetime.utcnow),
    )


class ProductList(rx.Model, table=True):
    __tablename__ = "product_lists"
    name: str
    description: Optional[str] = Field(default="")
    owner_id: int = Field(foreign_key="users.id")
    folder_name: str = Field(default="")   # sanitized folder on image server
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=datetime.utcnow),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )


class Product(rx.Model, table=True):
    __tablename__ = "products"
    list_id: int = Field(foreign_key="product_lists.id")
    store: Optional[str] = Field(default="")
    store_contact: Optional[str] = Field(default="")   # NEW
    reference: Optional[str] = Field(default="")
    # image_paths: comma-separated list of paths e.g. "ListA/REF1_1.jpg,ListA/REF1_2.jpg"
    image_paths: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="")
    measurement: Optional[str] = Field(default="")
    price: Optional[float] = Field(default=None)
    qty: Optional[int] = Field(default=None)
    cbm: Optional[float] = Field(default=None)
    material: Optional[str] = Field(default="")
    notes: Optional[str] = Field(default="")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=datetime.utcnow),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )
