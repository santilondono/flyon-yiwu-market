import reflex as rx
from yiwu_app.models.product_state import ProductState
from yiwu_app.styles.theme import *


def field(label: str, component) -> rx.Component:
    return rx.vstack(rx.text(label, **label_style), component, align="start", width="100%", gap="4px")


def txt_input(placeholder: str, value, on_change) -> rx.Component:
    return rx.input(
        placeholder=placeholder, value=value, on_change=on_change,
        background=BG2, border=f"1px solid {BORDER}", border_radius="10px",
        color=TEXT, font_family=FONT, font_size="15px", padding="10px 14px", width="100%",
        _focus=dict(border_color=ACCENT, box_shadow=f"0 0 0 3px {ACCENT_D}", outline="none"),
        _placeholder=dict(color=TEXT3),
    )


def num_input(placeholder: str, value, on_change, step="0.01") -> rx.Component:
    return rx.input(
        placeholder=placeholder, value=value, on_change=on_change,
        type="number", step=step,
        background=BG2, border=f"1px solid {BORDER}", border_radius="10px",
        color=TEXT, font_family=FONT, font_size="15px", padding="10px 14px", width="100%",
        _focus=dict(border_color=ACCENT, box_shadow=f"0 0 0 3px {ACCENT_D}", outline="none"),
        _placeholder=dict(color=TEXT3),
    )


def image_thumbnail(img: dict, index: int) -> rx.Component:
    return rx.box(
        rx.image(
            src=img["preview"],
            width="80px", height="80px",
            object_fit="cover",
            border_radius="8px",
            border=f"1px solid {BORDER}",
        ),
        rx.button(
            rx.icon("x", size=11),
            on_click=ProductState.remove_image(index),
            position="absolute", top="-6px", right="-6px",
            background=DANGER, color="white", border="none",
            border_radius="50%", width="20px", height="20px",
            cursor="pointer", display="flex",
            align_items="center", justify_content="center",
            padding="0",
            _hover=dict(background="#a32020"),
        ),
        position="relative",
        display="inline-flex",
        flex_shrink="0",
    )


def image_upload_section() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Photos", **label_style),
            rx.cond(
                ProductState.pf_images.length() > 0,
                rx.box(
                    rx.text(ProductState.pf_images.length().to_string() + " selected",
                            font_size="12px", color=ACCENT, font_family=FONT),
                    **badge_accent,
                ),
            ),
            align="center", gap="8px", width="100%",
        ),
        rx.cond(
            ProductState.pf_images.length() > 0,
            rx.flex(
                rx.foreach(ProductState.pf_images, image_thumbnail),
                wrap="wrap", gap="10px", width="100%",
            ),
        ),
        rx.upload(
            rx.vstack(
                rx.icon("camera", size=24, color=TEXT3),
                rx.text("Tap to add photos", font_size="13px", color=TEXT3, text_align="center"),
                rx.text("JPG · PNG · WebP · Multiple allowed", font_size="11px", color=TEXT3),
                align="center", gap="4px",
            ),
            id="product_images",
            accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"], "image/webp": [".webp"]},
            max_files=10,
            multiple=True,
            on_drop=ProductState.handle_image_upload(rx.upload_files(upload_id="product_images")),
            border=f"2px dashed {BORDER_L}", border_radius="10px",
            padding="18px 16px", width="100%", cursor="pointer",
            background=BG3, _hover=dict(border_color=ACCENT), transition="border-color 0.15s",
        ),
        align="start", width="100%", gap="8px",
    )


def product_modal() -> rx.Component:
    return rx.cond(
        ProductState.show_product_modal,
        rx.box(
            rx.box(
                rx.hstack(
                    rx.text(
                        rx.cond(ProductState.editing_product_id > 0, "Edit product", "New product"),
                        font_size="18px", font_weight="600", color=TEXT, font_family=FONT,
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x", size=18), on_click=ProductState.close_product_modal,
                        background="transparent", color=TEXT3, border="none",
                        cursor="pointer", padding="4px", border_radius="6px",
                        _hover=dict(color=TEXT, background=BG3),
                    ),
                    width="100%", align="center", margin_bottom="16px",
                ),

                image_upload_section(),

                rx.grid(
                    field("Store", txt_input("e.g. Fashion World A-12", ProductState.pf_store, ProductState.set_pf_store)),
                    field("Store contact", txt_input("e.g. WeChat: john88", ProductState.pf_store_contact, ProductState.set_pf_store_contact)),
                    columns="2", gap="12px", width="100%",
                ),
                rx.grid(
                    field("Reference *", txt_input("e.g. FW-2025-001", ProductState.pf_reference, ProductState.set_pf_reference)),
                    field("Description", txt_input("Product name / model", ProductState.pf_description, ProductState.set_pf_description)),
                    columns="2", gap="12px", width="100%",
                ),
                field("Measurement", txt_input("e.g. 30×20×15 cm", ProductState.pf_measurement, ProductState.set_pf_measurement)),
                rx.grid(
                    field("Price (¥)", num_input("0.00", ProductState.pf_price, ProductState.set_pf_price)),
                    field("QTY", num_input("0", ProductState.pf_qty, ProductState.set_pf_qty, step="1")),
                    field("CBM (m³)", num_input("0.00", ProductState.pf_cbm, ProductState.set_pf_cbm)),
                    columns="3", gap="12px", width="100%",
                ),
                field("Material", txt_input("e.g. Stainless steel", ProductState.pf_material, ProductState.set_pf_material)),
                field("Notes",
                    rx.text_area(
                        placeholder="MOQ, packaging, lead time...",
                        value=ProductState.pf_notes, on_change=ProductState.set_pf_notes,
                        rows="2",
                        background=BG2, border=f"1px solid {BORDER}", border_radius="10px",
                        color=TEXT, font_family=FONT, font_size="15px", padding="10px 14px", width="100%",
                        _focus=dict(border_color=ACCENT, box_shadow=f"0 0 0 3px {ACCENT_D}", outline="none"),
                        _placeholder=dict(color=TEXT3), resize="none",
                    ),
                ),

                rx.cond(
                    ProductState.product_error != "",
                    rx.text(ProductState.product_error, color=DANGER, font_size="13px"),
                ),
                rx.hstack(
                    rx.button("Cancel", on_click=ProductState.close_product_modal, **btn_ghost),
                    rx.button(
                        rx.cond(
                            ProductState.is_saving,
                            rx.hstack(rx.spinner(size="2"), rx.text("Saving...")),
                            rx.hstack(rx.icon("save", size=15), rx.text(rx.cond(ProductState.editing_product_id > 0, "Update", "Add product"))),
                        ),
                        on_click=ProductState.save_product,
                        disabled=ProductState.is_saving, **btn_primary,
                    ),
                    justify="end", gap="10px", width="100%", margin_top="4px",
                ),

                display="flex", flex_direction="column", gap="14px",
                background=BG2, border=f"1px solid {BORDER}", border_radius="16px",
                padding="24px",
                width="min(700px, 96vw)",
                max_height="92vh", overflow_y="auto",
                position="relative", z_index="201",
                box_shadow="0 8px 40px rgba(15,31,46,0.15)",
            ),
            position="fixed", top="0", left="0", width="100vw", height="100vh",
            background="rgba(15,31,46,0.45)",
            display="flex", align_items="center", justify_content="center",
            z_index="200", backdrop_filter="blur(4px)",
            padding="16px",
        ),
    )
