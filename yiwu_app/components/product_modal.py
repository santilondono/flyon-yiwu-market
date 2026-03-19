import reflex as rx
from yiwu_app.models.product_state import ProductState
from yiwu_app.styles.theme import *
import os

IMAGE_SERVER_URL = os.getenv("IMAGE_SERVER_URL", "https://images.flyon-yiwu-market.com")
IMAGE_SERVER_API_KEY = os.getenv("IMAGE_SERVER_API_KEY", "")


def field(label: str, component) -> rx.Component:
    return rx.vstack(rx.text(label, **label_style), component, align="start", width="100%", gap="4px")


def txt_input(placeholder: str, value, on_change) -> rx.Component:
    return rx.input(
        placeholder=placeholder, value=value, on_change=on_change,
        background=BG2, border=f"1px solid {BORDER}", border_radius="10px",
        color=TEXT, font_family=FONT, font_size="15px",
        padding="12px 14px", height="46px", width="100%",
        _focus=dict(border_color=ACCENT, box_shadow=f"0 0 0 3px {ACCENT_D}", outline="none"),
        _placeholder=dict(color=TEXT3),
    )


def num_input(placeholder: str, value, on_change, step="0.01") -> rx.Component:
    return rx.input(
        placeholder=placeholder, value=value, on_change=on_change,
        type="number", step=step,
        background=BG2, border=f"1px solid {BORDER}", border_radius="10px",
        color=TEXT, font_family=FONT, font_size="15px",
        padding="12px 14px", height="46px", width="100%",
        _focus=dict(border_color=ACCENT, box_shadow=f"0 0 0 3px {ACCENT_D}", outline="none"),
        _placeholder=dict(color=TEXT3),
    )


def image_url_thumbnail(url: str, index: int) -> rx.Component:
    """Thumbnail that takes a plain string URL — no dict field access."""
    return rx.box(
        rx.image(
            src=url,
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
        ),
        position="relative", display="inline-flex", flex_shrink="0",
    )


def upload_script() -> rx.Component:
    """Global upload script — injected at page level, always available."""
    SERVER = IMAGE_SERVER_URL
    API_KEY = IMAGE_SERVER_API_KEY
    return rx.script(f"""
window.__uploadInit = function() {{
    const input = document.getElementById('direct-file-input');
    if (!input || input._bound) return;
    input._bound = true;
    input.addEventListener('change', async function() {{
        const files = Array.from(this.files);
        if (!files.length) return;
        const spinner = document.getElementById('upload-spinner');
        if (spinner) spinner.style.display = 'flex';
        const folderEl = document.getElementById('_folder_data');
        const folder = folderEl ? (folderEl.getAttribute('data-folder') || 'default') : 'default';
        console.log('Uploading to folder:', folder, 'files:', files.length);
        for (const file of files) {{
            try {{
                const blob = await new Promise(resolve => {{
                    const reader = new FileReader();
                    reader.onload = e => {{
                        const img = new Image();
                        img.onload = () => {{
                            const MAX = 900;
                            let w = img.width, h = img.height;
                            if (w > MAX || h > MAX) {{
                                if (w > h) {{ h = Math.round(h*MAX/w); w=MAX; }}
                                else {{ w = Math.round(w*MAX/h); h=MAX; }}
                            }}
                            const c = document.createElement('canvas');
                            c.width=w; c.height=h;
                            c.getContext('2d').drawImage(img,0,0,w,h);
                            c.toBlob(resolve, 'image/jpeg', 0.75);
                        }};
                        img.src = e.target.result;
                    }};
                    reader.readAsDataURL(file);
                }});
                const tmpName = 'tmp_' + Math.random().toString(36).substr(2,10) + '.jpg';
                const fd = new FormData();
                fd.append('file', new File([blob], tmpName, {{type:'image/jpeg'}}));
                fd.append('folder', folder);
                console.log('Fetching:', '{SERVER}/upload', 'folder:', folder);
                const r = await fetch('{SERVER}/upload', {{
                    method: 'POST',
                    headers: {{'x-api-key': '{API_KEY}'}},
                    body: fd
                }});
                console.log('Upload response:', r.status);
                if (r.ok) {{
                    const data = await r.json();
                    console.log('Upload data:', data);
                    const fp = data.filepath || (folder + '/' + tmpName);
                    const pu = '{SERVER}/images/' + fp;
                    // Send fp|||pu via controlled input on_change
                    const bridge = document.getElementById('_img_bridge');
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(bridge, fp + '|||' + pu);
                    bridge.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    console.log('Notified Reflex:', fp, pu);
                }}
            }} catch(e) {{ console.error('Upload error:', e); }}
        }}
        if (spinner) spinner.style.display = 'none';
        this.value = '';
    }});
}};
""")


def direct_upload_section() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Photos", **label_style),
            rx.cond(
                ProductState.pf_image_urls.length() > 0,
                rx.box(
                    rx.text(ProductState.pf_image_urls.length().to_string() + " uploaded",
                            font_size="12px", color=ACCENT, font_family=FONT),
                    **badge_accent,
                ),
            ),
            align="center", gap="8px", width="100%",
        ),

        rx.cond(
            ProductState.pf_image_urls.length() > 0,
            rx.flex(
                rx.foreach(ProductState.pf_image_urls, image_url_thumbnail),
                wrap="wrap", gap="10px", width="100%",
            ),
        ),

        # Hidden file input
        rx.el.input(
            id="direct-file-input",
            type="file",
            accept="image/jpeg,image/png,image/webp",
            multiple=True,
            style={"display": "none"},
        ),

        # JS→Reflex bridge: JS sets value and triggers native input event
        rx.el.input(
            id="_img_bridge",
            type="text",
            on_change=ProductState.receive_uploaded_image,
            style={"display": "none", "position": "absolute", "opacity": "0"},
        ),

        # Folder data carrier
        rx.box(
            id="_folder_data",
            custom_attrs={"data-folder": ProductState.current_list_folder},
            display="none",
        ),

        # Upload tap area
        rx.box(
            rx.box(
                rx.vstack(
                    rx.icon("camera", size=24, color=TEXT3),
                    rx.text("Tap to add photos", font_size="13px", color=TEXT3, text_align="center"),
                    rx.text("JPG · PNG · WebP", font_size="11px", color=TEXT3),
                    align="center", gap="4px",
                ),
                on_click=rx.call_script(
                    "window.__uploadInit && window.__uploadInit();"
                    "document.getElementById('direct-file-input').click();"
                ),
                border=f"2px dashed {BORDER_L}", border_radius="10px",
                padding="18px 16px", width="100%", cursor="pointer",
                background=BG3, _hover=dict(border_color=ACCENT), transition="border-color 0.15s",
            ),
            rx.box(
                rx.vstack(
                    rx.spinner(size="3", color="blue"),
                    rx.text("Uploading...", font_size="13px", color=TEXT2, font_family=FONT),
                    align="center", gap="8px",
                ),
                id="upload-spinner",
                position="absolute", top="0", left="0",
                width="100%", height="100%",
                background="rgba(232,238,245,0.93)",
                border_radius="10px",
                display="none",
                align_items="center",
                justify_content="center",
                z_index="10",
            ),
            position="relative", width="100%",
        ),

        align="start", width="100%", gap="8px",
    )


def product_modal() -> rx.Component:
    return rx.fragment(
        # Script always in DOM, not inside cond
        upload_script(),
        rx.cond(
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

                    direct_upload_section(),

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
                    padding="24px", padding_bottom="32px",
                    width="min(700px, 96vw)",
                    max_height="85vh", overflow_y="auto",
                    position="relative", z_index="201",
                    box_shadow="0 8px 40px rgba(15,31,46,0.15)",
                ),
                position="fixed", top="0", left="0", width="100vw", height="100vh",
                background="rgba(15,31,46,0.45)",
                display="flex", align_items="flex-start", justify_content="center",
                z_index="200", backdrop_filter="blur(4px)",
                padding="16px",
            ),
        ),
    )
