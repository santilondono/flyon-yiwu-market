"""Design tokens — Light mode, Blue palette, Flyon Yiwu Market"""

# ── Palette (Light / Blue) ─────────────────────────────────────────────────
BG        = "#f0f4f8"
BG2       = "#ffffff"
BG3       = "#e8eef5"
BORDER    = "#d1dce8"
BORDER_L  = "#b0c4d8"
TEXT      = "#0f1f2e"
TEXT2     = "#3d5470"
TEXT3     = "#7a95ae"
ACCENT    = "#1d6fb8"       # primary blue
ACCENT_H  = "#1558a0"       # hover darker
ACCENT_D  = "rgba(29,111,184,0.10)"
ACCENT_D2 = "rgba(29,111,184,0.06)"
ACCENT2   = "#0ea5e9"       # sky accent for highlights
SUCCESS   = "#0d7a4e"
SUCCESS_D = "rgba(13,122,78,0.10)"
DANGER    = "#c0392b"
DANGER_D  = "rgba(192,57,43,0.08)"
WARNING   = "#b45309"

# ── Typography ─────────────────────────────────────────────────────────────
FONT      = "'DM Sans', sans-serif"
FONT_MONO = "'DM Mono', monospace"

# ── Common style dicts ──────────────────────────────────────────────────────
page_style = dict(
    background=BG,
    color=TEXT,
    font_family=FONT,
    min_height="100vh",
)

card = dict(
    background=BG2,
    border=f"1px solid {BORDER}",
    border_radius="14px",
    padding="24px",
    box_shadow="0 1px 8px rgba(15,31,46,0.07)",
)

card_sm = dict(
    background=BG2,
    border=f"1px solid {BORDER}",
    border_radius="12px",
    padding="16px",
    box_shadow="0 1px 4px rgba(15,31,46,0.05)",
)

input_style = dict(
    background=BG2,
    border=f"1px solid {BORDER}",
    border_radius="10px",
    color=TEXT,
    font_family=FONT,
    font_size="15px",
    padding="10px 14px",
    width="100%",
    _focus=dict(
        border_color=ACCENT,
        box_shadow=f"0 0 0 3px {ACCENT_D}",
        outline="none",
    ),
    _placeholder=dict(color=TEXT3),
)

btn_primary = dict(
    background=ACCENT,
    color="white",
    border="none",
    border_radius="10px",
    padding="10px 20px",
    font_family=FONT,
    font_size="14px",
    font_weight="500",
    cursor="pointer",
    display="inline-flex",
    align_items="center",
    gap="8px",
    white_space="nowrap",
    _hover=dict(background=ACCENT_H, transform="translateY(-1px)"),
    transition="all 0.15s",
)

btn_ghost = dict(
    background="transparent",
    color=TEXT2,
    border=f"1px solid {BORDER}",
    border_radius="10px",
    padding="10px 18px",
    font_family=FONT,
    font_size="14px",
    font_weight="500",
    cursor="pointer",
    display="inline-flex",
    align_items="center",
    gap="8px",
    _hover=dict(background=BG3, color=TEXT),
    transition="all 0.15s",
)

btn_danger = dict(
    background=DANGER_D,
    color=DANGER,
    border="1px solid transparent",
    border_radius="10px",
    padding="8px 14px",
    font_family=FONT,
    font_size="13px",
    font_weight="500",
    cursor="pointer",
    display="inline-flex",
    align_items="center",
    gap="6px",
    _hover=dict(background="rgba(192,57,43,0.15)"),
    transition="all 0.15s",
)

btn_success = dict(
    background=SUCCESS_D,
    color=SUCCESS,
    border="1px solid transparent",
    border_radius="10px",
    padding="8px 14px",
    font_family=FONT,
    font_size="13px",
    font_weight="500",
    cursor="pointer",
    display="inline-flex",
    align_items="center",
    gap="6px",
    _hover=dict(background="rgba(13,122,78,0.18)"),
    transition="all 0.15s",
)

label_style = dict(
    font_size="13px",
    font_weight="500",
    color=TEXT2,
    margin_bottom="5px",
    display="block",
)

badge_accent = dict(
    background=ACCENT_D,
    color=ACCENT,
    border_radius="20px",
    padding="3px 10px",
    font_size="12px",
    font_weight="500",
    display="inline-flex",
    align_items="center",
)
