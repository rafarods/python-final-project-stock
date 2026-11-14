import tkinter
import tkinter.messagebox
import tkinter.simpledialog
import tkinter.ttk
import config
import traceback
import modules.dao.product_dao as product_dao
import modules.dao.category_dao as category_dao
import modules.utils as utils

def show(parent: tkinter.Tk, on_deleted = None) -> None:
    """
    Ventana para buscar y eliminar un producto.
    """

    def set_fields_state(state: str) -> None:
        """
        Cambia el estado de los campos.
        """
        name_entry.config(state=state)
        quantity_entry.config(state=state)
        price_entry.config(state=state)
        description_text.config(state=state)

    def clear() -> None:
        """
        Limpia los campos del formulario.
        """
        nonlocal product_id, product_name
        product_id = None
        product_name = ""
        set_fields_state("normal")
        name_entry.delete(0, tkinter.END)
        category_combo.set("")
        quantity_entry.delete(0, tkinter.END)
        currency_combo.set("")
        price_entry.delete(0, tkinter.END)
        description_text.delete("1.0", tkinter.END)
        set_fields_state("disabled")
        category_combo.config(state="disabled")
        currency_combo.config(state="disabled")
        delete_button.config(state="disabled")
        search_button.focus_set()

    def load_product(product: dict) -> None:
        """
        Carga los datos del producto en el formulario.
        """
        nonlocal product_id, product_name
        product_id = product["id"]
        product_name = product["name"]
        set_fields_state("normal")
        name_entry.delete(0, tkinter.END)
        name_entry.insert(0, product_name)
        quantity_entry.delete(0, tkinter.END)
        quantity_entry.insert(0, utils.format_quantity(product["quantity"]))
        price_entry.delete(0, tkinter.END)
        price_entry.insert(0, utils.format_price(product["price"]))
        description_text.delete("1.0", tkinter.END)
        description_text.insert("1.0", product.get("description") or "")
        set_fields_state("disabled")
        category_combo.config(state="readonly")
        category_combo.set(product.get("category") or "")
        currency_combo.config(state="readonly")
        if product["currency"] in config.CURRENCIES:
            currency_combo.current(config.CURRENCIES.index(product["currency"]))
        else:
            currency_combo.set(product["currency"])
        category_combo.config(state="disabled")
        currency_combo.config(state="disabled")
        delete_button.config(state="normal")
        delete_button.focus_set()

    def search_product() -> None:
        """
        Solicita un ID o nombre y carga los datos del producto.
        """
        search_text: str | None = tkinter.simpledialog.askstring("Buscar producto", "Buscar producto por ID o palabras clave:", parent=window)
        if search_text is None:
            return
        search_text = search_text.strip()
        if not search_text:
            tkinter.messagebox.showwarning("Buscar producto", "Debe ingresar el nombre o del producto.", parent=window)
            return
        try:
            product: dict | None = product_dao.search_one(search_text)
            if product is None:
                clear()
                tkinter.messagebox.showwarning("Buscar producto", f"No se encontró el producto '{search_text}', pruebe buscar por ID.", parent=window)
                return
            load_product(product)
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Buscar producto", "Ocurrió un error al buscar el producto.", parent=window)

    def delete_product() -> None:
        """
        Elimina el producto seleccionado.
        """
        if product_id is None:
            tkinter.messagebox.showwarning("Eliminar producto", "Primero debe buscar un producto.", parent=window)
            return
        confirmed: bool = tkinter.messagebox.askyesno("Eliminar producto", f"¿Está seguro de eliminar el producto '{product_name}'?\n\nEsta acción no se puede deshacer.", parent=window )
        if not confirmed:
            return
        try:
            result: int | None = product_dao.delete(product_id)
            if result is None or result <= 0:
                raise RuntimeError(f"Falló eliminar producto: {product_name}")
            if on_deleted:
                on_deleted()
            tkinter.messagebox.showinfo("Eliminar producto", f"Producto '{product_name}' eliminado correctamente.", parent=window)
            clear()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Eliminar producto", "Ocurrió un error al eliminar el producto.", parent=window)

    product_id: int | None = None
    product_name: str = ""

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.withdraw()
    window.title("Eliminar producto")
    window.resizable(False, False)
    window.transient(parent)

    if product_dao.count() == 0:
        tkinter.messagebox.showerror("Eliminar producto", "No hay inventario de productos.", parent=window)
        window.destroy()
        return

    categories: list[dict] = category_dao.find_all()
    category_names: list[str] = []
    for category in categories:
        category_names.append(category["name"])

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=25, pady=20)
    frame.columnconfigure(1, weight=1)

    tkinter.Label(frame, text="Eliminar producto", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 18))
    
    tkinter.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)
    name_entry: tkinter.Entry = tkinter.Entry(frame, state="disabled")
    name_entry.grid( row=1, column=1, sticky="ew", pady=4 )

    search_button: tkinter.Button = tkinter.Button(frame, text="Buscar", width=10, command=search_product)
    search_button.grid(row=1, column=2, padx=(8, 0), pady=4)

    tkinter.Label(frame, text="Categoría:").grid( row=2, column=0, sticky="w", padx=(0, 10), pady=4)
    category_combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(frame, values=category_names, state="disabled")
    category_combo.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Cantidad:").grid( row=3, column=0, sticky="w", padx=(0, 10), pady=4)
    quantity_entry: tkinter.Entry = tkinter.Entry(frame, state="disabled")
    quantity_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Moneda:").grid( row=4, column=0, sticky="w", padx=(0, 10), pady=4)
    currency_combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(frame, values=config.CURRENCIES, state="disabled")
    currency_combo.grid(row=4, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Precio:").grid(row=5, column=0, sticky="w", padx=(0, 10), pady=4)
    price_entry: tkinter.Entry = tkinter.Entry(frame, state="disabled")
    price_entry.grid(row=5, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Descripción:").grid( row=6, column=0, sticky="nw", padx=(0, 10), pady=4)

    description_text: tkinter.Text = tkinter.Text(frame, height=5, state="disabled")
    description_text.grid(row=6, column=1, columnspan=2, sticky="ew", pady=4)

    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=7, column=0, columnspan=3, pady=(12, 0))

    delete_button: tkinter.Button = tkinter.Button(button_frame, text="Eliminar", width=10, state="disabled", command=delete_product)
    delete_button.pack(side="left", padx=5)

    tkinter.Button(button_frame, text="Limpiar", width=10, command=clear ).pack( side="left", padx=5)
    tkinter.Button(button_frame, text="Cancelar", width=10, command=window.destroy ).pack( side="left", padx=5)

    window.bind("<Return>", lambda event: delete_product())
    window.bind("<Escape>", lambda event: window.destroy())
    window.bind("<Control-f>", lambda event: search_product())

    utils.center_window(window, 500, 390)
    window.update_idletasks()
    window.deiconify()
    window.grab_set()
    window.after_idle(search_button.focus_set)