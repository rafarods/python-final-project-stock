import tkinter
import tkinter.messagebox
import tkinter.ttk
import config
import traceback
import modules.dao.user_dao as user_dao
import modules.utils as utils

def show(parent: tkinter.Tk) -> None:
    """
    Ventana para crear un usuario.
    """
    
    def reset() -> None:
        """
        Limpia los campos del formulario.
        """
        username_entry.delete(0, tkinter.END)
        password_entry.delete(0, tkinter.END)
        confirm_entry.delete(0, tkinter.END)
        role_combo.current(0)
        username_entry.focus_set()
        can_change_password_var.set(True)

    def create_user() -> None:
        """
        Crea un usuario.
        """
        username: str = username_entry.get().strip()
        password: str = password_entry.get()
        confirm: str = confirm_entry.get()
        role: str = role_combo.get()
        can_change_password: bool = can_change_password_var.get()
        if not username or not password or not confirm or not role:
            tkinter.messagebox.showwarning("Crear usuario", "Complete todos los campos requeridos.", parent=window)
            username_entry.focus_set()
            return
        if len(username) < 4:
            tkinter.messagebox.showwarning("Crear usuario", "El nombre de usuario debe tener 4 o más caracteres.", parent=window)
            username_entry.focus_set()
            return
        password = password.strip()
        if not password:
            tkinter.messagebox.showwarning("Crear usuario", "La contraseña no puede estar en blanco.", parent=window)
            confirm_entry.focus_set()
            return
        if password != confirm:
            tkinter.messagebox.showwarning("Crear usuario", "Las contraseñas no coinciden.", parent=window)
            password_entry.focus_set()
            return
        if len(password) < config.PASSWD_MIN_LEN:
            tkinter.messagebox.showwarning("Crear usuario", f"La contraseña debe tener {config.PASSWD_MIN_LEN} o más caracteres.", parent=window)
            username_entry.focus_set()
            return
        if user_dao.exist(username):
            tkinter.messagebox.showwarning("Crear usuario", "El usuario ya existe.", parent=window)
            username_entry.focus_set()
            return
        try:
            if role == "Administrador":
                role_user = config.ROLE_ADMIN
            else:
                role_user = config.ROLE_USER
            result: int | None = user_dao.insert(username, password, role_user, can_change_password)
            if result is None or result <= 0:
                raise RuntimeError(f"Fallo la creación del usuario: {username}")
            tkinter.messagebox.showinfo("Crear usuario", f"Usuario '{username}' creado correctamente.", parent=window)
            #window.destroy()
            reset()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Crear usuario", "Ocurrió un error al crear el usuario.", parent=window)

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.title("Crear usuario")
    window.resizable(False, False)
    utils.center_window(window, 400, 300)
    window.transient(parent)
    window.grab_set()

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=25, pady=20)
    frame.columnconfigure(1, weight=1)

    tkinter.Label(frame, text="Crear usuario", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 18))
    tkinter.Label(frame, text="Usuario:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)
    tkinter.Label(frame, text="Contraseña:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)
    tkinter.Label(frame, text="Confirmar:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=4)
    tkinter.Label(frame, text="Rol:").grid(row=4, column=0, sticky="w", padx=(0, 10), pady=4)

    username_entry: tkinter.Entry = tkinter.Entry(frame)
    username_entry.grid(row=1, column=1, sticky="ew", pady=4)

    password_entry: tkinter.Entry = tkinter.Entry(frame, show="*")
    password_entry.grid(row=2, column=1, sticky="ew", pady=4)

    confirm_entry: tkinter.Entry = tkinter.Entry(frame, show="*")
    confirm_entry.grid(row=3, column=1, sticky="ew", pady=4)

    role_combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(frame, values=("Usuario", "Administrador"), state="readonly")
    role_combo.grid(row=4, column=1, sticky="ew", pady=4)
    role_combo.current(0)

    can_change_password_var: tkinter.BooleanVar = tkinter.BooleanVar(value=True)
    tkinter.Checkbutton(frame, text="Puede cambiar su contraseña", variable=can_change_password_var).grid(row=5, column=0, columnspan=2, sticky="w", pady=8)

    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=6, column=0, columnspan=2, pady=(12, 0))

    tkinter.Button(button_frame, text="Crear", width=10, command=create_user).pack(side="left", padx=5)
    tkinter.Button(button_frame, text="Cancelar", width=10, command=window.destroy).pack(side="left", padx=5)

    window.bind("<Return>", lambda event: create_user())
    window.bind("<Escape>", lambda event: window.destroy())
    window.after_idle(username_entry.focus)