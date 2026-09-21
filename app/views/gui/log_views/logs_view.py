from datetime import datetime

from app.views.gui.theme import Theme
from app.utils.audit_logger import LOG_DIR

import customtkinter as ctk

class LogsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self._matches = []
        self._match_index = -1

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._create_header()
        self._create_search_bar()
        self._create_textbox()

        self.load_available_dates()
        self.load_log()

    # ==========================================================
    # HEADER
    # ==========================================================

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header, text="Logs",
            font=Theme.font(size=20, weight="bold"), text_color=Theme.TEXT,
        )
        title.grid(row=0, column=0, sticky="w")

        self.date_menu = ctk.CTkOptionMenu(
            header, values=["-"], width=160,
            fg_color=Theme.SURFACE, button_color=Theme.SURFACE,
            button_hover_color=Theme.BORDER, text_color=Theme.TEXT,
            dropdown_fg_color=Theme.SURFACE,
            command=self._on_date_selected,
        )
        self.date_menu.grid(row=0, column=2, padx=(10, 10))

        copy_button = ctk.CTkButton(
            header, text="Copiar tudo", width=110, height=30,
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=self.copy_all,
        )
        copy_button.grid(row=0, column=3, padx=(0, 10))

        refresh_button = ctk.CTkButton(
            header, text="⟳  Atualizar", width=110, height=30,
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=self.load_log,
        )
        refresh_button.grid(row=0, column=4)

    # ==========================================================
    # BARRA DE BUSCA
    # ==========================================================

    def _create_search_bar(self):
        search_bar = ctk.CTkFrame(self, fg_color="transparent")
        search_bar.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 10))
        search_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_bar, placeholder_text="Buscar no log (Ctrl+F)...",
            height=32, fg_color=Theme.SURFACE, border_color=Theme.BORDER,
            text_color=Theme.TEXT,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.search_entry.bind("<Return>", lambda event: self.find_next())
        self.search_entry.bind("<KeyRelease>", lambda event: self._search())

        self.match_label = ctk.CTkLabel(
            search_bar, text="", font=Theme.font(size=11),
            text_color=Theme.TEXT_MUTED, width=60,
        )
        self.match_label.grid(row=0, column=1, padx=(0, 8))

        prev_button = ctk.CTkButton(
            search_bar, text="◀", width=32, height=32,
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=self.find_previous,
        )
        prev_button.grid(row=0, column=2, padx=(0, 4))

        next_button = ctk.CTkButton(
            search_bar, text="▶", width=32, height=32,
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=self.find_next,
        )
        next_button.grid(row=0, column=3)

    # ==========================================================
    # TEXTO DO LOG
    # ==========================================================

    def _create_textbox(self):
        self.textbox = ctk.CTkTextbox(
            self, fg_color=Theme.CARD, text_color=Theme.TEXT,
            border_width=1, border_color=Theme.BORDER,
            font=("Consolas", 12), wrap="none",
        )
        self.textbox.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 20))

        # CTkTextbox não expõe busca própria — usamos o widget tk.Text
        # interno (padrão comum com customtkinter) para tags/realce.
        self._text = self.textbox._textbox
        self._text.tag_config("highlight", background=Theme.ACCENT, foreground=Theme.TEXT)
        self._text.tag_config("highlight_current", background=Theme.SUCCESS, foreground=Theme.BG_CONTENT)

        self._text.bind("<Control-f>", lambda event: self._focus_search())

    def _focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, "end")
        return "break"

    # ==========================================================
    # ARQUIVOS DE LOG (um por dia)
    # ==========================================================

    def load_available_dates(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        files = sorted(LOG_DIR.glob("logwatcher_audit_*.log"), reverse=True)
        dates = [f.stem.replace("logwatcher_audit_", "") for f in files]

        if not dates:
            dates = [datetime.now().strftime("%Y-%m-%d")]

        self.date_menu.configure(values=dates)
        self.date_menu.set(dates[0])

    def _on_date_selected(self, _value):
        self.load_log()

    def load_log(self):
        date = self.date_menu.get()
        log_path = LOG_DIR / f"logwatcher_audit_{date}.log"

        self._text.configure(state="normal")
        self._text.delete("1.0", "end")

        if log_path.exists():
            content = log_path.read_text(encoding="utf-8")
            self._text.insert("1.0", content or "Arquivo de log vazio.")
        else:
            self._text.insert("1.0", "Nenhum log encontrado para essa data.")

        self._text.configure(state="disabled")
        self._matches = []
        self._match_index = -1
        self.match_label.configure(text="")

    # ==========================================================
    # COPIAR
    # ==========================================================

    def copy_all(self):
        content = self._text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)

    # ==========================================================
    # BUSCA
    # ==========================================================

    def _search(self):
        term = self.search_entry.get()

        self._text.tag_remove("highlight", "1.0", "end")
        self._text.tag_remove("highlight_current", "1.0", "end")
        self._matches = []
        self._match_index = -1

        if not term:
            self.match_label.configure(text="")
            return

        start = "1.0"
        while True:
            pos = self._text.search(term, start, stopindex="end", nocase=True)
            if not pos:
                break

            end = f"{pos}+{len(term)}c"
            self._text.tag_add("highlight", pos, end)
            self._matches.append((pos, end))
            start = end

        if self._matches:
            self._match_index = 0
            self._highlight_current()
        else:
            self.match_label.configure(text="0/0")

    def _highlight_current(self):
        self._text.tag_remove("highlight_current", "1.0", "end")

        pos, end = self._matches[self._match_index]
        self._text.tag_add("highlight_current", pos, end)
        self._text.see(pos)

        self.match_label.configure(text=f"{self._match_index + 1}/{len(self._matches)}")

    def find_next(self):
        if not self._matches:
            self._search()
            return

        self._match_index = (self._match_index + 1) % len(self._matches)
        self._highlight_current()

    def find_previous(self):
        if not self._matches:
            self._search()
            return

        self._match_index = (self._match_index - 1) % len(self._matches)
        self._highlight_current()