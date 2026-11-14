import tkinter
import tkinter.filedialog
import tkinter.messagebox
import traceback
import modules.utils as utils

def show(parent: tkinter.Tk, username: str, on_success = None) -> None:
    """
    Muestra la ventana para importar inventario desde CSV.
    """

    def select_file() -> None:
        """
        Selecciona el archivo a importar
        """
        
        filename: str = tkinter.filedialog.askopenfilename(parent=window, title="Seleccionar archivo", filetypes=[("Archivos CSV", "*.csv")])
        if filename:
            file_var.set(filename)

    def import_csv() -> None:
        """
        Importar archivo en las tablas
        """
        
        filename: str = file_var.get().strip()
        if not filename:
            tkinter.messagebox.showerror("Importar inventario", "Debe seleccionar un archivo CSV.", parent=window)
            return
        try:
            result: dict = utils.import_stock_csv(username, filename, auto_create_var.get())
            if result is None:
                raise RuntimeError(f"Falló la importación desde el archivo: {utils.file_name(filename)}")
            tkinter.messagebox.showinfo("Importar inventario", f"Se han importado {utils.format_quantity(result["num_total"])} registros.", parent=window)
            if on_success:
                on_success(result)
            window.destroy()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Importar inventario", "Ocurrió un error al importar el inventario.", parent=window)

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.title("Importar inventario")
    window.resizable(False, False)
    window.transient(parent)
    window.grab_set()
    utils.center_window(window, 600, 210)

    file_var: tkinter.StringVar = tkinter.StringVar()
    auto_create_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # Archivo
    tkinter.Label(frame, text="Archivo CSV:").grid(row=0, column=0, sticky="w", pady=(0, 5))

    file_entry: tkinter.Entry = tkinter.Entry(frame, textvariable=file_var, width=55, state="readonly")
    file_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
    select_button: tkinter.Button = tkinter.Button( frame, text="...", command=select_file)
    select_button.grid(row=1, column=1)

    # Opciones
    auto_create_check: tkinter.Checkbutton = tkinter.Checkbutton(frame, text="Crear automáticamente categorías o productos", variable=auto_create_var)
    auto_create_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(20, 0))

    # Botones
    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=(25, 0))

    import_button: tkinter.Button = tkinter.Button(button_frame, text="Importar", width=12, command=import_csv)
    import_button.pack(side="left", padx=(0, 5))

    close_button: tkinter.Button = tkinter.Button(button_frame, text="Cerrar", width=12, command=window.destroy)
    close_button.pack(side="left")

    frame.columnconfigure(0, weight=1)

    window.bind("<Escape>", lambda event: window.destroy())
    window.after_idle(window.focus_force)
    window.wait_window()