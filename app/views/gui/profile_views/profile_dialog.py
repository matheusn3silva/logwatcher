import customtkinter as ctk
from app.services.table_parser import TableParser
from app.views.gui.theme import Theme

# ==============================================================
# DIALOG DE PERFIL
# ==============================================================
class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, master, title, profile=None):
        super().__init__(master)

        self.result = None
        self._profile = profile

        self.title(title)
        self.geometry("500x640")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CONTENT)

        self.transient(master)
        self.grab_set()

        self._create_fields(profile)

    def _create_fields(self, profile):

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=self.title(),
            font=Theme.font(size=22, weight="bold"),
            text_color=Theme.TEXT,
        )
        self.title_label.grid(
            row=0, column=0, columnspan=2, padx=30, pady=(25, 30)
        )

        self.name_entry = self._create_entry(
            "Nome do perfil",
            1,
            profile.name if profile else ""
        )

        self.server_entry = self._create_entry(
            "Servidor",
            2,
            profile.server if profile else ""
        )

        self.database_entry = self._create_entry(
            "Banco de dados",
            3,
            profile.database if profile else ""
        )

        self.username_entry = self._create_entry(
            "Usuário",
            4,
            profile.username if profile else ""
        )
        
        self._entries = {
            "name": self.name_entry,
            "server": self.server_entry,
            "database": self.database_entry,
            "username": self.username_entry,
        }

        # ==========================================================
        # TABELAS
        # ==========================================================

        if profile:
            current_tables_label = ctk.CTkLabel(
                self,
                text="Tabelas atualmente cadastradas:",
                anchor="w",
                font=Theme.font(size=12),
                text_color=Theme.TEXT_MUTED,
            )
            current_tables_label.grid(row=5, column=0, columnspan=2, padx=30, pady=(10, 5), sticky="w")

            current_tables = ", ".join(profile.tables)

            current_tables_value = ctk.CTkLabel(
                self,
                text=current_tables or "Nenhuma tabela cadastrada.",
                anchor="w",
                justify="left",
                text_color=Theme.TEXT,
            )
            current_tables_value.grid(row=6, column=0, columnspan=2, padx=30, pady=(0, 10), sticky="w")

            self.tables_entry = self._create_entry("Novas tabelas", 7, "")
            self._entries["tables"] = self.tables_entry

            info_row = 8
            error_row = 9
            buttons_row = 10

        else:
            self.tables_entry = self._create_entry("Tabelas monitoradas", 5, "")
            self._entries["tables"] = self.tables_entry

            info_row = 6
            error_row = 7
            buttons_row = 8

        # ==========================================================
        # INFORMAÇÃO
        # ==========================================================

        self.info_label = ctk.CTkLabel(
            self,
            text="Informe as tabelas separadas por vírgula.",
            font=Theme.font(size=12),
            text_color=Theme.TEXT_MUTED,
        )
        self.info_label.grid(row=info_row, column=1, padx=(0, 30), pady=(0, 15), sticky="w")
        
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=Theme.font(size=12, weight="bold"),
            text_color=Theme.DANGER,
            wraplength=440,
            justify="left",
        )
        self.error_label.grid(row=error_row, column=0, columnspan=2, padx=30, pady=(0, 5), sticky="w")

        # ==========================================================
        # BOTÕES
        # ==========================================================

        buttons = ctk.CTkFrame(
            self, 
            fg_color="transparent"
        )

        buttons.grid(row=buttons_row, column=0, columnspan=2, pady=30)

        cancel_button = ctk.CTkButton(
            buttons,
            text="Cancelar",
            width=120,
            height=36,
            font=Theme.font(size=13),
            fg_color=Theme.SURFACE,
            hover_color=Theme.BORDER,
            text_color=Theme.TEXT,
            command=self.destroy
        )
        cancel_button.pack(side="left", padx=5)

        save_button = ctk.CTkButton(
            buttons,
            text="Salvar",
            width=160,
            height=36,
            font=Theme.font(size=13, weight="bold"),
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            text_color=Theme.TEXT,
            command=self.save
        )
        save_button.pack(side="left", padx=5)
        self.after(150, self.name_entry.focus_force)
    
    def _create_entry(self, label_text, row, value):
        label = ctk.CTkLabel(
            self,
            text=label_text,
            anchor="w",
            font=Theme.font(size=12),
            text_color=Theme.TEXT_MUTED,
        )
        label.grid(row=row, column=0, padx=(30, 15), pady=8, sticky="w")

        entry = ctk.CTkEntry(
            self,
            width=320,
            height=34,
            fg_color=Theme.SURFACE,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT,
        )
        entry.grid(row=row, column=1, padx=(0, 30), pady=8, sticky="ew")
        entry.insert(0, value)

        return entry
    
    def _clear_field_errors(self):
        self.error_label.configure(text="")

        for entry in self._entries.values():
            entry.configure(border_color=Theme.BORDER)

    def _set_field_error(self, field_key, message):
        self.error_label.configure(text=message)

        entry = self._entries.get(field_key)
        if entry is not None:
            entry.configure(border_color=Theme.DANGER)

    def save(self):
        self._clear_field_errors()

        name = self.name_entry.get().strip()
        server = self.server_entry.get().strip()
        database = self.database_entry.get().strip()
        username = self.username_entry.get().strip()
        tables_text = self.tables_entry.get().strip()

        if not name:
            self._set_field_error("name", "Informe o nome do perfil.")
            return

        if not server:
            self._set_field_error("server", "Informe o IP do servidor.")
            return

        if not database:
            self._set_field_error("database", "Informe o banco de dados.")
            return

        if not username:
            self._set_field_error("username", "Informe o usuário do banco.")
            return

        try:
            tables = TableParser.parse(tables_text)
        except ValueError as error:
            self._set_field_error(
                "tables",
                f"{error} — separe os nomes por vírgula (,), "
                "usando apenas letras, números e underline (_)."
            )
            return
        
        if not tables and self._profile is None:
            self._set_field_error(
                "tables",
                "Informe pelo menos uma tabela monitorada para criar o perfil."
            )
            return

        self.result = {
            "name": name,
            "server": server,
            "database": database,
            "username": username,
            "tables": tables
        }

        self.destroy()

    def show_error(self, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Validação")
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Theme.BG_CONTENT)

        dialog.transient(self)
        dialog.grab_set()

        label = ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=350
        )
        label.pack(padx=20, pady=30)

        button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        button.pack()