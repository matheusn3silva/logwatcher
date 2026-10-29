import customtkinter as ctk

from app.views.gui.theme import Theme
from app.views.gui.tooltip import Tooltip

class MaintenanceView(ctk.CTkFrame):
    def __init__(self, master, connection_manager, profile):
        super().__init__(master, fg_color="transparent")

        self.connection_manager = connection_manager
        self.profile = profile
        self.service = connection_manager.get_service(profile.id)
        self.summary = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_scroll_area()

        self.load()

    # ==========================================================
    # HEADER
    # ==========================================================

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(0, 15))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text=f"Manutenção — {self.profile.name}",
            font=Theme.font(size=20, weight="bold"),
            text_color=Theme.TEXT,
        )
        title.grid(row=0, column=0, sticky="w")

        self.refresh_button = ctk.CTkButton(
            header,
            text="⟳  Atualizar",
            width=110,
            height=30,
            fg_color=Theme.SURFACE,
            hover_color=Theme.BORDER,
            text_color=Theme.TEXT,
            command=self.load,
        )
        self.refresh_button.grid(row=0, column=1, padx=(10, 0))

    # ==========================================================
    # ÁREA ROLÁVEL
    # ==========================================================

    def _create_scroll_area(self):
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Theme.BORDER,
            scrollbar_button_hover_color=Theme.ACCENT,
        )
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        self.scroll.grid_columnconfigure(0, weight=1)

    def _clear_scroll(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

    # ==========================================================
    # CARREGAMENTO
    # ==========================================================

    def load(self):
        self._clear_scroll()

        if self.service is None:
            self._show_message("Este perfil não está conectado.", is_error=True)
            return

        try:
            _, logs = self.service.get_log_status()
            _, data_files = self.service.get_data_status()

            self.summary = None

            if self.profile.tables:
                tables_text = ",".join(self.profile.tables)
                self.summary = self.service.analyze_database(tables_text)

        except Exception as error:
            self._show_message(
                f"Não foi possível consultar os dados.\nMotivo: {error}",
                is_error=True,
            )
            return

        self._clear_scroll()

        row = self._render_tables_section(row=0)
        row = self._render_shrink_section(
            row=row,
            title="Arquivos de Log",
            files=logs,
            empty_text="Nenhum arquivo de log encontrado.",
            on_shrink=self.shrink_log,
        )
        self._render_shrink_section(
            row=row,
            title="Arquivos de Dados",
            files=data_files,
            empty_text="Nenhum arquivo de dados encontrado.",
            on_shrink=self.shrink_data,
        )

    def _show_message(self, text, is_error=False, row=0):
        label = ctk.CTkLabel(
            self.scroll,
            text=text,
            font=Theme.font(size=13),
            text_color=Theme.DANGER if is_error else Theme.TEXT_MUTED,
            justify="left",
        )
        label.grid(row=row, column=0, sticky="w", padx=5, pady=30)

    # ==========================================================
    # TABELAS MONITORADAS (TRUNCATE / DELETE)
    # ==========================================================

    def _render_tables_section(self, row):
        wrapper = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            wrapper, text="Tabelas Monitoradas",
            font=Theme.font(size=14, weight="bold"), text_color=Theme.TEXT,
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        table = ctk.CTkFrame(
            wrapper, fg_color=Theme.CARD, corner_radius=10,
            border_width=1, border_color=Theme.BORDER,
        )
        table.grid(row=1, column=0, sticky="ew")

        headers = ["Tabela", "Schema", "Linhas", "Espaço (MB)", "Usado (MB)", ""]
        numeric_cols = {2, 3, 4}

        for col in range(len(headers)):
            table.grid_columnconfigure(col, weight=0 if col == 5 else 1)

        for col, header_text in enumerate(headers):
            header_label = ctk.CTkLabel(
                table, text=header_text,
                font=Theme.font(size=11, weight="bold"), text_color=Theme.TEXT_MUTED,
                anchor="e" if col in numeric_cols else "w",
            )
            header_label.grid(row=0, column=col, sticky="ew", padx=14, pady=(12, 8))

        divider = ctk.CTkFrame(table, height=1, fg_color=Theme.BORDER)
        divider.grid(row=1, column=0, columnspan=len(headers), sticky="ew", padx=14)

        tables = self.summary.tables if self.summary else []

        if not tables:
            empty_label = ctk.CTkLabel(
                table,
                text=(
                    "Nenhuma tabela encontrada."
                    if self.profile.tables else
                    "Nenhuma tabela monitorada configurada neste perfil."
                ),
                font=Theme.font(size=12), text_color=Theme.TEXT_MUTED,
            )
            empty_label.grid(
                row=2, column=0, columnspan=len(headers),
                sticky="w", padx=14, pady=(10, 14),
            )
            return row + 1

        for r, monitored_table in enumerate(tables, start=2):
            is_last = r == len(tables) + 1
            values = [
                monitored_table.name,
                monitored_table.schema,
                f"{monitored_table.rows:,}".replace(",", "."),
                f"{monitored_table.total_mb:,.2f}",
                f"{monitored_table.used_mb:,.2f}",
            ]

            for col, value in enumerate(values):
                cell = ctk.CTkLabel(
                    table, text=value,
                    font=Theme.font(size=12), text_color=Theme.TEXT,
                    anchor="e" if col in numeric_cols else "w",
                )
                cell.grid(
                    row=r, column=col, sticky="ew",
                    padx=14, pady=(8, 14 if is_last else 8),
                )

            actions = ctk.CTkFrame(table, fg_color="transparent")
            actions.grid(
                row=r, column=5, sticky="e",
                padx=(0, 14), pady=(8, 14 if is_last else 8),
            )

            truncate_button = ctk.CTkButton(
                actions, text="Truncate", width=82, height=26,
                font=Theme.font(size=11),
                fg_color=Theme.DANGER, hover_color=Theme.DANGER_HOVER,
                command=lambda t=monitored_table, index=r - 2: self.clean_table(t, index, "TRUNCATE"),
            )
            truncate_button.pack(side="left", padx=(0, 6))
            Tooltip(truncate_button, "TRUNCATE remove todos os registros rapidamente, sem acionar triggers, e não pode ser desfeito.")

            delete_button = ctk.CTkButton(
                actions, text="Delete", width=82, height=26,
                font=Theme.font(size=11),
                fg_color=Theme.DANGER, hover_color=Theme.DANGER_HOVER,
                command=lambda t=monitored_table, index=r - 2: self.clean_table(t, index, "DELETE"),
            )
            delete_button.pack(side="left")
            Tooltip(delete_button, "DELETE remove todos os registros linha a linha, aciona triggers (se existirem) e não pode ser desfeito.")

        return row + 1

    def clean_table(self, table, index, action):
        table_name = f"{table.schema}.{table.name}"

        method = (
            self.service.truncate_monitored_table
            if action == "TRUNCATE"
            else self.service.delete_monitored_table
        )

        hint = (
            "TRUNCATE é mais rápido, reinicia a contagem de identidade "
            "e não aciona triggers da tabela."
            if action == "TRUNCATE" else
            "DELETE remove linha a linha, aciona triggers (se existirem) "
            "e gera mais log de transação — pode ser mais lento em tabelas grandes."
        )

        self._confirm_danger(
            title=f"{action} de tabela",
            table_name=table_name,
            description=(
                f"Você está prestes a executar {action} na tabela abaixo. "
                f"Essa operação remove todos os registros e não pode ser desfeita."
            ),
            hint=hint,
            run=lambda: method(self.summary, index),
            operation=action,
        )

    # ==========================================================
    # ARQUIVOS (LOG / DADOS) — SHRINK
    # ==========================================================

    def _render_shrink_section(self, row, title, files, empty_text, on_shrink):
        wrapper = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            wrapper, text=title,
            font=Theme.font(size=14, weight="bold"), text_color=Theme.TEXT,
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        table = ctk.CTkFrame(
            wrapper, fg_color=Theme.CARD, corner_radius=10,
            border_width=1, border_color=Theme.BORDER,
        )
        table.grid(row=1, column=0, sticky="ew")

        headers = ["Arquivo", "Tamanho (MB)", "Usado (MB)", "Livre (MB)", ""]
        numeric_cols = {1, 2, 3}

        for col in range(len(headers)):
            table.grid_columnconfigure(col, weight=0 if col == 4 else 1)

        for col, header_text in enumerate(headers):
            header_label = ctk.CTkLabel(
                table, text=header_text,
                font=Theme.font(size=11, weight="bold"), text_color=Theme.TEXT_MUTED,
                anchor="e" if col in numeric_cols else "w",
            )
            header_label.grid(row=0, column=col, sticky="ew", padx=14, pady=(12, 8))

        divider = ctk.CTkFrame(table, height=1, fg_color=Theme.BORDER)
        divider.grid(row=1, column=0, columnspan=len(headers), sticky="ew", padx=14)

        if not files:
            empty_label = ctk.CTkLabel(
                table, text=empty_text,
                font=Theme.font(size=12), text_color=Theme.TEXT_MUTED,
            )
            empty_label.grid(
                row=2, column=0, columnspan=len(headers),
                sticky="w", padx=14, pady=(10, 14),
            )
            return row + 1

        for r, file in enumerate(files, start=2):
            is_last = r == len(files) + 1
            values = [
                file.logical_name,
                f"{file.size_mb:,.2f}",
                f"{file.used_mb:,.2f}",
                f"{file.free_mb:,.2f}",
            ]

            for col, value in enumerate(values):
                cell = ctk.CTkLabel(
                    table, text=value,
                    font=Theme.font(size=12), text_color=Theme.TEXT,
                    anchor="e" if col in numeric_cols else "w",
                )
                cell.grid(
                    row=r, column=col, sticky="ew",
                    padx=14, pady=(8, 14 if is_last else 8),
                )

            shrink_button = ctk.CTkButton(
                table, text="Shrink", width=82, height=26,
                font=Theme.font(size=11),
                fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
                command=lambda f=file, index=r - 2: on_shrink(f, index),
            )
            shrink_button.grid(
                row=r, column=4, sticky="e",
                padx=(0, 14), pady=(8, 14 if is_last else 8),
            )
            Tooltip(shrink_button, "Reduz o tamanho físico do arquivo. Requer permissão db_owner ou sysadmin.")

        return row + 1

    def shrink_log(self, log_file, index):
        self._confirm_shrink(
            "Shrink do arquivo de Log", log_file,
            lambda: self.service.shrink_log(index),
        )

    def shrink_data(self, data_file, index):
        self._confirm_shrink(
            "Shrink do arquivo de Dados", data_file,
            lambda: self.service.shrink_data(index),
        )

    # ==========================================================
    # DIÁLOGO — OPERAÇÃO DESTRUTIVA (TRUNCATE / DELETE)
    # ==========================================================

    def _confirm_danger(self, title, table_name, description, hint, run, operation):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("480x320")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Theme.BG_CONTENT)

        dialog.transient(self)
        dialog.grab_set()

        icon_label = ctk.CTkLabel(
            dialog, text="⚠ Operação irreversível",
            font=Theme.font(size=15, weight="bold"), text_color=Theme.DANGER,
            wraplength=420, justify="left",
        )
        icon_label.pack(padx=25, pady=(22, 10), anchor="w")

        description_label = ctk.CTkLabel(
            dialog, text=description,
            font=Theme.font(size=13), wraplength=420, justify="left",
        )
        description_label.pack(padx=25, pady=(0, 10), anchor="w", fill="x")

        table_box = ctk.CTkLabel(
            dialog, text=table_name,
            font=Theme.font(size=13, weight="bold"), text_color=Theme.TEXT,
            fg_color=Theme.SURFACE, corner_radius=6,
            wraplength=420, justify="left",
        )
        table_box.pack(padx=25, pady=(0, 12), fill="x", ipady=8)

        hint_label = ctk.CTkLabel(
            dialog, text=f"💡 {hint}",
            font=Theme.font(size=11), text_color=Theme.TEXT_MUTED,
            wraplength=420, justify="left",
        )
        hint_label.pack(padx=25, pady=(0, 18), anchor="w", fill="x")

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(pady=(0, 20))

        def confirm():
            try:
                run()
                dialog.destroy()
                self.load()

                self._show_result(
                    title=f"{operation} concluído",
                    rows=[
                        ("Operação", operation),
                        ("Tabela", table_name),
                    ],
                )

            except Exception as error:
                dialog.destroy()
                self._show_error(
                    f"Não foi possível executar a operação.\n\n{error}"
                )

        ctk.CTkButton(
            buttons, text="Cancelar",
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=dialog.destroy,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons, text="Confirmar",
            fg_color=Theme.DANGER, hover_color=Theme.DANGER_HOVER,
            command=confirm,
        ).pack(side="left", padx=5)

    # ==========================================================
    # DIÁLOGO — SHRINK
    # ==========================================================

    def _confirm_shrink(self, title, file, action):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("480x380")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Theme.BG_CONTENT)

        dialog.transient(self)
        dialog.grab_set()

        icon_label = ctk.CTkLabel(
            dialog, text="⚠ Atenção",
            font=Theme.font(size=15, weight="bold"), text_color=Theme.DANGER,
            wraplength=420, justify="left",
        )
        icon_label.pack(padx=25, pady=(22, 10), anchor="w")

        description_label = ctk.CTkLabel(
            dialog,
            text=(
                "Executar SHRINK no arquivo abaixo? O SQL Server determinará "
                "o menor tamanho possível, o que pode gerar fragmentação."
            ),
            font=Theme.font(size=13), wraplength=420, justify="left",
        )
        description_label.pack(padx=25, pady=(0, 10), anchor="w", fill="x")

        file_box = ctk.CTkLabel(
            dialog, text=file.logical_name,
            font=Theme.font(size=13, weight="bold"), text_color=Theme.TEXT,
            fg_color=Theme.SURFACE, corner_radius=6,
            wraplength=420, justify="left",
        )
        file_box.pack(padx=25, pady=(0, 12), fill="x", ipady=8)

        impact_label = ctk.CTkLabel(
            dialog,
            text=(
                f"Tamanho atual : {file.size_mb:,.2f} MB\n"
                f"Em uso : {file.used_mb:,.2f} MB\n"
                f"Estimativa recuperável : até {file.free_mb:,.2f} MB"
            ),
            font=Theme.font(size=12), text_color=Theme.TEXT, justify="left",
        )
        impact_label.pack(padx=25, pady=(0, 12), anchor="w")

        permission_label = ctk.CTkLabel(
            dialog,
            text=(
                "💡 O valor recuperado real pode ser menor que a estimativa. "
                "É necessário que o usuário do banco tenha a permissão "
                "db_owner ou sysadmin para executar o SHRINK."
            ),
            font=Theme.font(size=11), text_color=Theme.TEXT_MUTED,
            wraplength=420, justify="left",
        )
        permission_label.pack(padx=25, pady=(0, 18), anchor="w", fill="x")

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(pady=(0, 20))

        def confirm():
            try:
                result = action()
                dialog.destroy()
                self.load()

                footer = None
                if result.recovered_mb <= 0:
                    footer = (
                        "O arquivo já estava no menor tamanho possível — "
                        "nenhum espaço foi recuperado."
                    )

                self._show_result(
                    title="SHRINK concluído",
                    rows=[
                        ("Arquivo", result.logical_name),
                        ("Antes", f"{result.before_mb:.2f} MB"),
                        ("Depois", f"{result.after_mb:.2f} MB"),
                        ("Recuperado", f"{result.recovered_mb:.2f} MB"),
                    ],
                    footer=footer,
                )

            except Exception as error:
                dialog.destroy()
                self._show_error(
                    f"Não foi possível executar o SHRINK.\n\n"
                    f"Verifique se o usuário do banco possui a permissão "
                    f"db_owner ou sysadmin.\n\n{error}"
                )

        ctk.CTkButton(
            buttons, text="Cancelar",
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=dialog.destroy,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons, text="Executar",
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=confirm,
        ).pack(side="left", padx=5)

    # ==========================================================
    # MENSAGENS DE RESULTADO
    # ==========================================================

    def _show_info(self, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Resultado")
        dialog.geometry("420x240")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Theme.BG_CONTENT)

        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=message,
            font=Theme.font(size=13), wraplength=360, justify="left",
        ).pack(padx=30, pady=(30, 15))

        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=(0, 20))

    def _show_error(self, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Erro")
        dialog.geometry("420x260")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Theme.BG_CONTENT)

        dialog.transient(self)
        dialog.grab_set()

        icon_label = ctk.CTkLabel(
            dialog, text="✕",
            font=Theme.font(size=24, weight="bold"),
            text_color=Theme.DANGER,
            fg_color=Theme.SURFACE,
            width=52, height=52, corner_radius=26,
        )
        icon_label.pack(pady=(25, 10))

        ctk.CTkLabel(
            dialog, text=message, text_color=Theme.TEXT,
            font=Theme.font(size=13), wraplength=360, justify="left",
        ).pack(padx=30, pady=(0, 15))

        ctk.CTkButton(
            dialog, text="OK",
            fg_color=Theme.DANGER, hover_color=Theme.DANGER_HOVER,
            command=dialog.destroy,
        ).pack(pady=(0, 20))
        
    def _show_result(self, title, rows, footer=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Resultado")
        dialog.geometry(f"420x{220 + len(rows) * 26}")
        dialog.resizable(False, False)
        dialog.configure(fg_color=Theme.BG_CONTENT)

        dialog.transient(self)
        dialog.grab_set()

        icon_label = ctk.CTkLabel(
            dialog, text="✓",
            font=Theme.font(size=28, weight="bold"),
            text_color=Theme.SUCCESS,
            fg_color=Theme.SURFACE,
            width=52, height=52, corner_radius=26,
        )
        icon_label.pack(pady=(25, 10))

        ctk.CTkLabel(
            dialog, text=title,
            font=Theme.font(size=16, weight="bold"), text_color=Theme.TEXT,
        ).pack(pady=(0, 15))

        rows_frame = ctk.CTkFrame(dialog, fg_color=Theme.SURFACE, corner_radius=8)
        rows_frame.pack(padx=30, pady=(0, 10), fill="x")
        rows_frame.grid_columnconfigure(0, weight=0)
        rows_frame.grid_columnconfigure(1, weight=1)

        for i, (label, value) in enumerate(rows):
            ctk.CTkLabel(
                rows_frame, text=label,
                font=Theme.font(size=12), text_color=Theme.TEXT_MUTED,
            ).grid(row=i, column=0, sticky="w", padx=(14, 10), pady=6)

            ctk.CTkLabel(
                rows_frame, text=str(value),
                font=Theme.font(size=12, weight="bold"), text_color=Theme.TEXT,
            ).grid(row=i, column=1, sticky="e", padx=(0, 14), pady=6)

        if footer:
            ctk.CTkLabel(
                dialog, text=footer,
                font=Theme.font(size=11), text_color=Theme.TEXT_MUTED,
                wraplength=360, justify="left",
            ).pack(padx=30, pady=(0, 10), anchor="w")

        ctk.CTkButton(
            dialog, text="OK",
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=dialog.destroy,
        ).pack(pady=(5, 20))