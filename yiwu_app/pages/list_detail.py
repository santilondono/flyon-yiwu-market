import reflex as rx
from yiwu_app.models.product_state import ProductState
from yiwu_app.components.navbar import navbar
from yiwu_app.components.product_modal import product_modal
from yiwu_app.styles.theme import *



# ── Confirm Delete ─────────────────────────────────────────────────────────────

def confirm_delete_dialog() -> rx.Component:
    return rx.cond(
        ProductState.confirm_delete_id > 0,
        rx.box(
            rx.box(
                rx.vstack(
                    rx.icon("triangle_alert", size=32, color=WARNING),
                    rx.text("¿Eliminar producto?", font_size="17px", font_weight="600", color=TEXT, font_family=FONT),
                    rx.text("Las fotos también serán eliminadas.", font_size="13px", color=TEXT3, font_family=FONT),
                    rx.hstack(
                        rx.button("Cancelar", on_click=ProductState.cancel_delete, **btn_ghost),
                        rx.button(
                            rx.hstack(rx.icon("trash_2", size=14), rx.text("Eliminar")),
                            on_click=ProductState.confirm_delete, **btn_danger,
                        ),
                        gap="10px",
                    ),
                    align="center", gap="12px",
                ),
                background=BG2, border=f"1px solid {BORDER}", border_radius="14px",
                padding="28px", width="min(340px, 90vw)",
                position="relative", z_index="301", text_align="center",
                box_shadow="0 8px 32px rgba(15,31,46,0.15)",
            ),
            position="fixed", top="0", left="0", width="100vw", height="100vh",
            background="rgba(15,31,46,0.45)",
            display="flex", align_items="center", justify_content="center", z_index="300",
        ),
    )


# ── Product Row ────────────────────────────────────────────────────────────────

def product_row(p: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                # Image
                rx.cond(
                    p["first_image_url"] != "",
                    rx.hstack(
                        rx.image(
                            src=p["first_image_url"],
                            width="52px", height="52px",
                            object_fit="cover", border_radius="8px",
                            border=f"1px solid {BORDER}", flex_shrink="0",
                        ),
                        rx.cond(
                            p["image_count"].to(int) > 1,
                            rx.box(
                                rx.text("+" + (p["image_count"].to(int) - 1).to_string(),
                                        font_size="11px", font_weight="600", color=ACCENT),
                                background=ACCENT_D, border_radius="6px", padding="3px 7px", flex_shrink="0",
                            ),
                        ),
                        align="center", gap="4px",
                    ),
                    rx.box(
                        rx.icon("image", size=20, color=TEXT3),
                        width="52px", height="52px", background=BG3, border_radius="8px",
                        display="flex", align_items="center", justify_content="center", flex_shrink="0",
                    ),
                ),
                # Name + store
                rx.vstack(
                    rx.cond(
                        p["reference"] != "",
                        rx.text(p["reference"], font_size="15px", font_weight="600", color=TEXT, font_family=FONT),
                        rx.text(p["description"], font_size="15px", font_weight="600", color=TEXT, font_family=FONT, no_of_lines=1),
                    ),
                    rx.hstack(
                        rx.cond(
                            p["store"] != "",
                            rx.hstack(rx.icon("store", size=11, color=TEXT3),
                                      rx.text(p["store"], font_size="12px", color=TEXT3, font_family=FONT),
                                      align="center", gap="3px"),
                        ),
                        rx.cond(
                            p["store_contact"] != "",
                            rx.hstack(rx.icon("phone", size=11, color=TEXT3),
                                      rx.text(p["store_contact"], font_size="12px", color=TEXT3, font_family=FONT),
                                      align="center", gap="3px"),
                        ),
                        gap="10px", flex_wrap="wrap",
                    ),
                    align="start", gap="3px", flex="1",
                ),
                # Actions
                rx.hstack(
                    rx.button(rx.icon("copy", size=14),
                              on_click=ProductState.duplicate_product(p["id"]),
                              background="transparent", color=TEXT3, border=f"1px solid {BORDER}",
                              border_radius="8px", padding="6px 10px", cursor="pointer",
                              _hover=dict(color=SUCCESS, border_color=SUCCESS), transition="all 0.15s"),
                    rx.button(rx.icon("pencil", size=14),
                              on_click=ProductState.open_edit_product(p["id"]),
                              background="transparent", color=TEXT3, border=f"1px solid {BORDER}",
                              border_radius="8px", padding="6px 10px", cursor="pointer",
                              _hover=dict(color=ACCENT, border_color=ACCENT), transition="all 0.15s"),
                    rx.button(rx.icon("trash_2", size=14),
                              on_click=ProductState.request_delete(p["id"]),
                              background="transparent", color=TEXT3, border=f"1px solid {BORDER}",
                              border_radius="8px", padding="6px 10px", cursor="pointer",
                              _hover=dict(color=DANGER, border_color=DANGER), transition="all 0.15s"),
                    gap="6px", align="center", flex_shrink="0",
                ),
                width="100%", align="center", gap="10px",
            ),
            rx.cond(
                (p["description"] != "") & (p["reference"] != ""),
                rx.text(p["description"], font_size="13px", color=TEXT2, font_family=FONT, no_of_lines=2),
            ),
            rx.flex(
                rx.cond(p["price"] != "",
                    rx.box(rx.text("¥ ", p["price"], font_size="14px", font_weight="700", color=SUCCESS, font_family=FONT),
                           background=SUCCESS_D, border_radius="6px", padding="3px 10px")),
                rx.cond(p["qty"] != "",
                    rx.hstack(rx.icon("package", size=12, color=TEXT3),
                              rx.text(p["qty"], " pcs", font_size="12px", color=TEXT2, font_family=FONT),
                              align="center", gap="3px", background=BG3, border_radius="6px", padding="3px 8px")),
                rx.cond(p["cbm"] != "",
                    rx.hstack(rx.icon("box", size=12, color=TEXT3),
                              rx.text(p["cbm"], " m³", font_size="12px", color=TEXT2, font_family=FONT),
                              align="center", gap="3px", background=BG3, border_radius="6px", padding="3px 8px")),
                rx.cond(p["measurement"] != "",
                    rx.hstack(rx.icon("ruler", size=12, color=TEXT3),
                              rx.text(p["measurement"], font_size="12px", color=TEXT2, font_family=FONT),
                              align="center", gap="3px", background=BG3, border_radius="6px", padding="3px 8px")),
                rx.cond(p["material"] != "",
                    rx.hstack(rx.icon("layers", size=12, color=TEXT3),
                              rx.text(p["material"], font_size="12px", color=TEXT2, font_family=FONT),
                              align="center", gap="3px", background=BG3, border_radius="6px", padding="3px 8px")),
                wrap="wrap", gap="6px", width="100%",
            ),
            rx.cond(p["notes"] != "",
                rx.text(p["notes"], font_size="12px", color=TEXT3, font_family=FONT, font_style="italic")),
            gap="8px", width="100%", align="start",
        ),
        background=BG2, border=f"1px solid {BORDER}", border_radius="12px",
        padding="14px 16px", width="100%",
        _hover=dict(border_color=BORDER_L, box_shadow="0 2px 12px rgba(15,31,46,0.08)"),
        transition="all 0.15s",
    )


# ── Pagination ─────────────────────────────────────────────────────────────────

def _nav_btn(icon: str, on_click, disabled) -> rx.Component:
    return rx.button(
        rx.icon(icon, size=15),
        on_click=on_click,
        disabled=disabled,
        width="34px", height="34px", padding="0",
        border_radius="8px", border=f"1px solid {BORDER}",
        background="transparent", color=TEXT2,
        display="flex", align_items="center", justify_content="center",
        cursor="pointer",
        _hover=dict(border_color=ACCENT, color=ACCENT),
        _disabled=dict(opacity="0.35", cursor="not-allowed"),
        transition="all 0.15s",
    )


def _page_btn(num: int) -> rx.Component:
    is_cur = ProductState.page == num
    return rx.button(
        (num + 1).to_string(),
        on_click=ProductState.go_to_page(num),
        width="34px", height="34px", padding="0",
        font_size="13px", font_family=FONT,
        font_weight=rx.cond(is_cur, "700", "400"),
        border_radius="8px",
        border=rx.cond(is_cur, f"1px solid {ACCENT}", f"1px solid {BORDER}"),
        background=rx.cond(is_cur, ACCENT, "transparent"),
        color=rx.cond(is_cur, "white", TEXT2),
        cursor=rx.cond(is_cur, "default", "pointer"),
        display="flex", align_items="center", justify_content="center",
        _hover=rx.cond(is_cur, {}, dict(border_color=ACCENT, color=ACCENT)),
        transition="all 0.15s",
    )


def pagination_controls() -> rx.Component:
    return rx.cond(
        ProductState.total_pages > 1,
        rx.vstack(
            rx.hstack(
                _nav_btn("chevrons_left", ProductState.go_to_page(0),
                         ProductState.page == 0),
                _nav_btn("chevron_left", ProductState.prev_page,
                         ProductState.page == 0),
                rx.foreach(ProductState.visible_pages, _page_btn),
                _nav_btn("chevron_right", ProductState.next_page,
                         ProductState.page >= ProductState.total_pages - 1),
                _nav_btn("chevrons_right",
                         ProductState.go_to_page(ProductState.total_pages - 1),
                         ProductState.page >= ProductState.total_pages - 1),
                gap="4px", align="center", justify="center", width="100%",
            ),
            rx.text(
                ProductState.page_start.to_string(), " – ",
                ProductState.page_end.to_string(), " de ",
                ProductState.products.length().to_string(), " productos",
                font_size="12px", color=TEXT3, font_family=FONT,
            ),
            gap="8px", align="center", width="100%", padding_top="12px",
        ),
    )


# ── Main Page ──────────────────────────────────────────────────────────────────

def export_overlay() -> rx.Component:
    is_done = ProductState.export_progress >= 100
    return rx.cond(
        ProductState.is_exporting,
        rx.box(
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.icon("file_spreadsheet", size=32, color=SUCCESS),
                        background=SUCCESS_D, border_radius="50%",
                        padding="16px", display="flex",
                        align_items="center", justify_content="center",
                    ),
                    rx.cond(
                        is_done,
                        rx.text("Excel listo", font_size="17px", font_weight="700",
                                color=SUCCESS, font_family=FONT),
                        rx.text("Generando Excel", font_size="17px", font_weight="700",
                                color=TEXT, font_family=FONT),
                    ),
                    rx.text(ProductState.export_current, font_size="13px", color=TEXT3,
                            font_family=FONT, text_align="center",
                            max_width="260px", no_of_lines=2),
                    rx.box(
                        rx.box(
                            width=ProductState.export_progress.to_string() + "%",
                            height="100%",
                            background=SUCCESS,
                            border_radius="4px",
                            transition="width 0.4s ease",
                        ),
                        width="260px", height="8px",
                        background=BG3, border_radius="4px", overflow="hidden",
                    ),
                    rx.text(
                        ProductState.export_progress.to_string() + "%",
                        font_size="13px", font_weight="600",
                        color=TEXT2, font_family=FONT,
                    ),
                    # Download link shown when done
                    rx.cond(
                        is_done,
                        rx.vstack(
                            rx.text(
                                "Si la descarga no inició automáticamente,",
                                font_size="12px", color=TEXT3, font_family=FONT,
                                text_align="center",
                            ),
                            rx.el.a(
                                "haz clic aquí para descargar",
                                href=ProductState.export_download_url,
                                download=ProductState.export_download_filename,
                                font_size="13px", font_weight="600",
                                color=ACCENT, font_family=FONT,
                                text_decoration="underline",
                                cursor="pointer",
                            ),
                            gap="4px", align="center",
                        ),
                    ),
                    # Cancel or Close button
                    rx.cond(
                        is_done,
                        rx.button(
                            "Cerrar",
                            on_click=ProductState.close_export_modal,
                            background=SUCCESS, color="white",
                            border="none", border_radius="8px",
                            padding="8px 28px", font_family=FONT, font_size="13px",
                            font_weight="600", cursor="pointer",
                            _hover=dict(background="#0a6040"),
                            margin_top="4px",
                        ),
                        rx.button(
                            rx.hstack(rx.icon("x", size=14), rx.text("Cancelar")),
                            on_click=ProductState.cancel_export,
                            background="transparent", color=DANGER,
                            border=f"1px solid {DANGER}", border_radius="8px",
                            padding="8px 20px", font_family=FONT, font_size="13px",
                            cursor="pointer",
                            _hover=dict(background=DANGER_D),
                            margin_top="4px",
                        ),
                    ),
                    align="center", gap="14px",
                ),
                background=BG2, border=f"1px solid {BORDER}",
                border_radius="16px", padding="36px 40px",
                width="min(360px, 92vw)",
                display="flex", align_items="center", justify_content="center",
                position="relative", z_index="401",
                box_shadow="0 8px 40px rgba(15,31,46,0.20)",
            ),
            position="fixed", top="0", left="0",
            width="100vw", height="100vh",
            background="rgba(15,31,46,0.55)",
            display="flex", align_items="center", justify_content="center",
            z_index="400", backdrop_filter="blur(4px)",
        ),
    )


def list_detail_page() -> rx.Component:
    return rx.box(
        navbar(),
        product_modal(),
        confirm_delete_dialog(),
        export_overlay(),

        rx.box(
            # Back button
            rx.button(
                rx.hstack(rx.icon("chevron_left", size=15), rx.text("Mis Listas", font_size="14px")),
                on_click=rx.redirect("/lists"),
                background="transparent", color=TEXT2, border="none",
                cursor="pointer", padding="4px 8px", border_radius="8px", font_family=FONT,
                _hover=dict(color=TEXT, background=BG3), transition="all 0.15s",
                margin_bottom="8px",
            ),
            # Title
            rx.vstack(
                rx.text(ProductState.current_list_name, font_size="24px", font_weight="700", color=TEXT, font_family=FONT),
                rx.cond(ProductState.current_list_desc != "",
                    rx.text(ProductState.current_list_desc, font_size="13px", color=TEXT3, font_family=FONT)),
                align="start", gap="4px", width="100%",
            ),
            # Action bar
            rx.hstack(
                rx.hstack(
                    rx.text(ProductState.products.length().to_string(), font_size="14px", font_weight="600", color=ACCENT),
                    rx.text(" productos", font_size="14px", color=TEXT3),
                    align="center",
                ),
                rx.spacer(),

                rx.button(
                    rx.hstack(rx.icon("download", size=14), rx.text("Excel")),
                    on_click=ProductState.export_excel,
                    disabled=ProductState.is_exporting,
                    background=SUCCESS_D, color=SUCCESS,
                    border=f"1px solid {SUCCESS}", border_radius="10px",
                    padding="8px 16px", font_family=FONT, font_size="13px",
                    font_weight="500", cursor="pointer",
                    display="inline-flex", align_items="center", gap="6px",
                    _hover=dict(background="rgba(13,122,78,0.18)"),
                    _disabled=dict(opacity="0.5", cursor="not-allowed"),
                    transition="all 0.15s",
                ),
                rx.button(
                    rx.hstack(rx.icon("plus", size=15), rx.text("Agregar")),
                    on_click=ProductState.open_create_product,
                    **{**btn_primary, "padding": "8px 16px"},
                ),
                width="100%", align="center", gap="8px",
            ),

            # Loading / Products / Empty
            rx.cond(
                ProductState.is_loading_products,
                rx.box(
                    rx.vstack(
                        rx.spinner(size="3", color="blue"),
                        rx.text("Cargando productos...", font_size="14px", color=TEXT3, font_family=FONT),
                        align="center", gap="12px",
                    ),
                    display="flex", align_items="center", justify_content="center",
                    padding="60px 24px", width="100%",
                ),
                rx.cond(
                    ProductState.products.length() > 0,
                    rx.vstack(
                        rx.vstack(rx.foreach(ProductState.paged_products, product_row), gap="10px", width="100%"),
                        pagination_controls(),
                        gap="0px", width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.icon("package_plus", size=44, color=TEXT3),
                            rx.text("Sin productos aún", font_size="16px", font_weight="600", color=TEXT2, font_family=FONT),
                            rx.text('Toca "Agregar" para registrar tu primer producto.',
                                    font_size="13px", color=TEXT3, font_family=FONT, text_align="center"),
                            rx.button(
                                rx.hstack(rx.icon("plus", size=15), rx.text("Agregar primer producto")),
                                on_click=ProductState.open_create_product,
                                **{**btn_primary, "margin_top": "8px"},
                            ),
                            align="center", gap="10px",
                        ),
                        display="flex", align_items="center", justify_content="center",
                        padding="60px 24px",
                        background=BG2, border=f"2px dashed {BORDER}", border_radius="14px", width="100%",
                    ),
                ),
            ),

            # FAB
            rx.button(
                rx.icon("plus", size=22),
                on_click=ProductState.open_create_product,
                position="fixed", bottom="24px", right="20px",
                width="52px", height="52px",
                background=ACCENT, color="white", border="none",
                border_radius="50%", cursor="pointer",
                box_shadow="0 4px 16px rgba(29,111,184,0.4)",
                display="flex", align_items="center", justify_content="center",
                _hover=dict(background=ACCENT_H, transform="scale(1.05)"),
                transition="all 0.15s", z_index="50",
            ),

            max_width="800px", margin="0 auto",
            padding="16px 16px 80px 16px",
            display="flex", flex_direction="column", gap="16px",
        ),
        background=BG, color=TEXT, font_family=FONT, min_height="100vh",
    )
