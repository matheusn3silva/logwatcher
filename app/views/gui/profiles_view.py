import customtkinter as ctk

from app.services.connection_profile_service import ConnectionProfileService
from app.config.database_config import DatabaseConfig
from app.services.connection_service import ConnectionService
from app.services.logwatcher_service import LogWatcherService
from app.views.gui.theme import Theme
from app.views.gui.tooltip import Tooltip

class ProfilesView(ctk.CTkFrame):
    def __init__(self, master, connection_manager, on_profile_selected,
                 on_profile_disconnected=None):
        super().__init__(master, fg_color="transparent")

        self.profile_service = ConnectionProfileService()
        self.connection_manager = connection_manager
        self.on_profile_selected = on_profile_selected
        self.on_profile_disconnected = on_profile_disconnected

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_profile_area()

        self.load_profiles()

    # ==========================================================
    # ÁREA DOS PERFIS
    # ==========================================================

    def _create_profile_area(self):
        self.profiles_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Theme.BORDER,
            scrollbar_button_hover_color=Theme.ACCENT,
        )
        self.profiles_frame.grid(row=0, column=0, sticky="nsew")
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
                text="Nenhum perfil cadastrado.\nClique em \"+ Novo Perfil\".",
                font=Theme.font(size=13),
                text_color=Theme.TEXT_MUTED,
                justify="center"
            )
            empty_label.grid(row=0, column=0, pady=30, padx=5)
            return

        for index, profile in enumerate(profiles):
            self._create_profile_card(profile, index)

    # ==========================================================
    # CARD DO PERFIL
    # ==========================================================

    def _create_profile_card(self, profile, row):
        connected = self.connection_manager.is_connected(profile.id)

        card = ctk.CTkFrame(
            self.profiles_frame,
            fg_color=Theme.CARD,
            corner_radius=10,
            border_width=1,
            border_color=Theme.ACCENT if connected else Theme.BORDER,
        )
        card.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        card.grid_columnconfigure(0, weight=1)

        # Nome + status (empilhados, não mais lado a lado com os botões)
        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 2))
        header_row.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(
            header_row, text=profile.name,
            font=Theme.font(size=14, weight="bold"),
            anchor="w", justify="left", wraplength=170,
        )
        name_label.grid(row=0, column=0, sticky="w")

        status_label = ctk.CTkLabel(
            header_row,
            text="● Conectado" if connected else "○ Offline",
            font=Theme.font(size=11),
            text_color=Theme.SUCCESS if connected else Theme.TEXT_MUTED,
        )
        status_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        database_label = ctk.CTkLabel(
            card,
            text=(
                f"Servidor: {profile.server}\n"
                f"Banco: {profile.database}\n"
                f"Usuário: {profile.username}"
            ),
            font=Theme.font(size=11),
            text_color=Theme.TEXT_MUTED,
            justify="left", anchor="w", wraplength=200,
        )
        database_label.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

        # Botões: grade de 2 colunas, nunca estoura a largura do card
        buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        small_font = Theme.font(size=11)

        if connected:
            select_button = ctk.CTkButton(
                buttons_frame, text="Selecionar", height=26, font=small_font,
                fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
                command=lambda p=profile: self.select_profile(p)
            )
            select_button.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

            disconnect_button = ctk.CTkButton(
                buttons_frame, text="Desconectar", height=26, font=small_font,
                fg_color=Theme.DANGER, hover_color=Theme.DANGER_HOVER,
                command=lambda p=profile: self.disconnect_profile(p)
            )
            disconnect_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))
            edit_row = 2
        else:
            connect_button = ctk.CTkButton(
                buttons_frame, text="Conectar", height=26, font=small_font,
                fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
                command=lambda p=profile: self.connect_profile(p)
            )
            connect_button.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
            edit_row = 1

        edit_button = ctk.CTkButton(
            buttons_frame, text="Editar", height=26, font=small_font,
            fg_color=Theme.SUCCESS, hover_color=Theme.SUCCESS_HOVER,
            command=lambda p=profile: self.open_edit_dialog(p)
        )
        edit_button.grid(row=edit_row, column=0, sticky="ew", padx=(0, 3))

        delete_button = ctk.CTkButton(
            buttons_frame, text="Excluir", height=26, font=small_font,
            fg_color=Theme.SURFACE, hover_color=Theme.DANGER_HOVER,
            border_width=1, border_color="#ffffff",
            command=lambda p=profile: self.confirm_delete(p)
        )
        delete_button.grid(row=edit_row, column=1, sticky="ew", padx=(3, 0))
        Tooltip(delete_button, "Remove o perfil salvo localmente. Não afeta os dados do banco.")

    # ==========================================================
    # NOVO PERFIL
    # ==========================================================
    def open_create_dialog(self):
        dialog = ProfileDialog(self, title="Novo perfil")

        self.wait_window(dialog)

        if dialog.result is None:
            return

        data = dialog.result

        password_dialog = PasswordDialog(
            self,
            profile_name=data["name"],
            server=data["server"],
            database=data["database"],
        )

        self.wait_window(password_dialog)

        if password_dialog.password is None:
            return

        password = password_dialog.password

        connection_service = ConnectionService()

        try:
            config = DatabaseConfig(
                server=data["server"],
                database=data["database"],
                username=data["username"],
                password=password
            )

            connection_service.connect(config)

            logwatcher_service = LogWatcherService(connection_service.repository)

            valid_tables, invalid_tables = (
                logwatcher_service.validate_tables(
                    ",".join(data["tables"])
                )
            )

            if invalid_tables:
                self.show_invalid_tables(invalid_tables)

            if not valid_tables:
                self.show_error(
                    "Nenhuma das tabelas informadas existe "
                    "no banco de dados."
                )
                return

            self.profile_service.create_profile(
                name=data["name"],
                server=data["server"],
                database=data["database"],
                username=data["username"],
                tables=valid_tables
            )

            self.load_profiles()

            if invalid_tables:
                self.show_info(
                    "Perfil criado.\n\n"
                    "Somente as tabelas existentes foram salvas."
                )

        except Exception as error:
            self.show_error(
                "Não foi possível criar o perfil.\n\n"
                f"{error}"
            )

        finally:
            connection_service.disconnect()

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

        if not data["tables"]:
            self.profile_service.update_profile(
                profile_id=profile.id,
                name=data["name"],
                server=data["server"],
                database=data["database"],
                username=data["username"],
                tables=[]
            )

            self.load_profiles()
            return

        password_dialog = PasswordDialog(
            self,
            profile_name=data["name"],
            server=data["server"],
            database=data["database"],
        )

        self.wait_window(password_dialog)

        if password_dialog.password is None:
            return

        password = password_dialog.password

        connection_service = ConnectionService()

        try:
            config = DatabaseConfig(
                server=data["server"],
                database=data["database"],
                username=data["username"],
                password=password
            )

            connection_service.connect(config)

            logwatcher_service = LogWatcherService(connection_service.repository)

            valid_tables, invalid_tables = (
                logwatcher_service.validate_tables(
                    ",".join(data["tables"])
                )
            )

            if invalid_tables:
                self.show_invalid_tables(invalid_tables)

            if not valid_tables:
                self.show_info(
                    "Nenhuma das novas tabelas existe.\n\n"
                    "As tabelas já cadastradas não foram alteradas."
                )

                return

            self.profile_service.update_profile(
                profile_id=profile.id,
                name=data["name"],
                server=data["server"],
                database=data["database"],
                username=data["username"],
                tables=valid_tables
            )

            self.load_profiles()

            if invalid_tables:
                self.show_info(
                    "Perfil atualizado.\n\n"
                    "As tabelas existentes foram mantidas "
                    "e somente as novas tabelas válidas foram adicionadas."
                )

        except Exception as error:
            self.show_error(
                "Não foi possível atualizar o perfil.\n\n"
                f"{error}"
            )

        finally:
            connection_service.disconnect()


    def show_invalid_tables(self, tables):
        text = (
            "As seguintes tabelas não foram encontradas:\n\n"
            + "\n".join(
                f"• {table}"
                for table in tables
            )
        )
        self.show_info(text)


    def show_info(self, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Informação")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Theme.BG_CONTENT)

        dialog.transient(self)
        dialog.grab_set()

        label = ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=440,
            justify="left"
        )
        label.pack(padx=30, pady=40)

        button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        button.pack()

    # ==========================================================
    # EXCLUIR
    # ==========================================================
    def confirm_delete(self, profile):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Excluir perfil")
        dialog.geometry("400x190")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Theme.BG_CONTENT)

        dialog.transient(self)
        dialog.grab_set()

        label = ctk.CTkLabel(
            dialog,
            text=(
                f"Deseja realmente excluir o perfil?\n\n"
                f"{profile.name}"
            ),
            font=Theme.font(size=15)
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
    # CONEXÃO
    # ==========================================================

    def connect_profile(self, profile):
        dialog = PasswordDialog(
            self,
            profile_name=profile.name,
            server=profile.server,
            database=profile.database,
        )

        self.wait_window(dialog)

        if dialog.password is None:
            return

        try:
            self.connection_manager.connect(profile, dialog.password)

            self.load_profiles()
            self.select_profile(profile)

        except Exception as error:
            self.show_error(
                f"Não foi possível conectar ao perfil.\n\n"
                f"{error}"
            )


    def disconnect_profile(self, profile):
        try:
            self.connection_manager.disconnect(profile.id)
            self.load_profiles()

            if self.on_profile_disconnected:
                self.on_profile_disconnected(profile)

        except Exception as error:
            self.show_error(
                f"Não foi possível desconectar do perfil.\n\n"
                f"{error}"
            )


    def select_profile(self, profile):
        if not self.connection_manager.is_connected(profile.id):
            return

        self.on_profile_selected(profile)

    # ==========================================================
    # ERRO
    # ==========================================================
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
            wraplength=350,
            text_color=Theme.TEXT,
        )
        label.pack(padx=20, pady=30)

        button = ctk.CTkButton(
            dialog,
            text="OK",
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
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

            info_row = 8
            buttons_row = 9

        else:
            self.tables_entry = self._create_entry("Tabelas monitoradas", 5, "")

            info_row = 6
            buttons_row = 7

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

class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, master, profile_name=None, server=None, database=None):
        super().__init__(master)

        self.password = None

        self.title("Senha do banco")
        self.geometry("420x260")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CONTENT)

        self.transient(master)
        self.grab_set()

        self._create_widgets(profile_name, server, database)

    def _create_widgets(self, profile_name, server, database):
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
            text="Digite a senha do usuário do banco para continuar.",
            font=Theme.font(size=12), text_color=Theme.TEXT_MUTED,
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