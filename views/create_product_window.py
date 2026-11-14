import tkinter
import tkinter.messagebox
import tkinter.ttk
import config
import traceback
import modules.dao.product_dao as product_dao
import modules.dao.category_dao as category_dao
import modules.utils as utils

def show(parent: tkinter.Tk, on_created = None) -> None:
    """
    Ventana para crear un producto.
    """

    def reset() -> None:
        """
        Limpia los campos del formulario.
        """
        name_entry.delete(0, tkinter.END)
        category_combo.set("")
        quantity_entry.delete(0, tkinter.END)
        currency_combo.current(0)
        price_entry.delete(0, tkinter.END)
        description_text.delete("1.0", tkinter.END)
        name_entry.focus_set()

    def create_product() -> None:
        """
        Añade el producto
        """
        name: str = name_entry.get().strip()
        category_index: int = category_combo.current()
        quantity_text: str = quantity_entry.get()
        currency: str = currency_combo.get()
        price_text: str = price_entry.get()
        description: str = description_text.get("1.0", "end-1c").strip()
        if not name or category_index == -1 or not quantity_text or not currency or not price_text:
            tkinter.messagebox.showwarning("Agregar producto", "Complete todos los campos.", parent=window)
            return
        if len(name) > 64:
            tkinter.messagebox.showwarning("Agregar producto", "El nombre no puede exceder los 64 caracteres.", parent=window)
            name_entry.focus_set()
            return
        if product_dao.exists(name):
            tkinter.messagebox.showwarning("Agregar producto", f"El producto '{name}' ya existe.", parent=window)
            name_entry.focus_set()
            return
        if len(description) > 512:
            tkinter.messagebox.showwarning("Agregar producto", "La descripción no puede exceder los 512 caracteres.", parent=window)
            description_text.focus_set()
            return
        if not utils.is_quantity(quantity_text):
            tkinter.messagebox.showwarning("Agregar producto", "La cantidad debe ser un número entero.", parent=window)
            quantity_entry.focus_set()
            return
        quantity: int = utils.to_quantity(quantity_text)
        if quantity < config.MIN_QUANTITY or quantity > config.MAX_QUANTITY:
            tkinter.messagebox.showwarning("Agregar producto", f"""
            La cantidad debe estar entre: {utils.format_quantity(config.MIN_QUANTITY)} y {utils.format_quantity(config.MAX_QUANTITY)}
            """, parent=window)
            quantity_entry.focus_set()
            return
        if not utils.is_price(price_text) :
            tkinter.messagebox.showwarning("Agregar producto", "El precio es inválido.", parent=window)
            price_entry.focus_set()
            return
        price: float = utils.to_price(price_text)
        if price < config.MIN_PRICE or price > config.MAX_PRICE:
            tkinter.messagebox.showwarning("Agregar producto", f"El precio debe estar entre: {utils.format_price(config.MIN_PRICE)} y {utils.format_price(config.MAX_PRICE)}", parent=window)
            price_entry.focus_set()
            return
        try:
            result: int | None = product_dao.insert({
                "category_id": categories[category_index]["id"],
                "name": name,
                "description": description,
                "quantity": quantity,
                "currency": currency,
                "price": price
            })
            if result is None or result <= 0:
                raise RuntimeError(f"Falló agregar producto: {name}")
            if on_created:
                on_created() 
            tkinter.messagebox.showinfo("Agregar producto", f"Producto '{name}' agregado correctamente.", parent=window)
            reset()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Agregar producto", "Ocurrió un error al agregar el producto.", parent=window)

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.withdraw()
    window.title("Agregar producto")
    window.resizable(False, False)
    window.transient(parent)

    categories: list[dict] = category_dao.find_all()
    if not categories:
        tkinter.messagebox.showerror("Agregar producto", "No hay categorías de productos registradas.", parent=window)
        window.destroy()
        return

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=25, pady=20)
    frame.columnconfigure(1, weight=1)

    tkinter.Label(frame, text="Agregar Producto", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 18))

    tkinter.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)
    name_entry: tkinter.Entry = tkinter.Entry(frame)
    name_entry.grid(row=1, column=1, sticky="ew", pady=4)

    category_names: list[str] = []
    for category in categories:
        category_names.append(category["name"])
    
    tkinter.Label(frame, text="Categoría:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)
    category_combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(frame, values=category_names, state="readonly")
    category_combo.grid(row=2, column=1, sticky="ew", pady=4)

    tkinter.Label(frame, text="Cantidad:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=4)
    quantity_entry: tkinter.Entry = tkinter.Entry(frame)
    quantity_entry.grid(row=3, column=1, sticky="ew", pady=4)

    tkinter.Label(frame, text="Moneda:").grid(row=4, column=0, sticky="w", padx=(0, 10), pady=4)
    currency_combo: tkinter.ttk.Combobox = tkinter.ttk.Combobox(frame, values=config.CURRENCIES, state="readonly")
    currency_combo.grid(row=4, column=1, sticky="ew", pady=4)
    currency_combo.current(0)

    tkinter.Label(frame, text="Precio:").grid(row=5, column=0, sticky="w", padx=(0, 10), pady=4)
    price_entry: tkinter.Entry = tkinter.Entry(frame)
    price_entry.grid(row=5, column=1, sticky="ew", pady=4)

    tkinter.Label(frame, text="Descripción:").grid(row=6, column=0, sticky="nw", padx=(0, 10), pady=4)
    description_text: tkinter.Text = tkinter.Text(frame, height=5)
    description_text.grid(row=6, column=1, sticky="ew", pady=4)

    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=7, column=0, columnspan=2, pady=(12, 0))

    tkinter.Button(button_frame, text="Agregar", width=10, command=create_product).pack(side="left", padx=5)
    tkinter.Button(button_frame, text="Cancelar", width=10, command=window.destroy).pack(side="left", padx=5)

    window.bind("<Return>", lambda event: create_product())
    window.bind("<Escape>", lambda event: window.destroy())
    
    utils.center_window(window, 450, 390)
    window.update_idletasks()
    window.deiconify()
    window.grab_set()
    window.after_idle(name_entry.focus_set)