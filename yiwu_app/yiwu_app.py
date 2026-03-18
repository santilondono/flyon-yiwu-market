import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

from yiwu_app.pages.login import login_page
from yiwu_app.pages.lists import lists_page
from yiwu_app.pages.list_detail import list_detail_page
from yiwu_app.pages.admin import admin_page
from yiwu_app.models.auth_state import AuthState
from yiwu_app.models.list_state import ListState
from yiwu_app.models.product_state import ProductState
from yiwu_app.models.admin_state import AdminState

GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap"

app = rx.App(
    stylesheets=[GOOGLE_FONTS],
    style={
        "font_family": "'DM Sans', sans-serif",
        "background": "#f0f4f8",
        "color": "#0f1f2e",
    },
    head_components=[
        rx.el.title("Flyon Yiwu Market"),
        rx.el.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
    ],
)


@rx.page(route="/", title="Flyon Yiwu Market", on_load=AuthState.index_redirect)
def index() -> rx.Component:
    return rx.box(background="#f0f4f8", min_height="100vh")


@rx.page(route="/login", title="Flyon Yiwu Market | Sign In", on_load=AuthState.login_guard)
def login() -> rx.Component:
    return login_page()


@rx.page(route="/lists", title="Flyon Yiwu Market | My Lists", on_load=ListState.load_lists)
def lists() -> rx.Component:
    return lists_page()


@rx.page(route="/list/[list_id]", title="Flyon Yiwu Market", on_load=ProductState.on_load)
def list_detail() -> rx.Component:
    return list_detail_page()


@rx.page(route="/admin", title="Flyon Yiwu Market | Admin", on_load=AdminState.on_load)
def admin() -> rx.Component:
    return admin_page()
