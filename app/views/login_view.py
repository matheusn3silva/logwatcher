import customtkinter as ctk

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
        
        