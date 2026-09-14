import customtkinter as ctk

ctk.set_appearance_mode("System")

app = ctk.CTk()
app.title("LogWatcher")
app.geometry("500x300")

label = ctk.CTkLabel(app, text="Ambiente configurado!")
label.pack(pady=50)

app.mainloop()