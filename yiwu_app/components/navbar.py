import reflex as rx
from yiwu_app.models.auth_state import AuthState
from yiwu_app.styles.theme import *


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.text("F", color="white", font_weight="700", font_size="16px"),
                    background=ACCENT, border_radius="8px", width="30px", height="30px",
                    display="flex", align_items="center", justify_content="center",
                    flex_shrink="0",
                ),
                rx.text("Flyon Yiwu Market", font_size="15px", font_weight="600",
                        color=TEXT, font_family=FONT,
                        overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                align="center", gap="9px", cursor="pointer", on_click=rx.redirect("/lists"),
                min_width="0",
            ),
            rx.spacer(),
            rx.cond(
                AuthState.is_authenticated,
                rx.hstack(
                    # Name hidden on small screens
                    rx.text(AuthState.user_name, font_size="13px", font_weight="500",
                            color=TEXT2, font_family=FONT,
                            overflow="hidden", text_overflow="ellipsis", white_space="nowrap",
                            max_width="120px"),
                    rx.button(
                        rx.icon("log_out", size=15),
                        on_click=AuthState.logout,
                        background="transparent", color=TEXT3,
                        border=f"1px solid {BORDER}",
                        border_radius="8px", padding="7px 10px",
                        cursor="pointer",
                        _hover=dict(color=DANGER, border_color=DANGER), transition="all 0.15s",
                        title="Sign out",
                    ),
                    align="center", gap="10px", flex_shrink="0",
                ),
                rx.box(),
            ),
            align="center", width="100%", gap="8px",
        ),
        background=BG2, border_bottom=f"1px solid {BORDER}",
        padding="0 16px", height="54px",
        display="flex", align_items="center",
        position="sticky", top="0", z_index="100",
        box_shadow="0 1px 6px rgba(15,31,46,0.07)",
    )
