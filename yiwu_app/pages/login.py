import reflex as rx
from yiwu_app.models.auth_state import AuthState
from yiwu_app.styles.theme import *


def login_page() -> rx.Component:
    return rx.box(
        rx.box(
            # ── Logo ───────────────────────────────────────
            rx.vstack(
                rx.box(
                    rx.text("F", color="white", font_weight="800", font_size="28px"),
                    background=f"linear-gradient(135deg, {ACCENT}, #0ea5e9)",
                    border_radius="16px", width="56px", height="56px",
                    display="flex", align_items="center", justify_content="center",
                    box_shadow=f"0 4px 20px {ACCENT_D}",
                ),
                rx.text("Flyon Yiwu Market",
                        font_size="24px", font_weight="700", color=TEXT, font_family=FONT),
                rx.text("Product catalog management",
                        font_size="14px", color=TEXT3, font_family=FONT),
                align="center", gap="8px", margin_bottom="28px",
            ),

            # ── Form ───────────────────────────────────────
            rx.vstack(
                rx.vstack(
                    rx.text("Username", **label_style),
                    rx.input(
                        placeholder="Enter your username",
                        value=AuthState.form_email,
                        on_change=AuthState.set_email,
                        **input_style,
                    ),
                    align="start", width="100%", gap="4px",
                ),
                rx.vstack(
                    rx.text("Password", **label_style),
                    rx.input(
                        placeholder="••••••••",
                        value=AuthState.form_password,
                        on_change=AuthState.set_password,
                        type="password",
                        **input_style,
                    ),
                    align="start", width="100%", gap="4px",
                ),

                # Error message
                rx.cond(
                    AuthState.error != "",
                    rx.box(
                        rx.hstack(
                            rx.icon("circle_alert", size=14, color=DANGER),
                            rx.text(AuthState.error,
                                    color=DANGER, font_size="13px", font_family=FONT),
                            align="center", gap="6px",
                        ),
                        background=DANGER_D,
                        border=f"1px solid rgba(192,57,43,0.2)",
                        border_radius="8px", padding="10px 14px", width="100%",
                    ),
                ),

                # Submit button
                rx.button(
                    rx.cond(
                        AuthState.is_loading,
                        rx.hstack(rx.spinner(size="2"), rx.text("Signing in...")),
                        rx.hstack(rx.icon("log_in", size=16), rx.text("Sign in")),
                    ),
                    on_click=AuthState.login,
                    disabled=AuthState.is_loading,
                    width="100%",
                    background=ACCENT,
                    color="white",
                    border="none",
                    border_radius="10px",
                    padding="12px",
                    font_family=FONT,
                    font_size="15px",
                    font_weight="500",
                    cursor="pointer",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    gap="8px",
                    _hover=dict(background=ACCENT_H),
                    transition="all 0.15s",
                ),

                gap="16px", width="100%",
            ),

            **card,
            width="min(420px, 94vw)",
            position="relative", z_index="1",
        ),
        background=BG, color=TEXT, font_family=FONT,
        min_height="100vh",
        display="flex", align_items="center", justify_content="center", padding="24px",
        on_mount=AuthState.on_load,
    )
