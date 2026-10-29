import customtkinter as ctk


class Theme:
    # Paleta baseada no tema Dracula
    BG_APP = "#21222c"       # fundo mais escuro (sidebar/base)
    BG_CONTENT = "#282a36"   # fundo principal (Dracula background)
    SURFACE = "#343746"      # botões/inputs neutros
    CARD = "#2f313e"         # cards e painéis

    BORDER = "#44475a"       # Dracula "current line" / selection

    TEXT = "#f8f8f2"         # Dracula foreground
    TEXT_MUTED = "#6272a4"   # Dracula comment

    ACCENT = "#4f7cff"       # azul original, mantido
    ACCENT_HOVER = "#3f65d9"

    SUCCESS = "#50fa7b"      # Dracula green
    SUCCESS_HOVER = "#3ddb64"
    DANGER = "#ff5555"       # Dracula red
    DANGER_HOVER = "#e64545"

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