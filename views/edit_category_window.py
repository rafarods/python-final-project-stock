import tkinter
import tkinter.messagebox
import tkinter.simpledialog
import traceback
import modules.dao.category_dao as category_dao
import modules.utils as utils

def show(parent: tkinter.Tk) -> None:
    """
    Ventana para editar una categoría
    """

    def search_category() -> None:
        """
        Abre una ventana para buscar la categoría
        """
        name: str | None = tkinter.simpledialog.askstring("Buscar categoría", "Categoría:", parent=window)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        category: dict | None = category_dao.find_one(name)
        if category is None:
            tkinter.messagebox.showwarning("Buscar categoría", f"No existe la categoría: {name}", parent=window)
            return
        load_category(category)

    def load_category(category: dict) -> None:
        """
        Llena el formulario
        """
        category_entry.config(state="normal")
        category_entry.delete(0, "end")
        category_entry.insert(0, category["name"])
        category_entry.config(state="readonly")
        new_name_entry.delete(0, "end")
        new_name_entry.insert(0, category["name"])
        new_name_entry.focus_set()
        new_name_entry.select_range(0, "end")

    def update_category() -> None:
        """
        Actualiza la categoría
        """
        name: str = category_entry.get()
        new_name: str = new_name_entry.get().strip()
        if not name:
            tkinter.messagebox.showwarning("Editar categoría", "Debe seleccionar una categoría.", parent=window)
            return
        if not new_name:
            tkinter.messagebox.showwarning("Editar categoría", "El nuevo nombre no puede estar en blanco.", parent=window)
            new_name_entry.focus_set()
            return
        if utils.normalize_text(name) == utils.normalize_text(new_name):
            tkinter.messagebox.showwarning("Editar categoría", "Los nombres son iguales. Las mayúsculas, minúsculas y acentos no hacen la diferencia.", parent=window)
            new_name_entry.focus_set()
            return
        if not category_dao.exist(name):
            tkinter.messagebox.showwarning("Editar categoría", "La categoría no existe.", parent=window)
            new_name_entry.focus_set()
            return
        if category_dao.exist(new_name):
            tkinter.messagebox.showwarning("Editar categoría", f"La categoría '{new_name}' ya existe.", parent=window)
            new_name_entry.focus_set()
            return
        try:
            result: int | None = category_dao.update(name, new_name)
            if result is None or result <= 0:
                raise RuntimeError(f"Falló la modificada de la categoría: {name}")
            tkinter.messagebox.showinfo("Editar categoría", f"Categoría '{name} → {new_name}' modificada correctamente.", parent=window)
            window.destroy()
        except Exception:
            traceback.print_exc()
            tkinter.messagebox.showerror("Editar categoría", "Ocurrió un error al actualizar la categoría.", parent=window)

    window: tkinter.Toplevel = tkinter.Toplevel(parent)
    window.title("Editar categoría")
    window.resizable(False, False)
    utils.center_window(window, 440, 210)
    window.transient(parent)
    window.grab_set()

    frame: tkinter.Frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both", padx=25, pady=15)
    frame.columnconfigure(1, weight=1)

    tkinter.Label(frame, text="Editar categoría", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 12))

    tkinter.Label(frame, text="Categoría:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=3)
    category_entry: tkinter.Entry = tkinter.Entry(frame, state="readonly")
    category_entry.grid(row=1, column=1, sticky="ew", pady=3)
    tkinter.Button(frame, text="Buscar", width=8, command=search_category).grid(row=1, column=2, padx=(5, 0), pady=3)

    tkinter.Label(frame, text="Nuevo nombre:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=3)
    new_name_entry: tkinter.Entry = tkinter.Entry(frame)
    new_name_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=3)

    button_frame: tkinter.Frame = tkinter.Frame(frame)
    button_frame.grid(row=3, column=0, columnspan=3, pady=(12, 0))

    tkinter.Button(button_frame, text="Guardar", width=10, command=update_category).pack(side="left", padx=5)
    tkinter.Button(button_frame, text="Cancelar", width=10, command=window.destroy).pack(side="left", padx=5)

    window.bind("<Return>", lambda event: update_category())
    window.bind("<Escape>", lambda event: window.destroy())
    window.after_idle(lambda: window.focus_force())