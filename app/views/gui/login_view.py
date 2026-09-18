import customtkinter as ctk
from app.interfaces.gui.widgets.profile_list_widget import ProfileListWidget

class LoginView(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("LogWatcher")
        self.geometry("1000x650")
        self.minsize(900, 600)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # SIDEBAR
        self.sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0
        )
        
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        
        self.sidebar.grid_propagate(False)
        
        ctk.CTkLabel(
            self.sidebar,
            text="LogWatcher",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        ).pack(pady=(30, 20))
        
        self.profile_list = ProfileListWidget(
            self.sidebar,
            on_select=self.on_profile_selected
        )
        
        self.profile_list.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )
        
        # CONTENT
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0
        )
        
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew"
        )
        
        ctk.CTkLabel(
            self.content,
            text="Selecionar Perfil de Conexão",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).pack(pady=40)
        
    def on_profile_selected(self, profile):
        print(f"Perfil selecionado: {profile.name}")
        
        