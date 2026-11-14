import tkinter
import tkinter.ttk
import config
import modules.dao.user_dao as user_dao
import modules.utils as utils

def show(parent: tkinter.Misc) -> None:
    """Listado de usuarios."""

    def load_users() -> None:
        """
        Carga los usuarios
        """
        
        tree.delete(*tree.get_children())
        users: list[dict] = user_dao.find_all()
        for user in users:
            if user["role"] == config.ROLE_ADMIN:
                role = "Administrador"
            else:
                role = "Usuario"
            if bool(user["can_change_password"]):
                can_change_password = "Si"
            else:
                can_change_password = "No"
            tree.insert("", "end", values=(user["username"], role, can_change_password))
        total_var.set(f"{utils.format_quantity(len(tree.get_children()))} registros")

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.title("Usuarios")
    window.geometry("700x450")
    window.resizable(False, False)
    window.transient(parent)
    utils.center_window(window, 700, 450)

    header_frame: tkinter.ttk.Frame = tkinter.ttk.Frame(window, padding=10)
    header_frame.pack(fill="x")

    tkinter.ttk.Label(header_frame, text="Listado de Usuarios", font=("Arial", 12, "bold")).pack(side="left")

    total_var: tkinter.StringVar = tkinter.StringVar(value="0 registros")
    tkinter.ttk.Label(header_frame, textvariable=total_var).pack(side="right")

    table_frame: tkinter.ttk.Frame = tkinter.ttk.Frame(window, padding=(10, 0, 10, 10))
    table_frame.pack(fill="both", expand=True)
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    tree: tkinter.ttk.Treeview = tkinter.ttk.Treeview(table_frame, columns=("username", "role", "can_change_password"), show="headings")

    tree.heading("username", text="Usuario")
    tree.column("username", width=220, minwidth=100, anchor="w")

    tree.heading("role", text="Rol")
    tree.column("role", width=160, minwidth=100, anchor="w")

    tree.heading("can_change_password", text="¿Puede cambiar la contraseña?")
    tree.column("can_change_password", width=180, minwidth=150, anchor="center")

    scroll_y: tkinter.ttk.Scrollbar = tkinter.ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scroll_x: tkinter.ttk.Scrollbar = tkinter.ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    button_frame: tkinter.ttk.Frame = tkinter.ttk.Frame(window, padding=(10, 0, 10, 10))
    button_frame.pack(fill="x")

    tkinter.Button(button_frame, text="Cerrar", width=10, command=window.destroy).pack()

    window.bind("<Escape>", lambda event: window.destroy())

    load_users()