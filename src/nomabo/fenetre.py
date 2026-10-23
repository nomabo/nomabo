import customtkinter as ctk


def ouvrir_fenetre(titre="nomabo"):
    app = ctk.CTk()
    app.title(titre)
    app.geometry("400x200")

    label = ctk.CTkLabel(app, text="Bonjour depuis nomabo !")
    label.pack(pady=20)

    bouton = ctk.CTkButton(app, text="Fermer", command=app.destroy)
    bouton.pack()

    app.mainloop()