import customtkinter as ctk


class Theme:
    BG_APP = "#15161b"
    BG_CONTENT = "#1b1c23"
    SURFACE = "#20222b"
    CARD = "#22242e"

    BORDER = "#2f3140"

    TEXT = "#eef0f5"
    TEXT_MUTED = "#8b8fa3"

    ACCENT = "#4f7cff"
    ACCENT_HOVER = "#3f65d9"

    SUCCESS = "#3ecf8e"
    SUCCESS_HOVER = "#31a873"
    DANGER = "#e5484d"
    DANGER_HOVER = "#c93f43"

    FONT_FAMILY = "Bahnschrift"

    @classmethod
    def font(cls, size=13, weight="normal"):
        return ctk.CTkFont(
            family=cls.FONT_FAMILY,
            size=size,
            weight=weight,
        )


def apply():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")