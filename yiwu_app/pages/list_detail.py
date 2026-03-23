import reflex as rx
from yiwu_app.models.product_state import ProductState
from yiwu_app.components.navbar import navbar
from yiwu_app.components.product_modal import product_modal
from yiwu_app.styles.theme import *


# ── Export View ────────────────────────────────────────────────────────────────

def export_row(p: dict) -> rx.Component:
    is_selected = ProductState.selected_ids_csv.contains("," + p["id"].to(str) + ",")
    return rx.hstack(
        rx.box(
            rx.cond(is_selected, rx.icon("check", size=12, color="white"), rx.text("")),
            width="22px", height="22px", flex_shrink="0",
            border_radius="6px",
            background=rx.cond(is_selected, ACCENT, "transparent"),
            border=rx.cond(is_selected, f"2px solid {ACCENT}", f"2px solid {BORDER}"),
            display="flex", align_items="center", justify_content="center",
            pointer_events="none",
        ),
        rx.vstack(
            rx.text(p["reference"], font_size="14px", font_weight="600", color=TEXT, font_family=FONT),
            rx.cond(
                p["description"] != "",
                rx.text(p["description"], font_size="12px", color=TEXT3, font_family=FONT, no_of_lines=1),
            ),
            align="start", gap="2px", flex="1",
        ),
        rx.cond(
            p["price"] != "",
            rx.text("¥", p["price"], font_size="14px", font_weight="600", color=SUCCESS, font_family=FONT),
        ),
        width="100%", align="center", gap="12px",
        padding="12px 16px",
        background=rx.cond(is_selected, ACCENT_D, BG2),
        border=rx.cond(is_selected, f"1px solid {ACCENT}", f"1px solid {BORDER}"),
        border_radius="10px",
        cursor="pointer",
        on_click=ProductState.toggle_select(p["id"]),
        transition="all 0.15s",
    )


def export_progress_overlay() -> rx.Component:
    return rx.cond(
        ProductState.is_exporting_excel | ProductState.is_exporting_zip,
        rx.box(
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.cond(
                            ProductState.is_exporting_zip,
                            rx.icon("archive", size=32, color="#6433dc"),
                            rx.icon("file_spreadsheet", size=32, color=SUCCESS),
                        ),
                        background=rx.cond(ProductState.is_exporting_zip, "rgba(100,60,220,0.12)", SUCCESS_D),
                        border_radius="50%", padding="16px",
                        display="flex", align_items="center", justify_content="center",
                    ),
                    rx.text(
                        rx.cond(ProductState.is_exporting_zip, "Generando ZIP", "Generando Excel"),
                        font_size="17px", font_weight="600", color=TEXT, font_family=FONT,
                    ),
                    rx.text(
                        ProductState.export_current,
                        font_size="13px", color=TEXT3, font_family=FONT,
                        text_align="center", max_width="260px", no_of_lines=1,
                    ),
                    rx.box(
                        rx.box(
                            width=ProductState.export_progress.to_string() + "%",
                            height="100%",
                            background=rx.cond(ProductState.is_exporting_zip, "#6433dc", SUCCESS),
                            border_radius="4px",
                            transition="width 0.3s ease",
                        ),
                        width="260px", height="8px",
                        background=BG3, border_radius="4px", overflow="hidden",
                    ),
                    rx.text(
                        ProductState.export_progress.to_string() + "%",
                        font_size="13px", font_weight="600", color=TEXT2, font_family=FONT,
                    ),
                    rx.button(
                        rx.hstack(rx.icon("x", size=14), rx.text("Cancelar")),
                        on_click=ProductState.cancel_export,
                        background="transparent", color=DANGER,
                        border=f"1px solid {DANGER}", border_radius="8px",
                        padding="8px 20px", font_family=FONT, font_size="13px",
                        cursor="pointer", _hover=dict(background="rgba(192,57,43,0.08)"),
                        margin_top="4px",
                    ),
                    align="center", gap="12px",
                ),
                background=BG2, border=f"1px solid {BORDER}", border_radius="16px",
                padding="36px 40px",
                width="min(340px, 90vw)",
                display="flex", align_items="center", justify_content="center",
                position="relative", z_index="401",
                box_shadow="0 8px 40px rgba(15,31,46,0.18)",
            ),
            position="fixed", top="0", left="0", width="100vw", height="100vh",
            background="rgba(15,31,46,0.65)",
            display="flex", align_items="center", justify_content="center",
            z_index="400", backdrop_filter="blur(4px)",
        ),
    )


def export_view() -> rx.Component:
    return rx.cond(
        ProductState.show_export_view,
        rx.box(
            export_progress_overlay(),
            # Header
            rx.box(
                rx.hstack(
                    rx.button(
                        rx.icon("arrow_left", size=18),
                        on_click=ProductState.close_export_view,
                        background="transparent", color=TEXT2, border="none",
                        cursor="pointer", padding="8px", border_radius="8px",
                        _hover=dict(background=BG3, color=TEXT), transition="all 0.15s",
                    ),
                    rx.text("Exportar", font_size="20px", font_weight="700", color=TEXT, font_family=FONT),
                    rx.spacer(),
                    # Select all toggle
                    rx.button(
                        rx.cond(
                            ProductState.select_all,
                            rx.hstack(rx.icon("square_check", size=14), rx.text("Deseleccionar todo")),
                            rx.hstack(rx.icon("square", size=14), rx.text("Seleccionar todo")),
                        ),
                        on_click=ProductState.toggle_select_all,
                        background="transparent", color=TEXT2, border=f"1px solid {BORDER}",
                        border_radius="8px", padding="8px 14px", font_size="13px",
                        font_family=FONT, cursor="pointer",
                        _hover=dict(border_color=ACCENT, color=ACCENT), transition="all 0.15s",
                    ),
                    width="100%", align="center", gap="12px",
                    padding="16px",
                    border_bottom=f"1px solid {BORDER}",
                    background=BG2,
                    position="sticky", top="0", z_index="10",
                ),
            ),

            # Selection info bar
            rx.cond(
                ProductState.selected_ids.length() > 0,
                rx.hstack(
                    rx.text(
                        ProductState.selected_ids.length().to_string() + " de " +
                        ProductState.products.length().to_string() + " seleccionados",
                        font_size="13px", color=ACCENT, font_family=FONT, font_weight="500",
                    ),
                    rx.spacer(),
                    rx.button(
                        "Limpiar",
                        on_click=ProductState.clear_selection,
                        background="transparent", color=TEXT3, border="none",
                        font_size="12px", font_family=FONT, cursor="pointer",
                        _hover=dict(color=DANGER),
                    ),
                    width="100%", align="center",
                    padding="8px 16px",
                    background=ACCENT_D,
                ),
            ),

            # Product list
            rx.box(
                rx.vstack(
                    rx.foreach(ProductState.products, export_row),
                    gap="8px", width="100%",
                ),
                padding="16px",
                padding_bottom="120px",
                overflow_y="auto",
                flex="1",
            ),

            # Bottom export buttons
            rx.box(
                rx.vstack(
                    rx.text(
                        rx.cond(
                            ProductState.selected_ids.length() > 0,
                            "Exportando " + ProductState.selected_ids.length().to_string() + " productos",
                            "Exportando todos — " + ProductState.products.length().to_string() + " productos",
                        ),
                        font_size="12px", color=TEXT3, font_family=FONT, text_align="center",
                    ),
                    rx.hstack(
                        rx.button(
                            rx.cond(
                                ProductState.is_exporting_excel,
                                rx.hstack(rx.spinner(size="2"), rx.text("Excel...")),
                                rx.hstack(rx.icon("file_spreadsheet", size=16), rx.text("Exportar Excel")),
                            ),
                            on_click=ProductState.export_excel,
                            disabled=ProductState.is_exporting_excel | ProductState.is_exporting_zip,
                            **{**btn_success, "flex": "1"},
                        ),
                        rx.button(
                            rx.cond(
                                ProductState.is_exporting_zip,
                                rx.hstack(rx.spinner(size="2"), rx.text("ZIP...")),
                                rx.hstack(rx.icon("archive", size=16), rx.text("Exportar ZIP")),
                            ),
                            on_click=ProductState.export_zip,
                            disabled=ProductState.is_exporting_excel | ProductState.is_exporting_zip,
                            background="rgba(100,60,220,0.10)", color="#6433dc",
                            border="1px solid transparent", border_radius="10px",
                            padding="10px 16px", font_family=FONT, font_size="14px",
                            font_weight="500", cursor="pointer", flex="1",
                            display="inline-flex", align_items="center", gap="6px",
                            _hover=dict(background="rgba(100,60,220,0.18)"),
                            transition="all 0.15s",
                        ),
                        gap="10px", width="100%",
                    ),
                    gap="8px", width="100%",
                ),
                position="fixed", bottom="0", left="0", width="100%",
                padding="16px",
                background=BG2, border_top=f"1px solid {BORDER}",
                box_shadow="0 -4px 20px rgba(15,31,46,0.08)",
                z_index="10",
            ),

            position="fixed", top="0", left="0",
            width="100vw", height="100vh",
            background=BG,
            display="flex", flex_direction="column",
            z_index="200", overflow="hidden",
        ),
    )


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

def pagination_controls() -> rx.Component:
    return rx.cond(
        ProductState.total_pages > 1,
        rx.hstack(
            rx.button(
                rx.icon("chevron_left", size=16),
                on_click=ProductState.prev_page,
                disabled=ProductState.page == 0,
                background="transparent", color=TEXT2, border=f"1px solid {BORDER}",
                border_radius="8px", padding="8px 12px", cursor="pointer",
                _hover=dict(border_color=ACCENT, color=ACCENT),
                _disabled=dict(opacity="0.4", cursor="not-allowed"),
                transition="all 0.15s",
            ),
            rx.text(
                "Page ",
                rx.text.span((ProductState.page + 1).to_string(), font_weight="600"),
                " de ",
                rx.text.span(ProductState.total_pages.to_string(), font_weight="600"),
                font_size="14px", color=TEXT2, font_family=FONT,
            ),
            rx.button(
                rx.icon("chevron_right", size=16),
                on_click=ProductState.next_page,
                disabled=ProductState.page >= ProductState.total_pages - 1,
                background="transparent", color=TEXT2, border=f"1px solid {BORDER}",
                border_radius="8px", padding="8px 12px", cursor="pointer",
                _hover=dict(border_color=ACCENT, color=ACCENT),
                _disabled=dict(opacity="0.4", cursor="not-allowed"),
                transition="all 0.15s",
            ),
            justify="center", gap="16px", width="100%", padding_top="8px",
        ),
    )


# ── Main Page ──────────────────────────────────────────────────────────────────

def list_detail_page() -> rx.Component:
    return rx.box(
        navbar(),
        product_modal(),
        confirm_delete_dialog(),
        export_view(),

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
                    rx.hstack(rx.icon("download", size=14), rx.text("Exportar")),
                    disabled=True,
                    background="rgba(100,60,220,0.05)", color="#9b8fd4",
                    border="1px solid transparent", border_radius="10px",
                    padding="8px 16px", font_family=FONT, font_size="13px",
                    font_weight="500", cursor="not-allowed",
                    display="inline-flex", align_items="center", gap="6px",
                    title="Coming soon",
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
