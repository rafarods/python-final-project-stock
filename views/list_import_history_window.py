import tkinter
import tkinter.ttk
import modules.dao.product_dao as product_dao
import modules.utils as utils

def show(parent: tkinter.Misc, process_id: str | None = None) -> None:
    """
    Historial de importaciones
    """
    
    def load_process_ids() -> list[str]:
        """
        Cargar los ID de procesos
        """
        
        ids: list[str] = []
        for row in product_dao.find_all_import_processes():
            ids.append(row["process_id"])
        return ids

    def load_list(_: tkinter.Event | None = None) -> None:
        """
        Cargar listado
        """
        
        tree.delete(*tree.get_children())
        match utils.normalize_text(filter_var.get()):
            case "invalidos":
                filter = "ER"
            case "validos":
                filter = "PR"
            case "no procesados":
                filter = "SP"
            case _:
                filter = None
        products: list[dict] = product_dao.find_all_imports(process_var.get(), filter)
        for product in products:
            tree.insert("", "end", values=(
                product["line"],
                product["username"] or "",
                utils.file_name(product["filename"]),
                product["name"] or "",
                product["description"] or "", 
                product["category"] or "",
                product["quantity"] or "",
                product["currency"] or "",
                product["price"] or "",
                f"{product["status"]}: {product["status_description"]}",
                utils.format_datetime(product["create_at"]),
            ))
        total_var.set(f"{utils.format_quantity(len(tree.get_children()))} registros")

    window = tkinter.Toplevel(parent)
    window.title("Historial de importaciones")
    window.transient(parent)
    utils.center_window(window, 1300, 650)

    filter_frame = tkinter.ttk.Frame(window, padding=10)
    filter_frame.pack(fill="x")

    tkinter.ttk.Label(filter_frame, text="Proceso ID:").pack(side="left", padx=(0, 8))

    process_ids: list[str] = load_process_ids()
    process_var = tkinter.StringVar()
    process_combo = tkinter.ttk.Combobox(filter_frame, textvariable=process_var, values=process_ids, state="readonly", width=40)
    process_combo.pack(side="left")

    tkinter.ttk.Label(filter_frame, text="Filtrar por:").pack(side="left", padx=(20, 8))

    filter_var = tkinter.StringVar(value="Todos")
    filter_combo = tkinter.ttk.Combobox(filter_frame, textvariable=filter_var, values=("Todos", "Válidos", "Inválidos", "No procesados"), state="readonly", width=15)
    filter_combo.pack(side="left")

    total_var = tkinter.StringVar(value="0 registros")
    tkinter.ttk.Label(filter_frame, textvariable=total_var).pack(side="right")

    table_frame = tkinter.ttk.Frame(window, padding=(10, 0, 10, 10))
    table_frame.pack(fill="both", expand=True)
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    tree = tkinter.ttk.Treeview(table_frame, columns=("line", "username", "filename", "name", "description", "category", "quantity", "currency", "price", "message", "create_at"), show="headings")

    tree.heading("line", text="Fila")
    tree.column("line", width=50, minwidth=50, anchor="e")

    tree.heading("username", text="Usuario")
    tree.column("username", width=110, minwidth=50, anchor="w")

    tree.heading("filename", text="Archivo")
    tree.column("filename", width=160, minwidth=50, anchor="w")

    tree.heading("name", text="Producto")
    tree.column("name", width=180, minwidth=50, anchor="w")
    
    tree.heading("description", text="Descripción")
    tree.column("description", width=180, minwidth=50, anchor="w")

    tree.heading("category", text="Categoría")
    tree.column("category", width=180, minwidth=50, anchor="w")
    
    tree.heading("quantity", text="Cantidad")
    tree.column("quantity", width=80, minwidth=50, anchor="e")

    tree.heading("currency", text="Moneda")
    tree.column("currency", width=70, minwidth=50, anchor="center")

    tree.heading("price", text="Precio")
    tree.column("price", width=100, minwidth=50, anchor="e")

    tree.heading("message", text="Mensaje")
    tree.column("message", width=260, minwidth=50, anchor="w")

    tree.heading("create_at", text="Fecha")
    tree.column("create_at", width=145, minwidth=50, anchor="center")

    scroll_y = tkinter.ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scroll_x = tkinter.ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    button_frame: tkinter.ttk.Frame = tkinter.ttk.Frame(window, padding=(10, 0, 10, 10))
    button_frame.pack(fill="x")

    tkinter.Button(button_frame, text="Cerrar", width=10, command=window.destroy).pack()

    process_combo.bind("<<ComboboxSelected>>", load_list)
    filter_combo.bind("<<ComboboxSelected>>", load_list)

    if process_ids:
        if process_id is not None and process_id in process_ids:
            process_var.set(process_id)
        else:
            process_combo.current(0)
        load_list()