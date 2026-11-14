import tkinter
import tkinter.messagebox
import tkinter.simpledialog
import config
import traceback
import modules.dao.user_dao as user_dao
import modules.utils as utils


def show(parent: tkinter.Tk, current_user: dict) -> None:
    """
    Ventana para eliminar un usuario.
    """

    def reset() -> None:
        """
        Limpia los campos del formulario.
        """
        username_var.set("")
        role_var.set("")
        can_change_password_var.set("")
        search_button.focus_set()

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
            tkinter.messagebox.showerror("Buscar usuario", f"El usuario '{username}' está restringido y no puede eliminarse.", parent=window)
            return
        if user.get("username") == current_user.get("username"): 
            tkinter.messagebox.showerror("Buscar usuario", "No puede eliminar el usuario de la sesión actual.", parent=window)
            return
        load_user(user)

    def load_user(user: dict) -> None:
        """
        Llena el formulario.
        """
        username_var.set(user["username"])
        if user.get("role") == config.ROLE_ADMIN:
            role_var.set("Administrador")
        else:
            role_var.set("Usuario")
        if bool(user.get("can_change_password")):
            can_change_password_var.set("Sí")
        else:
            can_change_password_var.set("No")
            
    def delete_user() -> None:
        """
        Elimina el usuario.
        """
        username: str = username_var.get()
        if not username:
            tkinter.messagebox.showwarning("Eliminar usuario", "Debe seleccionar un usuario.", parent=window)
            return
        if username == config.ADMIN.get("username"):
            tkinter.messagebox.showerror("Eliminar usuario", f"El usuario '{username}' está restringido y no puede eliminarse.", parent=window )
            reset()
            return
        if username == current_user.get("username"):
            tkinter.messagebox.showerror("Eliminar usuario", "No puede eliminar el usuario de la sesión actual.", parent=window)
            reset()
            return
        if not user_dao.exist(username):
            tkinter.messagebox.showwarning("Eliminar usuario", f"No existe el usuario: {username}", parent=window)
            reset()
            return
        confirm: bool = tkinter.messagebox.askyesno("Eliminar usuario", f"¿Está seguro que desea eliminar el usuario '{username}'?", parent=window )
        if not confirm:
            return
        try:
            result: int | None = user_dao.delete(username)
            if result is None or result <= 0:
                raise RuntimeError(f"Falló la eliminación del usuario: {username}")
            tkinter.messagebox.showinfo("Eliminar usuario", f"Usuario '{username}' fue eliminado correctamente.", parent=window)
            reset()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Eliminar usuario", "Ocurrió un error al eliminar el usuario.", parent=window)

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.title("Eliminar usuario")
    window.resizable(False, False)
    utils.center_window(window, 440, 210)
    window.transient(parent)
    window.grab_set()

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=20, pady=12)
    frame.columnconfigure(1, weight=1)

    username_var: tkinter.StringVar = tkinter.StringVar()
    role_var: tkinter.StringVar = tkinter.StringVar()
    can_change_password_var: tkinter.StringVar = tkinter.StringVar()

    tkinter.Label(frame, text="Eliminar usuario", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 12))
    tkinter.Label(frame, text="Usuario:" ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)

    username_entry: tkinter.Entry = tkinter.Entry(frame, textvariable=username_var, state="readonly")
    username_entry.grid(row=1, column=1, sticky="ew", pady=2)

    search_button: tkinter.Button = tkinter.Button(frame, text="Buscar", width=8, command=search_user)
    search_button.grid(row=1, column=2, padx=(5, 0), pady=2)

    tkinter.Label(frame, text="Rol:").grid( row=2, column=0, sticky="w", padx=(0, 10), pady=2)
    tkinter.Entry(frame, textvariable=role_var, state="readonly").grid(row=2, column=1, columnspan=2, sticky="ew", pady=2)

    tkinter.Label(frame, text="Puede cambiar contraseña:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=2)
    tkinter.Entry(frame, textvariable=can_change_password_var, state="readonly").grid(row=3, column=1, columnspan=2, sticky="ew", pady=2)
    
    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
    tkinter.Button(button_frame, text="Eliminar", width=10, command=delete_user).pack( side="left", padx=5)
    tkinter.Button(button_frame, text="Cancelar", width=10, command=window.destroy).pack( side="left", padx=5)

    window.bind("<Return>", lambda event: delete_user())
    window.bind("<Escape>", lambda event: window.destroy())
    window.bind("<Control-f>", lambda event: search_user())
    window.after_idle(search_button.focus_set)