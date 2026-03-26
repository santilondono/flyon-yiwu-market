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
