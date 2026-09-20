import customtkinter as ctk
from app.views.gui.profiles_view import ProfilesView
from app.services.connection_manager import ConnectionManager

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LogWatcher")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.connection_manager = ConnectionManager()
        self.active_profile = None

        self._configure_grid()
        self._create_sidebar()
        self._create_content()

        self.current_view = None

    # ==========================================================
    # CONFIGURAÇÃO
    # ==========================================================
    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)

    # ==========================================================
    # MENU LATERAL
    # ==========================================================
    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)

        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="LogWatcher",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        self.profile_button = ctk.CTkButton(
            self.sidebar,
            text="Perfis de conexões",
            command=self.show_profiles
        )
        self.profile_button.grid(row=1, column=0, padx=20, pady=10)

        self.dashboard_button = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            command=self.show_dashboard
        )
        self.dashboard_button.grid(row=2, column=0, padx=20, pady=10)

        self.maintenance_button = ctk.CTkButton(
            self.sidebar,
            text="Manutenção",
            command=self.show_maintenance
        )
        self.maintenance_button.grid(row=3, column=0, padx=20, pady=10)

        self.exit_button = ctk.CTkButton(
            self.sidebar,
            text="Sair",
            command=self.destroy
        )
        self.exit_button.grid(row=6, column=0, padx=20, pady=(10, 20))

    # ==========================================================
    # CONTEÚDO
    # ==========================================================
    def _create_content(self):
        self.content = ctk.CTkFrame(
            self, 
            corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.show_dashboard()

    # ==========================================================
    # NAVEGAÇÃO
    # ==========================================================
    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        self.current_view = None

    def show_dashboard(self):
        self._clear_content()

        label = ctk.CTkLabel(
            self.content,
            text="Dashboard",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        )
        label.grid(row=0, column=0, padx=30, pady=30, sticky="nw")

    def show_profiles(self):
        self._clear_content()

        self.current_view = ProfilesView(
            self.content,
            self.connection_manager,
            self.on_profile_selected
        )

        self.current_view.grid(row=0, column=0, sticky="nsew")

    def on_profile_selected(self, profile):
        self.active_profile = profile

        print(f"Perfil ativo: {profile.name}")

    def show_maintenance(self):
        self._clear_content()

        label = ctk.CTkLabel(
            self.content,
            text="Manutenção",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        )
        label.grid(row=0, column=0, padx=30, pady=30, sticky="nw")

    

def run():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    run()