import customtkinter as ctk


class Theme:
    # Fundos
    BG_APP = "#15161b"        # janela / sidebar
    BG_CONTENT = "#1b1c23"    # painel de conteúdo (direita)
    SURFACE = "#20222b"       # botões secundários / inputs
    CARD = "#22242e"          # cards de perfil

    # Bordas / divisores
    BORDER = "#2f3140"

    # Texto
    TEXT = "#eef0f5"
    TEXT_MUTED = "#8b8fa3"

    # Accent (ação primária)
    ACCENT = "#4f7cff"
    ACCENT_HOVER = "#3f65d9"

    # Estados
    SUCCESS = "#3ecf8e"
    DANGER = "#e5484d"
    DANGER_HOVER = "#c93f43"


def apply():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")