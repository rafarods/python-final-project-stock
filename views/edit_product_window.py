import tkinter
import tkinter.messagebox
import tkinter.simpledialog
import tkinter.ttk
import config
import traceback
import modules.dao.product_dao as product_dao
import modules.dao.category_dao as category_dao
import modules.utils as utils


def show(parent: tkinter.Tk, on_updated=None) -> None:
    """
    Ventana para buscar y editar un producto.
    """
    
    def enable_fields() -> None:
        """
        Habilita los campos para editar el producto.
        """
        name_entry.config(state="normal")
        category_combo.config(state="readonly")
        quantity_entry.config(state="normal")
        currency_combo.config(state="readonly")
        price_entry.config(state="normal")
        description_text.config(state="normal", background="white")
        update_button.config(state="normal")
        clear_button.config(state="normal")

    def disable_fields() -> None:
        """
        Deshabilita los campos del formulario.
        """
        name_entry.config(state="readonly")
        category_combo.config(state="disabled")
        quantity_entry.config(state="readonly")
        currency_combo.config(state="disabled")
        price_entry.config(state="readonly")
        description_text.config(state="disabled", background=window.cget("background"))
        update_button.config(state="disabled")
        clear_button.config(state="disabled")

    def clear() -> None:
        """
        Limpia y deshabilita los campos del formulario.
        """
        nonlocal product_id, original_name
        product_id = None
        original_name = ""
        enable_fields()
        id_entry.config(state="normal")
        id_entry.delete(0, tkinter.END)
        id_entry.config(state="readonly")
        name_entry.delete(0, tkinter.END)
        category_combo.set("")
        quantity_entry.delete(0, tkinter.END)
        currency_combo.current(0)
        price_entry.delete(0, tkinter.END)
        description_text.delete("1.0", tkinter.END)
        disable_fields()
        search_button.focus_set()

    def load_product(product: dict) -> None:
        """
        Carga los datos del producto en el formulario.
        """
        nonlocal product_id, original_name
        product_id = product["id"]
        original_name = product["name"]
        enable_fields()
        id_entry.config(state="normal")
        id_entry.delete(0, tkinter.END)
        id_entry.insert(0, str(product_id))
        id_entry.config(state="readonly")
        name_entry.delete(0, tkinter.END)
        name_entry.insert(0, original_name)
        category_combo.set("")
        for index, category in enumerate(categories):
            if category["id"] == product["category_id"]:
                category_combo.current(index)
                break
        quantity_entry.delete(0, tkinter.END)
        quantity_entry.insert(0, utils.format_quantity(product["quantity"]))
        if product["currency"] in config.CURRENCIES:
            currency_combo.current(config.CURRENCIES.index(product["currency"]))
        else:
            currency_combo.current(0)
        price_entry.delete(0, tkinter.END)
        price_entry.insert(0, utils.format_price(product["price"]))
        description_text.delete("1.0", tkinter.END)
        description_text.insert("1.0", product.get("description") or "")
        name_entry.focus_set()
        name_entry.select_range(0, tkinter.END)

    def search_product() -> None:
        """
        Solicita un ID o nombre, y llena el formulario del producto.
        """
        search_text: str | None = tkinter.simpledialog.askstring("Buscar producto", "Buscar producto por ID o palabras clave:", parent=window)
        if search_text is None:
            return
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

    def update_product() -> None:
        """
        Actualiza el producto seleccionado.
        """
        if product_id is None: 
            tkinter.messagebox.showwarning("Editar producto", "Primero debe buscar un producto.", parent=window)
            return
        name: str = name_entry.get().strip()
        category_index: int = category_combo.current()
        quantity_text: str = quantity_entry.get().strip()
        currency: str = currency_combo.get()
        price_text: str = price_entry.get().strip()
        description: str = description_text.get("1.0", "end-1c").strip()
        if not name or category_index == -1 or not quantity_text or not currency or not price_text:
            tkinter.messagebox.showwarning("Editar producto", "Complete todos los campos.", parent=window)
            return
        if len(name) > 64:
            tkinter.messagebox.showwarning("Editar producto", "El nombre no puede exceder los 64 caracteres.", parent=window)
            name_entry.focus_set()
            return
        if name != original_name and product_dao.exists(name):
            tkinter.messagebox.showwarning("Editar producto", f"El producto '{name}' ya existe.", parent=window) 
            name_entry.focus_set()
            return
        if len(description) > 512:
            tkinter.messagebox.showwarning("Editar producto", "La descripción no puede exceder los 512 caracteres.", parent=window)
            description_text.focus_set()
            return
        if not utils.is_quantity(quantity_text):
            tkinter.messagebox.showwarning("Editar producto", "La cantidad debe ser un número entero.", parent=window)
            quantity_entry.focus_set()
            return
        quantity: int = utils.to_quantity(quantity_text)
        if quantity < config.MIN_QUANTITY or quantity > config.MAX_QUANTITY:
            tkinter.messagebox.showwarning("Editar producto", f"La cantidad debe estar entre: {utils.format_quantity(config.MIN_QUANTITY)} y {utils.format_quantity(config.MAX_QUANTITY)}.", parent=window)
            quantity_entry.focus_set()
            return
        if not utils.is_price(price_text):
            tkinter.messagebox.showwarning("Editar producto", "El precio es inválido.", parent=window)
            price_entry.focus_set()
            return
        price: float = utils.to_price(price_text)
        if price < config.MIN_PRICE or price > config.MAX_PRICE:
            tkinter.messagebox.showwarning("Editar producto", f"El precio debe estar entre: {utils.format_price(config.MIN_PRICE)} y {utils.format_price(config.MAX_PRICE)}.", parent=window)
            price_entry.focus_set()
            return
        try:
            result: int | None = product_dao.update(product_id, {
                "category_id": categories[category_index]["id"],
                "name": name,
                "description": description,
                "quantity": quantity,
                "currency": currency,
                "price": price
            })
            if result is None or result <= 0:
                raise RuntimeError(f"Falló actualizar producto: {name}")
            if on_updated:
                on_updated()
            tkinter.messagebox.showinfo("Editar producto", f"Producto '{name}' actualizado correctamente.", parent=window)
            clear()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Editar producto", "Ocurrió un error al actualizar el producto.", parent=window)
            
    product_id: int | None = None
    original_name: str = ""

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.withdraw()
    window.title("Editar producto")
    window.resizable(False, False)
    window.transient(parent)

    if product_dao.is_empty():
        tkinter.messagebox.showerror("Editar producto", "No hay inventario de productos.", parent=window)
        window.destroy()
        return

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=25, pady=20)
    frame.columnconfigure(1, weight=1)

    tkinter.Label(frame, text="Editar producto", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 18))
    
    tkinter.Label(frame, text="ID:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)
    id_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    id_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Nombre:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)
    name_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    name_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)
    
    categories: list[dict] = category_dao.find_all()
    category_names: list[str] = []
    for category in categories:
        category_names.append(category["name"])

    tkinter.Label(frame, text="Categoría:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=4)
    category_combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(frame, values=category_names, state="disabled")
    category_combo.grid(row=3, column=1, columnspan=2, sticky="ew", pady=4)
    
    tkinter.Label(frame, text="Cantidad:").grid(row=4, column=0, sticky="w", padx=(0, 10), pady=4)
    quantity_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    quantity_entry.grid(row=4, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Moneda:").grid(row=5, column=0, sticky="w", padx=(0, 10), pady=4)
    currency_combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(frame, values=config.CURRENCIES, state="disabled")
    currency_combo.grid(row=5, column=1, columnspan=2, sticky="ew", pady=4)
    currency_combo.current(0)
    
    tkinter.Label(frame, text="Precio:").grid(row=6, column=0, sticky="w", padx=(0, 10), pady=4)
    price_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly", )
    price_entry.grid(row=6, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Descripción:").grid(row=7, column=0, sticky="nw", padx=(0, 10), pady=4)
    description_text: tkinter.Text = tkinter.Text(frame, height=5, state="disabled", background=window.cget("background"))
    description_text.grid(row=7, column=1, columnspan=2, sticky="ew", pady=4)

    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=8, column=0, columnspan=3, pady=(12, 0))

    search_button: tkinter.Button = tkinter.Button(button_frame, text="Buscar", width=10, command=search_product)
    search_button.pack(side="left", padx=5)

    update_button: tkinter.Button = tkinter.Button(button_frame, text="Actualizar", width=10, state="disabled", command=update_product)
    update_button.pack(side="left", padx=5)

    clear_button: tkinter.Button = tkinter.Button(button_frame, text="Limpiar", width=10, state="disabled", command=clear)
    clear_button.pack(side="left", padx=5)
    
    tkinter.Button(button_frame, text="Cancelar", width=10, command=window.destroy).pack(side="left", padx=5)

    window.bind("<Return>", lambda event: update_product())
    window.bind("<Escape>", lambda event: window.destroy())

    utils.center_window(window, 500, 390)
    window.update_idletasks()
    window.deiconify()
    window.grab_set()
    window.after_idle(search_button.focus_set)