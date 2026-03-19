import reflex as rx
from yiwu_app.models.list_state import ListState
from yiwu_app.components.navbar import navbar
from yiwu_app.styles.theme import *


def list_card(lst: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            # Left: name + meta
            rx.vstack(
                rx.text(lst["name"], font_size="16px", font_weight="600", color=TEXT, font_family=FONT, no_of_lines=1),
                rx.cond(
                    lst["description"] != "",
                    rx.text(lst["description"], font_size="12px", color=TEXT3, font_family=FONT, no_of_lines=1),
                ),
                rx.hstack(
                    rx.icon("clock", size=11, color=TEXT3),
                    rx.text(lst["updated_at"], font_size="11px", color=TEXT3, font_family=FONT),
                    align="center", gap="3px",
                ),
                align="start", gap="4px", flex="1",
            ),
            # Center: count badge
            rx.vstack(
                rx.text(lst["product_count"], font_size="22px", font_weight="700", color=ACCENT, font_family=FONT),
                rx.text("items", font_size="11px", color=TEXT3, font_family=FONT),
                align="center",
                background=ACCENT_D, border_radius="10px", padding="8px 14px", min_width="62px",
            ),
            # Right: actions
            rx.vstack(
                rx.button(
                    rx.hstack(rx.icon("folder_open", size=14), rx.text("Open")),
                    on_click=ListState.go_to_list(lst["id"]),
                    **{**btn_primary, "padding": "8px 14px", "font_size": "13px"},
                ),
                rx.hstack(
                    rx.button(
                        rx.icon("pencil", size=13),
                        on_click=ListState.open_edit_modal(lst["id"], lst["name"], lst["description"]),
                        background="transparent", color=TEXT3, border=f"1px solid {BORDER}",
                        border_radius="7px", padding="5px 9px", cursor="pointer",
                        _hover=dict(color=ACCENT, border_color=ACCENT), transition="all 0.15s",
                    ),
                    rx.button(
                        rx.icon("trash_2", size=13),
                        on_click=ListState.delete_list(lst["id"]),
                        background="transparent", color=TEXT3, border=f"1px solid {BORDER}",
                        border_radius="7px", padding="5px 9px", cursor="pointer",
                        _hover=dict(color=DANGER, border_color=DANGER), transition="all 0.15s",
                    ),
                    gap="6px",
                ),
                align="end", gap="6px", flex_shrink="0",
            ),
            width="100%", align="center", gap="12px",
        ),
        background=BG2, border=f"1px solid {BORDER}", border_radius="12px",
        padding="14px 16px", width="100%",
        box_shadow="0 1px 4px rgba(15,31,46,0.05)",
        _hover=dict(border_color=BORDER_L, box_shadow="0 3px 12px rgba(15,31,46,0.09)"),
        transition="all 0.15s",
    )


def list_modal() -> rx.Component:
    return rx.cond(
        ListState.show_list_modal,
        rx.box(
            rx.box(
                rx.hstack(
                    rx.text(
                        rx.cond(ListState.editing_list_id > 0, "Edit list", "New list"),
                        font_size="18px", font_weight="600", color=TEXT, font_family=FONT,
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x", size=18), on_click=ListState.close_list_modal,
                        background="transparent", color=TEXT3, border="none",
                        cursor="pointer", padding="4px", border_radius="6px",
                        _hover=dict(color=TEXT, background=BG3),
                    ),
                    width="100%", align="center", margin_bottom="20px",
                ),
                rx.vstack(
                    rx.vstack(
                        rx.text("List name *", **label_style),
                        rx.input(
                            placeholder="e.g. Yiwu Trip Feb 2025",
                            value=ListState.list_form_name, on_change=ListState.set_list_name,
                            **input_style,
                        ),
                        align="start", width="100%", gap="4px",
                    ),
                    rx.vstack(
                        rx.text("Description (optional)", **label_style),
                        rx.text_area(
                            placeholder="e.g. Summer season products...",
                            value=ListState.list_form_desc, on_change=ListState.set_list_desc,
                            rows="3", **{**input_style, "resize": "none"},
                        ),
                        align="start", width="100%", gap="4px",
                    ),
                    rx.cond(
                        ListState.list_error != "",
                        rx.text(ListState.list_error, color=DANGER, font_size="13px"),
                    ),
                    rx.hstack(
                        rx.button("Cancel", on_click=ListState.close_list_modal, **btn_ghost),
                        rx.button(
                            rx.hstack(rx.icon("save", size=15), rx.text(rx.cond(ListState.editing_list_id > 0, "Save", "Create"))),
                            on_click=ListState.save_list, **btn_primary,
                        ),
                        justify="end", gap="10px", width="100%",
                    ),
                    gap="16px", width="100%",
                ),
                **card,
                width="min(460px, 94vw)",
                position="relative", z_index="201",
            ),
            position="fixed", top="0", left="0", width="100vw", height="100vh",
            background="rgba(15,31,46,0.45)",
            display="flex", align_items="center", justify_content="center",
            z_index="200", backdrop_filter="blur(4px)", padding="16px",
        ),
    )


def lists_page() -> rx.Component:
    return rx.box(
        navbar(),
        list_modal(),

        rx.box(
            # ── Header ─────────────────────────────────────
            rx.hstack(
                rx.vstack(
                    rx.text("My Lists", font_size="24px", font_weight="700", color=TEXT, font_family=FONT),
                    rx.text(
                        rx.cond(
                            ListState.lists.length() > 0,
                            ListState.lists.length().to_string() + " lists",
                            "No lists yet",
                        ),
                        font_size="13px", color=TEXT3, font_family=FONT,
                    ),
                    align="start", gap="2px",
                ),
                rx.spacer(),
                rx.button(
                    rx.hstack(rx.icon("plus", size=16), rx.text("New list")),
                    on_click=ListState.open_create_modal,
                    **{**btn_primary, "padding": "9px 16px"},
                ),
                width="100%", align="center",
            ),

            # ── List ───────────────────────────────────────
            rx.cond(
                ListState.is_loading_lists,
                rx.box(
                    rx.vstack(
                        rx.spinner(size="3", color="blue"),
                        rx.text("Loading lists...", font_size="14px", color=TEXT3, font_family=FONT),
                        align="center", gap="12px",
                    ),
                    display="flex", align_items="center", justify_content="center",
                    padding="60px 24px", width="100%",
                ),
                rx.cond(
                    ListState.lists.length() > 0,
                    rx.vstack(
                        rx.foreach(ListState.lists, list_card),
                        gap="10px", width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.icon("package_open", size=44, color=TEXT3),
                            rx.text("No lists yet", font_size="16px", font_weight="600", color=TEXT2, font_family=FONT),
                            rx.text("Create your first list to start cataloging.", font_size="13px", color=TEXT3, font_family=FONT, text_align="center"),
                            rx.button(
                                rx.hstack(rx.icon("plus", size=15), rx.text("Create first list")),
                                on_click=ListState.open_create_modal,
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
                on_click=ListState.open_create_modal,
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
        on_mount=ListState.load_lists,
    )
