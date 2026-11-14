import tkinter
import tkinter.messagebox
import config
import modules.utils as utils
import modules.dao.user_dao as user_dao

auth_user: dict | None = None

"""
Ventana de inicio de sesión.
"""
def login() -> None:
    global auth_user
    username: str = username_entry.get().strip()
    password: str = password_entry.get()
    if not username or not password:
        tkinter.messagebox.showwarning("Inicio de Sesión", "Ingrese usuario y contraseña.")
        return
    if not user_dao.check_password(username, password):
        tkinter.messagebox.showerror("Inicio de Sesión", "Usuario o contraseña incorrectos.")
        return
    auth_user = user_dao.auth_user(username)
    root.destroy()

"""
Muestra la ventana de inicio de sesión.
"""
def show() -> str | None:
    global root
    global auth_user
    global username_entry
    global password_entry
    auth_user = None

    root = tkinter.Tk()
    root.title("Inicio de Sesión")
    root.resizable(False, False)
    utils.center_window(root, 360, 260)

    frame: tkinter.Frame = tkinter.Frame(root)
    frame.pack(expand=True, fill="both", padx=25, pady=20)
    frame.columnconfigure(1, weight=1)

    title_label: tkinter.Label = tkinter.Label(frame, text=f"{config.APP_NAME} v{config.APP_VERSION}", font=("Arial", 16, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 18))

    username_label: tkinter.Label = tkinter.Label(frame, text="Usuario:")
    username_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)

    username_entry = tkinter.Entry(frame)
    username_entry.grid(row=1, column=1, sticky="ew", pady=4)

    password_label: tkinter.Label = tkinter.Label(frame, text="Contraseña:")
    password_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)

    password_entry = tkinter.Entry(frame, show="*")
    password_entry.grid(row=2, column=1, sticky="ew", pady=4)

    login_button: tkinter.Button = tkinter.Button(frame, text="Aceptar", command=login)
    login_button.grid(row=3, column=0, columnspan=2, pady=(14, 8))

    credentials_label: tkinter.Label = tkinter.Label(frame, text=f'Acceso: {config.ADMIN["username"]} / {config.ADMIN["password"]}', font=("Arial", 10))
    credentials_label.grid(row=4, column=0, columnspan=2)

    author_label: tkinter.Label = tkinter.Label(frame, text=f'Autor: {config.AUTHOR["name"]} - {config.AUTHOR["email"]}', font=("Arial", 10))
    author_label.grid(row=5, column=0, columnspan=2, pady=(12, 0))

    root.bind("<Return>", lambda event: login())
    username_entry.focus()
    root.mainloop()

    return auth_user