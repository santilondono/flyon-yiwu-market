import reflex as rx
from yiwu_app.models.admin_state import AdminState
from yiwu_app.components.navbar import navbar
from yiwu_app.styles.theme import *


def create_user_modal() -> rx.Component:
    return rx.cond(
        AdminState.show_create_modal,
        rx.box(
            rx.box(
                rx.hstack(
                    rx.text("New User", font_size="18px", font_weight="600", color=TEXT, font_family=FONT),
                    rx.spacer(),
                    rx.button(rx.icon("x", size=18), on_click=AdminState.close_create_modal,
                        background="transparent", color=TEXT3, border="none", cursor="pointer",
                        padding="4px", border_radius="6px", _hover=dict(color=TEXT, background=BG3)),
                    width="100%", align="center", margin_bottom="20px",
                ),
                rx.vstack(
                    rx.vstack(
                        rx.text("Full name", **label_style),
                        rx.input(placeholder="e.g. Juan García", value=AdminState.new_name,
                                 on_change=AdminState.set_new_name, **input_style),
                        align="start", width="100%", gap="4px",
                    ),
                    rx.vstack(
                        rx.text("Username / Email", **label_style),
                        rx.input(placeholder="e.g. juan.garcia", value=AdminState.new_email,
                                 on_change=AdminState.set_new_email, **input_style),
                        align="start", width="100%", gap="4px",
                    ),
                    rx.vstack(
                        rx.text("Password", **label_style),
                        rx.input(placeholder="Min. 6 characters", value=AdminState.new_password,
                                 on_change=AdminState.set_new_password, type="password", **input_style),
                        align="start", width="100%", gap="4px",
                    ),
                    rx.cond(
                        AdminState.create_error != "",
                        rx.box(
                            rx.hstack(rx.icon("circle_alert", size=13, color=DANGER),
                                rx.text(AdminState.create_error, font_size="13px", color=DANGER, font_family=FONT),
                                align="center", gap="6px"),
                            background=DANGER_D, border_radius="8px", padding="9px 12px", width="100%",
                        ),
                    ),
                    rx.hstack(
                        rx.button("Cancel", on_click=AdminState.close_create_modal, **btn_ghost),
                        rx.button(
                            rx.cond(
                                AdminState.is_saving,
                                rx.hstack(rx.spinner(size="2"), rx.text("Creating...")),
                                rx.hstack(rx.icon("user_plus", size=15), rx.text("Create user")),
                            ),
                            on_click=AdminState.create_user,
                            disabled=AdminState.is_saving, **btn_primary,
                        ),
                        justify="end", gap="10px", width="100%",
                    ),
                    gap="16px", width="100%",
                ),
                **card, width="min(440px, 94vw)", position="relative", z_index="201",
            ),
            position="fixed", top="0", left="0", width="100vw", height="100vh",
            background="rgba(15,31,46,0.45)", display="flex", align_items="center",
            justify_content="center", z_index="200", backdrop_filter="blur(4px)", padding="16px",
        ),
    )


def change_password_modal() -> rx.Component:
    return rx.cond(
        AdminState.show_pw_modal,
        rx.box(
            rx.box(
                rx.hstack(
                    rx.text("Change Password", font_size="18px", font_weight="600", color=TEXT, font_family=FONT),
                    rx.spacer(),
                    rx.button(rx.icon("x", size=18), on_click=AdminState.close_pw_modal,
                        background="transparent", color=TEXT3, border="none", cursor="pointer",
                        padding="4px", border_radius="6px", _hover=dict(color=TEXT, background=BG3)),
                    width="100%", align="center", margin_bottom="20px",
                ),
                rx.vstack(
                    rx.vstack(
                        rx.text("Current password", **label_style),
                        rx.input(placeholder="••••••••", value=AdminState.pw_current,
                                 on_change=AdminState.set_pw_current, type="password", **input_style),
                        align="start", width="100%", gap="4px",
                    ),
                    rx.vstack(
                        rx.text("New password", **label_style),
                        rx.input(placeholder="Min. 6 characters", value=AdminState.pw_new,
                                 on_change=AdminState.set_pw_new, type="password", **input_style),
                        align="start", width="100%", gap="4px",
                    ),
                    rx.vstack(
                        rx.text("Confirm new password", **label_style),
                        rx.input(placeholder="Repeat new password", value=AdminState.pw_confirm,
                                 on_change=AdminState.set_pw_confirm, type="password", **input_style),
                        align="start", width="100%", gap="4px",
                    ),
                    rx.cond(
                        AdminState.pw_error != "",
                        rx.box(
                            rx.hstack(rx.icon("circle_alert", size=13, color=DANGER),
                                rx.text(AdminState.pw_error, font_size="13px", color=DANGER, font_family=FONT),
                                align="center", gap="6px"),
                            background=DANGER_D, border_radius="8px", padding="9px 12px", width="100%",
                        ),
                    ),
                    rx.cond(
                        AdminState.pw_success != "",
                        rx.box(
                            rx.hstack(rx.icon("check_circle", size=13, color=SUCCESS),
                                rx.text(AdminState.pw_success, font_size="13px", color=SUCCESS, font_family=FONT),
                                align="center", gap="6px"),
                            background=SUCCESS_D, border_radius="8px", padding="9px 12px", width="100%",
                        ),
                    ),
                    rx.hstack(
                        rx.button("Cancel", on_click=AdminState.close_pw_modal, **btn_ghost),
                        rx.button(
                            rx.hstack(rx.icon("lock", size=15), rx.text("Update password")),
                            on_click=AdminState.change_password, **btn_primary,
                        ),
                        justify="end", gap="10px", width="100%",
                    ),
                    gap="16px", width="100%",
                ),
                **card, width="min(420px, 94vw)", position="relative", z_index="201",
            ),
            position="fixed", top="0", left="0", width="100vw", height="100vh",
            background="rgba(15,31,46,0.45)", display="flex", align_items="center",
            justify_content="center", z_index="200", backdrop_filter="blur(4px)", padding="16px",
        ),
    )


def user_row(u: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            # Avatar circle
            rx.box(
                rx.text(u["name"].to(str)[0], font_size="16px", font_weight="700", color="white"),
                background=ACCENT, border_radius="50%",
                width="40px", height="40px", min_width="40px",
                display="flex", align_items="center", justify_content="center",
            ),
            # Name + username
            rx.vstack(
                rx.text(u["name"], font_size="15px", font_weight="600", color=TEXT, font_family=FONT),
                rx.text(u["email"], font_size="12px", color=TEXT3, font_family=FONT),
                align="start", gap="2px", flex="1",
            ),
            # Joined date
            rx.text(u["created_at"], font_size="12px", color=TEXT3, font_family=FONT,
                    display=["none", "block", "block"]),
            # Delete
            rx.button(
                rx.icon("trash_2", size=14),
                on_click=AdminState.delete_user(u["id"]),
                background="transparent", color=TEXT3, border=f"1px solid {BORDER}",
                border_radius="8px", padding="6px 10px", cursor="pointer",
                _hover=dict(color=DANGER, border_color=DANGER), transition="all 0.15s",
            ),
            width="100%", align="center", gap="12px",
        ),
        background=BG2, border=f"1px solid {BORDER}", border_radius="12px",
        padding="14px 16px", width="100%",
        _hover=dict(border_color=BORDER_L),
        transition="border-color 0.15s",
    )


def admin_page() -> rx.Component:
    return rx.box(
        navbar(),
        create_user_modal(),
        change_password_modal(),

        rx.box(
            # ── Header ─────────────────────────────────────
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("shield_check", size=18, color="white"),
                            background=ACCENT, border_radius="8px", padding="6px",
                            display="flex", align_items="center", justify_content="center",
                        ),
                        rx.text("Admin Panel", font_size="22px", font_weight="700", color=TEXT, font_family=FONT),
                        align="center", gap="10px",
                    ),
                    rx.text("Flyon Yiwu Market — User Management",
                            font_size="13px", color=TEXT3, font_family=FONT),
                    align="start", gap="4px",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        rx.hstack(rx.icon("lock", size=14), rx.text("Change password")),
                        on_click=AdminState.open_pw_modal,
                        **{**btn_ghost, "font_size": "13px", "padding": "8px 14px"},
                    ),
                    rx.button(
                        rx.hstack(rx.icon("user_plus", size=15), rx.text("New user")),
                        on_click=AdminState.open_create_modal,
                        **{**btn_primary, "padding": "9px 16px"},
                    ),
                    gap="8px", align="center",
                ),
                width="100%", align="center",
            ),

            # ── Stats card ─────────────────────────────────
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.text(AdminState.users.length().to_string(),
                                font_size="32px", font_weight="700", color=ACCENT, font_family=FONT),
                        rx.text("Active users", font_size="13px", color=TEXT3, font_family=FONT),
                        align="start", gap="2px",
                    ),
                    rx.spacer(),
                    rx.box(
                        rx.icon("users", size=36, color=ACCENT),
                        background=ACCENT_D, border_radius="12px", padding="14px",
                        display="flex", align_items="center", justify_content="center",
                    ),
                    width="100%", align="center",
                ),
                **card, width="100%",
            ),

            # ── Users list ─────────────────────────────────
            rx.vstack(
                rx.hstack(
                    rx.text("Users", font_size="16px", font_weight="600", color=TEXT, font_family=FONT),
                    rx.spacer(),
                    rx.text(AdminState.users.length().to_string() + " total",
                            font_size="13px", color=TEXT3, font_family=FONT),
                    width="100%", align="center",
                ),
                rx.cond(
                    AdminState.users.length() > 0,
                    rx.vstack(
                        rx.foreach(AdminState.users, user_row),
                        gap="8px", width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.icon("users", size=40, color=TEXT3),
                            rx.text("No users yet", font_size="15px", font_weight="600",
                                    color=TEXT2, font_family=FONT),
                            rx.text("Create the first user to get started.",
                                    font_size="13px", color=TEXT3, font_family=FONT),
                            rx.button(
                                rx.hstack(rx.icon("user_plus", size=15), rx.text("Create first user")),
                                on_click=AdminState.open_create_modal, **{**btn_primary, "margin_top": "8px"},
                            ),
                            align="center", gap="8px",
                        ),
                        display="flex", align_items="center", justify_content="center",
                        padding="50px 24px",
                        background=BG2, border=f"2px dashed {BORDER}", border_radius="14px", width="100%",
                    ),
                ),
                gap="12px", width="100%",
            ),

            max_width="800px", margin="0 auto",
            padding="20px 16px 80px 16px",
            display="flex", flex_direction="column", gap="20px",
        ),

        background=BG, color=TEXT, font_family=FONT, min_height="100vh",
    )
