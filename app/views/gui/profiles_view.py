import customtkinter as ctk

from app.services.connection_profile_service import ConnectionProfileService

class ProfilesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.profile_service = ConnectionProfileService()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_header()
        self._create_profile_area()

        self.load_profiles()

    # ==========================================================
    # HEADER
    # ==========================================================

    def _create_header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")

        self.header.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 10))

        self.header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header,
            text="Perfis de Conexão",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.new_button = ctk.CTkButton(
            self.header,
            text="Novo Perfil",
            command=self.open_create_dialog
        )
        self.new_button.grid(row=0, column=1, padx=(10, 0))

    # ==========================================================
    # ÁREA DOS PERFIS
    # ==========================================================

    def _create_profile_area(self):
        self.profiles_frame = ctk.CTkScrollableFrame(self)
        self.profiles_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=(10, 25))
        self.profiles_frame.grid_columnconfigure(0, weight=1)

    # ==========================================================
    # CARREGAMENTO
    # ==========================================================
    def load_profiles(self):
        for widget in self.profiles_frame.winfo_children():
            widget.destroy()

        profiles = self.profile_service.load_profiles()

        if not profiles:
            empty_label = ctk.CTkLabel(
                self.profiles_frame,
                text="Nenhum perfil de conexão cadastrado",
                font=ctk.CTkFont(size=15)
            )
            empty_label.grid(row=0, column=0, pady=40)

            return

        for index, profile in enumerate(profiles):
            self._create_profile_card(profile, index)

    # ==========================================================
    # CARD DO PERFIL
    # ==========================================================

    def _create_profile_card(self, profile, row):
        card = ctk.CTkFrame(
            self.profiles_frame
        )
        card.grid(row=row, column=0, sticky="ew", padx=5, pady=6)
        card.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(
            card,
            text=profile.name,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )
        name_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 3))

        database_label = ctk.CTkLabel(
            card,
            text=(
                f"Servidor (IP): {profile.server}\n"
                f"Nome do banco: {profile.database}\n"
                f"Usuário do banco: {profile.username}"
            ),
            justify="left"
        )
        database_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))

        buttons_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        buttons_frame.grid(row=0, column=1, rowspan=2, padx=20)

        edit_button = ctk.CTkButton(
            buttons_frame,
            text="Editar",
            width=90,
            command=lambda p=profile:
                self.open_edit_dialog(p)
        )
        edit_button.pack(side="left", padx=5)

        delete_button = ctk.CTkButton(
            buttons_frame,
            text="Excluir",
            width=90,
            command=lambda p=profile:
                self.confirm_delete(p)
        )
        delete_button.pack(side="left", padx=5)

    # ==========================================================
    # NOVO PERFIL
    # ==========================================================
    def open_create_dialog(self):
        dialog = ProfileDialog(self, title="Novo perfil")

        self.wait_window(dialog)

        if dialog.result is None:
            return

        data = dialog.result

        try:

            self.profile_service.create_profile(
                name=data["name"],
                server=data["server"],
                database=data["database"],
                username=data["username"],
                tables=data["tables"]
            )

            self.load_profiles()

        except Exception as error:
            self.show_error(
                f"Não foi possível criar o perfil.\n\n"
                f"{error}"
            )

    # ==========================================================
    # EDITAR PERFIL
    # ==========================================================
    def open_edit_dialog(self, profile):
        dialog = ProfileDialog(
            self,
            title="Editar perfil",
            profile=profile
        )

        self.wait_window(dialog)

        if dialog.result is None:
            return

        data = dialog.result

        try:
            self.profile_service.update_profile(
                profile_id=profile.id,
                name=data["name"],
                server=data["server"],
                database=data["database"],
                username=data["username"],
                tables=data["tables"]
            )

            self.load_profiles()

        except Exception as error:
            self.show_error(
                f"Não foi possível atualizar o perfil\n\n"
                f"{error}"
            )

    # ==========================================================
    # EXCLUIR
    # ==========================================================
    def confirm_delete(self, profile):
        dialog = ctk.CTkToplevel(self)

        dialog.title("Excluir perfil")
        dialog.geometry("400x190")
        dialog.resizable(False, False)

        dialog.transient(self)
        dialog.grab_set()

        label = ctk.CTkLabel(
            dialog,
            text=(
                f"Deseja realmente excluir o perfil?\n\n"
                f"{profile.name}"
            ),
            font=ctk.CTkFont(size=15)
        )
        label.pack(padx=20, pady=(25, 20))

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack()

        def delete():
            try:
                self.profile_service.delete_profile(profile.id)

                dialog.destroy()
                self.load_profiles()

            except Exception as error:
                self.show_error(
                    f"Não foi possível excluir o perfil.\n\n"
                    f"{error}"
                )

        cancel_button = ctk.CTkButton(
            buttons,
            text="Cancelar",
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=5)

        confirm_button = ctk.CTkButton(
            buttons,
            text="Excluir",
            command=delete
        )
        confirm_button.pack(side="left", padx=5)

    # ==========================================================
    # ERRO
    # ==========================================================
    def show_error(self, message):
        dialog = ctk.CTkToplevel(self)

        dialog.title("Erro")
        dialog.geometry("450x220")
        dialog.resizable(False, False)

        dialog.transient(self)
        dialog.grab_set()

        label = ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=400,
            justify="center"
        )
        label.pack(padx=20, pady=30)

        button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        button.pack()

# ==============================================================
# DIALOG DE PERFIL
# ==============================================================
class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, master, title, profile=None):
        super().__init__(master)

        self.result = None

        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        self._create_fields(profile)

    def _create_fields(self, profile):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=self.title(),
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=30, pady=(25, 30))

        self.name_entry = self._create_entry("Nome do perfil", 1, profile.name if profile else "")

        self.server_entry  = self._create_entry("Servidor", 2, profile.server if profile else "")

        self.database_entry = self._create_entry("Banco de dados", 3, profile.database if profile else "")

        self.username_entry = self._create_entry("Usuário", 4, profile.username if profile else "")

        tables = ""

        if profile and profile.tables:
            tables = ", ".join(profile.tables)

        self.tables_entry = self._create_entry("Tabelas monitoradas", 5, tables)

        self.info_label = ctk.CTkLabel(
            self,
            text=("Informe as tabelas separadas por vírgula."),
            font=ctk.CTkFont(size=12)
        )
        self.info_label.grid(row=6, column=1, padx=(0, 30), pady=(0, 15), sticky="w")

        buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        buttons.grid(row=7, column=0, columnspan=2, pady=30)

        cancel_button = ctk.CTkButton(
            buttons,
            text="Cancelar",
            command=self.destroy
        )
        cancel_button.pack(side="left", padx=5)

        save_button = ctk.CTkButton(
            buttons,
            text="Salvar",
            command=self.save
        )
        save_button.pack(side="left", padx=5)

    def _create_entry(self, label_text, row, value):
        label = ctk.CTkLabel(
            self, 
            text=label_text,
            anchor="e"
        )
        label.grid(row=row, column=0, padx=(30, 15), pady=8, sticky="e")

        entry = ctk.CTkEntry(
            self,
            width=320
        )
        entry.grid(row=row, column=1, padx=(0, 30), pady=8, sticky="ew")
        entry.insert(0, value)

        return entry

    def save(self):
        name = self.name_entry.get().strip()
        server = self.server_entry.get().strip()
        database = self.database_entry.get().strip()
        username = self.username_entry.get().strip()
        tables_text = self.tables_entry.get().strip()

        if not name:
            self.show_error("Informe o nome do perfil.")
            return

        if not server:
            self.show_error("Informe o IP do Servidor.")
            return

        if not database:
            self.show_error("Informe o banco de dados.")
            return

        if not username:
            self.show_error("Informe o usuário do banco.")
            return

        tables = [
            table.strip()
            for table in tables_text.split(",")
            if table.strip()
        ]

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
