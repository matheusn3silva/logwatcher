import customtkinter as ctk
from pathlib import Path
import sys

from app.views.gui.profile_views.profiles_view import ProfilesView
from app.views.gui.dashboard_views.dashboard_view import DashboardView
from app.views.gui.maintenance_views.maintenance_view import MaintenanceView
from app.views.gui.theme import Theme
from app.views.gui import theme as theme_module
from app.services.connection_manager import ConnectionManager
from app.views.gui.log_views.logs_view import LogsView

class MainWindow(ctk.CTk):
    def __init__(self):
        theme_module.apply()

        super().__init__()
        
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
        icon = base / "assets" / "logo.ico"
        if icon.exists():
            try:
                self.after(250, lambda: self.iconbitmap(str(icon)))
            except Exception:
                pass

        self.configure(fg_color=Theme.BG_APP)

        self.title("LogWatcher")
        self.geometry("1100x700")
        self.minsize(950, 620)

        self.connection_manager = ConnectionManager()
        self.active_profile = None
        self.current_view = None

        self._configure_grid()
        self._create_sidebar()
        self._create_content()

    # ==========================================================
    # CONFIGURAÇÃO
    # ==========================================================

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=0)   
        self.grid_columnconfigure(1, weight=0)   
        self.grid_columnconfigure(2, weight=1) 
        self.grid_rowconfigure(0, weight=1)

    # ==========================================================
    # PERFIS - LADO ESQUERDO
    # ==========================================================

    def _create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=270,
            corner_radius=0,
            fg_color=Theme.BG_APP,
            border_width=0,
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)
        
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)

        self.divider = ctk.CTkFrame(
            self,
            width=1,
            corner_radius=0,
            fg_color=Theme.BORDER,
        )
        self.divider.grid(row=0, column=1, sticky="ns")

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="LogWatcher",
            font=Theme.font(
                size=24,
                weight="bold"
            )
        )

        self.logo_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(25, 20),
            sticky="w"
        )

        self.profiles_title = ctk.CTkLabel(
            self.sidebar,
            text="PERFIS DE CONEXÃO",
            font=Theme.font(size=12, weight="bold"),
            text_color=Theme.TEXT_MUTED,
        )

        self.profiles_title.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 10),
            sticky="w"
        )

        self.profiles_container = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        self.profiles_container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=10
        )

        self.profiles_container.grid_columnconfigure(
            0,
            weight=1
        )

        self.profiles_container.grid_rowconfigure(
            0,
            weight=1
        )

        self._create_profiles_view()

        self.new_profile_button = ctk.CTkButton(
            self.sidebar,
            text="+ Novo Perfil",
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            command=self.open_new_profile
        )

        self.new_profile_button.grid(
            row=3,
            column=0,
            padx=15,
            pady=15,
            sticky="ew"
        )

        self.exit_button = ctk.CTkButton(
            self.sidebar,
            text="Sair",
            fg_color=Theme.SURFACE,
            hover_color=Theme.BORDER,
            text_color=Theme.TEXT,
            command=self.destroy
        )

        self.exit_button.grid(
            row=4,
            column=0,
            padx=15,
            pady=(0, 20),
            sticky="ew"
        )

    # ==========================================================
    # PERFIS
    # ==========================================================

    def _create_profiles_view(self):
        self.profiles_view = ProfilesView(
            self.profiles_container,
            self.connection_manager,
            self.on_profile_selected,
            on_profile_disconnected=self.on_profile_disconnected,
        )

        self.profiles_view.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    def open_new_profile(self):

        self.profiles_view.open_create_dialog()

    # ==========================================================
    # CONTEÚDO DIREITO
    # ==========================================================

    def _create_content(self):
        self.content = ctk.CTkFrame(
            self, corner_radius=0, fg_color=Theme.BG_CONTENT,
        )
        self.content.grid(row=0, column=2, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self._create_content_navigation()
        self._create_empty_state()
        self._refresh_content()

    # ==========================================================
    # NAVEGAÇÃO DO CONTEÚDO
    # ==========================================================

    def _create_content_navigation(self):
        self.navigation = ctk.CTkFrame(self.content, fg_color="transparent")
        self.navigation.grid_columnconfigure(3, weight=1)

        self.dashboard_button = ctk.CTkButton(
            self.navigation, text="Dashboard", width=130,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=self.show_dashboard
        )
        self.dashboard_button.grid(row=0, column=0, padx=(0, 10))

        self.maintenance_button = ctk.CTkButton(
            self.navigation, text="Manutenção", width=130,
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=self.show_maintenance
        )
        self.maintenance_button.grid(row=0, column=1, padx=(0, 10))

        self.logs_button = ctk.CTkButton(
            self.navigation, text="Logs", width=130,
            fg_color=Theme.SURFACE, hover_color=Theme.BORDER, text_color=Theme.TEXT,
            command=self.show_logs
        )
        self.logs_button.grid(row=0, column=2)

    def _set_nav_active(self, button):
        for btn in (self.dashboard_button, self.maintenance_button, self.logs_button):
            is_active = btn is button
            btn.configure(
                fg_color=Theme.ACCENT if is_active else Theme.SURFACE,
                hover_color=Theme.ACCENT_HOVER if is_active else Theme.BORDER,
            )

    # ==========================================================
    # ÁREA PRINCIPAL
    # ==========================================================

    def _clear_content(self):
        for widget in self.content.winfo_children():
            if widget not in (self.navigation, self.empty_state):
                widget.destroy()
        self.current_view = None

    def _create_empty_state(self):
        self.empty_state = ctk.CTkFrame(self.content, fg_color="transparent")
        self.empty_state.grid_columnconfigure(0, weight=1)
        self.empty_state.grid_rowconfigure(0, weight=1)
        self.empty_state.grid_rowconfigure(2, weight=1)

        icon_label = ctk.CTkLabel(
            self.empty_state, text="⛁", font=Theme.font(size=42),
            text_color=Theme.TEXT_MUTED,
        )
        icon_label.grid(row=1, column=0)

        label = ctk.CTkLabel(
            self.empty_state, text="Nenhum perfil conectado",
            font=Theme.font(size=20, weight="bold"), text_color=Theme.TEXT,
        )
        label.grid(row=2, column=0, sticky="n", pady=(10, 4))

        hint = ctk.CTkLabel(
            self.empty_state,
            text="Conecte um perfil na barra lateral para ver o dashboard.",
            font=Theme.font(size=13), text_color=Theme.TEXT_MUTED,
        )
        hint.grid(row=3, column=0, sticky="n")

    def _refresh_content(self):
        if self.active_profile is None:
            self.navigation.grid_forget()
            self._clear_content()
            self.empty_state.grid(row=0, column=0, sticky="nsew")
            return

        self.empty_state.grid_forget()
        self.navigation.grid(
            row=0, column=0, sticky="ew", padx=20, pady=(15, 5)
        )
        self.show_dashboard()

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    def show_dashboard(self):
        self._clear_content()
        self._set_nav_active(self.dashboard_button)

        self.current_view = DashboardView(
            self.content,
            self.connection_manager,
            self.active_profile,
        )

        self.current_view.grid(row=1, column=0, sticky="nsew")

    # ==========================================================
    # MANUTENÇÃO
    # ==========================================================

    def show_maintenance(self):
        self._clear_content()
        self._set_nav_active(self.maintenance_button)

        self.current_view = MaintenanceView(
            self.content,
            self.connection_manager,
            self.active_profile,
        )

        self.current_view.grid(row=1, column=0, sticky="nsew")
        
    def show_logs(self):
        self._clear_content()
        self._set_nav_active(self.logs_button)

        self.current_view = LogsView(self.content)
        self.current_view.grid(row=1, column=0, sticky="nsew")

    # ==========================================================
    # PERFIL ATIVO
    # ==========================================================

    def on_profile_selected(self, profile):
        self.active_profile = profile
        self._refresh_content()

    def on_profile_disconnected(self, profile):
        if self.active_profile and self.active_profile.id == profile.id:
            self.active_profile = None
            self._refresh_content()
