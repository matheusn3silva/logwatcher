import customtkinter as ctk

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LogWatcher")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self._configure_grid()
        self._create_sidebar()
        self._create_content()

    # CONFIGURAÇÃO
    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)

    # MENU LATERAL
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

    # CONTEÚDO
    def _create_content(self):
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self.content,
            text="CONTEUDO",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")

        self.content_label = ctk.CTkLabel(
            self.content,
            text="Selecione uma opção no menu.",
            font=ctk.CTkFont(
                size=16
            )
        )
        self.content_label.grid(row=1, column=0)

    # NAVEGAÇÃO
    def _set_content(self, title, message):
        self.title_label.configure(text=title)
        self.content_label.configure(text=message)

    def show_dashboard(self):
        self._set_content("Dashboard", "Dashboard será implementado aqui")

    def show_profiles(self):
        self._set_content("Perfis de Conexão", "Gerenciamento de perfis será implementado aqui")

    def show_maintenance(self):
        self._set_content("Maintenance", "Operações de manutenção serão implementados aqui")

def run():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    run()