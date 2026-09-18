import customtkinter as ctk

from app.services.connection_profile_service import ConnectionProfileService

class ProfileListWidget(ctk.CTkFrame):
    def __init__(self, master, on_select=None):
        super().__init__(master)
        
        self._service = ConnectionProfileService()
        self._on_select = on_select
        self._profiles = []
        
        self._build()
        self.refresh()
        
    def _build(self):
        ctk.CTkLabel(
            self,
            text="Perfis de conexão",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(pady=(10, 20))
        
        self.list_frame = ctk.CTkScrollableFrame(self)
        
        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )
    
    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        self._profiles = self._service.load_profiles()
        
        for profile in self._profiles:
            
            button = ctk.CTkButton(
                self.list_frame,
                text=profile.name,
                anchor="w",
                command=lambda p=profile: self._select_profile(p)
            )
            
            button.pack(
                fill="x", 
                pady=4
            )
        
    def _select_profile(self, profile):
        if self._on_select:
            self._on_select(profile)