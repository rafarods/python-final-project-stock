import tkinter
import tkinter.messagebox
import tkinter.simpledialog
import traceback
import modules.dao.category_dao as category_dao

def show(parent: tkinter.Tk) -> None:
    """Solicitud para eliminar una categoría."""
    name: str | None = tkinter.simpledialog.askstring("Eliminar categoría", "Nombre:", parent=parent)
    if not name:
        return
    name = name.strip()
    if not name:
        tkinter.messagebox.showwarning("Eliminar categoría", "El nombre no puede estar en blanco.", parent=parent)
        return
    if not category_dao.exist(name):
        tkinter.messagebox.showwarning("Eliminar categoría", f"La categoría '{name}' no existe.", parent=parent)
        return
    if category_dao.has_products(name):
        tkinter.messagebox.showwarning("Eliminar categoría", f"No puede eliminar la categoría '{name}' porque posee productos relacionados.", parent=parent)
        return
    try:
        result: int | None = category_dao.delete(name)
        if result is None or result <= 0:
            raise RuntimeError(f"Falló la eliminación de la categoría: {name}")
        tkinter.messagebox.showinfo("Eliminar categoría", f"Categoría '{name}' eliminanda correctamente.", parent=parent)
    except Exception:
        traceback.print_exc()
        tkinter.messagebox.showerror("Eliminar categoría", "Ocurrió un error al eliminar la categoría.", parent=parent)