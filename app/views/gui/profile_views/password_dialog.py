import customtkinter as ctk
from app.views.gui.theme import Theme

class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, master, profile_name=None, server=None, database=None, message=None):
        super().__init__(master)

        self.password = None

        self.title("Senha do banco")
        self.geometry("420x260")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CONTENT)

        self.transient(master)
        self.grab_set()

        self._create_widgets(profile_name, server, database, message)

    def _create_widgets(self, profile_name, server, database, message):
        title = ctk.CTkLabel(
            self,
            text="Autenticação necessária",
            font=Theme.font(size=18, weight="bold"),
            text_color=Theme.TEXT,
        )
        title.pack(pady=(25, 6))

        info_parts = [part for part in [profile_name, database, server] if part]
        if info_parts:
            info_label = ctk.CTkLabel(
                self, text=" • ".join(info_parts),
                font=Theme.font(size=12), text_color=Theme.TEXT_MUTED,
            )
            info_label.pack(pady=(0, 15))

        description = ctk.CTkLabel(
            self,
            text=message or "Digite a senha do usuário do banco para conectar.",
            font=Theme.font(size=12), text_color=Theme.TEXT_MUTED,
            wraplength=340, justify="center",
        )
        description.pack(pady=(0, 12))

        self.password_entry = ctk.CTkEntry(
            self, width=300, height=34, show="*",
            fg_color=Theme.SURFACE, border_color=Theme.BORDER, text_color=Theme.TEXT,
        )
        self.password_entry.pack(pady=5)
        self.password_entry.bind("<Return>", lambda event: self.confirm())

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(pady=20)

        cancel_button = ctk.CTkButton(
            buttons, text="Cancelar", width=120, height=34,
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=self.destroy,
        )
        cancel_button.pack(side="left", padx=5)

        connect_button = ctk.CTkButton(
            buttons, text="Conectar", width=120, height=34,
            font=Theme.font(size=13, weight="bold"),
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=self.confirm,
        )
        connect_button.pack(side="left", padx=5)

        self.after(150, self._focus_password)

    def _focus_password(self):
        self.password_entry.focus_force()

    def confirm(self):
        self.password = self.password_entry.get()

        if not self.password:
            return

        self.destroy()