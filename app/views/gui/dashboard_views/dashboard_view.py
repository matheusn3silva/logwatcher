import customtkinter as ctk

from app.views.gui.theme import Theme

class DashboardView(ctk.CTkFrame):
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
            text=f"Dashboard — {self.profile.name}",
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

        if not self.profile.tables:
            self._show_message(
                "Nenhuma tabela de monitoramento está configurada "
                "neste perfil.\nEdite o perfil para adicionar tabelas."
            )
            return

        if self.service is None:
            self._show_message(
                "Este perfil não está conectado.", is_error=True
            )
            return

        self._show_message("Carregando dados do banco...", row=0)
        self.update_idletasks()

        try:
            tables_text = ",".join(self.profile.tables)
            self.summary = self.service.analyze_database(tables_text)

        except Exception as error:
            self._clear_scroll()
            self._show_message(
                f"Não foi possível consultar o Dashboard.\n"
                f"Motivo: {error}",
                is_error=True,
            )
            return

        self._clear_scroll()

        row = self._render_summary_cards(row=0)
        row = self._render_table_section(
            row,
            title="Arquivos de Log",
            headers=["Arquivo", "Tamanho (MB)", "Usado (MB)", "Livre (MB)"],
            rows=[
                [
                    log.logical_name,
                    f"{log.size_mb:,.2f}",
                    f"{log.used_mb:,.2f}",
                    f"{log.free_mb:,.2f}",
                ]
                for log in self.summary.logs
            ],
            numeric_cols={1, 2, 3},
            empty_text="Nenhum arquivo de log encontrado.",
        )
        self._render_table_section(
            row,
            title="Tabelas Monitoradas",
            headers=["Tabela", "Schema", "Linhas", "Espaço (MB)", "Usado (MB)"],
            rows=[
                [
                    table.name,
                    table.schema,
                    f"{table.rows:,}".replace(",", "."),
                    f"{table.total_mb:,.2f}",
                    f"{table.used_mb:,.2f}",
                ]
                for table in self.summary.tables
            ],
            numeric_cols={2, 3, 4},
            empty_text="Nenhuma tabela encontrada.",
        )

    # ==========================================================
    # MENSAGEM (vazio / erro / carregando)
    # ==========================================================

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
    # CARDS DE RESUMO
    # ==========================================================

    def _render_summary_cards(self, row):
        cards_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cards_frame.grid(row=row, column=0, sticky="ew", pady=(0, 20))

        for col in range(3):
            cards_frame.grid_columnconfigure(col, weight=1, uniform="cards")

        stats = [
            ("Tabelas monitoradas", f"{self.summary.total_tables}"),
            ("Total de linhas", f"{self.summary.total_rows:,}".replace(",", ".")),
            ("Espaço das tabelas", f"{self.summary.total_space_mb:,.2f} MB"),
            ("Espaço utilizado", f"{self.summary.used_space_mb:,.2f} MB"),
            ("Tamanho do log", f"{self.summary.total_log_size_mb:,.2f} MB"),
            ("Log utilizado", f"{self.summary.total_log_used_mb:,.2f} MB"),
        ]

        for index, (label_text, value_text) in enumerate(stats):
            grid_row, grid_col = divmod(index, 3)

            card = ctk.CTkFrame(
                cards_frame,
                fg_color=Theme.CARD,
                corner_radius=10,
                border_width=1,
                border_color=Theme.BORDER,
            )
            card.grid(
                row=grid_row, column=grid_col,
                sticky="ew", padx=6, pady=6,
            )
            card.grid_columnconfigure(0, weight=1)

            value_label = ctk.CTkLabel(
                card,
                text=value_text,
                font=Theme.font(size=19, weight="bold"),
                text_color=Theme.TEXT,
                anchor="w",
            )
            value_label.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 0))

            title_label = ctk.CTkLabel(
                card,
                text=label_text,
                font=Theme.font(size=11),
                text_color=Theme.TEXT_MUTED,
                anchor="w",
            )
            title_label.grid(row=1, column=0, sticky="w", padx=16, pady=(2, 14))

        return row + 1

    # ==========================================================
    # TABELAS (log files / tabelas monitoradas)
    # ==========================================================

    def _render_table_section(self, row, title, headers, rows, numeric_cols, empty_text):
        wrapper = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            wrapper,
            text=title,
            font=Theme.font(size=14, weight="bold"),
            text_color=Theme.TEXT,
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        table = ctk.CTkFrame(
            wrapper,
            fg_color=Theme.CARD,
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER,
        )
        table.grid(row=1, column=0, sticky="ew")

        for col in range(len(headers)):
            table.grid_columnconfigure(col, weight=1)

        for col, header_text in enumerate(headers):
            header_label = ctk.CTkLabel(
                table,
                text=header_text,
                font=Theme.font(size=11, weight="bold"),
                text_color=Theme.TEXT_MUTED,
                anchor="e" if col in numeric_cols else "w",
            )
            header_label.grid(
                row=0, column=col, sticky="ew",
                padx=14, pady=(12, 8),
            )

        divider = ctk.CTkFrame(table, height=1, fg_color=Theme.BORDER)
        divider.grid(row=1, column=0, columnspan=len(headers), sticky="ew", padx=14)

        if not rows:
            empty_label = ctk.CTkLabel(
                table,
                text=empty_text,
                font=Theme.font(size=12),
                text_color=Theme.TEXT_MUTED,
            )
            empty_label.grid(
                row=2, column=0, columnspan=len(headers),
                sticky="w", padx=14, pady=(10, 14),
            )
            return row + 1

        for r, row_values in enumerate(rows, start=2):
            is_last = r == len(rows) + 1

            for col, value in enumerate(row_values):
                cell = ctk.CTkLabel(
                    table,
                    text=value,
                    font=Theme.font(size=12),
                    text_color=Theme.TEXT,
                    anchor="e" if col in numeric_cols else "w",
                )
                cell.grid(
                    row=r, column=col, sticky="ew",
                    padx=14, pady=(8, 14 if is_last else 8),
                )

        return row + 1