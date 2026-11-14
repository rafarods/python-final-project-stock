import tkinter
import tkinter.messagebox
import tkinter.simpledialog
import tkinter.ttk
import config
import traceback
import modules.dao.user_dao as user_dao
import modules.utils as utils

def show(parent: tkinter.Tk, current_user: dict) -> None:
    """
    Ventana para editar un usuario.
    """

    def reset() -> None:
        """
        Limpia los campos del formulario.
        """
        username_entry.config(state="normal")
        username_entry.delete(0, tkinter.END)
        username_entry.config(state="readonly")
        role_combo.current(0)
        can_change_password_var.set(True)
        password_entry.config(state="normal")
        password_entry.delete(0, tkinter.END)
        confirm_password_entry.config(state="normal")
        confirm_password_entry.delete(0, tkinter.END)
        search_button.focus_set()

    def load_user(user: dict) -> None:
        """
        Llena el formulario.
        """
        username_entry.config(state="normal")
        username_entry.delete(0, tkinter.END)
        username_entry.insert(0, user["username"])
        username_entry.config(state="readonly")
        if user.get("role") == config.ROLE_ADMIN:
            role_combo.set("Administrador")
        else:
            role_combo.set("Usuario")
        can_change_password_var.set(bool(user["can_change_password"]))
        password_entry.config(state="normal")
        password_entry.delete(0, tkinter.END)
        confirm_password_entry.config(state="normal")
        confirm_password_entry.delete(0, tkinter.END)
        print(f"{user.get("username")} == {current_user.get("username")}")
        if user.get("username") == current_user.get("username"):
            password_entry.config(state="disabled")
            confirm_password_entry.config(state="disabled")
        else:
            password_entry.focus_set()

    def search_user() -> None:
        """
        Abre una ventana para buscar el nombre de usuario.
        """
        username: str | None = tkinter.simpledialog.askstring("Buscar usuario", "Usuario:", parent=window)
        if not username:
            return
        username = username.strip()
        if not username:
            return
        user: dict | None = user_dao.find_one(username)
        if user is None:
            tkinter.messagebox.showwarning("Buscar usuario", f"No existe el nombre de usuario: {username}", parent=window)
            return
        if user.get("username") == config.ADMIN.get("username"):
            tkinter.messagebox.showerror("Buscar usuario", f"El usuario '{username}' está restringido.", parent=window)
            return
        load_user(user)
    
    def update_user() -> None:
        """
        Actualiza los datos del usuario.
        """
        username: str = username_entry.get()
        role: str = role_combo.get()
        can_change_password: bool = can_change_password_var.get()
        if not username:
            tkinter.messagebox.showwarning("Editar usuario", "Debe seleccionar un usuario.", parent=window)
            return
        if not role:
            tkinter.messagebox.showwarning("Editar usuario", "Seleccione el rol.", parent=window)
            role_combo.focus_set()
            return
        if not user_dao.exist(username):
            tkinter.messagebox.showwarning("Editar usuario", "Usuario no existe.", parent=window)
            return
        if role == "Administrador":
            role_user = config.ROLE_ADMIN
        else:
            role_user = config.ROLE_USER
        # Datos a actualizar
        data: dict = {"role": role_user, "can_change_password": can_change_password}
        if username != current_user.get("username"):
            password: str = password_entry.get()
            confirm_password: str = confirm_password_entry.get()
            if password or confirm_password:
                if not password:
                    tkinter.messagebox.showwarning("Editar usuario", "Ingrese la nueva contraseña.", parent=window)
                    password_entry.focus_set()
                    return
                if not confirm_password:
                    tkinter.messagebox.showwarning("Editar usuario", "Confirme la nueva contraseña.", parent=window)
                    confirm_password_entry.focus_set()
                    return
                if password != confirm_password:
                    tkinter.messagebox.showwarning("Editar usuario", "Las contraseñas no coinciden.", parent=window)
                    confirm_password_entry.focus_set()
                    return
            data["password"] = password
        try:
            result: int | None = user_dao.update(username, data)
            if result is None or result <= 0:
                raise RuntimeError(f"Falló la actualización del usuario: {username}")
            tkinter.messagebox.showinfo("Editar usuario", f"Usuario '{username}' actualizado correctamente.", parent=window)
            reset()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Editar usuario", "Ocurrió un error al actualizar el usuario.", parent=window)

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.title("Editar usuario")
    window.resizable(False, False)
    window.transient(parent)
    window.grab_set()

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=25, pady=20)
    frame.columnconfigure(1, weight=1)
    tkinter.Label(frame, text="Editar usuario", font=("Arial", 14, "bold")).grid( row=0, column=0, columnspan=3, pady=(0, 18) )
    tkinter.Label(frame, text="Usuario:").grid( row=1, column=0, sticky="w", padx=(0, 10), pady=4)

    username_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    username_entry.grid(row=1, column=1, sticky="ew", pady=4)
    
    search_button: tkinter.Button = tkinter.Button(frame, text="Buscar", width=8, command=search_user)
    search_button.grid(row=1, column=2, padx=(5, 0), pady=4)

    tkinter.Label(frame, text="Rol:" ).grid( row=2, column=0, sticky="w", padx=(0, 10), pady=4)
    role_combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(frame, values=("Usuario", "Administrador"), state="readonly")
    role_combo.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)
    role_combo.current(0)
    
    can_change_password_var: tkinter.BooleanVar = tkinter.BooleanVar(value=True)
    tkinter.Checkbutton(frame, text="Puede cambiar su contraseña", variable=can_change_password_var ).grid( row=3, column=0, columnspan=3, sticky="w", pady=8)
    
    separator: tkinter.ttk.Separator = tkinter.ttk.Separator(frame, orient="horizontal")
    separator.grid( row=4, column=0, columnspan=3, sticky="ew", pady=(8, 12) )
    
    tkinter.Label(frame, text="Nueva contraseña:").grid(row=5, column=0, sticky="w", padx=(0, 10), pady=4)
    password_entry: tkinter.Entry = tkinter.Entry(frame, show="*")
    password_entry.grid(row=5, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Confirmar contraseña:" ).grid(row=6, column=0, sticky="w", padx=(0, 10), pady=4)
    confirm_password_entry: tkinter.Entry = tkinter.Entry(frame, show="*")
    confirm_password_entry.grid(row=6, column=1, columnspan=2, sticky="ew", pady=4)

    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=7, column=0, columnspan=3, pady=(12, 0))

    tkinter.Button(button_frame, text="Guardar", width=10, command=update_user).pack(side="left", padx=5)
    tkinter.Button(button_frame, text="Cancelar", width=10, command=window.destroy).pack( side="left", padx=5)

    window.bind("<Return>", lambda event: update_user())
    window.bind("<Escape>", lambda event: window.destroy())
    window.bind("<Control-f>", lambda event: search_user())

    utils.center_window(window, 440, 320)
    window.after_idle(search_button.focus_set)