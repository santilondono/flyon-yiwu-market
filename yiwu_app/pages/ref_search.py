import reflex as rx
from yiwu_app.models.ref_search_state import RefSearchState, RefResult, RefStore
from yiwu_app.components.navbar import navbar
from yiwu_app.styles.theme import *


def _search_input(value, on_change, on_clear, placeholder: str, icon: str,
                  large: bool, auto_focus: bool = False) -> rx.Component:
    height = "52px" if large else "40px"
    return rx.box(
        rx.icon(icon, size=18 if large else 15, color=TEXT3,
                position="absolute", left="14px", top="50%",
                transform="translateY(-50%)", pointer_events="none", z_index="1"),
        rx.debounce_input(
            rx.input(
                value=value,
                on_change=on_change,
                placeholder=placeholder,
                auto_focus=auto_focus,
                auto_complete=False,
                **{
                    **input_style,
                    "height": height,
                    "font_size": "17px" if large else "14px",
                    "padding": "0 40px 0 40px" if large else "0 36px 0 36px",
                },
            ),
            debounce_timeout=300,
        ),
        rx.cond(
            value != "",
            rx.button(
                rx.icon("x", size=15),
                on_click=on_clear,
                position="absolute", right="8px", top="50%",
                transform="translateY(-50%)",
                background="transparent", color=TEXT3, border="none",
                border_radius="50%", width="28px", height="28px", padding="0",
                display="flex", align_items="center", justify_content="center",
                cursor="pointer", _hover=dict(color=TEXT, background=BG3),
                title="Limpiar",
            ),
        ),
        position="relative", width="100%",
    )


def _store_row(s: RefStore) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text(s.store_number, font_size="15px", font_weight="700",
                    color=ACCENT, font_family=FONT_MONO),
            rx.cond(
                s.is_latest,
                rx.text("Última", background=SUCCESS_D, color=SUCCESS,
                        border_radius="20px", padding="1px 8px",
                        font_size="11px", font_weight="600", font_family=FONT),
            ),
            rx.spacer(),
            rx.text(s.price, font_size="14px", font_weight="600",
                    color=TEXT, font_family=FONT, white_space="nowrap"),
            align="center", gap="8px", width="100%",
        ),
        rx.cond(
            s.contact != "",
            rx.text(s.contact, font_size="13px", color=TEXT2, font_family=FONT,
                    word_break="break-word"),
        ),
        rx.hstack(
            rx.text(s.times, font_size="12px", color=TEXT3, font_family=FONT),
            rx.spacer(),
            rx.cond(
                s.last_date != "",
                rx.hstack(
                    rx.icon("clock", size=11, color=TEXT3),
                    rx.text(s.last_date, font_size="12px", color=TEXT3, font_family=FONT),
                    align="center", gap="3px",
                ),
            ),
            align="center", width="100%",
        ),
        background=rx.cond(s.matches, ACCENT_D, BG),
        border=rx.cond(s.matches, f"1px solid {ACCENT}", f"1px solid {BORDER}"),
        border_radius="8px", padding="8px 10px", width="100%",
        display="flex", flex_direction="column", gap="3px",
    )


def _result_card(r: RefResult) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.cond(
                r.image_url != "",
                rx.image(
                    src=r.image_url, width="72px", height="72px",
                    object_fit="cover", border_radius="8px",
                    border=f"1px solid {BORDER}", cursor="pointer", flex_shrink="0",
                    loading="lazy",
                    on_click=RefSearchState.open_lightbox(r.image_url),
                    _hover=dict(opacity="0.85"), transition="opacity 0.15s",
                ),
                rx.box(
                    rx.icon("image_off", size=22, color=TEXT3),
                    width="72px", height="72px", border_radius="8px",
                    background=BG3, flex_shrink="0",
                    display="flex", align_items="center", justify_content="center",
                ),
            ),
            rx.vstack(
                rx.text(r.ref, font_size="16px", font_weight="700", color=TEXT,
                        font_family=FONT_MONO, word_break="break-all"),
                rx.text(r.name, font_size="14px", color=TEXT2, font_family=FONT),
                rx.cond(
                    r.composition != "",
                    rx.text(r.composition, font_size="12px", color=TEXT3, font_family=FONT),
                ),
                align="start", gap="2px", min_width="0", flex="1",
            ),
            align="start", gap="12px", width="100%",
        ),
        rx.cond(
            r.stores.length() > 0,
            rx.vstack(
                rx.foreach(r.stores, _store_row),
                gap="6px", width="100%", margin_top="12px",
            ),
        ),
        **{**card_sm, "padding": "12px", "width": "100%"},
    )


def _status_box(icon: str, title: str, subtitle: str = "") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.icon(icon, size=40, color=TEXT3),
            rx.text(title, font_size="15px", font_weight="600", color=TEXT2,
                    font_family=FONT, text_align="center"),
            rx.cond(
                subtitle != "",
                rx.text(subtitle, font_size="13px", color=TEXT3, font_family=FONT,
                        text_align="center"),
            ),
            align="center", gap="8px",
        ),
        display="flex", align_items="center", justify_content="center",
        padding="48px 24px", width="100%",
        background=BG2, border=f"2px dashed {BORDER}", border_radius="14px",
    )


def _results_view() -> rx.Component:
    return rx.cond(
        ~RefSearchState.available,
        _status_box("database", "La base de referencias aún no está disponible"),
        rx.cond(
            ~RefSearchState.has_search,
            _status_box("search", "Escribe para buscar",
                        "Referencia, descripción o número de tienda"),
            rx.cond(
                RefSearchState.is_loading & (RefSearchState.results.length() == 0),
                rx.box(
                    rx.vstack(
                        rx.spinner(size="3", color="blue"),
                        rx.text("Buscando...", font_size="14px", color=TEXT3, font_family=FONT),
                        align="center", gap="12px",
                    ),
                    display="flex", align_items="center", justify_content="center",
                    padding="48px 24px", width="100%",
                ),
                rx.cond(
                    RefSearchState.results.length() > 0,
                    rx.vstack(
                        rx.foreach(RefSearchState.results, _result_card),
                        gap="10px", width="100%",
                        opacity=rx.cond(RefSearchState.is_loading, "0.6", "1"),
                        transition="opacity 0.15s",
                    ),
                    _status_box("package_search", "Sin resultados"),
                ),
            ),
        ),
    )


def _lightbox() -> rx.Component:
    return rx.cond(
        RefSearchState.show_lightbox,
        rx.box(
            rx.box(
                position="absolute", top="0", left="0",
                width="100%", height="100%",
                on_click=RefSearchState.close_lightbox,
            ),
            rx.image(
                src=RefSearchState.lightbox_url,
                max_width="92vw", max_height="88vh",
                object_fit="contain", border_radius="8px",
                box_shadow="0 8px 40px rgba(0,0,0,0.6)",
                position="relative", z_index="1",
            ),
            position="fixed", top="0", left="0",
            width="100vw", height="100vh",
            background="rgba(0,0,0,0.88)",
            display="flex", align_items="center", justify_content="center",
            z_index="500",
        ),
    )


def ref_search_page() -> rx.Component:
    return rx.box(
        navbar(),
        _lightbox(),
        rx.box(
            rx.vstack(
                _search_input(
                    RefSearchState.query, RefSearchState.set_query,
                    RefSearchState.clear_query,
                    "Referencia o descripción", "search", large=True, auto_focus=True,
                ),
                rx.box(
                    _search_input(
                        RefSearchState.store_filter, RefSearchState.set_store_filter,
                        RefSearchState.clear_store_filter,
                        "Filtrar por tienda", "store", large=False,
                    ),
                    width="100%", max_width="320px",
                ),
                rx.cond(
                    RefSearchState.exported_at != "",
                    rx.text("Datos actualizados: ", RefSearchState.exported_at,
                            font_size="12px", color=TEXT3, font_family=FONT),
                ),
                gap="8px", width="100%",
            ),
            _results_view(),
            max_width="800px", margin="0 auto",
            padding="16px 16px 40px 16px",
            display="flex", flex_direction="column", gap="16px",
        ),
        background=BG, color=TEXT, font_family=FONT, min_height="100vh",
    )
