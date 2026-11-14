import tkinter
import tkinter.messagebox
import config
import modules.utils as utils
import modules.dao.user_dao as user_dao

def show(parent: tkinter.Misc, username: str) -> None:
    """
    Ventana para cambiar la contraseña del usuario.
    """
    
    def change_password() -> None:
        """
        Validación del cambio contraseña del usuario
        """
        current_password = current_entry.get()
        new_password = new_entry.get()
        confirm_password = confirm_entry.get()
        if not current_password or not new_password or not confirm_password:
            tkinter.messagebox.showwarning("Cambiar contraseña", "Debe completar todos los campos.", parent=window)
            current_entry.focus_set()
            return
        new_password = new_password.strip()
        if new_password == "":
            tkinter.messagebox.showwarning("Cambiar contraseña", "No se permite contraseñas en blanco.", parent=window)
            new_entry.focus_set()
            return
        if len(new_password) < config.PASSWD_MIN_LEN:
            tkinter.messagebox.showwarning("Cambiar contraseña", f"La contraseña debe tener {config.PASSWD_MIN_LEN} o más caracteres.", parent=window)
            new_entry.focus_set()
            return
        if new_password != confirm_password.strip():
            tkinter.messagebox.showwarning("Cambiar contraseña", "Las nuevas contraseñas no coinciden.", parent=window)
            new_entry.focus_set()
            return
        if current_password == new_password:
            tkinter.messagebox.showwarning("Cambiar contraseña", "La nueva contraseña puede ser igual a la actual.", parent=window)
            new_entry.focus_set()
            return
        if not user_dao.check_password(username, current_password):
            tkinter.messagebox.showerror("Cambiar contraseña", "La contraseña actual es incorrecta.", parent=window)
            current_entry.focus_set()
            return
        user_dao.change_password(username, new_password)
        tkinter.messagebox.showinfo("Cambiar contraseña", "Contraseña modificada correctamente.", parent=window)
        window.destroy()

    window = tkinter.Toplevel(parent)
    window.title("Cambiar contraseña")
    window.resizable(False, False)
    window.transient(parent)
    window.grab_set()

    tkinter.Label(window, text="Contraseña actual:").grid(row=0, column=0, padx=(15, 8), pady=(12, 5), sticky="e")
    current_entry = tkinter.Entry(window, show="*", width=30)
    current_entry.grid(row=0, column=1, padx=(0, 15), pady=(12, 5))

    tkinter.Label(window, text="Nueva contraseña:").grid(row=1, column=0, padx=(15, 8), pady=5, sticky="e")
    new_entry = tkinter.Entry(window, show="*", width=30)
    new_entry.grid(row=1, column=1, padx=(0, 15), pady=5)

    tkinter.Label(window, text="Confirmar contraseña:").grid(row=2, column=0, padx=(15, 8), pady=5, sticky="e")
    confirm_entry = tkinter.Entry(window, show="*", width=30)
    confirm_entry.grid(row=2, column=1, padx=(0, 15), pady=5)

    button_frame = tkinter.Frame(window)
    button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 12))

    tkinter.Button(button_frame, text="Cambiar contraseña", command=change_password).pack(side="left", padx=4)
    tkinter.Button(button_frame, text="Cancelar", command=window.destroy).pack(side="left", padx=4)

    utils.center_window(window, 360, 160)

    current_entry.focus_set()
    window.bind("<Return>", lambda event: change_password())
    window.bind("<Escape>", lambda event: window.destroy())
    window.wait_window()