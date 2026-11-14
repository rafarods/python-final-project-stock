import tkinter
import tkinter.messagebox
import tkinter.simpledialog
import traceback
import modules.dao.category_dao as category_dao

def show(parent: tkinter.Tk) -> None:
    """
    Solicitud para crear una categoría.
    """
    
    name: str | None = tkinter.simpledialog.askstring("Crear categoría", "Nombre:", parent=parent)
    if not name:
        return
    name = name.strip()
    if not name:
        tkinter.messagebox.showwarning("Crear categoría", "El nombre no puede estar en blanco.", parent=parent)
        return
    if category_dao.exist(name):
        tkinter.messagebox.showwarning("Crear categoría", f"La categoría '{name}' ya existe.", parent=parent)
        return
    try:
        result: int | None = category_dao.insert(name)
        if result is None or result <= 0:
            raise RuntimeError(f"Falló la creación de la categoría: {name}")
        tkinter.messagebox.showinfo("Crear categoría", f"Categoría '{name}' creada correctamente.", parent=parent)
    except Exception:
        traceback.print_exc()
        tkinter.messagebox.showerror("Crear categoría", "Ocurrió un error al crear la categoría.", parent=parent)