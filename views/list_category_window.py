import tkinter
import tkinter.ttk
import modules.dao.category_dao as category_dao
import modules.utils as utils

def show(parent: tkinter.Misc) -> None:
    """Listado de categorías."""

    def load_categories() -> None:
        """Carga las categorías."""
        tree.delete(*tree.get_children())
        categories: list[dict] = category_dao.find_all()
        for category in categories:
            tree.insert("", "end", values=(category["id"], category["name"], utils.format_quantity(category["total_products"])))

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.title("Categorías")
    window.resizable(False, False)
    window.transient(parent)
    utils.center_window(window, 600, 450)

    header_frame: tkinter.ttk.Frame = tkinter.ttk.Frame(window, padding=10)
    header_frame.pack(fill="x")

    tkinter.ttk.Label(header_frame, text="Listado de Categorías", font=("Arial", 12, "bold")).pack(side="left")

    table_frame: tkinter.ttk.Frame = tkinter.ttk.Frame(window, padding=(10, 0, 10, 10))
    table_frame.pack(fill="both", expand=True)
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    tree: tkinter.ttk.Treeview = tkinter.ttk.Treeview(table_frame, columns=("id", "name", "total_products"), show="headings")

    tree.heading("id", text="ID")
    tree.column("id", width=70, minwidth=50, anchor="e")

    tree.heading("name", text="Categoría")
    tree.column("name", width=280, minwidth=150, anchor="w")

    tree.heading("total_products", text="Total de productos")
    tree.column("total_products", width=150, minwidth=120, anchor="e")

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

    load_categories()