import tkinter
import tkinter.ttk
import modules.dao.category_dao as category_dao
import modules.dao.product_dao as product_dao
import modules.utils as utils

def show(parent: tkinter.Misc) -> None:
    """
    Listado de productos
    """

    def load_list(_: tkinter.Event | None = None) -> None:
        """
        Cargar listado
        """
        nonlocal category_var, search_entry
        
        filter: dict = {}
        category_name = category_var.get()
        if category_name not in ("", "Todas"):
            filter["category"] = category_name
        text_search = search_entry.get().strip()
        if text_search != "":
            filter["search"] = text_search
        tree.delete(*tree.get_children())
        products: list[dict] = product_dao.find_all(filter)       
        for product in products:
            tree.insert("", "end", values=(
                product["id"] or "",
                product["name"] or "",
                product["description"] or "",
                product["category"] or "",
                utils.format_quantity(product["quantity"]),
                product["currency"] or "",
                utils.format_price(product["price"]), 
            ))
        total_var.set(f"{utils.format_quantity(len(tree.get_children()))} registros")

    window = tkinter.Toplevel(parent)
    window.title("Listado de Productos")
    window.transient(parent)
    utils.center_window(window, 800, 600)

    filter_frame = tkinter.ttk.Frame(window, padding=10)
    filter_frame.pack(fill="x")

    tkinter.ttk.Label(filter_frame, text="Buscar por:").pack(side="left", padx=(0, 8))
    search_entry: tkinter.Entry = tkinter.Entry(filter_frame, width=40)
    search_entry.pack(side="left")

    tkinter.ttk.Label(filter_frame, text="Categoría:").pack(side="left", padx=(20, 8))
    category_var = tkinter.StringVar(value="Todas")
    categories: tuple = ("Todas",)
    for row in category_dao.find_all():
        categories += (row["name"],)
    category_combo = tkinter.ttk.Combobox(filter_frame, textvariable=category_var, values=categories, state="readonly", width=15)
    category_combo.current(0)
    category_combo.pack(side="left")
    
    total_var = tkinter.StringVar(value="0 registros")
    tkinter.ttk.Label(filter_frame, textvariable=total_var).pack(side="right")

    table_frame = tkinter.ttk.Frame(window, padding=(10, 0, 10, 10))
    table_frame.pack(fill="both", expand=True)
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    tree = tkinter.ttk.Treeview(table_frame, columns=("id", "name", "description", "category", "quantity", "currency", "price"), show="headings")

    tree.heading("id", text="ID")
    tree.column("id", width=10, minwidth=10, anchor="e")

    tree.heading("name", text="Nombre")
    tree.column("name", width=120, minwidth=120, anchor="w")
    
    tree.heading("description", text="Descripción")
    tree.column("description", width=180, minwidth=50, anchor="w")

    tree.heading("category", text="Categoría")
    tree.column("category", width=80, minwidth=80, anchor="w")
    
    tree.heading("quantity", text="Cantidad")
    tree.column("quantity", width=25, minwidth=25, anchor="e")

    tree.heading("currency", text="Moneda")
    tree.column("currency", width=25, minwidth=25, anchor="center")

    tree.heading("price", text="Precio")
    tree.column("price", width=25, minwidth=25, anchor="e")

    scroll_y = tkinter.ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scroll_x = tkinter.ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    button_frame: tkinter.ttk.Frame = tkinter.ttk.Frame(window, padding=(10, 0, 10, 10))
    button_frame.pack(fill="x")

    tkinter.Button(button_frame, text="Cerrar", width=10, command=window.destroy).pack()

    category_combo.bind("<<ComboboxSelected>>", load_list)
    search_entry.bind("<KeyRelease>", load_list)

    load_list()