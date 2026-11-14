import tkinter
import tkinter.messagebox
import tkinter.simpledialog
import tkinter.ttk
import config
import traceback
import modules.dao.product_dao as product_dao
import modules.dao.category_dao as category_dao
import modules.utils as utils

def show(parent: tkinter.Tk, on_deleted=None) -> None:
    """
    Ventana para buscar y eliminar un producto.
    """

    def enable_buttons() -> None:
        """
        Habilita los botones asociados al producto seleccionado.
        """
        delete_button.config(state="normal")
        clear_button.config(state="normal")

    def disable_buttons() -> None:
        """
        Deshabilita los botones asociados al producto seleccionado.
        """
        delete_button.config(state="disabled")
        clear_button.config(state="disabled")

    def clear() -> None:
        """
        Limpia los campos del formulario.
        """
        nonlocal product_id
        product_id = None
        id_entry.config(state="normal")
        id_entry.delete(0, tkinter.END)
        id_entry.config(state="readonly")
        name_entry.config(state="normal")
        name_entry.delete(0, tkinter.END)
        name_entry.config(state="readonly")
        category_entry.config(state="normal")
        category_entry.delete(0, tkinter.END)
        category_entry.config(state="readonly")
        quantity_entry.config(state="normal")
        quantity_entry.delete(0, tkinter.END)
        quantity_entry.config(state="readonly")
        currency_entry.config(state="normal")
        currency_entry.delete(0, tkinter.END)
        currency_entry.config(state="readonly")
        price_entry.config(state="normal")
        price_entry.delete(0, tkinter.END)
        price_entry.config(state="readonly")
        description_text.config(state="normal")
        description_text.delete("1.0", tkinter.END)
        description_text.config(state="disabled", background=window.cget("background"))
        disable_buttons()
        search_button.focus_set()

    def set_entry(entry: tkinter.Entry, value: str) -> None:
        """
        Establece el valor de un campo de solo lectura.
        """
        entry.config(state="normal")
        entry.delete(0, tkinter.END)
        entry.insert(0, value)
        entry.config(state="readonly")

    def load_product(product: dict) -> None:
        """
        Carga los datos del producto en el formulario.
        """
        nonlocal product_id
        product_id = product["id"]
        category_name: str = ""
        for category in categories:
            if category["id"] == product["category_id"]:
                category_name = category["name"]
                break
        set_entry(id_entry, str(product["id"]))
        set_entry(name_entry, product["name"])
        set_entry(category_entry, category_name)
        set_entry(quantity_entry, utils.format_quantity(product["quantity"]))
        set_entry(currency_entry, product["currency"])
        set_entry(price_entry, utils.format_price(product["price"]))
        description_text.config(state="normal", background=window.cget("background"))
        description_text.delete("1.0", tkinter.END)
        description_text.insert("1.0", product.get("description") or "")
        description_text.config(state="disabled", background=window.cget("background"))
        enable_buttons()
        delete_button.focus_set()

    def search_product() -> None:
        """
        Solicita un ID o nombre, y llena el formulario del producto.
        """
        search_text: str | None = tkinter.simpledialog.askstring("Buscar producto", "Buscar producto por ID o palabras clave:", parent=window)
        if search_text is None:
            return
        if not search_text:
            tkinter.messagebox.showwarning("Buscar producto", "Debe ingresar el nombre del producto.", parent=window)
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

        name: str = name_entry.get().strip()
        confirmed: bool = tkinter.messagebox.askyesno("Eliminar producto", f"¿Está seguro de eliminar el producto '{name}'?\nEstá acción no puede deshacerse.", parent=window)
        if not confirmed:
            return
        try:
            result: int | None = product_dao.delete(product_id)
            if result is None or result <= 0:
                raise RuntimeError(f"Falló eliminar producto: {name}")
            if on_deleted:
                on_deleted()
            tkinter.messagebox.showinfo("Eliminar producto", f"Producto '{name}' eliminado correctamente.", parent=window)
            clear()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Eliminar producto", "Ocurrió un error al eliminar el producto.", parent=window)

    product_id: int | None = None

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.withdraw()
    window.title("Eliminar producto")
    window.resizable(False, False)
    window.transient(parent)

    if product_dao.is_empty():
        tkinter.messagebox.showerror("Eliminar producto", "No hay inventario de productos.", parent=window)
        window.destroy()
        return

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=25, pady=20)
    frame.columnconfigure(1, weight=1)

    tkinter.Label(frame, text="Eliminar producto", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 18))

    tkinter.Label(frame, text="ID:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)
    id_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    id_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Nombre:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)
    name_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    name_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)

    categories: list[dict] = category_dao.find_all()

    tkinter.Label(frame, text="Categoría:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=4)
    category_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    category_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Cantidad:").grid(row=4, column=0, sticky="w", padx=(0, 10), pady=4)
    quantity_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    quantity_entry.grid(row=4, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Moneda:").grid(row=5, column=0, sticky="w", padx=(0, 10), pady=4)
    currency_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    currency_entry.grid(row=5, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Precio:").grid(row=6, column=0, sticky="w", padx=(0, 10), pady=4)
    price_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    price_entry.grid(row=6, column=1, columnspan=2, sticky="ew", pady=4)

    tkinter.Label(frame, text="Descripción:").grid(row=7, column=0, sticky="nw", padx=(0, 10), pady=4)
    description_text: tkinter.Text = tkinter.Text(frame, height=5, state="disabled", background=window.cget("background"))
    description_text.grid(row=7, column=1, columnspan=2, sticky="ew", pady=4)

    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=8, column=0, columnspan=3, pady=(12, 0))

    search_button: tkinter.Button = tkinter.Button(button_frame, text="Buscar", width=10, command=search_product)
    search_button.pack(side="left", padx=5)

    delete_button: tkinter.Button = tkinter.Button(button_frame, text="Eliminar", width=10, state="disabled", command=delete_product)
    delete_button.pack(side="left", padx=5)

    clear_button: tkinter.Button = tkinter.Button(button_frame, text="Limpiar", width=10, state="disabled", command=clear)
    clear_button.pack(side="left", padx=5)
    tkinter.Button(button_frame, text="Cancelar", width=10, command=window.destroy).pack(side="left", padx=5)

    window.bind("<Return>", lambda event: delete_product())
    window.bind("<Escape>", lambda event: window.destroy())

    utils.center_window(window, 500, 390)
    window.update_idletasks()
    window.deiconify()
    window.grab_set()
    window.after_idle(search_button.focus_set)