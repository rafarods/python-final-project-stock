import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
import traceback
import config
import modules.dao.product_dao as product_dao
import modules.utils as utils
import views.change_password_window as change_password_window
import views.create_category_window as create_category_window
import views.create_product_window as create_product_window
import views.create_user_window as create_user_window
import views.delete_category_window as delete_category_window
import views.delete_product_window as delete_product_window
import views.delete_user_window as delete_user_window
import views.edit_category_window as edit_category_window
import views.edit_product_window as edit_product_window
import views.edit_user_window as edit_user_window
import views.import_stock_window as import_stock_window
import views.list_category_window as list_category_window
import views.list_import_history_window as list_import_history_window
import views.list_user_window as list_user_window
import views.list_product_window as list_product_window

def show(user: dict) -> bool:
    """
    Muestra la ventana principal.
    """
    
    def logout() -> None:
        """
        Termina la sesión del usuario
        """
        nonlocal logout_requested
        logout_requested = True
        root.destroy()

    def exit_app() -> None:
        """ Cierra la aplicación """
        if tkinter.messagebox.askyesno("Salir", "¿Desea salir de la aplicación?", parent=root):
            root.destroy()

    def import_stock_success(result: dict) -> None:
        load_products()
        list_import_history_window.show(root, result.get("process_id"))

    def load_products() -> None:
        """
        Recarga la tabla de productos.
        """
        table.delete(*table.get_children())
        products: list[dict] = product_dao.find_all()
        for product in products:
            table.insert("", "end", values=(
                product.get("id") or "",
                product.get("name") or "",
                product.get("description") or "",
                product.get("category") or "",
                product.get("quantity") or "",
                product.get("currency") or "",
                utils.format_price(product.get("price")) or "",
            ))
        count_label.config(text=f"Total registros: {utils.format_quantity(len(products))}")

    def export_stock_csv() -> None:
        """
        Exportar inventario CSV
        """
        filename: str = tkinter.filedialog.asksaveasfilename(
            parent=root,
            title="Exportar inventario",
            initialfile="inventario.csv",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if not filename:
            return
        try:
            count: int = utils.export_stock_csv(filename)
            tkinter.messagebox.showinfo("Exportar CSV", f"Se exportaron {utils.format_quantity(count)} registros.", parent=root)
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Exportar CSV", "Ocurrió un error al exportar el inventario.", parent=root)

    def delete_all_stock() -> None:
        """
        Vaciar inventario
        """
        if product_dao.count() == 0:
            tkinter.messagebox.showerror("Vaciar inventario", "No hay inventario cargado.", parent=root)
            return
        if not tkinter.messagebox.askyesno("Vaciar inventario", f"¿Estás seguro de que desea vaciar todo el inventario? Esta acción no se puede deshacer.", icon="warning", parent=root):
            return
        count: int = product_dao.delete_all()
        load_products()
        tkinter.messagebox.showinfo("Vaciar inventario", f"Se eliminaron {utils.format_quantity(count, config.LANG)} registros", parent=root)
        
    def delete_all_import() -> None:
        """
        Vaciar historial
        """
        if product_dao.count_imports() == 0:
            tkinter.messagebox.showerror("Eliminar historial", "No hay registros historicos.", parent=root)
            return
        if not tkinter.messagebox.askyesno("Eliminar historial", f"¿Estás seguro de que desea eliminar el historial? Esta acción no se puede deshacer.", icon="warning", parent=root):
            return
        count: int = product_dao.delete_all_imports()
        tkinter.messagebox.showinfo("Eliminar historial", f"Se eliminaron {utils.format_quantity(count, config.LANG)} registros", parent=root)

    logout_requested: bool = False
    root: tkinter.Tk = tkinter.Tk()
    root.title(f"{config.APP_NAME} v{config.APP_VERSION}")
    root.resizable(False, False)
    utils.center_window(root, 900, 450)
    
    root.protocol("WM_DELETE_WINDOW", exit_app)

    # Barra de menú
    menu_bar: tkinter.Menu = tkinter.Menu(root)

    # Aplicación
    app_menu: tkinter.Menu = tkinter.Menu(menu_bar, tearoff=False)
    # ¿usuario puede cambiar la contraseña?
    if bool(user.get("can_change_password")):
        change_password_window_state = utils.get_state_allow_access(user.get("role"), "change_password")
    else:
        change_password_window_state = "disabled"
    app_menu.add_command(label="Cambiar contraseña", command=lambda: change_password_window.show(root, user.get("username")), state=change_password_window_state)
    app_menu.add_command(label="Cerrar sesión", command=logout, state=utils.get_state_allow_access(user.get("role"), "logout"))
    app_menu.add_separator()
    app_menu.add_command(label="Salir", command=exit_app, state=utils.get_state_allow_access(user.get("role"), "exit"))
    menu_bar.add_cascade(label="Aplicación", menu=app_menu, state=utils.get_state_allow_access(user.get("role"), "menu_application"))

    # Inventario
    inventory_menu: tkinter.Menu = tkinter.Menu(menu_bar, tearoff=False)
    inventory_menu.add_command(label="Agregar producto", command=lambda: create_product_window.show(root, load_products), state=utils.get_state_allow_access(user.get("role"), "add_product"))
    inventory_menu.add_command(label="Modificar producto", command=lambda: edit_product_window.show(root, load_products), state=utils.get_state_allow_access(user.get("role"), "edit_product"))
    inventory_menu.add_command(label="Eliminar producto", command=lambda: delete_product_window.show(root, load_products), state=utils.get_state_allow_access(user.get("role"), "delete_product"))    
    inventory_menu.add_command(label="Listado de productos", command=lambda: list_product_window.show(root), state=utils.get_state_allow_access(user.get("role"), "list_product"))       
    inventory_menu.add_separator()
    inventory_menu.add_command(label="Importar CSV", command=lambda: import_stock_window.show(root, user.get("username"), import_stock_success), state=utils.get_state_allow_access(user.get("role"), "import_stock"))
    inventory_menu.add_command(label="Exportar CSV", command=export_stock_csv, state=utils.get_state_allow_access(user.get("role"), "export_stock"))
    inventory_menu.add_command(label="Ver historial", command=lambda: list_import_history_window.show(root), state=utils.get_state_allow_access(user.get("role"), "import_list"))
    inventory_menu.add_separator()
    inventory_menu.add_command(label="Eliminar historial", command=delete_all_import, state=utils.get_state_allow_access(user.get("role"), "delete_all_import"))
    inventory_menu.add_separator()
    inventory_menu.add_command(label="Vaciar inventario", command=delete_all_stock, state=utils.get_state_allow_access(user.get("role"), "delete_all_stock"))
    menu_bar.add_cascade(label="Inventario", menu=inventory_menu, state=utils.get_state_allow_access(user.get("role"), "menu_stock"))

    # Categorías
    category_menu: tkinter.Menu = tkinter.Menu(menu_bar, tearoff=False)
    category_menu.add_command(label="Nuevo", command=lambda: create_category_window.show(root), state=utils.get_state_allow_access(user.get("role"), "add_category"))
    category_menu.add_command(label="Listado", command=lambda: list_category_window.show(root), state=utils.get_state_allow_access(user.get("role"), "list_category"))
    category_menu.add_separator()
    category_menu.add_command(label="Modificar", command=lambda: edit_category_window.show(root), state=utils.get_state_allow_access(user.get("role"), "edit_category"))
    category_menu.add_command(label="Eliminar", command=lambda: delete_category_window.show(root), state=utils.get_state_allow_access(user.get("role"), "delete_category"))    
    menu_bar.add_cascade(label="Categoría", menu=category_menu, state=utils.get_state_allow_access(user.get("role"), "menu_category"))

    # Usuarios
    user_menu: tkinter.Menu = tkinter.Menu(menu_bar, tearoff=False)
    user_menu.add_command(label="Nuevo", command=lambda: create_user_window.show(root), state=utils.get_state_allow_access(user.get("role"), "add_user"))
    user_menu.add_command(label="Listado", command=lambda: list_user_window.show(root), state=utils.get_state_allow_access(user.get("role"), "list_user"))
    user_menu.add_separator()
    user_menu.add_command(label="Modificar", command=lambda: edit_user_window.show(root, user), state=utils.get_state_allow_access(user.get("role"), "edit_user"))
    user_menu.add_command(label="Eliminar", command=lambda: delete_user_window.show(root, user), state=utils.get_state_allow_access(user.get("role"), "delete_user"))
    menu_bar.add_cascade(label="Usuario", menu=user_menu, state=utils.get_state_allow_access(user.get("role"), "menu_user"))

    root.config(menu=menu_bar)

    # Contenido
    frame: tkinter.Frame = tkinter.Frame(root)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # Cabecera
    header_frame: tkinter.Frame = tkinter.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 5))

    title_label: tkinter.Label = tkinter.Label(header_frame, text="Inventario Actual", font=("Arial", 14, "bold"))
    title_label.pack(side="left")

    user_label: tkinter.Label = tkinter.Label(header_frame, text=f'Usuario: {user.get("username")}', font=("Arial", 8))
    user_label.pack(side="right")

    # Tabla
    table_frame: tkinter.Frame = tkinter.Frame(frame)
    table_frame.pack(expand=True, fill="both")

    columns: tuple[str, ...] = ("id", "name", "description", "category", "quantity", "currency", "price")

    table: tkinter.ttk.Treeview = tkinter.ttk.Treeview(table_frame, columns=columns, show="headings")
    table.heading("id", text="ID")
    table.heading("name", text="Producto")
    table.heading("description", text="Descripción")    
    table.heading("category", text="Categoría")
    table.heading("quantity", text="Cantidad")
    table.heading("currency", text="Moneda")
    table.heading("price", text="Precio")

    table.column("id", width=40, anchor="e", stretch=False)
    table.column("name", width=120)
    table.column("description", width=180)
    table.column("category", width=100)
    table.column("quantity", width=70, anchor="e", stretch=False)
    table.column("currency", width=70, anchor="center", stretch=False)
    table.column("price", width=70, anchor="e", stretch=False)

    scrollbar: tkinter.ttk.Scrollbar = tkinter.ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    
    table.pack(side="left", expand=True, fill="both")
    scrollbar.pack(side="right", fill="y")

    count_label: tkinter.Label = tkinter.Label(frame, text="Total registros: 0", font=("Arial", 8))
    count_label.pack(anchor="e", pady=(4, 0))
    
    load_products()

    author_label: tkinter.Label = tkinter.Label(frame, text=config.TEXT_FOOTER, font=("Arial", 8))
    author_label.pack(side="bottom", pady=(4, 0))

    root.after_idle(root.focus_force)
    root.mainloop()
    
    return logout_requested